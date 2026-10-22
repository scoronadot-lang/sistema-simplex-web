# Kevin 9365 · API, persistencia e integración pendiente

Este aporte corresponde a Kevin (`kmoralesm19UMG`) en **scoronadot-lang/sistema-simplex-web**, rama `kevin_9365`. Se adaptó con asistencia de IA a la estructura real del equipo. No incluye ni atribuye al coordinador los módulos de preparación, fase I, motor o vistas de sus compañeros. Cada integrante debe revisar y comprender su entrega. La aplicación completa de referencia permanece en otra carpeta local.

## Estado y alcance

La rama parte de `main` e7fb0cb y conserva los commits originales. Se revisó también `feature/forma-estandar` bb2a4a2, que añade README y documentación; no se integró ni sobrescribió esa rama. No se encontraron instrucciones AGENTS.md en el clon.

La preparación existente (`backend/simplex/standard_form.py`) sí se ejecuta realmente. `backend/main.py`, `backend/simplex/phase_one.py` y `backend/simplex/simplex.py` están vacíos en la base revisada. No existe todavía `frontend/index.html`. Por ello esta entrega ofrece API, preparación y persistencia de modelos, pero **el cálculo completo y la interfaz quedan pendientes del equipo**. No desplegar como aplicación completa ni dar por aprobadas las pruebas matemáticas del motor.

El repositorio alternativo del coordinador no es destino de esta rama. No se cambian archivos de Shelsi, Diana, Dulce o Jhonatan. El pull request se debe mantener como borrador hasta acordar el contrato e integrar el motor.

## Archivos de Kevin y ajustes compartidos

| Archivo | Responsabilidad |
|---|---|
| backend/kevin_9365_api.py | Esquemas, adaptador de preparación, API y carga diferida del motor |
| backend/kevin_9365_bd.py | SQLAlchemy, SQLite/PostgreSQL e inicialización idempotente |
| frontend/js/kevin_9365_api.js | Cliente relativo /api, clave explícita y errores por campo |
| database/kevin_9365_esquema_postgresql.sql | Esquema PostgreSQL equivalente |
| tests/test_kevin_9365_api_bd.py | API/SQLite reales, preparación existente, pruebas de integración bloqueadas |
| docs/kevin_9365_instalacion_despliegue.md | Instalación, contratos, pruebas y despliegue futuro |

Ajustes compartidos mínimos: `backend/requirements.txt` agrega SQLAlchemy, Psycopg y dotenv y fija versiones probadas, conservando pytest existente; `backend/requirements-dev.txt` agrega httpx para pruebas; `.gitignore` excluye SQLite, ZIP, registros y temporales; `.env.example` contiene únicamente variables de ejemplo; `pytest.ini` permite probar desde la raíz tanto `backend/tests/` existente como `tests/` sin alterar imports de los compañeros. No se cambia README para evitar conflicto con la documentación de `feature/forma-estandar`.

## Instalación local Windows / PowerShell

Usar Python 3.12 de 64 bits y Git. Se verificó Python 3.12.14. Clonar preferentemente en una ruta corta como `C:\proyectos\sistema-simplex-web`; rutas largas de Windows pueden impedir instalar/importar extensiones binarias. No copiar entornos virtuales entre computadoras.

Desde la raíz del clon, después de cambiar a la rama `kevin_9365`:

```powershell
py -3.12 --version
git --version
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m backend.kevin_9365_bd
.\.venv\Scripts\python.exe -m uvicorn backend.kevin_9365_api:app --host 127.0.0.1 --port 8001
```

No sobrescribir un .env que ya tenga configuración. Se usa 8001 para no interferir con la aplicación local completa en 8000. Abrir http://127.0.0.1:8001/docs y http://127.0.0.1:8001/api/health. La raíz devuelve un mensaje de API pendiente de interfaz, no un diseño inventado. Al existir el índice del equipo, la API lo servirá junto a sus recursos. Ctrl+C detiene el servicio. No se requiere activar .venv ni cambiar ExecutionPolicy.

El .env se carga **solo desde la raíz de este clon**, sin buscar el .env de la aplicación vecina. DATABASE_URL permite sobreescribir la conexión. SQLite predeterminado se crea en la raíz del clon; si se configura una ruta relativa en .env, ejecutar desde esa raíz. `inicializar` crea tablas ausentes y conserva registros; no es una herramienta de migración de esquemas ya existentes.

