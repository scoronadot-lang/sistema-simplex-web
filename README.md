# Shelsi 11504 - Sistema web para resolver programación lineal mediante el método símplex

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
6. Iniciar el servidor cuando la API esté integrada.

## Estado del desarrollo
El proyecto se encuentra en desarrollo. Los comandos definitivos de ejecución y los requisitos de la base de datos se documentarán al finalizar la integración.
