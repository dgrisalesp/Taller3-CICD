# app/calculadora.py

AUTOR = "???"  # IMPORTANTE: Reemplaza con tu nombre completo (debe coincidir con el nombre que uses en cualquier otro identificador del proyecto. Sugerencia: Usuario de correo de EAFIT)


def sumar(a, b):
    return a + b


def restar(a, b):
    return a - b


def multiplicar(a, b):
    return a * b


def dividir(a, b):
    if b == 0:
        raise ZeroDivisionError("No se puede dividir por cero")
    return a / b
