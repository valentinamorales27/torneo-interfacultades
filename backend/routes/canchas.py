
from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion
#para controlar permisos
from auth import requiere_rol

#gestion de las canchas

canchas_bp = Blueprint("canchas", __name__, url_prefix="/canchas")


#validamos que el identificador del complejo sea correcto
def validar_id(id_complejo):

    if not isinstance(id_complejo, int) or isinstance(id_complejo, bool) or id_complejo <= 0:
        return False

    return True


#validamos los datos de una cancha
def validar_cancha(datos):

    if not datos:
        return "Se deben enviar los datos de la cancha"

    nombre_cancha = datos.get("nombre_cancha")
    id_complejo = datos.get("id_complejo")
    superficie = datos.get("superficie")
    techada = datos.get("techada")

    if not nombre_cancha or not isinstance(nombre_cancha, str) or not nombre_cancha.strip():
        return "El nombre de la cancha es obligatorio"

    if not validar_id(id_complejo):
        return "El identificador del complejo debe ser un entero positivo"

    if superficie not in ["sintético", "parquet"]:
        return "La superficie debe ser sintético o parquet"

    if not isinstance(techada, bool):
        return "El campo techada debe ser verdadero o falso"

    return None


#validamos los datos que se pueden modificar de una cancha
def validar_modificacion_cancha(datos):

    if not datos:
        return "Se deben enviar los datos de la cancha"

    superficie = datos.get("superficie")
    techada = datos.get("techada")

    if superficie not in ["sintético", "parquet"]:
        return "La superficie debe ser sintético o parquet"

    if not isinstance(techada, bool):
        return "El campo techada debe ser verdadero o falso"

    return None


#obtenemos todas las canchas
@canchas_bp.route("/", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_canchas():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    #se obtienen por la clave primaria compuesta,
    #puede haber canchas con el mismo nombre pero si son de
    #diferentes complejos
    try:
        consulta = """
            SELECT c.nombre_cancha, c.id_complejo,
                   c.superficie, c.techada,
                   co.nombre AS nombre_complejo
            FROM cancha c
            JOIN complejo co ON c.id_complejo = co.id_complejo
            ORDER BY c.id_complejo, c.nombre_cancha
        """

        cursor.execute(consulta)
        canchas = cursor.fetchall()

        return jsonify(canchas), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#obtenemos una cancha por su nombre y complejo
@canchas_bp.route("/<int:id_complejo>/<string:nombre_cancha>", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_cancha(id_complejo, nombre_cancha):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT c.nombre_cancha, c.id_complejo,
                   c.superficie, c.techada,
                   co.nombre AS nombre_complejo
            FROM cancha c
            JOIN complejo co ON c.id_complejo = co.id_complejo
            WHERE c.nombre_cancha = %s
            AND c.id_complejo = %s
        """

        cursor.execute(consulta, (nombre_cancha, id_complejo))
        cancha = cursor.fetchone()

        if not cancha:
            return jsonify({"error": "No existe una cancha con esos datos"}), 404

        return jsonify(cancha), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#registramos una nueva cancha
@canchas_bp.route("/", methods=["POST"])
@requiere_rol("administrador")
def crear_cancha():

    datos = request.get_json(silent=True)

    error_validacion = validar_cancha(datos)

    if error_validacion:
        return jsonify({"error": error_validacion}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        consulta = """
            INSERT INTO cancha (nombre_cancha, id_complejo, superficie, techada)
            VALUES (%s, %s, %s, %s)
        """

        valores = (
            datos["nombre_cancha"].strip(),
            datos["id_complejo"],
            datos["superficie"],
            datos["techada"]
        )

        cursor.execute(consulta, valores)
        conexion.commit()

        return jsonify({
            "mensaje": "Cancha creada correctamente"
        }), 201

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1062:
            return jsonify({
                "error": "Ya existe una cancha con ese nombre en ese complejo"
            }), 409

        if error.errno == 1452:
            return jsonify({
                "error": "No existe el complejo indicado"
            }), 404

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#modificamos los datos de una cancha
@canchas_bp.route("/<int:id_complejo>/<string:nombre_cancha>", methods=["PUT"])
@requiere_rol("administrador")
def modificar_cancha(id_complejo, nombre_cancha):

    datos = request.get_json(silent=True)

    error_validacion = validar_modificacion_cancha(datos)

    if error_validacion:
        return jsonify({"error": error_validacion}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        #verificamos que exista la cancha
        cursor.execute(
            """
            SELECT nombre_cancha
            FROM cancha
            WHERE nombre_cancha = %s AND id_complejo = %s
            """,
            (nombre_cancha, id_complejo)
        )

        if not cursor.fetchone():
            return jsonify({"error": "No existe una cancha con esos datos"}), 404

        consulta = """
            UPDATE cancha
            SET superficie = %s,
                techada = %s
            WHERE nombre_cancha = %s
            AND id_complejo = %s
        """

        valores = (
            datos["superficie"],
            datos["techada"],
            nombre_cancha,
            id_complejo
        )

        cursor.execute(consulta, valores)
        conexion.commit()

        return jsonify({"mensaje": "Cancha modificada correctamente"}), 200

    except mysql.connector.Error as error:
        conexion.rollback()
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#eliminamos una cancha
@canchas_bp.route("/<int:id_complejo>/<string:nombre_cancha>", methods=["DELETE"])
@requiere_rol("administrador")
def eliminar_cancha(id_complejo, nombre_cancha):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        #verificamos que exista la cancha
        cursor.execute(
            """
            SELECT nombre_cancha
            FROM cancha
            WHERE nombre_cancha = %s AND id_complejo = %s
            """,
            (nombre_cancha, id_complejo)
        )

        if not cursor.fetchone():
            return jsonify({"error": "No existe una cancha con esos datos"}), 404

        cursor.execute(
            """
            DELETE FROM cancha
            WHERE nombre_cancha = %s
            AND id_complejo = %s
            """,
            (nombre_cancha, id_complejo)
        )

        conexion.commit()

        return jsonify({"mensaje": "Cancha eliminada correctamente"}), 200

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1451:
            return jsonify({
                "error": "No se puede eliminar la cancha porque tiene partidos asociados"
            }), 409

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()
