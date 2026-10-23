"""
Integración de la preparación matemática del método símplex.

Responsable: shelsi_11504.

Este módulo conecta la información matemática del problema
con la construcción del tableau inicial, organizando los
datos necesarios para ejecutar el método símplex.

"""

from simplex.initial_tableau import construir_tableau


def preparar_modelo(
    A,
    b,
    variables,
    base,
    costos,
    artificiales=None,
    objetivo="max",
):

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
    }
