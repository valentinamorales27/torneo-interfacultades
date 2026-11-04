
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from db import obtener_conexion
login_bp = Blueprint("login", __name__)

# acá usamos lo de session que es una herramienta de Flask
#que guarda la info. de usuarios en distintas solicitudes digamos
#iniciar sesion
@login_bp.route("/login", methods=["POST"])
def iniciar_sesion():

    datos = request.get_json()

    #verificamos que se hayan enviado los datos
    if not datos or not datos.get("correo") or not datos.get("contraseña"):
        return jsonify({"error": "Debe ingresar correo y contraseña"}), 400

    correo = datos["correo"]
    contraseña = datos["contraseña"]

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #buscamos el usuario por su correo
        consulta = """
            SELECT correo, contraseña, rol
            FROM login
            WHERE correo = %s
        """

        cursor.execute(consulta, (correo,))
        usuario = cursor.fetchone()

        #verificamos si existe el usuario y si la contraseña es correcta
        if usuario is None or not check_password_hash(usuario["contraseña"], contraseña):
            return jsonify({"error": "Correo o contraseña incorrectos"}), 401

        #guardamos los datos del usuario en la sesion
        session.clear()
        session["correo"] = usuario["correo"]
        session["rol"] = usuario["rol"]

        return jsonify({
            "mensaje": "Inicio de sesion exitoso",
            "correo": usuario["correo"],
            "rol": usuario["rol"]
        }), 200

    finally:
        cursor.close()
        conexion.close()


#consultar quien inicio sesion
@login_bp.route("/sesion", methods=["GET"])
def consultar_sesion():

    if "correo" not in session:
        return jsonify({"error": "No hay una sesion iniciada"}), 401

    return jsonify({
        "correo": session["correo"],
        "rol": session["rol"]
    }), 200


#cerrar sesion
@login_bp.route("/logout", methods=["POST"])
def cerrar_sesion():
    session.clear()
    return jsonify({"mensaje": "Sesion cerrada correctamente"}), 200
