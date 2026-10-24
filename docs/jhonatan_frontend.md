# Documentación del frontend asignado a Jhonatan

## Alcance

Según el reparto del equipo, a Jhonatan Alexander Poz le corresponden las vistas de **Preparación**, **Procedimiento**, **Resultados** e **Historial**, además de su presentación UX/UI y su conexión con la API. Esta documentación describe ese alcance en el código actual.

El frontend concentra varias responsabilidades en `frontend/app/src/App.jsx`; por eso el archivo no pertenece por completo a una sola persona. La captura y validación del modelo corresponden a Dulce. La preparación matemática y las iteraciones corresponden a Shelsi y Diana. La API y la persistencia corresponden a Kevin. Las vistas de Jhonatan muestran o consumen esos datos.

## Archivos relacionados

| Archivo | Relación con el trabajo de Jhonatan |
| --- | --- |
| [`App.jsx`](../frontend/app/src/App.jsx) | Contiene `PreparationView`, `ProcedureView`, `ResultView` e `HistoryView`, componentes compartidos y el estado que conecta las vistas. |
| [`styles.css`](../frontend/app/src/styles.css) | Define el sistema visual común: tema oscuro, tarjetas, tablas, navegación, pasos, estados y reglas adaptables. Jhonatan y Dulce coordinan el estilo. |
| [`overrides.css`](../frontend/app/src/overrides.css) | Ajusta estilos compartidos, incluido el resaltado de la fila saliente y la legibilidad de controles. |
| [`main.jsx`](../frontend/app/src/main.jsx) | Punto de entrada común de React; registra Mantine y los estilos antes de montar `App`. |
| [`kevin_9365_api.js`](../frontend/js/kevin_9365_api.js) | Cliente HTTP del backend, mantenido en el módulo de Kevin. `App.jsx` lo invoca a través de `request`; no implementa el motor ni la base de datos. |

## Recorrido de las vistas

### 1. Preparación

