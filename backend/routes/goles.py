
from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion

#gestion de los goles de los partidos

goles_bp = Blueprint("goles", __name__, url_prefix="/partidos")


#validamos que la cedula sea correcta
def validar_ci(ci):

    if not isinstance(ci, str) or not ci.isdigit() or len(ci) > 8:
        return False

    return True


#obtenemos los datos del partido
def obtener_partido(cursor, id_partido):

    cursor.execute(
        """
        SELECT p.id_partido, p.id_torneo, p.estado,
               TIMESTAMP(p.dia, t.hora_fin) <= NOW() AS finalizado_horario
        FROM partido p
        JOIN turno t ON p.id_turno = t.id_turno
        WHERE p.id_partido = %s
        """,
        (id_partido,)
    )

    return cursor.fetchone()


#obtenemos los goles de un partido
@goles_bp.route("/<int:id_partido>/goles", methods=["GET"])
def obtener_goles(id_partido):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        partido = obtener_partido(cursor, id_partido)

        if not partido:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

        #consultamos los goles junto con los datos de los jugadores
        cursor.execute(
            """
            SELECT g.id_gol, g.id_partido, g.ci_jugador,
                   j.nombre, j.apellido,
                   g.minuto, g.autogol,
                   pp.id_equipo
            FROM gol g
            JOIN jugador j ON g.ci_jugador = j.ci
            JOIN planilla_partido pp
                ON g.id_partido = pp.id_partido
                AND g.ci_jugador = pp.ci_jugador
            WHERE g.id_partido = %s
            ORDER BY g.minuto
            """,
            (id_partido,)
        )

        goles = cursor.fetchall()

        return jsonify(goles), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#registramos un gol en un partido
@goles_bp.route("/<int:id_partido>/goles", methods=["POST"])
def agregar_gol(id_partido):

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se deben enviar los datos del gol"}), 400

    ci_jugador = datos.get("ci_jugador")
    minuto = datos.get("minuto")
    autogol = datos.get("autogol")

    #validamos los datos recibidos
    if not validar_ci(ci_jugador):
        return jsonify({"error": "La cédula del jugador no es válida"}), 400

    if not isinstance(minuto, int) or isinstance(minuto, bool) or minuto < 0:
        return jsonify({"error": "El minuto debe ser un número entero mayor o igual a cero"}), 400

    if not isinstance(autogol, bool):
        return jsonify({"error": "El campo autogol debe ser verdadero o falso"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        partido = obtener_partido(cursor, id_partido)

        if not partido:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

        if partido["estado"] == "cancelado":
            return jsonify({"error": "No se pueden registrar goles en un partido cancelado"}), 409

        if partido["estado"] == "postergado":
            return jsonify({"error": "No se pueden registrar goles en un partido postergado"}), 409

        #verificamos que el turno del partido haya finalizado
        if not partido["finalizado_horario"]:
            return jsonify({
                "error": "Los goles solamente se pueden registrar después de finalizado el turno del partido"
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

        #registramos el gol
        cursor.execute(
            """
            INSERT INTO gol (id_partido, ci_jugador, minuto, autogol)
            VALUES (%s, %s, %s, %s)
            """,
            (id_partido, ci_jugador, minuto, autogol)
        )

        id_gol = cursor.lastrowid

        conexion.commit()

        return jsonify({
            "mensaje": "Gol registrado correctamente",
            "id_gol": id_gol,
            "id_partido": id_partido,
            "ci_jugador": ci_jugador
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


#eliminamos un gol
@goles_bp.route("/goles/<int:id_gol>", methods=["DELETE"])
def eliminar_gol(id_gol):

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        #verificamos que exista el gol
        cursor.execute(
            """
            SELECT id_gol
            FROM gol
            WHERE id_gol = %s
            """,
            (id_gol,)
        )

        if not cursor.fetchone():
            return jsonify({"error": "No existe un gol con ese identificador"}), 404

        #eliminamos el gol
        cursor.execute(
            """
            DELETE FROM gol
            WHERE id_gol = %s
            """,
            (id_gol,)
        )

        conexion.commit()

        return jsonify({"mensaje": "Gol eliminado correctamente"}), 200

    except mysql.connector.Error as error:
        conexion.rollback()
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()
