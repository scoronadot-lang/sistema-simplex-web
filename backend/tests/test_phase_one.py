
"""
Pruebas de preparación de la Fase I del método símplex.

Responsable: shelsi_11504.

Verifica la construcción del objetivo auxiliar,
la identificación de variables artificiales
y la generación del tableau inicial.
"""

import pytest

from simplex.phase_one import preparar_fase_uno


def test_preparar_fase_uno():
    resultado = preparar_fase_uno(
        A=[[1, 1, -1, 1]],
        b=[6],
        variables=["x", "y", "e1", "A1"],
        base=["A1"],
        artificiales=["A1"],
        costos_originales=[3, 2, 0, 0],
    )

    assert resultado["fase"] == 1
    assert resultado["base"] == ["A1"]
    assert resultado["artificiales"] == ["A1"]

    assert resultado["objetivo_auxiliar"] == {
        "x": 0.0,
        "y": 0.0,
        "e1": 0.0,
        "A1": -1.0,
    }

    assert resultado["tableau"] == [
        [1, 1, -1, 1, 6],
        [-1, -1, 1, 0, -6],
    ]


def test_fase_uno_sin_artificiales():
    with pytest.raises(ValueError):
        preparar_fase_uno(
            A=[[1, 1, 1]],
            b=[4],
            variables=["x", "y", "s1"],
            base=["s1"],
            artificiales=[],
        )
