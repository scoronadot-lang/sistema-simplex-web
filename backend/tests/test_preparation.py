"""
Pruebas de integración de la preparación matemática.

Responsable: shelsi_11504.

Este archivo contiene las pruebas que permiten verificar
el funcionamiento del módulo de preparación matemática
y su conexión con la construcción del tableau inicial.

"""


from simplex.preparation import preparar_modelo


def test_preparacion_sin_artificiales():
    resultado = preparar_modelo(
        A=[
            [1, 1, 1, 0],
            [2, 1, 0, 1],
        ],
        b=[4, 5],
        variables=["x", "y", "s1", "s2"],
        base=["s1", "s2"],
        costos=[3, 2, 0, 0],
    )

    assert resultado["fase"] == 2
    assert resultado["base"] == ["s1", "s2"]
    assert resultado["estado"] == "Listo para Fase II"

    assert resultado["tableau"] == [
        [1, 1, 1, 0, 4],
        [2, 1, 0, 1, 5],
        [-3, -2, 0, 0, 0],
    ]


def test_preparacion_con_artificial():
    resultado = preparar_modelo(
        A=[[1, 1, -1, 1]],
        b=[6],
        variables=["x", "y", "e1", "A1"],
        base=["A1"],
        costos=[3, 2, 0, 0],
        artificiales=["A1"],
    )

    assert resultado["fase"] == 1
    assert resultado["base"] == ["A1"]
    assert resultado["estado"] == "Requiere Fase I"

    assert resultado["tableau"] == [
        [1, 1, -1, 1, 6],
        [-1, -1, 1, 0, -6],
    ]
