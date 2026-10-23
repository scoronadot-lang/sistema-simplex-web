"""
Preparación matemática del método símplex.

Responsable: shelsi_11504.

Este módulo transforma un problema de programación lineal
a forma estándar, normaliza restricciones y prepara las
variables auxiliares necesarias para su resolución.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class StandardForm:
    variable_names: list[str]
    rows: list[list[float]]
    rhs: list[float]
    relations_originales: list[str]
    slack_variables: list[str]
    surplus_variables: list[str]
    artificial_variables: list[str]
    phase_one_objective: list[float]


def prepare_standard_form(
    variables: list[str],
    constraints: list[dict[str, Any]]
) -> StandardForm:
    """
    Prepara un modelo para el método de dos fases.

    Cada restricción debe tener:
    {
        "coefficients": [1, 2],
        "relation": "<=",
        "rhs": 10
    }

    La función devuelve las ecuaciones y la función
    auxiliar de la fase I, usando maximizar -sum(A).
    """

    if not 2 <= len(variables) <= 6:
        raise ValueError(
            "El modelo debe tener entre 2 y 6 variables."
        )

    if variables != ["abcdef"[i] for i in range(len(variables))]:
        raise ValueError(
            "Las variables deben estar en orden: a, b, c, d, e, f."
        )

    if not constraints:
        raise ValueError("Debe existir al menos una restricción.")

    prepared = []
    slack = []
    surplus = []
    artificial = []

    # Normalizar los datos y asignar variables auxiliares.
    for index, constraint in enumerate(constraints, start=1):
        coefficients = constraint.get("coefficients")
        relation = constraint.get("relation")
        rhs = constraint.get("rhs")

        if not isinstance(coefficients, list):
            raise ValueError(f"Restricción {index}: coeficientes inválidos.")

        if len(coefficients) != len(variables):
            raise ValueError(
                f"Restricción {index}: cantidad incorrecta de coeficientes."
            )

        if relation not in ("<=", ">=", "="):
            raise ValueError(
                f"Restricción {index}: use <=, >= o =."
            )

        if not isinstance(rhs, (int, float)) or isinstance(rhs, bool):
            raise ValueError(
                f"Restricción {index}: término independiente inválido."
            )

        if any(
            not isinstance(value, (int, float)) or isinstance(value, bool)
            for value in coefficients
        ):
            raise ValueError(
                f"Restricción {index}: todos los coeficientes deben ser numéricos."
            )

        coefficients = [float(value) for value in coefficients]
        rhs = float(rhs)

        # Un RHS negativo requiere multiplicar toda la
        # restricción por -1 e invertir el sentido.
        if rhs < 0:
            coefficients = [-value for value in coefficients]
            rhs = -rhs
            relation = {
                "<=": ">=",
                ">=": "<=",
                "=": "="
            }[relation]

        row_aux = {}

        if relation == "<=":
            name = f"s{index}"
            slack.append(name)
            row_aux[name] = 1.0

        elif relation == ">=":
            name = f"e{index}"
            surplus.append(name)
            row_aux[name] = -1.0

            name_art = f"A{index}"
            artificial.append(name_art)
            row_aux[name_art] = 1.0

        else:
            name_art = f"A{index}"
            artificial.append(name_art)
            row_aux[name_art] = 1.0

        prepared.append({
            "coefficients": coefficients,
            "rhs": rhs,
            "aux": row_aux
        })

    variable_names = variables + slack + surplus + artificial
    rows = []

    for constraint in prepared:
        row = list(constraint["coefficients"])

        row.extend(
            constraint["aux"].get(name, 0.0)
            for name in variable_names[len(variables):]
        )

        rows.append(row)

    # Convención de maximización: maximizar -sum(A).
    # El algoritmo debe adaptar la fila objetivo a su
    # convención de tableau antes de comenzar a pivotar.
    phase_one_objective = [
        -1.0 if name in artificial else 0.0
        for name in variable_names
    ]

    return StandardForm(
        variable_names=variable_names,
        rows=rows,
        rhs=[item["rhs"] for item in prepared],
        relations_originales=[
            item for item in [c["relation"] for c in constraints]
        ],
        slack_variables=slack,
        surplus_variables=surplus,
        artificial_variables=artificial,
        phase_one_objective=phase_one_objective
    )
