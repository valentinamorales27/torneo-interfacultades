from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion

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
        SELECT p.id_partido, p.id_torneo, p.numero_fecha,
               p.estado,
               TIMESTAMP(p.dia, t.hora_fin) <= NOW() AS finalizado_horario
        FROM partido p
        JOIN turno t ON p.id_turno = t.id_turno
        WHERE p.id_partido = %s
        """,
        (id_partido,)
    )

    return cursor.fetchone()


#registramos una sancion automatica
#son para amarillas o rojas, el torneo elige las fechas no el planillero
#el planillero elige solo las de las disciplinarias
def registrar_sancion_automatica(cursor, ci_jugador, id_torneo, motivo, numero_fecha):
    #pq la sanción corre a partir de la siguiente fecha
    numero_fecha_inicio = numero_fecha + 1

    #verificamos que no exista ya esa sancion para el jugador
    cursor.execute(
        """
        SELECT id_sancion
        FROM sancion_jugador
        WHERE ci_jugador = %s
        AND id_torneo = %s
        AND motivo = %s
        AND numero_fecha_inicio = %s
        """,
        (ci_jugador, id_torneo, motivo, numero_fecha_inicio)
    )

    if cursor.fetchone():
        return

    #creamos una sancion de una fecha
    cursor.execute(
        """
        INSERT INTO sancion_jugador
            (ci_jugador, id_torneo, motivo, numero_fecha_inicio, cantidad_fechas)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (ci_jugador, id_torneo, motivo, numero_fecha_inicio, 1)
    )


#obtenemos las tarjetas de un partido
@tarjetas_bp.route("/<int:id_partido>/tarjetas", methods=["GET"])
def obtener_tarjetas(id_partido):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        partido = obtener_partido(cursor, id_partido)

        if not partido:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

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
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#registramos una tarjeta en un partido
@tarjetas_bp.route("/<int:id_partido>/tarjetas", methods=["POST"])
def agregar_tarjeta(id_partido):

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se deben enviar los datos de la tarjeta"}), 400

    ci_jugador = datos.get("ci_jugador")
    minuto = datos.get("minuto")
    color = datos.get("color")

    #validamos los datos recibidos
    if not validar_ci(ci_jugador):
        return jsonify({"error": "La cédula del jugador no es válida"}), 400

    if not isinstance(minuto, int) or isinstance(minuto, bool) or minuto < 0:
        return jsonify({"error": "El minuto debe ser un número entero mayor o igual a cero"}), 400

    if color not in ["amarilla", "roja"]:
        return jsonify({"error": "El color debe ser amarilla o roja"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        partido = obtener_partido(cursor, id_partido)

        if not partido:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

        if partido["estado"] == "cancelado":
            return jsonify({"error": "No se pueden registrar tarjetas en un partido cancelado"}), 409

        if partido["estado"] == "postergado":
            return jsonify({"error": "No se pueden registrar tarjetas en un partido postergado"}), 409

        #verificamos que el turno del partido haya finalizado
        if not partido["finalizado_horario"]:
            return jsonify({
                "error": "Las tarjetas solamente se pueden registrar después de finalizado el turno del partido"
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

        #contamos las tarjetas amarillas que ya tiene el jugador en el torneo
        cursor.execute(
            """
            SELECT COUNT(*) AS cantidad_amarillas
            FROM tarjeta t
            JOIN partido p ON t.id_partido = p.id_partido
            WHERE t.ci_jugador = %s
            AND p.id_torneo = %s
            AND t.color = 'amarilla'
            """,
            (ci_jugador, partido["id_torneo"])
        )

        resultado = cursor.fetchone()
        cantidad_amarillas = resultado["cantidad_amarillas"]

        #registramos la tarjeta
        cursor.execute(
            """
            INSERT INTO tarjeta (id_partido, ci_jugador, minuto, color)
            VALUES (%s, %s, %s, %s)
            """,
            (id_partido, ci_jugador, minuto, color)
        )

        id_tarjeta = cursor.lastrowid

        #si es roja, generamos una sancion automatica de una fecha
        if color == "roja":

            registrar_sancion_automatica(
                cursor,
                ci_jugador,
                partido["id_torneo"],
                "roja",
                partido["numero_fecha"]
            )

        #si es la tercera amarilla acumulada, generamos una sancion
        elif color == "amarilla" and cantidad_amarillas + 1 == 3:

            registrar_sancion_automatica(
                cursor,
                ci_jugador,
                partido["id_torneo"],
                "acumulación de amarillas",
                partido["numero_fecha"]
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

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()