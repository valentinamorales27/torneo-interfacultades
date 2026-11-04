
from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion
#para controlar permisos
from auth import requiere_rol

#gestion de los complejos deportivos

complejos_bp = Blueprint("complejos", __name__, url_prefix="/complejos")


#validamos que los datos del complejo sean correctos
def validar_complejo(datos):

    if not datos:
        return "Se deben enviar los datos del complejo"

    nombre = datos.get("nombre")
    direccion = datos.get("direccion")
    departamento = datos.get("departamento")
    #isinstance es para comprobar tipo del dato
    if not nombre or not isinstance(nombre, str) or not nombre.strip():
        return "El nombre del complejo es obligatorio"

    if not direccion or not isinstance(direccion, str) or not direccion.strip():
        return "La dirección del complejo es obligatoria"

    if not departamento or not isinstance(departamento, str) or not departamento.strip():
        return "El departamento es obligatorio"

    return None


#obtenemos todos los complejos
@complejos_bp.route("/", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_complejos():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT id_complejo, nombre, direccion, departamento
            FROM complejo
            ORDER BY id_complejo
        """

        cursor.execute(consulta)
        complejos = cursor.fetchall()

        return jsonify(complejos), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#obtenemos un complejo por su identificador
@complejos_bp.route("/<int:id_complejo>", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_complejo(id_complejo):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT id_complejo, nombre, direccion, departamento
            FROM complejo
            WHERE id_complejo = %s
        """

        cursor.execute(consulta, (id_complejo,))
        complejo = cursor.fetchone()

        if not complejo:
            return jsonify({"error": "No existe un complejo con ese identificador"}), 404

        return jsonify(complejo), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#registramos un nuevo complejo
@complejos_bp.route("/", methods=["POST"])
@requiere_rol("administrador")
def crear_complejo():

    datos = request.get_json(silent=True)

    error_validacion = validar_complejo(datos)

    if error_validacion:
        return jsonify({"error": error_validacion}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        consulta = """
            INSERT INTO complejo (nombre, direccion, departamento)
            VALUES (%s, %s, %s)
        """

        valores = (
            datos["nombre"].strip(),
            datos["direccion"].strip(),
            datos["departamento"].strip()
        )

        cursor.execute(consulta, valores)
        id_complejo = cursor.lastrowid

        conexion.commit()

        return jsonify({
            "mensaje": "Complejo creado correctamente",
            "id_complejo": id_complejo
        }), 201

    except mysql.connector.Error as error:
        conexion.rollback()
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#modificamos los datos de un complejo
@complejos_bp.route("/<int:id_complejo>", methods=["PUT"])
@requiere_rol("administrador")
def modificar_complejo(id_complejo):

    datos = request.get_json(silent=True)

    error_validacion = validar_complejo(datos)

    if error_validacion:
        return jsonify({"error": error_validacion}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        #verificamos que exista el complejo
        cursor.execute(
            "SELECT id_complejo FROM complejo WHERE id_complejo = %s",
            (id_complejo,)
        )

        if not cursor.fetchone():
            return jsonify({"error": "No existe un complejo con ese identificador"}), 404

        consulta = """
            UPDATE complejo
            SET nombre = %s,
                direccion = %s,
                departamento = %s
            WHERE id_complejo = %s
        """

        valores = (
            datos["nombre"].strip(),
            datos["direccion"].strip(),
            datos["departamento"].strip(),
            id_complejo
        )

        cursor.execute(consulta, valores)
        conexion.commit()

        return jsonify({"mensaje": "Complejo modificado correctamente"}), 200

    except mysql.connector.Error as error:
        conexion.rollback()
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#eliminamos un complejo
@complejos_bp.route("/<int:id_complejo>", methods=["DELETE"])
@requiere_rol("administrador")
def eliminar_complejo(id_complejo):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        #verificamos que exista el complejo
        cursor.execute(
            "SELECT id_complejo FROM complejo WHERE id_complejo = %s",
            (id_complejo,)
        )

        if not cursor.fetchone():
            return jsonify({"error": "No existe un complejo con ese identificador"}), 404

        cursor.execute(
            "DELETE FROM complejo WHERE id_complejo = %s",
            (id_complejo,)
        )

        conexion.commit()

        return jsonify({"mensaje": "Complejo eliminado correctamente"}), 200

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1451:
            return jsonify({
                "error": "No se puede eliminar el complejo porque tiene canchas asociadas"
            }), 409

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()