En esta máquina el clon anidado tiene una ruta excepcionalmente larga. Se instaló y ejecutó usando el prefijo extendido de Windows `\\?\` con un Python auxiliar ya disponible para gestionar pip. Si aparecen WinError 206 o DLL load failed por longitud, usar un clon corto o invocar el intérprete así:

```powershell
$pythonKevin = '\\?\' + (Join-Path (Get-Location) '.venv\Scripts\python.exe')
& $pythonKevin -m pytest -q -rs
```

## Contrato de captura, preparación y motor

Entrada JSON de la API:

```json
{"nombre":"Ejemplo MAX","sentido":"max","objetivo":[5,4,3],"restricciones":[{"coeficientes":[2,3,1],"signo":"<=","rhs":5},{"coeficientes":[4,1,2],"signo":"<=","rhs":11},{"coeficientes":[3,4,2],"signo":"<=","rhs":8}]}
```

Todas las variables son no negativas. Entre 2 y 6 variables y 1–40 restricciones. La cantidad de coeficientes de cada fila debe coincidir con el objetivo. Se rechazan campos desconocidos, booleanos, números como texto, no finitos y magnitudes mayores que 1e9. Los errores 422 incluyen `type`, `loc` y `msg`, sin reflejar valores potencialmente privados o no serializables.

`Modelo.preparar()` traduce `coeficientes/signo` a `coefficients/relation`, genera `variables=['a',...]` y llama al `prepare_standard_form` existente. La respuesta de `/api/preparar` conserva los campos reales de `StandardForm`: `variable_names`, `rows` (sin RHS), `rhs`, `relations_originales`, `slack_variables`, `surplus_variables`, `artificial_variables`, `phase_one_objective`. No cambia el orden real de columnas: variables originales, holguras, excesos y artificiales. Este orden difiere del paquete local anterior. `relations_originales` conserva los signos originales tal como hace el módulo actual.

**Dependencia por acordar con Diana y Shelsi:** el archivo ya existente `backend/simplex/simplex.py` debe exportar una función síncrona `resolver(modelo: dict) -> dict` que reciba el JSON validado anterior. La API usa ese punto de integración mediante import relativo y carga diferida; no importa ni copia `diana_25767_simplex.py` desde la aplicación local. Si el equipo elige otra firma, adaptar únicamente este punto y sus pruebas antes de integrar.

La respuesta real del motor deberá incluir:

- `estado`: optimal, infeasible, unbounded, iteration_limit o numerical_error.
- `fase`: 1 o 2; `variables`: mapa de a-f; `objetivo`: Z original si es optimal y null en otros estados.
- `tabla_inicial`, `tablas`: snapshots con columnas, IDs de filas estables, base y valores; fila OBJ arriba y RHS al final. Las tablas sucesivas conservan número y fase.
- `pivotes`: fila/columna entrante, variable saliente, valor, razones válidas y referencia a tabla anterior; operaciones por tabla para explicar normalización y eliminación.
- `comprobacion`: evaluación de cada restricción original; recomendable también `preparacion`.

No aceptar el límite de iteraciones como óptimo ni devolver valores prefijados de los ejemplos. U=-W en fase I; para MIN, convertir Y=-Z al objetivo original. El motor debe ejecutar sus propios cálculos y verificación; esta API no los implementa.

Mientras falte la función, `/api/resolver` y `/api/modelos/{id}/resolver` responden **503 con “Motor pendiente”**. Una respuesta de motor con campos obligatorios ausentes o estado inválido produce 502. La presencia de una función callable en health solo indica disponibilidad del punto de entrada, no certifica su corrección matemática.

## Guardar y resolver son acciones separadas

| Ruta | Comportamiento |
|---|---|
| GET /api/health | Conexión real a BD, estado del punto de entrada del motor y preparación |
| POST /api/preparar | Ejecutar preparación real de Shelsi |
| POST /api/resolver | Calcular sin guardar; 503 mientras falte motor |
| POST /api/modelos | Guardar entrada validada: estado pending, resultado null |
| GET /api/modelos | Buscar por q literal y filtrar sentido/estado, limite 1–200 y offset |
| GET /api/modelos/{id} | Recuperar entrada y resultado disponible |
| PUT /api/modelos/{id} | Reemplazar entrada e invalidar cualquier resultado anterior |
| POST /api/modelos/{id}/duplicar | Copiar la entrada con UUID nuevo, pendiente de resolver |
| POST /api/modelos/{id}/resolver | Calcular el registro y guardar resultado/iteraciones, cuando exista motor |
| DELETE /api/modelos/{id} | Eliminar ese registro; 404 si no existe |

Esta separación es una adaptación respecto del paquete original, que intentaba resolver automáticamente al guardar. Ahora se puede probar y usar la persistencia sin sustituir el motor ausente. Una resolución fallida no convierte el modelo pendiente en resuelto. Todas las escrituras usan transacciones. `modelo` y `resultado` JSON pertenecen a un registro UUID; no hay usuarios ni relaciones inventadas.

Frontend: importar `api` desde el archivo común; ejemplo `api('/modelos','POST',modelo,{historyKey:clave})`. El cliente no depende de un elemento DOM #clave todavía inexistente. Enviar la clave desde la captura cuando se configure; no almacenarla en código. El historial debe representar `pending`/resultado null sin intentar dibujar tablas. Para resolver y guardar resultado, llamar `/modelos/{id}/resolver`. El cliente conserva `error.status` y `error.detail` para mensajes por campo y 503.

HISTORY_WRITE_KEY es opcional y protege las escrituras; no crea cuentas ni privacidad de lectura. El historial sigue siendo compartido y legible. No guardar datos personales ni secretos en modelos.

## Pruebas y evidencias

```powershell
.\.venv\Scripts\python.exe -m pytest -q -rs
.\.venv\Scripts\python.exe -m pip check
```

La suite conserva las tres pruebas originales de preparación. Las pruebas de Kevin usan archivos SQLite temporales propios, llamadas HTTP a la API real y la preparación real existente. Comprueban CRUD, recarga tras reapertura de la aplicación, clave, validaciones, búsqueda literal, paginación, idempotencia y 503 sin motor. **No se incorpora un motor falso ni se simulan soluciones.**

Las dos pruebas de solución MAX/MIN y persistencia de iteraciones se marcan bloqueadas hasta que exista la función real; se ejecutarán automáticamente al integrarla. La prueba PostgreSQL requiere TEST_DATABASE_URL configurado de forma privada hacia una base exclusiva de pruebas. Solo elimina UUID creados por esa prueba, nunca tablas o datos ajenos. Verificar el controlador y la URL TLS sin conexión no equivale a haber probado PostgreSQL real.

Comprobación real en el clon, 22/10/2026: **23 passed, 3 skipped, 1 warning en 1.71 s**. Incluye las tres pruebas originales de Shelsi sin modificar. Omitidas: dos del motor real ausente y una de PostgreSQL sin TEST_DATABASE_URL. `pip check`: sin dependencias incompatibles. Advertencia: Starlette anuncia deprecación de su integración con httpx; no impide la ejecución. Evidencia JUnit local, excluida de Git: `evidencias/kevin_pruebas.xml`. El primer intento detectó que la respuesta de validación de un número infinito no era serializable; se corrigió omitiendo los valores de entrada en los errores 422 y la suite pasó. No se atribuyen a esta rama las pruebas de la aplicación completa anterior.

## Publicación futura, después de integrar

Kevin configura Neon Free con TLS y guarda DATABASE_URL únicamente en Environment de Render o .env privado. Usar `postgresql+psycopg://` (también se normalizan postgres:// y postgresql:// sin eliminar sslmode). SQLite se reserva para local. La API rechaza SQLite cuando detecta RENDER.

