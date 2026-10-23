
"""
Integración de la preparación matemática del método símplex.

Responsable: shelsi_11504.

Construye automáticamente la base y el tableau inicial
a partir de un modelo previamente normalizado.
"""

from math import isfinite

from .initial_tableau import construir_tableau
from .phase_one import preparar_fase_uno
from .standard_form import prepare_standard_form


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


def preparar(modelo):
    """Adapta la entrada de la API a la preparación de Shelsi y al motor."""
    if not isinstance(modelo, dict):
        raise ValueError("El modelo debe ser un objeto.")

    objetivo_original = modelo.get("objetivo")
    restricciones = modelo.get("restricciones")
    sentido = modelo.get("sentido")

    if not isinstance(objetivo_original, list):
        raise ValueError("El objetivo debe ser una lista de coeficientes.")
    if not 2 <= len(objetivo_original) <= 6:
        raise ValueError("El modelo debe tener entre 2 y 6 variables.")
    if not all(
        isinstance(valor, (int, float))
        and not isinstance(valor, bool)
        and isfinite(float(valor))
        for valor in objetivo_original
    ):
        raise ValueError("Los coeficientes del objetivo deben ser números finitos.")
    if sentido not in ("max", "min"):
        raise ValueError("El sentido debe ser max o min.")
    if not isinstance(restricciones, list) or not restricciones:
        raise ValueError("Debe existir al menos una restricción.")

    variables_decision = list("abcdef"[:len(objetivo_original)])
    restricciones_estandar = []
    for restriccion in restricciones:
        if not isinstance(restriccion, dict):
            raise ValueError("Cada restricción debe ser un objeto.")
        restricciones_estandar.append({
            "coefficients": restriccion.get("coeficientes"),
            "relation": restriccion.get("signo"),
            "rhs": restriccion.get("rhs"),
        })

    forma = prepare_standard_form(
        variables=variables_decision,
        constraints=restricciones_estandar,
    )
    costos = [float(valor) for valor in objetivo_original]
    costos.extend([0.0] * (len(forma.variable_names) - len(costos)))
    base_nombres = identificar_base(
        forma.rows,
        forma.variable_names,
        forma.artificial_variables,
    )

    if forma.artificial_variables:
        inicial = preparar_fase_uno(
            A=forma.rows,
            b=forma.rhs,
            variables=forma.variable_names,
            base=base_nombres,
            artificiales=forma.artificial_variables,
            costos_originales=costos,
        )
    else:
        inicial = preparar_modelo(
            A=forma.rows,
            b=forma.rhs,
            variables=forma.variable_names,
            base=base_nombres,
            costos=costos,
            artificiales=[],
            objetivo=sentido,
        )

    matriz_inicial = inicial["tableau"]
    base_indices = [forma.variable_names.index(nombre) for nombre in inicial["base"]]
    artificiales_indices = [
        forma.variable_names.index(nombre)
        for nombre in forma.artificial_variables
    ]
    ids_filas = [f"R{indice}" for indice in range(1, len(forma.rows) + 1)]

    detalle = {
        "variables": list(forma.variable_names),
        "filas": [list(fila) for fila in forma.rows],
        "rhs": list(forma.rhs),
        "relaciones_originales": list(forma.relations_originales),
        "relaciones_normalizadas": list(forma.relations_normalizadas),
        "rhs_originales": list(forma.rhs_originales),
        "signos_invertidos": list(forma.signos_invertidos),
        "holguras": list(forma.slack_variables),
        "excesos": list(forma.surplus_variables),
        "artificiales": list(forma.artificial_variables),
        "base": list(inicial["base"]),
        "fase": inicial["fase"],
        "estado": inicial["estado"],
        "convencion": "Zj - Cj",
        "objetivo_original": list(costos[:len(objetivo_original)]),
        "sentido": sentido,
        "objetivo_auxiliar": dict(zip(
            forma.variable_names,
            forma.phase_one_objective,
        )),
        "tabla_inicial": [list(fila) for fila in matriz_inicial],
    }

    return {
        # Estructura interna consumida por simplex.resolver.
        "columnas": list(forma.variable_names),
        "filas": [list(fila) for fila in matriz_inicial[:-1]],
        "base": base_indices,
        "filas_ids": ids_filas,
        "artificiales": artificiales_indices,
        "objetivo_fase1": list(forma.phase_one_objective),
        "tabla_inicial": [list(fila) for fila in matriz_inicial],
        # Datos matemáticos legibles que se devuelven al frontend.
        "detalle": detalle,
    }
