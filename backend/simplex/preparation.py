
"""
Integración de la preparación matemática del método símplex.

Responsable: shelsi_11504.

Construye automáticamente la base y el tableau inicial
a partir de un modelo previamente normalizado.
"""

from simplex.initial_tableau import construir_tableau


def identificar_base(A, variables, artificiales=None):
    """
    Identifica columnas identidad para construir la base.
    Prefiere holguras y artificiales antes que variables
    originales, cuando los nombres permiten distinguirlas.
    """
    artificiales = set(artificiales or [])
    m = len(A)

    if m == 0:
        raise ValueError("No existen restricciones")

    base = [None] * m
    utilizadas = set()

    def prioridad(nombre):
        if nombre in artificiales:
            return 0
        if nombre.startswith(("s", "h", "A")):
            return 0
        return 1

    candidatos = sorted(
        range(len(variables)),
        key=lambda j: prioridad(variables[j])
    )

    for j in candidatos:
        columna = [float(A[i][j]) for i in range(m)]

        for i in range(m):
            es_identidad = all(
                abs(columna[k] - (1 if k == i else 0)) < 1e-9
                for k in range(m)
            )

            if es_identidad and base[i] is None and j not in utilizadas:
                base[i] = variables[j]
                utilizadas.add(j)
                break

    if any(v is None for v in base):
        raise ValueError(
            "No se encontró una base identidad completa. "
            "Revisa las variables auxiliares generadas."
        )

    return base


def preparar_modelo(
    A,
    b,
    variables,
    costos,
    artificiales=None,
    objetivo="max",
    base=None,
):
    """
    Prepara el tableau para el algoritmo de iteraciones.

    A y b deben venir de la conversión a forma estándar.
    Los costos incluyen ceros para variables auxiliares.
    """
    artificiales = list(artificiales or [])

    if base is None:
        base = identificar_base(A, variables, artificiales)

    resultado = construir_tableau(
        A=A,
        b=b,
        variables=variables,
        base=base,
        costos=costos,
        artificiales=artificiales,
        objetivo=objetivo,
    )

    return {
        "variables": resultado.variables,
        "base": resultado.base,
        "tableau": resultado.matriz,
        "fase": resultado.fase,
        "artificiales": resultado.artificiales,
        "estado": resultado.estado,
        "convencion": "Zj - Cj",
        "objetivo_original": list(costos),
        "tipo_objetivo": objetivo,
    }
