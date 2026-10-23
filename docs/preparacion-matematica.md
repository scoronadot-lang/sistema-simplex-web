# Shelsi 11504 - Documentación del módulo de preparación matemática del método símplex

## 1. Objetivo

El objetivo de este módulo es preparar los modelos de programación lineal para que puedan resolverse mediante el método símplex. Para ello, se transforma el modelo a una forma adecuada, se identifican las variables auxiliares que sean necesarias y se prepara la información que se utilizará durante la primera fase del algoritmo.

## 2. Forma estándar

La forma estándar permite representar las restricciones del problema mediante ecuaciones. Dependiendo del tipo de restricción, se pueden agregar variables de holgura, exceso o artificiales.

También es importante revisar el signo del lado derecho de las restricciones. Si es negativo, puede ser necesario multiplicar toda la restricción por -1 e invertir el sentido de la desigualdad.

## 3. Variables auxiliares

Las variables auxiliares se utilizan para convertir las desigualdades en ecuaciones y facilitar el procedimiento del método símplex.

- **Variables de holgura:** se utilizan generalmente en restricciones de tipo menor o igual que.
- **Variables de exceso:** se restan en restricciones de tipo mayor o igual que.
- **Variables artificiales:** se agregan cuando es necesario obtener una base inicial para comenzar el algoritmo.

## 4. Preparación de la fase I

La fase I busca obtener una solución básica factible para el problema original. Para ello, se utiliza una función auxiliar relacionada con las variables artificiales.

Cuando la fase I termina correctamente, se debe comprobar si es posible continuar con la fase II. Si las variables artificiales no pueden eliminarse hasta obtener una solución factible, el modelo original no tiene una solución factible bajo las restricciones definidas.

## 5. Archivos del módulo

- `backend/simplex/standard_form.py`: contiene la preparación del modelo y la transformación de las restricciones.
- `backend/simplex/phase_one.py`: contiene la preparación correspondiente a la primera fase.
- `backend/simplex/simplex.py`: se utilizará para la lógica general del método símplex, de acuerdo con la distribución de tareas del equipo.
- `backend/tests/`: contiene las pruebas que permiten comprobar los resultados del módulo.

Los nombres y las responsabilidades exactas deben coincidir con el código implementado en el proyecto.

## 6. Pruebas realizadas

Las pruebas deben comprobar que las restricciones se transformen correctamente, que las variables auxiliares se agreguen cuando corresponda, que se manejen los lados derechos negativos y que se detecten entradas inválidas.

En esta sección se registrarán los resultados reales obtenidos al ejecutar las pruebas automatizadas.

## 7. Conclusión

La preparación matemática es una parte importante del sistema porque permite organizar los datos del modelo antes de aplicar las iteraciones del método símplex. Una transformación correcta ayuda a evitar errores en las fases posteriores y facilita la integración con los demás componentes del proyecto.

## Construcción de la base y del tableau inicial

Como parte de la preparación matemática del método símplex, se desarrolló un módulo encargado de construir la base inicial y el tableau que utilizará el algoritmo de resolución.

Primero se transforman las restricciones a forma estándar, incorporando variables de holgura, exceso y artificiales cuando corresponda. Después se identifican las variables básicas iniciales y se comprueba que sus columnas formen una matriz identidad.

El módulo `initial_tableau.py` recibe la matriz de restricciones, los valores del lado derecho, los nombres de las variables, la base inicial y los coeficientes de la función objetivo.

Cuando no existen variables artificiales, el tableau queda preparado para comenzar directamente la Fase II del método símplex.

Cuando existen variables artificiales, se construye la función objetivo auxiliar de la Fase I, que busca minimizar la suma de dichas variables. Para utilizar una convención de maximización, el módulo trabaja con el negativo de esa suma.

La conexión con el algoritmo de iteraciones se realiza mediante la matriz del tableau, la lista ordenada de variables y la base inicial. El módulo de iteraciones deberá actualizar estos datos después de cada pivote.

Al terminar la Fase I, se debe comprobar que el valor óptimo auxiliar sea cero. Después de retirar las variables artificiales de la base, se reconstruye la fila de la función objetivo original para continuar con la Fase II.

Esta separación permite que el módulo de preparación matemática se integre con el algoritmo de iteraciones y con la API del proyecto sin duplicar sus responsabilidades.

## Responsable de la preparación matemática

Desarrollado por: shelsi_11504.

Esta parte del proyecto se encarga de preparar el modelo de programación lineal, convertir las restricciones a forma estándar e identificar las variables auxiliares necesarias para las fases del método símplex.