Implementada en [`PreparationView`](../frontend/app/src/App.jsx#L185). Recibe el modelo original (`payload`), la respuesta de resolución (`result`) y una acción para continuar.

- `ModelCard` muestra la función objetivo, las restricciones originales y la no negatividad.
- `prettyEquation` presenta las filas de forma estándar recibidas del backend.
- Resume la base inicial, las variables de holgura, exceso y artificiales.
- Advierte cuando el backend indica que invirtió signos por un lado derecho negativo.
- Renderiza `result.tabla_inicial` con el componente compartido `Tableau` y muestra si comienza en Fase I o Fase II.
- El botón **Ver procedimiento** cambia a la vista de iteraciones y coloca el índice en la primera tabla.

Esta vista presenta la preparación que entrega el módulo de Shelsi a través del backend; no la calcula en el navegador.

### 2. Procedimiento

Implementado en [`ProcedureView`](../frontend/app/src/App.jsx#L218). Trabaja con `result.tablas` y el índice `tableIndex` que guarda `App`.

- Muestra la tabla actual, su número y la fase.
- Permite retroceder, avanzar o elegir una tabla desde la línea de tiempo.
- Si la tabla registra un pivote, busca la tabla anterior mediante `pivote.tabla_antes`.
- Ubica la celda del pivote usando `filas_ids` y `columnas`; no deduce la posición a partir del texto que ve el usuario.
- Presenta las variables entrante y saliente, el valor del pivote y las razones calculadas por el motor.
- Identifica la razón mínima válida y marca como excluidas las filas cuya razón llega como `null`.
- Muestra las operaciones guardadas en `tabla.operaciones` junto con la tabla resultante.
- Al llegar a la última tabla, habilita **Ver resultado**.

La selección del pivote y las operaciones las produce el motor de Diana. La vista las ordena y explica visualmente; no vuelve a calcularlas.

### 3. Resultados

Implementada en [`ResultView`](../frontend/app/src/App.jsx#L248). Recibe el modelo, el resultado y el estado de guardado.

- Traduce los estados técnicos mediante `statusLabels` y `statusDescriptions`.
- Cuando el estado es `optimal`, muestra el valor de Z, las variables de decisión y `result.comprobacion`.
- Para estados no óptimos no presenta valores de solución inventados; muestra la interpretación del estado reportado.
- Conserva a la vista el modelo original para contrastarlo con el cálculo.
- Muestra si el resultado ya está guardado y ofrece **Guardar en historial** cuando corresponde.

### 4. Historial

Implementada en [`HistoryView`](../frontend/app/src/App.jsx#L266). Mantiene sus filtros y estados de carga locales al componente.

- Busca por nombre y filtra por sentido (MAX/MIN) y estado.
- Actualiza la lista desde la API con límite de 100 registros. La búsqueda se retrasa 220 ms y cancela consultas anteriores si el usuario cambia rápidamente los filtros.
- Distingue carga, lista vacía y errores de consulta.
- Ofrece **Abrir**, **Duplicar** y **Eliminar**. El borrado pide confirmación antes de solicitarlo al servidor.
- Muestra el estado, la fecha, el número de variables y restricciones y, si es óptimo, el valor de Z.
- La clave de escritura, si se requiere, se conserva en `sessionStorage` durante la sesión del navegador.

El almacenamiento y las rutas son responsabilidad del backend de Kevin. La vista consume los registros que ese backend devuelve.

## Coordinación del estado en `App`

El componente [`App`](../frontend/app/src/App.jsx#L303) coordina las vistas y el intercambio con los otros módulos:

1. `solve()` verifica el formulario, envía el modelo a `/api/resolver` mediante el cliente común y, si recibe una respuesta, abre Preparación.
2. Al continuar desde Preparación, cambia a Procedimiento y reinicia `tableIndex`.
3. Al avanzar desde la última tabla, cambia a Resultados.
4. `save()` crea o actualiza el registro y pide al servidor resolver el modelo guardado; luego marca el resultado como persistido.
5. `openRecord()` recupera el modelo y el resultado para reabrir un registro. `duplicateRecord()` solicita una copia y la abre. `deleteRecord()` elimina el registro mediante la API.
6. La navegación mantiene disponibles Modelo e Historial. Preparación, Procedimiento y Resultados se habilitan cuando existe un cálculo vigente. Si se edita la entrada, el resultado previo queda marcado como desactualizado.

La función `request()` adapta las rutas relativas y entrega las solicitudes al cliente de Kevin. Los endpoints y el formato de datos deben coordinarse con ese módulo; la interfaz no reemplaza la validación del servidor.

## Datos que las vistas esperan

Los siguientes campos se observan en el consumo actual de `App.jsx`. El backend debe seguir entregándolos para que cada sección pueda presentarlos correctamente.

| Vista | Datos utilizados |
| --- | --- |
| Preparación | `preparacion.variables`, `filas`, `relaciones_normalizadas`, `rhs`, `base`, `holguras`, `excesos`, `artificiales`, `signos_invertidos`, `convencion`; además `tabla_inicial`. |
| Tabla | `columnas`, `valores`, `base`, `filas_ids` y `fase`. |
| Procedimiento | `tablas[]`; cada tabla puede incluir `fase`, `pivote`, `operaciones`, `columnas` y `filas_ids`. El pivote incluye `fila`, `columna`, `saliente`, `valor`, `razones` y `tabla_antes`. |
| Resultado | `estado`, `fase`, `objetivo`, `variables` y `comprobacion`. Cada comprobación usa `fila`, `lhs`, `signo`, `rhs` y `cumple`. |
| Historial | Registros con `id`, `nombre`, `sentido`, `estado`, `creado`, `modelo` y `resultado`. |

## Presentación y UX/UI

Las vistas usan componentes de Mantine como tarjetas, tablas, alertas, badges, botones y controles; Tabler aporta iconos. `ViewHeading`, `StatCard`, `ModelCard` y `Tableau` son piezas compartidas, no módulos exclusivos de Jhonatan.

Las clases `.surface-card`, `.tableau`, `.pivot-cell`, `.leaving-row`, `.timeline-step` y `.operation-line` conectan las vistas con el estilo común. Las tablas anchas y la línea de iteraciones permiten desplazamiento horizontal; las rejillas cambian columnas en tamaños menores. Esto describe las reglas implementadas en CSS, no certifica que se haya completado una prueba móvil.

Los números se formatean para lectura con `numberText`. El formato visual no altera los valores que conserva la respuesta del motor.

## Qué está implementado y qué debe comprobarse

El código contiene las cuatro vistas asignadas y sus controles de navegación, representación de tablas, estados y acciones del historial. Eso confirma su presencia en la interfaz; no demuestra por sí solo que la integración completa se haya probado.

Para cerrar la comprobación conjunta, el equipo debe verificar que:

- La API entregue los campos descritos arriba para los casos MAX, MIN y dos fases.
- Los índices del pivote correspondan a la tabla anterior y las razones excluidas lleguen diferenciadas de las válidas.
- Las operaciones mostradas sean las que registró Diana, sin reconstruirlas desde la tabla final.
- Un resultado óptimo incluya la comprobación de restricciones y los estados infactible/no acotado no expongan una solución numérica.
- Guardar, filtrar, abrir, duplicar y eliminar reflejen los datos persistidos por Kevin.
- Navegación, tablas anchas y controles mantengan legibilidad en móvil.

Esta guía documenta el código y el reparto de Jhonatan; no atribuye a Jhonatan el formulario de Dulce, el cálculo matemático de Shelsi o Diana ni la API/base de datos de Kevin.
