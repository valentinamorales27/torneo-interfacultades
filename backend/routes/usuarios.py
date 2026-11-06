
from flask import Blueprint, request, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash
from db import obtener_conexion
from auth import requiere_rol

#gestion de los usuarios planilleros

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


#obtenemos todos los planilleros
@usuarios_bp.route("/planilleros", methods=["GET"])
@requiere_rol("administrador")
def obtener_planilleros():

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT correo, rol
            FROM login
            WHERE rol = 'planillero'
            ORDER BY correo
        """)

        planilleros = cursor.fetchall()

        return jsonify(planilleros), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#registramos un nuevo planillero
@usuarios_bp.route("/planilleros", methods=["POST"])
@requiere_rol("administrador")
def crear_planillero():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "error": "Se deben enviar los datos del planillero"
        }), 400

    correo = datos.get("correo")
    contraseña = datos.get("contraseña")

    if not isinstance(correo, str):
        return jsonify({
            "error": "El correo debe ser un texto"
        }), 400

    correo = correo.strip().lower()

    if (
        not correo
        or len(correo) > 50
        or correo.count("@") != 1
        or " " in correo
        or "." not in correo.split("@")[1]
    ):
        return jsonify({
            "error": "El correo electrónico no es válido"
        }), 400

    if not isinstance(contraseña, str) or len(contraseña) < 8:
        return jsonify({
            "error": "La contraseña debe tener al menos 8 caracteres"
        }), 400

    if len(contraseña) > 128:
        return jsonify({
            "error": "La contraseña es demasiado larga"
        }), 400

    #guardamos el hash, nunca la contraseña original
    contraseña_hash = generate_password_hash(contraseña)

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO login (correo, contraseña, rol)
            VALUES (%s, %s, %s)
        """, (correo, contraseña_hash, "planillero"))

        conexion.commit()

        return jsonify({
            "mensaje": "Planillero creado correctamente",
            "correo": correo,
            "rol": "planillero"
        }), 201

    except mysql.connector.IntegrityError as error:
        if conexion:
            conexion.rollback()

        if error.errno == 1062:
            return jsonify({
                "error": "Ya existe un usuario con ese correo"
            }), 409

        return jsonify({
            "error": "No se pudo crear el planillero"
        }), 400

    except mysql.connector.Error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al crear el planillero"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


#eliminamos una cuenta de planillero
@usuarios_bp.route("/planilleros/<string:correo>", methods=["DELETE"])
@requiere_rol("administrador")
def eliminar_planillero(correo):

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #verificamos que exista y sea planillero
        cursor.execute("""
            SELECT correo
            FROM login
            WHERE correo = %s AND rol = 'planillero'
        """, (correo,))

        if not cursor.fetchone():
            return jsonify({
                "error": "No existe un planillero con ese correo"
            }), 404

        cursor.execute("""
            DELETE FROM login
            WHERE correo = %s AND rol = 'planillero'
        """, (correo,))

        conexion.commit()

        return jsonify({
            "mensaje": "Planillero eliminado correctamente"
        }), 200

    except mysql.connector.Error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al eliminar el planillero"
        }), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()
