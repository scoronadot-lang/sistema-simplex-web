"""API de Kevin. La preparación usa el módulo existente; el motor es externo."""
from contextlib import asynccontextmanager
from dataclasses import asdict
from importlib import import_module
import os
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import select, text

from .kevin_9365_bd import ModeloGuardado, conectar, inicializar
from .simplex.standard_form import prepare_standard_form

Numero = Annotated[float, Field(strict=True, allow_inf_nan=False, ge=-1e9, le=1e9)]


class Restriccion(BaseModel):
    model_config = ConfigDict(extra='forbid')
    coeficientes: list[Numero] = Field(min_length=2, max_length=6)
    signo: Literal['<=', '>=', '=']
    rhs: Numero


class Modelo(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)
    nombre: str = Field(default='Sin título', min_length=1, max_length=120)
    sentido: Literal['max', 'min']
    objetivo: list[Numero] = Field(min_length=2, max_length=6)
    restricciones: list[Restriccion] = Field(min_length=1, max_length=40)

    @model_validator(mode='after')
    def dimensiones(self):
        if any(len(r.coeficientes) != len(self.objetivo) for r in self.restricciones):
            raise ValueError('Cada restricción debe tener tantos coeficientes como el objetivo.')
        return self

    def preparar(self):
        """Adaptar los nombres de captura al contrato real de Shelsi, sin modificarlo."""
        return prepare_standard_form(
            variables=list('abcdef'[:len(self.objetivo)]),
            constraints=[
                {'coefficients': r.coeficientes, 'relation': r.signo, 'rhs': r.rhs}
                for r in self.restricciones
            ],
        )


def cargar_motor():
    """El equipo debe implementar resolver(modelo) en su módulo existente."""
    funcion = getattr(import_module('.simplex.simplex', package=__package__), 'resolver', None)
    if not callable(funcion):
        raise HTTPException(
            503, 'Motor pendiente: backend/simplex/simplex.py debe implementar resolver(modelo). '
            'La preparación y el historial están disponibles; no se calculó una solución.',
        )
    return funcion


def calcular_modelo(modelo: Modelo) -> dict:
    resultado = cargar_motor()(modelo.model_dump())
    estados = {'optimal', 'infeasible', 'unbounded', 'iteration_limit', 'numerical_error'}
    if not isinstance(resultado, dict) or resultado.get('estado') not in estados:
        raise HTTPException(502, 'La respuesta del motor no cumple el contrato documentado.')
    requeridas = {'fase', 'variables', 'objetivo', 'tabla_inicial', 'tablas', 'pivotes', 'comprobacion'}
    if not requeridas <= resultado.keys():
        raise HTTPException(502, 'Faltan campos del procedimiento en la respuesta del motor.')
    if resultado['estado'] != 'optimal' and resultado['objetivo'] is not None:
        raise HTTPException(502, 'Un estado sin óptimo no puede incluir un valor óptimo.')
    return resultado


