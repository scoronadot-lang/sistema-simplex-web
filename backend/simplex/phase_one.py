"""Adaptador entre la forma estándar de Shelsi_11504 y el motor de Diana_25767."""
from .standard_form import prepare_standard_form


def preparar(modelo):
    """Transforma el modelo recibido de la API al contrato de simplex.resolver."""
    coeficientes = modelo["objetivo"]
    restricciones = modelo["restricciones"]
    nombres = list("abcdef"[:len(coeficientes)])
    estandar = prepare_standard_form(
        variables=nombres,
        constraints=[
            {"coefficients": r["coeficientes"], "relation": r["signo"], "rhs": r["rhs"]}
            for r in restricciones
        ],
    )
    columnas = estandar.variable_names
    artificiales = {columnas.index(nombre) for nombre in estandar.artificial_variables}
    base = []
    for i in range(len(restricciones)):
        preferidas = [f"A{i + 1}", f"s{i + 1}"]
        nombre = next((n for n in preferidas if n in columnas), None)
        if nombre is None:
            raise ValueError(f"No se encontró variable básica para restricción {i + 1}")
        base.append(columnas.index(nombre))
    return {
        "columnas": columnas,
        "filas": [fila + [rhs] for fila, rhs in zip(estandar.rows, estandar.rhs)],
        "base": base,
        "filas_ids": [f"R{i + 1}" for i in range(len(restricciones))],
        "artificiales": artificiales,
        "objetivo_fase1": estandar.phase_one_objective,
    }

def preparar_fase_uno(
    A,
    b,
    variables,
    base,
    artificiales,
    costos_originales=None,
):
    """
    Prepara el tableau auxiliar de Fase I.

    Responsable: shelsi_11504.
    """

    from .initial_tableau import construir_tableau

    # Fase I solamente se necesita cuando existen
    # variables artificiales.
    if not artificiales:
        raise ValueError(
            "No se puede preparar Fase I sin variables artificiales."
        )

    if costos_originales is None:
        costos_originales = [0.0] * len(variables)

    # Construir los coeficientes de la función auxiliar:
    # 0 para variables normales y -1 para artificiales.
    objetivo_auxiliar = {
        variable: -1.0 if variable in artificiales else 0.0
        for variable in variables
    }

    # Construir el tableau inicial de Fase I.
    resultado = construir_tableau(
        A=A,
        b=b,
        variables=variables,
        base=base,
        costos=costos_originales,
        artificiales=artificiales,
    )

    return {
        "variables": resultado.variables,
        "base": resultado.base,
        "tableau": resultado.matriz,
        "fase": resultado.fase,
        "artificiales": resultado.artificiales,
        "estado": resultado.estado,
        "objetivo_auxiliar": objetivo_auxiliar,
    }