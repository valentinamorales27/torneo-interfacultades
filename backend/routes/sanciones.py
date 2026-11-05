
from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion
#permisos de usuarios
from auth import requiere_rol

#gestion de las sanciones

sanciones_bp = Blueprint("sanciones", __name__, url_prefix="/sanciones")


#validamos que la cedula sea correcta
def validar_ci(ci):
    if not isinstance(ci, str) or not ci.isdigit() or len(ci) > 8:
        return False

    return True


#obtenemos las sanciones de un torneo
@sanciones_bp.route("/", methods=["GET"])
@requiere_rol("administrador")
def obtener_sanciones():

    id_torneo = request.args.get("id_torneo")

    if not id_torneo or not id_torneo.isdigit() or int(id_torneo) <= 0:
        return jsonify({
            "error": "Se debe indicar un identificador de torneo válido"
        }), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT s.id_sancion, s.ci_jugador,
                   j.nombre, j.apellido,
                   s.id_torneo, t.nombre AS nombre_torneo,
                   s.motivo, s.numero_fecha_inicio,
                   s.cantidad_fechas
            FROM sancion_jugador s
            JOIN jugador j ON s.ci_jugador = j.ci
            JOIN torneo t ON s.id_torneo = t.id_torneo
            WHERE s.id_torneo = %s
            ORDER BY s.numero_fecha_inicio
            """,
            (int(id_torneo),)
        )

        sanciones = cursor.fetchall()

        return jsonify(sanciones), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#obtenemos las sanciones de un jugador
@sanciones_bp.route("/jugador/<string:ci_jugador>", methods=["GET"])
@requiere_rol("administrador")
def obtener_sanciones_jugador(ci_jugador):

    if not validar_ci(ci_jugador):
        return jsonify({"error": "La cédula del jugador no es válida"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT s.id_sancion, s.ci_jugador,
                   j.nombre, j.apellido,
                   s.id_torneo, t.nombre AS nombre_torneo,
                   s.motivo, s.numero_fecha_inicio,
                   s.cantidad_fechas
            FROM sancion_jugador s
            JOIN jugador j ON s.ci_jugador = j.ci
            JOIN torneo t ON s.id_torneo = t.id_torneo
            WHERE s.ci_jugador = %s
            ORDER BY s.id_torneo, s.numero_fecha_inicio
            """,
            (ci_jugador,)
        )

        sanciones = cursor.fetchall()
        return jsonify(sanciones), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#registramos una sancion disciplinaria
#estas si se pueden registrar manualmente, a diferencia de las automáticas que se generan por tarjetas
@sanciones_bp.route("/", methods=["POST"])
@requiere_rol("administrador")
def agregar_sancion_disciplinaria():

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se deben enviar los datos de la sanción"}), 400

    ci_jugador = datos.get("ci_jugador")
    id_torneo = datos.get("id_torneo")
    numero_fecha_inicio = datos.get("numero_fecha_inicio")
    cantidad_fechas = datos.get("cantidad_fechas")

    #validamos los datos recibidos
    if not validar_ci(ci_jugador):
        return jsonify({"error": "La cédula del jugador no es válida"}), 400

    if not isinstance(id_torneo, int) or isinstance(id_torneo, bool) or id_torneo <= 0:
        return jsonify({"error": "El identificador del torneo debe ser un entero positivo"}), 400

    if not isinstance(numero_fecha_inicio, int) or isinstance(numero_fecha_inicio, bool) or numero_fecha_inicio <= 0:
        return jsonify({"error": "La fecha de inicio debe ser un entero positivo"}), 400

    if not isinstance(cantidad_fechas, int) or isinstance(cantidad_fechas, bool) or cantidad_fechas <= 0:
        return jsonify({"error": "La cantidad de fechas debe ser un entero positivo"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el jugador
        cursor.execute(
            """
            SELECT ci
            FROM jugador
            WHERE ci = %s
            """,
            (ci_jugador,)
        )

        if not cursor.fetchone():
            return jsonify({"error": "No existe un jugador con esa cédula"}), 404

        #verificamos que exista el torneo
        cursor.execute(
            """
            SELECT id_torneo
            FROM torneo
            WHERE id_torneo = %s
            """,
            (id_torneo,)
        )

        if not cursor.fetchone():
            return jsonify({"error": "No existe un torneo con ese identificador"}), 404

        #registramos la sancion disciplinaria
        cursor.execute(
            """
            INSERT INTO sancion_jugador
                (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                ci_jugador,
                id_torneo,
                "disciplinaria",
                numero_fecha_inicio,
                cantidad_fechas
            )
        )

        id_sancion = cursor.lastrowid

        conexion.commit()

        return jsonify({
            "mensaje": "Sanción disciplinaria registrada correctamente",
            "id_sancion": id_sancion,
            "ci_jugador": ci_jugador,
            "cantidad_fechas": cantidad_fechas
        }), 201

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1452:
            return jsonify({
                "error": "El jugador o el torneo indicado no existe"
            }), 404

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#eliminamos una sancion disciplinaria
#las sanciones automaticas se deben corregir eliminando la tarjeta que las genero
@sanciones_bp.route("/<int:id_sancion>", methods=["DELETE"])
@requiere_rol("administrador")
def eliminar_sancion(id_sancion):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #buscamos la sancion
        cursor.execute(
            """
            SELECT motivo
            FROM sancion_jugador
            WHERE id_sancion = %s
            """,
            (id_sancion,)
        )

        sancion = cursor.fetchone()

        if not sancion:
            return jsonify({"error": "No existe una sanción con ese identificador"}), 404

        #solo permitimos eliminar sanciones disciplinarias
        if sancion["motivo"] != "disciplinaria":
            return jsonify({
                "error": "Las sanciones automáticas no se pueden eliminar directamente. Se debe corregir la tarjeta que las generó."
            }), 403

        cursor.execute(
            """
            DELETE FROM sancion_jugador
            WHERE id_sancion = %s
            """,
            (id_sancion,)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Sanción disciplinaria eliminada correctamente"
        }), 200

    except mysql.connector.Error as error:
        conexion.rollback()
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()
