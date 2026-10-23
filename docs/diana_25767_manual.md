# Diana · Entrega adaptada diana_25767

Repositorio exclusivo: https://github.com/scoronadot-lang/sistema-simplex-web
Base comprobada: main 43b11cd4f75971374b058ca30bbd36f22e4f7c25. Paquete: entrega_diana_25767_adaptada.zip.
Responsabilidad asignada; código preparado con asistencia de IA. Revisión, comprensión y contribución personal todavía pendientes. No se han publicado estos cambios desde la cuenta de Kevin.

## Propósito, funciones y adaptación

La única implementación se entrega en backend/simplex/simplex.py y exporta resolver(modelo, *, max_iteraciones=1000). Importa phase_one.preparar. La API de Kevin ya carga este módulo: no necesita modificación. No subir el módulo diana_25767_simplex.py del paquete antiguo.

Símplex primal de dos fases, Bland, razones válidas, normalización y eliminación de pivote, registro de operaciones, artificiales redundantes, MAX/MIN y cinco estados terminales. Tolerancia 1e-9; comprobación final relativa 1e-7. Las pruebas incluyen degeneración y 100 modelos nuevos comparados con SciPy, sin usarlo en producción. max_iteraciones=0 certifica que un límite no se devuelve como óptimo. Explicar ante el docente la elección de entrante/saliente y U=-W / Y=-Z.

## Dependencias y pruebas

Requiere el paquete compartido y el de Shelsi integrados; SciPy se instala solo para pruebas.

Con el intérprete de .venv: `python -m pytest tests/test_diana_25767_simplex.py -q`. En PowerShell sustituir `python` por `.\.venv\Scripts\python.exe`.
La copia completa adaptada pasó 53 pruebas; dos se omiten: la prueba del motor ausente porque ya está presente y PostgreSQL real por falta de base de pruebas. El informe final de reconstrucción va en INFORME_ADAPTACION.md junto a los ZIP. No interpretar esos resultados como pruebas individuales realizadas por Diana.

## Archivos y ubicación exacta

- `backend/simplex/simplex.py`
- `tests/test_diana_25767_simplex.py`
- `docs/diana_25767_manual.md`

## Pasos para entregar desde su cuenta

1. Aceptar invitación a scoronadot-lang/sistema-simplex-web. En GitHub Desktop iniciar sesión con su cuenta personal y revisar identidad Git.
2. Clonar en ruta breve, por ejemplo C:\proyectos\sistema-simplex-web. Si ya existe clon, main → Fetch origin → Pull origin.
3. Esperar las dependencias indicadas y actualizar main otra vez. Crear rama `diana_25767` desde main. Si existe, revisarla y actualizarla sin borrar trabajo. Shelsi puede continuar feature/forma-estandar, incorporando main con un merge normal después de revisar conflictos.
4. Extraer entrega_diana_25767_adaptada.zip primero en una carpeta temporal. Copiar su CONTENIDO a la raíz del clon, conservando backend/, frontend/, tests/ y docs/. No subir el ZIP ni una carpeta envolvente con nombre del integrante.
5. Revisar cada diferencia antes de sobrescribir archivos existentes, especialmente si main avanzó desde la base comprobada. No reemplazar cambios nuevos de otros compañeros.
6. Instalar backend/requirements-dev.txt en .venv según README y ejecutar la prueba indicada; al estar los cinco aportes, ejecutar python -m pytest -q -rs.
7. Revisar Changes: solo estos archivos y modificaciones compartidas coordinadas. Excluir .env, .venv, bases y ZIP. Crear commit con mensaje que describa su revisión y cambios reales, reconociendo asistencia de IA.
8. Publish branch / Push origin → Create Pull Request con base main. Explicar propósito, pruebas reales y pendientes. Usar Draft si falta integración; solicitar revisión y no integrar sin comprobar dependencias.
9. Tras merge, todos actualizan main. No usar force push, cambiar autores ni crear commits vacíos para aparentar participación.

## Errores frecuentes

Imports ausentes: falta integrar un paquete anterior. ModuleNotFoundError: seleccionar el intérprete de .venv e instalar requisitos. DLL o WinError 206: usar clon corto o prefijo extendido de Windows. Conflictos: comparar ambas versiones y mantener el contrato; no aceptar toda una versión sin revisar. API 503: confirmar que el motor está integrado; 403: clave compartida; 422: revisar campos. Guardar pending no equivale a guardar tablas.
