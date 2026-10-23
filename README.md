# Sistema web para resolver programación lineal mediante el método símplex

## Descripción
Aplicación web para resolver problemas de programación lineal con restricciones, permitiendo maximizar o minimizar una función objetivo y visualizar las tablas del método símplex paso a paso.

## Funcionalidades
- Configuración de entre 2 y 6 variables de decisión.
- Ingreso y edición de restricciones lineales.
- Conversión a forma estándar.
- Preparación de variables de holgura, exceso y artificiales.
- Método de dos fases.
- Visualización de las tablas de cada iteración.
- Presentación de la solución y del estado del modelo.

## Estructura
- `frontend/`: interfaz web.
- `backend/simplex/`: preparación matemática y algoritmo símplex.
- `backend/tests/`: pruebas automatizadas.
- `database/`: componentes de persistencia.
- `docs/`: manual y documentación.

## Instalación
1. Instalar Python y Git.
2. Clonar el repositorio.
3. Crear y activar un entorno virtual.
4. Instalar las dependencias indicadas en `backend/requirements.txt`.
5. Ejecutar las pruebas.
6. Iniciar la API y la interfaz con los comandos de la sección siguiente.

## Interfaz web

La interfaz usa React, Vite y componentes de Mantine. Desde `frontend/`, instala las dependencias con `pnpm install` y genera la versión que sirve FastAPI con `pnpm build`. El build publica `frontend/index.html` y `frontend/assets/`, que deben acompañar al backend.

Para desarrollo, inicia la API desde la raíz del repositorio con `uvicorn backend.kevin_9365_api:app --reload --port 8000` y, en otra terminal, ejecuta `pnpm dev` dentro de `frontend/`. Vite entrega la interfaz en el puerto 5173 y envía `/api` al backend del puerto 8000.

## Estado del desarrollo
El proyecto continúa en desarrollo. Antes del despliegue, el equipo debe verificar las pruebas de integración y la configuración de la base de datos del entorno.
