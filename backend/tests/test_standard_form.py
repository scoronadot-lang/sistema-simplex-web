
import pytest

from simplex.standard_form import prepare_standard_form


def test_modelo_con_holgura_y_artificial():
    result = prepare_standard_form(
        variables=["a", "b"],
        constraints=[
            {
                "coefficients": [1, 1],
                "relation": "<=",
                "rhs": 4
            },
            {
                "coefficients": [2, 1],
                "relation": ">=",
                "rhs": 5
            }
        ]
    )

    assert result.variable_names == ["a", "b", "s1", "e2", "A2"]
    assert result.rows == [
        [1.0, 1.0, 1.0, 0.0, 0.0],
        [2.0, 1.0, 0.0, -1.0, 1.0]
    ]
    assert result.rhs == [4.0, 5.0]
    assert result.artificial_variables == ["A2"]



def test_rhs_negativo_invierte_desigualdad():
    result = prepare_standard_form(
        variables=["a", "b"],
        constraints=[
            {
                "coefficients": [1, 2],
                "relation": "<=",
                "rhs": -6
            }
        ]
    )

    assert result.variable_names == ["a", "b", "e1", "A1"]
    assert result.rows == [[-1.0, -2.0, -1.0, 1.0]]
    assert result.rhs == [6.0]


def test_rechaza_mas_de_seis_variables():
    with pytest.raises(ValueError):
        prepare_standard_form(
            variables=list("abcdefg"),
            constraints=[
                {
                    "coefficients": [1] * 7,
                    "relation": "<=",
                    "rhs": 10
                }
            ]
        )
