from flask import Flask


#Este archivo define las rutas y la lógica del back (se agregan las reglas del obligatorio)

#traigo las rutas de todos los archivos de routes
from routes.jugadores import jugadores_bp
from routes.equipos import equipos_bp

app = Flask(__name__)

# Registramos las rutas de los files de routes
app.register_blueprint(jugadores_bp)
app.register_blueprint(equipos_bp)


@app.route("/")
def inicio():
    return "Backend del Torneo Interfacultades de Futbol 5"


if __name__ == "__main__":
    app.run(debug=True)