Render Web Service, raíz del repositorio, rama main **después de integrar y probar**, Python 3.12, plan Free: Build Command `pip install -r backend/requirements.txt`; Start Command `uvicorn backend.kevin_9365_api:app --host 0.0.0.0 --port $PORT`; Health Check `/api/health`. El esquema se inicializa sin borrar datos al arrancar. No se crea aquí un servicio ni se contrata un plan.

Al publicar: comprobar HTTPS, motor real, cuatro estados y entradas nuevas; guardar un modelo, resolverlo, recuperar sus tablas tras recarga y reinicio del servicio, y comprobar el mismo UUID en Neon. Render Free puede suspenderse y su disco es efímero; abrir antes de la exposición y conservar alternativa local. Confirmar las condiciones gratuitas vigentes antes de crear recursos. No usar pings artificiales.

Fuentes oficiales para verificar durante el despliegue: [Render Free](https://render.com/docs/free), [FastAPI en Render](https://render.com/docs/deploy-fastapi), [Neon Free](https://neon.com/pricing), [Conexión Neon](https://neon.com/docs/connect/connect-from-any-app).

## Explicar y defender el aporte

Kevin conecta la captura con la preparación existente, valida otra vez en el servidor y conserva datos reales mediante transacciones. Se puede demostrar guardar, consultar, modificar y duplicar sin atribuir un cálculo al motor que aún no existe. Las dependencias faltantes se muestran claramente; el equipo debe acordar el contrato y ejecutar las pruebas matemáticas antes de aprobar este borrador.
