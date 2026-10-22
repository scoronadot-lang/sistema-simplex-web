"""Pruebas de infraestructura real. No sustituye el motor pendiente por uno falso."""
import os
from importlib import import_module

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select

from backend.kevin_9365_api import crear_app
from backend.kevin_9365_bd import ModeloGuardado, conectar, inicializar, normalizar_url

MAX = dict(nombre='Prueba Kevin', sentido='max', objetivo=[5, 4, 3], restricciones=[
    dict(coeficientes=[2, 3, 1], signo='<=', rhs=5),
    dict(coeficientes=[4, 1, 2], signo='<=', rhs=11),
    dict(coeficientes=[3, 4, 2], signo='<=', rhs=8),
])
MIN = dict(nombre='Dos fases Kevin', sentido='min', objetivo=[2, 3], restricciones=[
    dict(coeficientes=[1, 1], signo='>=', rhs=4),
    dict(coeficientes=[1, 2], signo='<=', rhs=10),
])


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.delenv('HISTORY_WRITE_KEY', raising=False)
    with TestClient(crear_app('sqlite:///' + str(tmp_path / 'api.db'))) as c:
        yield c


def test_salud_y_arranque_sin_interfaz(client):
    data = client.get('/api/health').json()
    assert data['status'] == 'ok' and data['database'] == 'sqlite'
    assert data['preparacion'] == 'available'
    assert client.get('/').status_code == 200
    assert client.get('/docs').status_code == 200
    assert client.get('/.env').status_code == 404


def test_preparacion_real_existente(client):
    r = client.post('/api/preparar', json=MIN)
    assert r.status_code == 200
    data = r.json()
    assert data['variable_names'] == ['a', 'b', 's2', 'e1', 'A1']
    assert data['rows'] == [[1, 1, 0, -1, 1], [1, 2, 1, 0, 0]]
    assert data['phase_one_objective'] == [0, 0, 0, 0, -1]


def test_rhs_negativo_se_delega_a_preparacion(client):
    m = dict(MIN, restricciones=[dict(coeficientes=[-1, -2], signo='<=', rhs=-6)])
    data = client.post('/api/preparar', json=m).json()
    assert data['rows'] == [[1, 2, -1, 1]]
    assert data['rhs'] == [6]


def recorrido_crud(url):
    ids = []
    try:
        with TestClient(crear_app(url)) as c:
            r = c.post('/api/modelos', json=MAX)
            assert r.status_code == 201
            data = r.json()
            id = data['id']; ids.append(id)
            assert data['estado'] == 'pending' and data['resultado'] is None
            assert c.get('/api/modelos/' + id).json()['modelo'] == MAX
            registros = c.get('/api/modelos', params={'q': 'Prueba Kevin', 'sentido': 'max', 'estado': 'pending'}).json()
            assert any(r['id'] == id for r in registros)
            assert c.put('/api/modelos/' + id, json=MIN).json()['modelo'] == MIN
            assert c.get('/api/modelos', params={'q': 'Prueba Kevin', 'sentido': 'max'}).status_code == 200
            copia = c.post('/api/modelos/' + id + '/duplicar')
            assert copia.status_code == 201
            copia = copia.json(); ids.append(copia['id'])
            assert copia['id'] != id and copia['nombre'].endswith('(copia)')
            assert copia['resultado'] is None and copia['estado'] == 'pending'
            assert c.delete('/api/modelos/' + copia['id']).status_code == 204
            assert c.get('/api/modelos/' + copia['id']).status_code == 404
        # Reabrir la aplicación conserva los datos en disco/base externa.
        with TestClient(crear_app(url)) as c:
            data = c.get('/api/modelos/' + id).json()
            assert data['modelo'] == MIN and data['resultado'] is None
    finally:
        with TestClient(crear_app(url)) as c:
            for id in ids:
                c.delete('/api/modelos/' + id)  # Solo UUID creados por esta prueba.


def test_sqlite_crud_y_reinicio(tmp_path):
    recorrido_crud('sqlite:///' + str(tmp_path / 'persistencia.db'))


def test_busqueda_literal_y_paginacion(client):
    for nombre in ['Kevin 100%', 'Kevin normal', 'Kevin final']:
        assert client.post('/api/modelos', json=dict(MAX, nombre=nombre)).status_code == 201
    assert len(client.get('/api/modelos?q=%25').json()) == 1  # % literal, no comodín SQL.
    pagina1 = client.get('/api/modelos?limite=1&offset=0').json()
    pagina2 = client.get('/api/modelos?limite=1&offset=1').json()
    assert len(pagina1) == len(pagina2) == 1
    assert pagina1[0]['id'] != pagina2[0]['id']


