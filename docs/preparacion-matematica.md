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

## Contrato de integración con los demás módulos

El módulo de preparación matemática proporciona una función llamada `preparar_modelo`, ubicada en `backend/simplex/preparation.py`.

Esta función recibe una matriz de restricciones previamente convertida a forma estándar, el vector del lado derecho, los nombres de las variables, la base inicial, los coeficientes de la función objetivo y la lista de variables artificiales.

La función devuelve un diccionario con los siguientes campos:

- `variables`: nombres ordenados de las columnas.
- `base`: variables básicas iniciales.
- `tableau`: matriz inicial, incluyendo la fila objetivo y el lado derecho.
- `fase`: número de fase con la que debe comenzar el algoritmo.
- `artificiales`: variables artificiales que deberán eliminarse.
- `estado`: descripción de la preparación realizada.

El algoritmo de iteraciones debe utilizar la base y el tableau proporcionados para realizar las operaciones de pivoteo.

Cuando el modelo requiera Fase I, el algoritmo debe resolver primero la función objetivo auxiliar. Si su valor óptimo es cero, se podrá preparar la Fase II después de retirar las variables artificiales. Si el valor óptimo no es cero, el problema original no tiene solución factible.

La API podrá utilizar este contrato para recibir el modelo preparado y enviarlo al módulo de resolución.

## Base inicial, tableau y conexión con las fases del método símplex

La preparación matemática inicia con la conversión de las restricciones a forma estándar. Se normalizan los lados derechos y se incorporan variables de holgura, exceso y artificiales según el tipo de restricción.

Después se construye la base inicial. Esta debe contener una variable básica por cada restricción, y sus columnas deben formar una matriz identidad.

Con la base identificada se genera el tableau inicial, incluyendo los coeficientes de las restricciones, el lado derecho y la fila de la función objetivo expresada mediante la convención Zj − Cj.

**Conexión con la Fase I:** cuando existen variables artificiales, se construye una función objetivo auxiliar que busca minimizar su suma. El módulo entrega el tableau canónico de Fase I al algoritmo encargado de realizar las iteraciones.

**Conexión con la Fase II:** cuando no existen variables artificiales, el problema puede comenzar directamente con la función objetivo original. Si se necesitó Fase I, primero debe comprobarse que el valor óptimo auxiliar sea cero. Después se eliminan las variables artificiales y se reconstruye la fila objetivo original para continuar con Fase II.

**Integración con los demás integrantes:** el módulo `preparation.py` proporciona las variables, la base inicial, el tableau, la fase correspondiente y la identificación de variables artificiales. Estos datos serán utilizados por el módulo de iteraciones y posteriormente por la API del sistema.

La preparación matemática no realiza los pivoteos ni calcula por sí sola la solución óptima. Estas operaciones corresponden al algoritmo de resolución del método símplex.

## Responsable de la preparación matemática

Desarrollado por: shelsi_11504.

Esta parte del proyecto se encarga de preparar el modelo de programación lineal, convertir las restricciones a forma estándar e identificar las variables auxiliares necesarias para las fases del método símplex.