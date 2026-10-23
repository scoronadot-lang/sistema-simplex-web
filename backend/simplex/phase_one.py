
"""
Preparación de la Fase I del método símplex.

Responsable: shelsi_11504.

Este módulo prepara la función objetivo auxiliar y
el tableau inicial cuando existen variables artificiales.

La resolución mediante iteraciones y pivoteos corresponde
al módulo encargado del algoritmo símplex.
"""

from simplex.initial_tableau import construir_tableau


def preparar_fase_uno(
    A,
    b,
    variables,
    base,
    artificiales,
    costos_originales=None,
):
    """
    Prepara el tableau inicial para Fase I.

    Fase I minimiza la suma de variables artificiales.
    Para trabajar con maximización, se utiliza:

        Maximizar W = -A1 - A2 - ...

    La fila objetivo se construye en forma canónica.
    """

    if not artificiales:
        raise ValueError(
            "La Fase I requiere variables artificiales"
        )

    if costos_originales is None:
        costos_originales = [0.0] * len(variables)

    resultado = construir_tableau(
        A=A,
        b=b,
        variables=variables,
        base=base,
        costos=costos_originales,
        artificiales=artificiales,
        objetivo="max",
    )

    return {
        "fase": resultado.fase,
        "variables": resultado.variables,
        "base": resultado.base,
        "artificiales": resultado.artificiales,
        "tableau": resultado.matriz,
        "estado": resultado.estado,
        "objetivo_auxiliar": {
            nombre: -1.0 if nombre in artificiales else 0.0
            for nombre in variables
        },
    }
