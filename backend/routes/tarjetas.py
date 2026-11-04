
from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion
#para controlar los permisos de los usuarios
from auth import requiere_rol

#gestor de las tarjetas

tarjetas_bp = Blueprint("tarjetas", __name__, url_prefix="/partidos")


#validamos que la cedula sea correcta
def validar_ci(ci):
    if not isinstance(ci, str) or not ci.isdigit() or len(ci) > 8:
        return False

    return True


#obtenemos los datos del partido
def obtener_partido(cursor, id_partido):

    cursor.execute(
        """
        SELECT p.id_partido, p.id_torneo, p.numero_fecha, p.estado
        FROM partido p
        WHERE p.id_partido = %s
        """,
        (id_partido,)
    )

    return cursor.fetchone()


#recalculamos las sanciones automaticas de un jugador en un torneo
def recalcular_sanciones_automaticas(cursor, ci_jugador, id_torneo):

    #eliminamos solamente las sanciones automaticas
    #las disciplinarias se mantienen
    cursor.execute(
        """
        DELETE FROM sancion_jugador
        WHERE ci_jugador = %s
        AND id_torneo = %s
        AND motivo IN ('roja', 'acumulación de amarillas')
        """,
        (ci_jugador, id_torneo)
    )

    #obtenemos todas las tarjetas del jugador en partidos jugados
    cursor.execute(
        """
        SELECT t.color, t.id_tarjeta, p.numero_fecha, t.minuto
        FROM tarjeta t
        JOIN partido p ON t.id_partido = p.id_partido
        WHERE t.ci_jugador = %s
        AND p.id_torneo = %s
        AND p.estado = 'jugado'
        ORDER BY p.numero_fecha, t.minuto, t.id_tarjeta
        """,
        (ci_jugador, id_torneo)
    )

    tarjetas = cursor.fetchall()

    cantidad_amarillas = 0

    #guardamos cuantas sanciones corresponden a cada fecha de inicio
    sanciones = {}

    for tarjeta in tarjetas:

        #cada roja genera una sancion automatica
        if tarjeta["color"] == "roja":

            clave = ("roja", tarjeta["numero_fecha"] + 1)

            if clave not in sanciones:
                sanciones[clave] = 0

            sanciones[clave] += 1

        #cada tercera amarilla genera una sancion
        elif tarjeta["color"] == "amarilla":

            cantidad_amarillas += 1

            if cantidad_amarillas % 3 == 0:

                clave = (
                    "acumulación de amarillas",
                    tarjeta["numero_fecha"] + 1
                )

                if clave not in sanciones:
                    sanciones[clave] = 0

                sanciones[clave] += 1

    #volvemos a insertar las sanciones que correspondan
    for (motivo, numero_fecha_inicio), cantidad_fechas in sanciones.items():

        cursor.execute(
            """
            INSERT INTO sancion_jugador
                (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                ci_jugador,
                id_torneo,
                motivo,
                numero_fecha_inicio,
                cantidad_fechas
            )
        )


#obtenemos las tarjetas de un partido
@tarjetas_bp.route("/<int:id_partido>/tarjetas", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_tarjetas(id_partido):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        partido = obtener_partido(cursor, id_partido)

        if not partido:
            return jsonify({
                "error": "No existe un partido con ese identificador"
            }), 404

        #consultamos las tarjetas junto con los datos de los jugadores
        cursor.execute(
            """
            SELECT t.id_tarjeta, t.id_partido, t.ci_jugador,
                   j.nombre, j.apellido,
                   t.minuto, t.color,
                   pp.id_equipo
            FROM tarjeta t
            JOIN jugador j ON t.ci_jugador = j.ci
            JOIN planilla_partido pp
                ON t.id_partido = pp.id_partido
                AND t.ci_jugador = pp.ci_jugador
            WHERE t.id_partido = %s
            ORDER BY t.minuto
            """,
            (id_partido,)
        )

        tarjetas = cursor.fetchall()

        return jsonify(tarjetas), 200

    except mysql.connector.Error as error:
        return jsonify({
            "error": str(error)
        }), 500

    finally:
        cursor.close()
        conexion.close()


#registramos una tarjeta en un partido
@tarjetas_bp.route("/<int:id_partido>/tarjetas", methods=["POST"])
@requiere_rol("administrador", "planillero")
def agregar_tarjeta(id_partido):

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Se deben enviar los datos de la tarjeta"
        }), 400

    ci_jugador = datos.get("ci_jugador")
    minuto = datos.get("minuto")
    color = datos.get("color")

    #validamos los datos recibidos
    if not validar_ci(ci_jugador):
        return jsonify({
            "error": "La cédula del jugador no es válida"
        }), 400

    if not isinstance(minuto, int) or isinstance(minuto, bool) or minuto < 0:
        return jsonify({
            "error": "El minuto debe ser un número entero mayor o igual a cero"
        }), 400

    if color not in ["amarilla", "roja"]:
        return jsonify({
            "error": "El color debe ser amarilla o roja"
        }), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        partido = obtener_partido(cursor, id_partido)

        if not partido:
            return jsonify({
                "error": "No existe un partido con ese identificador"
            }), 404

        #verificamos que el partido esté jugado
        if partido["estado"] != "jugado":
            return jsonify({
                "error": "Solamente se pueden registrar tarjetas en partidos jugados"
            }), 409

        #verificamos que el jugador esté registrado en la planilla
        cursor.execute(
            """
            SELECT ci_jugador
            FROM planilla_partido
            WHERE id_partido = %s
            AND ci_jugador = %s
            """,
            (id_partido, ci_jugador)
        )

        if not cursor.fetchone():
            return jsonify({
                "error": "El jugador no está registrado en la planilla de este partido"
            }), 409

        #registramos la tarjeta
        cursor.execute(
            """
            INSERT INTO tarjeta (id_partido, ci_jugador, minuto, color)
            VALUES (%s, %s, %s, %s)
            """,
            (id_partido, ci_jugador, minuto, color)
        )

        id_tarjeta = cursor.lastrowid

        #recalculamos las sanciones automaticas del jugador
        recalcular_sanciones_automaticas(
            cursor,
            ci_jugador,
            partido["id_torneo"]
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Tarjeta registrada correctamente",
            "id_tarjeta": id_tarjeta,
            "ci_jugador": ci_jugador,
            "color": color
        }), 201

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1452:
            return jsonify({
                "error": "El jugador o el partido indicado no existe"
            }), 404

        return jsonify({
            "error": "Error al registrar la tarjeta",
            "detalle": str(error)
        }), 500

    finally:
        cursor.close()
        conexion.close()


#eliminamos una tarjeta
#solamente el administrador puede corregir o eliminar tarjetas
@tarjetas_bp.route("/tarjetas/<int:id_tarjeta>", methods=["DELETE"])
@requiere_rol("administrador")
def eliminar_tarjeta(id_tarjeta):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #buscamos la tarjeta y obtenemos los datos de su partido
        cursor.execute(
            """
            SELECT
                t.id_tarjeta,
                t.ci_jugador,
                t.color,
                p.id_torneo,
                p.estado
            FROM tarjeta t
            JOIN partido p ON t.id_partido = p.id_partido
            WHERE t.id_tarjeta = %s
            """,
            (id_tarjeta,)
        )

        tarjeta = cursor.fetchone()

        if tarjeta is None:
            return jsonify({
                "error": "No se encontró una tarjeta con ese identificador"
            }), 404

        #solamente se pueden eliminar tarjetas de partidos jugados
        if tarjeta["estado"] != "jugado":
            return jsonify({
                "error": "Solamente se pueden eliminar tarjetas de partidos jugados"
            }), 409

        #eliminamos la tarjeta
        cursor.execute(
            """
            DELETE FROM tarjeta
            WHERE id_tarjeta = %s
            """,
            (id_tarjeta,)
        )

        #recalculamos las sanciones automaticas del jugador
        #las sanciones disciplinarias no se modifican
        recalcular_sanciones_automaticas(
            cursor,
            tarjeta["ci_jugador"],
            tarjeta["id_torneo"]
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Tarjeta eliminada correctamente y sanciones automáticas recalculadas"
        }), 200

    except mysql.connector.Error as error:
        conexion.rollback()

        return jsonify({
            "error": "Error al eliminar la tarjeta",
            "detalle": str(error)
        }), 500

    finally:
        cursor.close()
        conexion.close()
