"""
Construcción de la base y del tableau inicial del método símplex.

Responsable: shelsi_11504.

Este módulo se encarga de construir la base inicial del
problema de programación lineal y generar el tableau
correspondiente a partir de las restricciones previamente
convertidas a forma estándar.

También identifica si el problema necesita comenzar con
la Fase I o si puede iniciar directamente con la Fase II,
preparando la fila de la función objetivo correspondiente.
"""

from dataclasses import dataclass
from math import isfinite
from typing import List


@dataclass
class TableauInicial:
    variables: List[str]
    base: List[str]
    matriz: List[List[float]]
    fase: int
    artificiales: List[str]
    estado: str


def construir_tableau(
    A, b, variables, base, costos,
    artificiales=None, objetivo="max"
):
    """
    Construye el tableau inicial en forma canónica.

    A: matriz de restricciones en forma estándar
    b: lados derechos normalizados
    variables: nombres de todas las columnas
    base: nombres de las variables básicas
    costos: coeficientes originales de todas las variables
    artificiales: nombres de las variables artificiales
    objetivo: "max" o "min"

    Convención: última fila = Zj - Cj.
    Se seleccionan columnas con valor negativo para entrar
    en un problema de maximización.
    """
    artificiales = list(artificiales or [])
    A = [[float(x) for x in fila] for fila in A]
    b = [float(x) for x in b]
    costos = [float(x) for x in costos]

    m = len(A)
    n = len(variables)

    if not m or n == 0:
        raise ValueError("La matriz no puede estar vacía")

    if (len(b) != m or len(base) != m
            or len(costos) != n):
        raise ValueError("Dimensiones incompatibles")

    if len(set(variables)) != n:
        raise ValueError("Hay nombres de variables repetidos")

    if len(set(base)) != m:
        raise ValueError("La base contiene variables repetidas")

    if any(len(fila) != n for fila in A):
        raise ValueError("Cada fila debe tener n columnas")

    if not all(isfinite(valor) for fila in A for valor in fila):
        raise ValueError("La matriz debe contener valores finitos")
    if not all(isfinite(valor) for valor in b + costos):
        raise ValueError("El lado derecho y los costos deben ser finitos")

    if any(valor < -1e-9 for valor in b):
        raise ValueError("El lado derecho debe ser no negativo")

    if objetivo not in ("max", "min"):
        raise ValueError("El objetivo debe ser max o min")

    if any(v not in variables for v in base + artificiales):
        raise ValueError("Variable desconocida")

    # Comprobar que las columnas básicas forman la identidad.
    indices = [variables.index(v) for v in base]
    for i in range(m):
        for k, j in enumerate(indices):
            esperado = 1.0 if i == k else 0.0
            if abs(A[i][j] - esperado) > 1e-8:
                raise ValueError(
                    "La base no forma una matriz identidad"
                )

    if artificiales:
        fase = 1
        # Fase I: maximizar -suma de variables artificiales.
        c = [-1.0 if v in artificiales else 0.0
             for v in variables]
        estado = "Requiere Fase I"
    else:
        fase = 2
        signo = 1.0 if objetivo == "max" else -1.0
        c = [signo * x for x in costos]
        estado = "Listo para Fase II"

    # Costos de las variables básicas.
    cb = [c[j] for j in indices]

    # Fila canónica Zj - Cj.
    fila_objetivo = [
        sum(cb[i] * A[i][j] for i in range(m)) - c[j]
        for j in range(n)
    ]

    # Término independiente de la función objetivo.
    valor_objetivo = sum(
        cb[i] * b[i] for i in range(m)
    )

    matriz = [
        A[i] + [b[i]]
        for i in range(m)
    ]
    matriz.append(fila_objetivo + [valor_objetivo])

    return TableauInicial(
        variables=list(variables),
        base=list(base),
        matriz=matriz,
        fase=fase,
        artificiales=artificiales,
        estado=estado
    )


def preparar_fase_dos(
    A, b, variables, base, costos,
    artificiales, objetivo="max", tolerancia=1e-8,
    estado_fase_uno="optimal", valor_objetivo_fase_uno=0.0,
):
    """
    Transición desde una solución óptima de Fase I.

    A y b deben representar el tableau de restricciones
    AL FINAL de Fase I, después del pivoteo.
    No acepta directamente el tableau inicial si
    todavía no se ha resuelto la Fase I. También exige
    que el motor reporte un óptimo factible en Fase I.
    """
    if not isfinite(float(tolerancia)) or tolerancia <= 0:
        raise ValueError("La tolerancia debe ser positiva.")
    if estado_fase_uno != "optimal":
        raise ValueError("La Fase I debe terminar en estado óptimo.")
    valor_objetivo_fase_uno = float(valor_objetivo_fase_uno)
    if not isfinite(valor_objetivo_fase_uno):
        raise ValueError("El objetivo de Fase I debe ser finito.")
    if abs(valor_objetivo_fase_uno) > tolerancia:
        raise ValueError("El modelo es infactible al terminar la Fase I.")

    artificiales = set(artificiales)
    if objetivo not in ("max", "min"):
        raise ValueError("El objetivo debe ser max o min")
    if not set(artificiales) <= set(variables):
        raise ValueError("Variable artificial desconocida")
    if len(costos) != len(variables):
        raise ValueError("La cantidad de costos debe coincidir con las variables")
    if not all(isfinite(float(valor)) for valor in costos):
        raise ValueError("Los costos deben ser finitos")

    if any(v in artificiales for v in base):
        raise ValueError(
            "Primero se deben sacar las artificiales de la "
            "base o eliminar restricciones redundantes"
        )

    restantes = [
        i for i, v in enumerate(variables)
        if v not in artificiales
    ]

    if not A:
        if b or base:
            raise ValueError("Dimensiones incompatibles en la transición a Fase II")
        nuevas_variables = [variables[i] for i in restantes]
        nuevos_costos = [float(costos[i]) for i in restantes]
        signo = 1.0 if objetivo == "max" else -1.0
        fila_objetivo = [-signo * costo for costo in nuevos_costos] + [0.0]
        return TableauInicial(
            variables=nuevas_variables,
            base=[],
            matriz=[fila_objetivo],
            fase=2,
            artificiales=[],
            estado="Listo para Fase II",
        )

    nuevas_variables = [variables[i] for i in restantes]
    nueva_A = [
        [fila[i] for i in restantes]
        for fila in A
    ]
    nuevos_costos = [costos[i] for i in restantes]

    return construir_tableau(
        A=nueva_A,
        b=b,
        variables=nuevas_variables,
        base=base,
        costos=nuevos_costos,
        artificiales=[],
        objetivo=objetivo
    )
