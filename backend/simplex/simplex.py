"""Motor símplex primal de dos fases con regla de Bland."""

from copy import deepcopy
from math import isfinite

from .initial_tableau import preparar_fase_dos
from .preparation import preparar

EPS = 1e-9


def resolver(modelo, *, max_iteraciones=1000):
    """Resuelve un modelo y conserva las tablas y operaciones realizadas."""
    if (
        not isinstance(max_iteraciones, int)
        or isinstance(max_iteraciones, bool)
        or max_iteraciones < 0
    ):
        raise ValueError("max_iteraciones debe ser un entero no negativo.")

    p = preparar(modelo)
    columnas = list(p["columnas"])
    filas = deepcopy(p["filas"])
    base = list(p["base"])
    filas_ids = list(p["filas_ids"])
    artificiales = set(p["artificiales"])
    tablas = []
    pivotes = []
    fase = 1 if artificiales else 2
    objetivo = list(p["tabla_inicial"][-1])

    def registrar(operaciones=None, pivote=None):
        tablas.append({
            "numero": len(tablas),
            "fase": fase,
            "columnas": columnas + ["RHS"],
            "filas_ids": ["OBJ"] + filas_ids[:],
            "base": [columnas[indice] for indice in base],
            "valores": deepcopy([objetivo] + filas),
            "operaciones": operaciones or [],
            "pivote": pivote,
        })

    def pivotar(fila_pivote, columna_pivote, razones):
        nonlocal objetivo

        valor = filas[fila_pivote][columna_pivote]
        if not isfinite(valor) or abs(valor) <= EPS:
            raise ArithmeticError("No se puede pivotear con un valor nulo o no finito.")

        saliente = columnas[base[fila_pivote]]
        filas[fila_pivote] = [x / valor for x in filas[fila_pivote]]
        operaciones = [
            f"{filas_ids[fila_pivote]} ← {filas_ids[fila_pivote]} / {valor:.10g}"
        ]

        for indice, fila in enumerate(filas):
            if indice == fila_pivote:
                continue
            factor = fila[columna_pivote]
            filas[indice] = [
                x - factor * y for x, y in zip(fila, filas[fila_pivote])
            ]
            operaciones.append(
                f"{filas_ids[indice]} ← {filas_ids[indice]} - "
                f"({factor:.10g}) × {filas_ids[fila_pivote]}"
            )

        factor_objetivo = objetivo[columna_pivote]
        objetivo = [
            x - factor_objetivo * y
            for x, y in zip(objetivo, filas[fila_pivote])
        ]
        operaciones.append(
            f"OBJ ← OBJ - ({factor_objetivo:.10g}) × {filas_ids[fila_pivote]}"
        )

        base[fila_pivote] = columna_pivote
        pivote = {
            "fila": filas_ids[fila_pivote],
            "columna": columnas[columna_pivote],
            "valor": valor,
            "saliente": saliente,
            "razones": razones,
            "tabla_antes": len(tablas) - 1,
            "fase": fase,
        }
        pivotes.append(pivote)
        registrar(operaciones, pivote)

    def ejecutar_fase():
        while True:
            if not all(isfinite(valor) for fila in [objetivo] + filas for valor in fila):
                return "numerical_error"

            entrantes = [
                indice
                for indice, valor in enumerate(objetivo[:-1])
                if valor < -EPS and indice not in base
            ]
            if not entrantes:
                return "optimal"
            if len(pivotes) >= max_iteraciones:
                return "iteration_limit"

            # Regla de Bland: escoger el índice más pequeño que puede entrar.
            columna = min(entrantes)
            razones = {
                filas_ids[indice]: (
                    max(0.0, fila[-1]) / fila[columna]
                    if fila[columna] > EPS
                    else None
                )
                for indice, fila in enumerate(filas)
            }
            validas = [
                indice
                for indice in range(len(filas))
                if razones[filas_ids[indice]] is not None
            ]
            if not validas:
                return "unbounded"

            minimo = min(razones[filas_ids[indice]] for indice in validas)
            empatadas = [
                indice
                for indice in validas
                if abs(razones[filas_ids[indice]] - minimo) <= EPS
            ]
            fila = min(empatadas, key=lambda indice: base[indice])
            pivotar(fila, columna, razones)

    registro_inicial = (
        "Fase I: maximizar U = -W; W es la suma de variables artificiales."
        if artificiales
        else "Fase II: objetivo original; para MIN se maximiza Y = -Z."
    )
    registrar([registro_inicial])

    estado = "optimal"
    if artificiales:
        estado = ejecutar_fase()
        if estado == "optimal":
            if objetivo[-1] < -EPS:
                estado = "infeasible"
            elif objetivo[-1] > EPS:
                estado = "numerical_error"

        operaciones_transicion = []
        if estado == "optimal":
            # Las artificiales básicas con valor cero se pivotean fuera. Si
            # no hay columna real que pueda reemplazarlas, la fila es redundante.
            for indice in range(len(filas) - 1, -1, -1):
                if base[indice] not in artificiales:
                    continue

                columna = next((
                    j for j in range(len(columnas))
                    if j not in artificiales
                    and j not in base
                    and abs(filas[indice][j]) > EPS
                ), None)
                if columna is not None:
                    if len(pivotes) >= max_iteraciones:
                        estado = "iteration_limit"
                        break
                    pivotar(indice, columna, {})
                else:
                    operaciones_transicion.append(
                        f"Eliminar {filas_ids[indice]}: restricción redundante."
                    )
                    filas.pop(indice)
                    base.pop(indice)
                    filas_ids.pop(indice)

        if estado == "optimal":
            sentido = modelo["sentido"]
            costos = [float(valor) for valor in modelo["objetivo"]]
            costos.extend([0.0] * (len(columnas) - len(costos)))
            tableau_fase_dos = preparar_fase_dos(
                A=[fila[:-1] for fila in filas],
                b=[fila[-1] for fila in filas],
                variables=columnas,
                base=[columnas[indice] for indice in base],
                costos=costos,
                artificiales=[
                    columnas[indice] for indice in sorted(artificiales)
                ],
                objetivo=sentido,
                estado_fase_uno="optimal",
                valor_objetivo_fase_uno=objetivo[-1],
            )

            columnas = list(tableau_fase_dos.variables)
            base = [columnas.index(nombre) for nombre in tableau_fase_dos.base]
            filas = [list(fila) for fila in tableau_fase_dos.matriz[:-1]]
            objetivo = list(tableau_fase_dos.matriz[-1])
            fase = 2
            operaciones_transicion.extend([
                "Retirar las columnas artificiales.",
                "Restaurar la función objetivo original.",
            ])
            registrar(operaciones_transicion)
            estado = ejecutar_fase()
    else:
        estado = ejecutar_fase()

    numero_variables = len(modelo["objetivo"])
    valores = [0.0] * numero_variables
    if estado == "optimal":
        for indice, fila in zip(base, filas):
            if indice < numero_variables:
                valores[indice] = fila[-1]

    comprobacion = []
    if estado == "optimal":
        for indice, restriccion in enumerate(modelo["restricciones"], start=1):
            lhs = sum(
                coeficiente * valor
                for coeficiente, valor in zip(restriccion["coeficientes"], valores)
            )
            rhs = restriccion["rhs"]
            diferencia = lhs - rhs
            tolerancia = 1e-7 * (1 + abs(lhs) + abs(rhs))
            cumple = (
                diferencia <= tolerancia
                if restriccion["signo"] == "<="
                else diferencia >= -tolerancia
                if restriccion["signo"] == ">="
                else abs(diferencia) <= tolerancia
            )
            comprobacion.append({
                "fila": f"R{indice}",
                "lhs": lhs,
                "rhs": rhs,
                "signo": restriccion["signo"],
                "cumple": cumple,
                "holgura": abs(diferencia),
            })

        if (
            not all(item["cumple"] for item in comprobacion)
            or min(valores) < -1e-7
        ):
            estado = "numerical_error"

    return {
        "estado": estado,
        "fase": fase,
        "variables": (
            dict(zip("abcdef"[:numero_variables], valores))
            if estado == "optimal"
            else {}
        ),
        "objetivo": (
            sum(c * x for c, x in zip(modelo["objetivo"], valores))
            if estado == "optimal"
            else None
        ),
        "preparacion": p["detalle"],
        "tabla_inicial": tablas[0],
        "tablas": tablas,
        "pivotes": pivotes,
        "comprobacion": comprobacion,
    }