def crear_app(url: str | None = None):
    engine, Session = conectar(url)

    @asynccontextmanager
    async def lifespan(app):
        inicializar(engine)
        yield
        engine.dispose()

    app = FastAPI(title='Sistema Simplex · API de Kevin', lifespan=lifespan)

    @app.exception_handler(RequestValidationError)
    async def validacion_invalida(request, exc):
        # No reflejar entradas no finitas (JSON inválido) ni datos privados del usuario.
        errores = [{k: error[k] for k in ('type', 'loc', 'msg')} for error in exc.errors()]
        return JSONResponse(status_code=422, content={'detail': errores})

    def escritura(x_history_key: str | None = Header(default=None)):
        clave = os.getenv('HISTORY_WRITE_KEY', '')
        if clave and x_history_key != clave:
            raise HTTPException(403, 'Clave de historial incorrecta.')

    def serializar(r):
        return dict(id=r.id, nombre=r.nombre, sentido=r.sentido, estado=r.estado,
                    modelo=r.modelo, resultado=r.resultado, creado=r.creado.isoformat())

    def encontrar(s, id):
        r = s.get(ModeloGuardado, id)
        if not r:
            raise HTTPException(404, 'Modelo no encontrado.')
        return r

    def asignar(r, m):
        # Guardar un modelo sin resolver es real y no atribuye cálculos al motor ausente.
        r.nombre, r.sentido, r.modelo = m.nombre, m.sentido, m.model_dump()
        r.estado, r.resultado = 'pending', None

    @app.get('/api/health')
    def health():
        try:
            with engine.connect() as c:
                c.execute(text('SELECT 1'))
        except Exception:
            raise HTTPException(503, 'Base de datos no disponible.') from None
        motor = getattr(import_module('.simplex.simplex', package=__package__), 'resolver', None)
        return dict(status='ok', database=engine.dialect.name,
                    motor='available' if callable(motor) else 'pending', preparacion='available')

    @app.post('/api/preparar')
    def preparar(m: Modelo):
        return asdict(m.preparar())

    @app.post('/api/resolver')
    def calcular(m: Modelo):
        return calcular_modelo(m)

    @app.post('/api/modelos', status_code=201, dependencies=[Depends(escritura)])
    def guardar(m: Modelo):
        with Session.begin() as s:
            r = ModeloGuardado()
            asignar(r, m)
            s.add(r)
            s.flush()
            return serializar(r)

    @app.get('/api/modelos')
    def listar(q: str = Query('', max_length=120), sentido: Literal['max', 'min'] | None = None,
               estado: Literal['pending', 'optimal', 'infeasible', 'unbounded', 'iteration_limit', 'numerical_error'] | None = None,
               limite: int = Query(100, ge=1, le=200), offset: int = Query(0, ge=0)):
        stmt = select(ModeloGuardado)
        if q:
            stmt = stmt.where(ModeloGuardado.nombre.icontains(q, autoescape=True))
        if sentido:
            stmt = stmt.where(ModeloGuardado.sentido == sentido)
        if estado:
            stmt = stmt.where(ModeloGuardado.estado == estado)
        with Session() as s:
            return [serializar(r) for r in s.scalars(
                stmt.order_by(ModeloGuardado.creado.desc(), ModeloGuardado.id).offset(offset).limit(limite))]

    @app.get('/api/modelos/{id}')
    def obtener(id: str):
        with Session() as s:
            return serializar(encontrar(s, id))

    @app.put('/api/modelos/{id}', dependencies=[Depends(escritura)])
    def actualizar(id: str, m: Modelo):
        with Session.begin() as s:
            r = encontrar(s, id)
            asignar(r, m)  # Editar invalida cualquier resultado anterior.
            s.flush()
            return serializar(r)

    @app.post('/api/modelos/{id}/duplicar', status_code=201, dependencies=[Depends(escritura)])
    def duplicar(id: str):
        with Session.begin() as s:
            origen = encontrar(s, id)
            m = Modelo.model_validate(dict(origen.modelo, nombre=origen.nombre[:110] + ' (copia)'))
            r = ModeloGuardado()
            asignar(r, m)
            s.add(r)
            s.flush()
            return serializar(r)

    @app.post('/api/modelos/{id}/resolver', dependencies=[Depends(escritura)])
    def resolver_guardado(id: str):
        with Session.begin() as s:
            r = encontrar(s, id)
            resultado = calcular_modelo(Modelo.model_validate(r.modelo))
            r.resultado, r.estado = resultado, resultado['estado']
            s.flush()
            return serializar(r)

    @app.delete('/api/modelos/{id}', status_code=204, dependencies=[Depends(escritura)])
    def eliminar(id: str):
        with Session.begin() as s:
            s.delete(encontrar(s, id))

    # No inventar una interfaz ni requerir archivos de compañeros para arrancar la API.
    frontend = Path(__file__).resolve().parents[1] / 'frontend'
    if (frontend / 'index.html').is_file():
        app.mount('/', StaticFiles(directory=frontend, html=True), name='frontend')
    else:
        @app.get('/')
        def inicio():
            return dict(mensaje='API de Kevin disponible. Interfaz del equipo pendiente.', docs='/docs')

    return app


app = crear_app()
