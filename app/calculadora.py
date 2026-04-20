# app/calculadora.py

"""Funciones básicas de una calculadora."""

# Test Change

AUTOR = "Daniela, Juan Miguel, Camilo y David"


def sumar(a, b):
    """Suma dos números."""
    return a + b


def restar(a, b):
    """Resta dos números."""
    return a - b


def multiplicar(a, b):
    """Multiplica dos números."""
    return a * b


def dividir(a, b):
    """Divide dos números."""
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a / b

def potencia(a, b):
    """potencia de dos números."""
    return a ** b
 
 
def modulo(a, b):
    """modulo de dos números."""
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a % b
 