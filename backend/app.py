
from flask import Flask
from dotenv import load_dotenv
from flask_cors import CORS
import os

# Este archivo define las rutas y la lógica del backend.

# Cargamos las variables de entorno del archivo .env
load_dotenv()

# Creamos la aplicación
app = Flask(__name__)

# Clave secreta para gestionar las sesiones
secret_key = os.environ.get("SECRET_KEY")

if not secret_key:
    raise RuntimeError("Falta configurar SECRET_KEY en el archivo .env")

app.config["SECRET_KEY"] = secret_key

# Configuración de las cookies de sesión
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Para desarrollo local con HTTP

# Permitimos que el frontend se comunique con el backend
origen_frontend = os.environ.get(
    "FRONTEND_ORIGIN",
    "http://localhost:5173"
)

CORS(
    app,
    origins=[origen_frontend],
    supports_credentials=True
)

#importamos las rutas de todos los archivos de routes
from routes.jugadores import jugadores_bp
from routes.equipos import equipos_bp
from routes.canchas import canchas_bp
from routes.complejos import complejos_bp
from routes.goles import goles_bp
from routes.partidos import partidos_bp
from routes.planillas import planillas_bp
from routes.sanciones import sanciones_bp
from routes.planteles import planteles_bp
from routes.tarjetas import tarjetas_bp
from routes.reportes import reportes_bp
from routes.login import login_bp
from routes.torneos import torneos_bp
from routes.usuarios import usuarios_bp

#registramos las rutas
app.register_blueprint(jugadores_bp)
app.register_blueprint(equipos_bp)
app.register_blueprint(canchas_bp)
app.register_blueprint(complejos_bp)
app.register_blueprint(goles_bp)
app.register_blueprint(partidos_bp)
app.register_blueprint(planillas_bp)
app.register_blueprint(sanciones_bp)
app.register_blueprint(planteles_bp)
app.register_blueprint(tarjetas_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(login_bp)
app.register_blueprint(torneos_bp)
app.register_blueprint(usuarios_bp)


@app.route("/")
def inicio():
    return "Backend del Torneo Interfacultades de Futbol 5"

if __name__ == "__main__":
    app.run(debug=True)
