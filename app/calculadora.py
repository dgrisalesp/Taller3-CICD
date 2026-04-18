# app/calculadora.py

AUTOR = "Daniela, Juan Miguel, Camilo y David"  # IMPORTANTE: Reemplaza con tu nombre completo (debe coincidir con el nombre que uses en cualquier otro identificador del proyecto. Sugerencia: Usuario de correo de EAFIT)


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