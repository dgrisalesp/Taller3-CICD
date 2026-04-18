# app/app.py

"""Aplicación Flask para una calculadora web."""

from flask import Flask, render_template, request

from .calculadora import dividir, multiplicar, restar, sumar

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    """Procesa la calculadora y renderiza la página principal."""
    resultado = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            operacion = request.form["operacion"]

            if operacion == "sumar":
                resultado = sumar(num1, num2)
            elif operacion == "restar":
                resultado = restar(num1, num2)
            elif operacion == "multiplicar":
                resultado = multiplicar(num1, num2)
            elif operacion == "dividir":
                resultado = dividir(num1, num2)
            else:
                resultado = "Operación no válida"
        except ValueError:
            resultado = "Error: Introduce números válidos"
        except ZeroDivisionError:
            resultado = "Error: No se puede dividir por cero"

    return render_template("index.html", resultado=resultado)


if __name__ == "__main__":  # pragma: no cover
    app.run(debug=True, port=5000, host='0.0.0.0')
