from flask import Flask


#Este archivo define las rutas y la lógica del back (se agregan las reglas del obligatorio)

#traigo las rutas de todos los archivos de routes
from routes.jugadores import jugadores_bp
from routes.equipos import equipos_bp
from routes.canchas import canchas_bp
from routes.complejos import complejos_bp
from routes.goles import goles_bp
from routes.partidos import partidos_bp
from routes.planillas import planillas_bp
from routes.sanciones import sanciones_bp
from routes.tarjetas import tarjetas_bp
from routes.partidos import reportes_bp

app = Flask(__name__)

#reegistramos las rutas de los archivos que están en routes
app.register_blueprint(jugadores_bp)
app.register_blueprint(equipos_bp)
app.register_blueprint(canchas_bp)
app.register_blueprint(complejos_bp)
app.register_blueprint(goles_bp)
app.register_blueprint(partidos_bp)
app.register_blueprint(planillas_bp)
app.register_blueprint(sanciones_bp)
app.register_blueprint(tarjetas_bp)
app.register_blueprint(reportes_bp)




@app.route("/")
def inicio():
    return "Backend del Torneo Interfacultades de Futbol 5"


if __name__ == "__main__":
    app.run(debug=True)