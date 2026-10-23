"""Modelos compartidos por las pruebas del motor símplex."""


def modelo(objetivo, restricciones, sentido="max"):
    """Construye un modelo con el mismo contrato que recibe el motor."""
    return {
        "nombre": f"Caso de prueba {sentido.upper()}",
        "sentido": sentido,
        "objetivo": list(objetivo),
        "restricciones": [
            {
                "coeficientes": list(coeficientes),
                "signo": signo,
                "rhs": rhs,
            }
            for coeficientes, signo, rhs in restricciones
        ],
    }


MAX = modelo(
    [5, 4, 3],
    [
        ([2, 3, 1], "<=", 5),
        ([4, 1, 2], "<=", 11),
        ([3, 4, 2], "<=", 8),
    ],
)

MIN = modelo(
    [2, 3],
    [
        ([1, 1], ">=", 4),
        ([1, 2], "<=", 10),
    ],
    "min",
)
