
import pytest

from simplex.initial_tableau import (
    construir_tableau,
    preparar_fase_dos,
)


def test_base_y_tableau_con_holguras():
    # Max Z = 3x + 2y
    # x + y + s1 = 4
    # 2x + y + s2 = 5

    t = construir_tableau(
        A=[
            [1, 1, 1, 0],
            [2, 1, 0, 1],
        ],
        b=[4, 5],
        variables=["x", "y", "s1", "s2"],
        base=["s1", "s2"],
        costos=[3, 2, 0, 0],
    )

    assert t.fase == 2
    assert t.base == ["s1", "s2"]
    assert t.matriz == [
        [1, 1, 1, 0, 4],
        [2, 1, 0, 1, 5],
        [-3, -2, 0, 0, 0],
    ]


def test_fase_uno_con_artificial():
    # x + y - e1 + A1 = 6

    t = construir_tableau(
        A=[[1, 1, -1, 1]],
        b=[6],
        variables=["x", "y", "e1", "A1"],
        base=["A1"],
        costos=[3, 2, 0, 0],
        artificiales=["A1"],
    )

    assert t.fase == 1
    assert t.base == ["A1"]
    assert t.matriz == [
        [1, 1, -1, 1, 6],
        [-1, -1, 1, 0, -6],
    ]


def test_rechaza_base_incorrecta():
    with pytest.raises(ValueError):
        construir_tableau(
            A=[[2, 1]],
            b=[4],
            variables=["x", "y"],
            base=["x"],
            costos=[3, 2],
        )


def test_transicion_fase_dos():
    # Estado ya pivotado al final de Fase I.
    t = preparar_fase_dos(
        A=[[1, 1, -1, 1]],
        b=[6],
        variables=["x", "y", "e1", "A1"],
        base=["x"],
        costos=[3, 2, 0, 0],
        artificiales=["A1"],
    )

    assert t.fase == 2
    assert t.variables == ["x", "y", "e1"]
    assert t.base == ["x"]
    assert t.matriz == [
    [1, 1, -1, 6],
    [0, 1, -3, 18],
]