@pytest.mark.parametrize('cambios', [
    {'nombre': '  '}, {'sentido': 'otro'}, {'objetivo': [1]}, {'objetivo': [1, 2]},
    {'objetivo': ['5', 4, 3]}, {'objetivo': [True, 4, 3]}, {'objetivo': [1e10, 4, 3]},
    {'restricciones': []}, {'dato_no_admitido': 1},
    {'restricciones': [dict(coeficientes=[1, 1, 1], signo='<', rhs=2)]},
])
def test_validacion_422_sin_motor(client, cambios):
    r = client.post('/api/modelos', json=dict(MAX, **cambios))
    assert r.status_code == 422
    assert client.get('/api/modelos').json() == []


def test_infinito_rechazado(client):
    texto = '{"sentido":"max","objetivo":[1e999,1],"restricciones":[{"coeficientes":[1,1],"signo":"<=","rhs":2}]}'
    assert client.post('/api/modelos', content=texto, headers={'Content-Type': 'application/json'}).status_code == 422


def test_clave_escritura(tmp_path, monkeypatch):
    monkeypatch.setenv('HISTORY_WRITE_KEY', 'clave-de-prueba-local')
    with TestClient(crear_app('sqlite:///' + str(tmp_path / 'clave.db'))) as c:
        assert c.post('/api/modelos', json=MAX).status_code == 403
        headers = {'X-History-Key': 'clave-de-prueba-local'}
        id = c.post('/api/modelos', json=MAX, headers=headers).json()['id']
        assert c.get('/api/modelos/' + id).status_code == 200
        assert c.put('/api/modelos/' + id, json=MIN).status_code == 403
        assert c.post('/api/modelos/' + id + '/duplicar').status_code == 403
        assert c.delete('/api/modelos/' + id).status_code == 403


def test_inicializacion_idempotente(tmp_path):
    engine, Session = conectar('sqlite:///' + str(tmp_path / 'schema.db'))
    try:
        inicializar(engine)
        with Session.begin() as s:
            s.add(ModeloGuardado(id='registro-propio', nombre='Persistente', sentido='max',
                                estado='pending', modelo=MAX, resultado=None))
        inicializar(engine)
        with Session() as s:
            assert len(list(s.scalars(select(ModeloGuardado)))) == 1
    finally:
        engine.dispose()


def test_postgresql_controlador_y_tls():
    url = normalizar_url('postgres://ejemplo:ejemplo@localhost/pruebas?sslmode=require')
    assert url == 'postgresql+psycopg://ejemplo:ejemplo@localhost/pruebas?sslmode=require'
    e = create_engine(url)
    assert e.dialect.name == 'postgresql' and e.dialect.driver == 'psycopg'
    assert e.url.query['sslmode'] == 'require'
    e.dispose()


MOTOR_DISPONIBLE = callable(getattr(import_module('backend.simplex.simplex'), 'resolver', None))


@pytest.mark.skipif(MOTOR_DISPONIBLE, reason='El motor ya fue integrado; ejecutar prueba matemática real.')
def test_motor_ausente_responde_503_sin_resultados_ficticios(client):
    assert client.post('/api/resolver', json=MAX).status_code == 503
    id = client.post('/api/modelos', json=MAX).json()['id']
    r = client.post('/api/modelos/' + id + '/resolver')
    assert r.status_code == 503 and 'Motor pendiente' in r.json()['detail']
    guardado = client.get('/api/modelos/' + id).json()
    assert guardado['estado'] == 'pending' and guardado['resultado'] is None


@pytest.mark.skipif(not MOTOR_DISPONIBLE, reason='BLOQUEADA: falta resolver(modelo) en backend/simplex/simplex.py')
@pytest.mark.parametrize('m,z', [(MAX, 13), (MIN, 8)])
def test_motor_real_y_persistencia_de_iteraciones(client, m, z):
    r = client.post('/api/resolver', json=m)
    assert r.status_code == 200
    assert r.json()['estado'] == 'optimal' and r.json()['objetivo'] == pytest.approx(z)
    assert r.json()['tablas']
    id = client.post('/api/modelos', json=m).json()['id']
    r = client.post('/api/modelos/' + id + '/resolver')
    assert r.status_code == 200 and r.json()['resultado']['tablas']
    assert client.get('/api/modelos/' + id).json()['resultado']['objetivo'] == pytest.approx(z)
    # Una edición debe invalidar las iteraciones previas.
    editado = client.put('/api/modelos/' + id, json=dict(m, nombre='Editado')).json()
    assert editado['estado'] == 'pending' and editado['resultado'] is None


@pytest.mark.skipif(not os.getenv('TEST_DATABASE_URL'), reason='Falta PostgreSQL exclusivo de pruebas en TEST_DATABASE_URL')
def test_postgresql_real():
    url = normalizar_url(os.environ['TEST_DATABASE_URL'])
    assert url.startswith('postgresql+psycopg://'), 'TEST_DATABASE_URL debe apuntar a PostgreSQL aislado.'
    recorrido_crud(url)
