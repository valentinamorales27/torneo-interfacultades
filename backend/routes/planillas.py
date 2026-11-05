
from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion
#para agregar los permisos de usuarios
from auth import requiere_rol


#gestion de las planillas de los partidos

planillas_bp = Blueprint("planillas", __name__, url_prefix="/partidos")


#validamos que la cedula sea correcta
def validar_ci(ci):

    if not isinstance(ci, str) or not ci.isdigit() or len(ci) > 8:
        return False

    return True


#obtenemos los datos del partido
def obtener_partido(cursor, id_partido):

    consulta = """
        SELECT p.id_partido, p.id_torneo, p.numero_fecha,
            p.id_equipo_local, p.id_equipo_visitante,
            p.estado
        FROM partido p
        WHERE p.id_partido = %s
    """

    cursor.execute(consulta, (id_partido,))

    return cursor.fetchone()
#verificamos si un jugador todavía tiene fechas de suspensión pendientes
def jugador_esta_suspendido(cursor, ci_jugador, id_torneo, id_equipo, numero_fecha, id_partido):

    # obtenemos la cantidad total de fechas de suspensión
    # y la fecha de inicio de la primera sanción
    consulta = """
        SELECT
            SUM(cantidad_fechas) AS total_sanciones,
            MIN(numero_fecha_inicio) AS primera_fecha
        FROM sancion_jugador
        WHERE ci_jugador = %s
        AND id_torneo = %s
        AND numero_fecha_inicio <= %s
    """

    cursor.execute(
        consulta,
        (ci_jugador, id_torneo, numero_fecha)
    )

    sanciones = cursor.fetchone()

    # si el jugador no tiene sanciones, puede jugar
    if sanciones["total_sanciones"] is None:
        return False

    # contamos las fechas que jugó su equipo desde la primera sanción
    consulta = """
        SELECT COUNT(DISTINCT p.numero_fecha) AS fechas_cumplidas
        FROM partido p
        WHERE p.id_torneo = %s
        AND (p.id_equipo_local = %s OR p.id_equipo_visitante = %s)
        AND p.numero_fecha >= %s
        AND p.numero_fecha <= %s
        AND (p.estado = 'jugado' OR p.id_partido = %s)
    """

    valores = (
        id_torneo,
        id_equipo,
        id_equipo,
        sanciones["primera_fecha"],
        numero_fecha,
        id_partido
    )

    cursor.execute(consulta, valores)

    fechas_cumplidas = cursor.fetchone()["fechas_cumplidas"]

    # si todavía no cumplió todas las fechas de suspensión,
    # el jugador sigue suspendido
    return fechas_cumplidas <= sanciones["total_sanciones"]

#obtenemos los jugadores de la planilla de un partido
@planillas_bp.route("/<int:id_partido>/planilla", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_planilla(id_partido):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        partido = obtener_partido(cursor, id_partido)

        if not partido:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

        consulta = """
            SELECT pp.id_partido, pp.ci_jugador, pp.id_equipo,
                   j.nombre, j.apellido, ej.numero_camiseta
            FROM planilla_partido pp
            JOIN jugador j ON pp.ci_jugador = j.ci
            JOIN equipo_jugador_torneo ej
                ON pp.id_equipo = ej.id_equipo
                AND pp.ci_jugador = ej.ci_jugador
                AND ej.id_torneo = %s
            WHERE pp.id_partido = %s
            ORDER BY pp.id_equipo, ej.numero_camiseta
        """

        cursor.execute(consulta, (partido["id_torneo"], id_partido))
        jugadores = cursor.fetchall()


        return jsonify(jugadores), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#agregamos un jugador a la planilla de un partido
@planillas_bp.route("/<int:id_partido>/planilla", methods=["POST"])
@requiere_rol("administrador", "planillero")
def agregar_jugador_planilla(id_partido):

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se deben enviar los datos del jugador"}), 400

    ci_jugador = datos.get("ci_jugador")

    if not validar_ci(ci_jugador):
        return jsonify({"error": "La cédula del jugador no es válida"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        partido = obtener_partido(cursor, id_partido)

        if not partido:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

        if partido["estado"] != "programado":
            return jsonify({
                "error": "Solo se pueden modificar planillas de partidos programados"
            }), 409

        #verificamos que el jugador exista y pertenezca a uno de los equipos del partido
        consulta = """
            SELECT ej.id_equipo
            FROM equipo_jugador_torneo ej
            JOIN jugador j ON ej.ci_jugador = j.ci
            WHERE ej.ci_jugador = %s
            AND ej.id_torneo = %s
            AND ej.id_equipo IN (%s, %s)
        """

        valores = (
            ci_jugador,
            partido["id_torneo"],
            partido["id_equipo_local"],
            partido["id_equipo_visitante"]
        )

        cursor.execute(consulta, valores)
        integrante = cursor.fetchone()

        if not integrante:
            return jsonify({
                "error": "El jugador no pertenece al plantel de ninguno de los equipos del partido"
            }), 409

        id_equipo = integrante["id_equipo"]

        #verificamos que el jugador no tenga fechas de suspension pendientes
        if jugador_esta_suspendido(
            cursor,
            ci_jugador,
            partido["id_torneo"],
            id_equipo,
            partido["numero_fecha"],
            id_partido
        ):
            return jsonify({
                "error": "El jugador está suspendido para esta fecha del torneo"
            }), 409

        #registramos al jugador en la planilla
        cursor.execute(
            """
            INSERT INTO planilla_partido (id_partido, ci_jugador, id_equipo)
            VALUES (%s, %s, %s)
            """,
            (id_partido, ci_jugador, id_equipo)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Jugador agregado a la planilla correctamente",
            "ci_jugador": ci_jugador,
            "id_equipo": id_equipo
        }), 201

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1062:
            return jsonify({
                "error": "El jugador ya está registrado en la planilla"
            }), 409

        if error.errno == 1452:
            return jsonify({
                "error": "El jugador o el partido indicado no existe"
            }), 404

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#eliminamos un jugador de la planilla
@planillas_bp.route("/<int:id_partido>/planilla/<string:ci_jugador>", methods=["DELETE"])
@requiere_rol("administrador")
def eliminar_jugador_planilla(id_partido, ci_jugador):

    if not validar_ci(ci_jugador):
        return jsonify({"error": "La cédula del jugador no es válida"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        #verificamos que exista el registro en la planilla
        cursor.execute(
            """
            SELECT id_partido, ci_jugador
            FROM planilla_partido
            WHERE id_partido = %s AND ci_jugador = %s
            """,
            (id_partido, ci_jugador)
        )

        if not cursor.fetchone():
            return jsonify({
                "error": "El jugador no está registrado en la planilla de ese partido"
            }), 404

        #eliminamos al jugador de la planilla
        cursor.execute(
            """
            DELETE FROM planilla_partido
            WHERE id_partido = %s AND ci_jugador = %s
            """,
            (id_partido, ci_jugador)
        )

        conexion.commit()

        return jsonify({"mensaje": "Jugador eliminado de la planilla correctamente"}), 200

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1451:
            return jsonify({
                "error": "No se puede quitar al jugador porque tiene goles o tarjetas registrados en este partido"
            }), 409

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()
