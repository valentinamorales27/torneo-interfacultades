from flask import Blueprint, jsonify, request
#Blueprint lo usamos porque esto permite que Flask
#pueda reconocer las rutas desde archivos diferentes al app
from db import obtener_conexion
import mysql.connector
from datetime import date

equipos_bp = Blueprint("equipos", __name__)

#>>> ABM DE EQUIPOS
#Alta de equipos:
@equipos_bp.route("/equipos", methods=["POST"])
def crear_equipo():

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({"error": "Se deben enviar los datos del equipo"}), 400

    campos = [
        "nombre",
        "id_torneo",
        "id_facultad",
        "ci_capitan",
        "numero_camiseta_capitan"
    ]

    for campo in campos:
        if campo not in datos or datos[campo] is None:
            return jsonify({"error": f"Falta el campo {campo}"}), 400

    if not str(datos["nombre"]).strip():
        return jsonify({"error": "El nombre del equipo es obligatorio"}), 400

    try:
        id_torneo = int(datos["id_torneo"])
        id_facultad = int(datos["id_facultad"])
        numero_camiseta = int(datos["numero_camiseta_capitan"])

        if id_torneo <= 0 or id_facultad <= 0 or numero_camiseta <= 0:
            return jsonify({"error": "Los IDs y el número de camiseta deben ser positivos"}), 400

    except (ValueError, TypeError):
        return jsonify({"error": "Los IDs y el número de camiseta deben ser números enteros"}), 400

    ci_capitan = str(datos["ci_capitan"]).strip()

    if not ci_capitan:
        return jsonify({"error": "La CI del capitán es obligatoria"}), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        #checkeamos que el torneo exista (esté en la tabla de torneos)
        #y que su estado sea inscripción porque sino no se puede realizar
        cursor.execute(
            "SELECT estado FROM torneo WHERE id_torneo = %s",
            (id_torneo,)
        )
        torneo = cursor.fetchone() #devuelve una tupla de un solo elemento que tiene la columna seleccionada

        if torneo is None:
            return jsonify({"error": "No existe ese torneo"}), 404

        if torneo[0] != "inscripción":
            return jsonify({"error": "Solo se pueden crear equipos durante la inscripción"}), 400

        #acá verificamos que el capitán exista dentro de los jugadores y
        #que efectivamente vaya a esa facultad
        cursor.execute(
            """
            SELECT ci
            FROM jugador
            WHERE ci = %s AND id_facultad = %s
            """,
            (ci_capitan, id_facultad)
        )
        capitan = cursor.fetchone()

        if capitan is None:
            return jsonify({
                "error": "El capitán no existe o no pertenece a esa facultad"
            }), 400

        #luego de todas las verificaciones lo creamos
        consulta = """
            INSERT INTO equipo (nombre, id_torneo, id_facultad, ci_capitan)
            VALUES (%s, %s, %s, %s)
        """

        valores = (
            datos["nombre"].strip(),
            id_torneo,
            id_facultad,
            ci_capitan
        )

        cursor.execute(consulta, valores)

        #cursor.lastrowid devuelve el último id que se genero automáticamente
        #porque en la bd pusimos auto increment así puede agregar al capitán 
        #como el primer jugador del plantel
        id_equipo = cursor.lastrowid

        consulta_plantel = """
            INSERT INTO equipo_jugador_torneo
            (id_equipo, ci_jugador, id_torneo, numero_camiseta)
            VALUES (%s, %s, %s, %s)
        """

        cursor.execute(
            consulta_plantel,
            (id_equipo, ci_capitan, id_torneo, numero_camiseta)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Equipo creado correctamente",
            "id_equipo": id_equipo
        }), 201

    except mysql.connector.IntegrityError:
        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "No se pudo crear el equipo. Verificá que el capitán no esté inscripto en otro equipo del mismo torneo"
        }), 409

    except mysql.connector.Error:
        if conexion:
            conexion.rollback()

        return jsonify({"error": "Ocurrió un error al crear el equipo"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#Modificar un equipo:
@equipos_bp.route("/equipos/<int:id_equipo>", methods=["PUT"])
def modificar_equipo(id_equipo):

    datos = request.get_json(silent=True)

    if not datos or "nombre" not in datos or datos["nombre"] is None:
        return jsonify({"error": "Se debe enviar el nombre del equipo"}), 400

    if not str(datos["nombre"]).strip():
        return jsonify({"error": "El nombre del equipo no puede estar vacío"}), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        #vemos si el equipo existe primero
        cursor.execute(
            "SELECT id_torneo FROM equipo WHERE id_equipo = %s",
            (id_equipo,)
        )
        equipo = cursor.fetchone()

        if equipo is None:
            return jsonify({"error": "No se encontró el equipo"}), 404

        #verificamos que el torneo este en estado inscripción porque sino no podemos ejecutarla
        cursor.execute(
            "SELECT estado FROM torneo WHERE id_torneo = %s",
            (equipo[0],)
        )
        torneo = cursor.fetchone()

        if torneo[0] != "inscripción":
            return jsonify({"error": "Solo se pueden modificar equipos durante la inscripción"}), 400

        cursor.execute(
            """
            UPDATE equipo
            SET nombre = %s
            WHERE id_equipo = %s
            """,
            (datos["nombre"].strip(), id_equipo)
        )

        conexion.commit()

        return jsonify({"mensaje": "Equipo modificado correctamente"}), 200

    except mysql.connector.IntegrityError:
        if conexion:
            conexion.rollback()
        return jsonify({"error": "No se pudo modificar el equipo"}), 409

    except mysql.connector.Error:
        if conexion:
            conexion.rollback()
        return jsonify({"error": "Ocurrió un error al modificar el equipo"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#Baja de un equipo
@equipos_bp.route("/equipos/<int:id_equipo>", methods=["DELETE"])
def eliminar_equipo(id_equipo):

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        #primero vemos si el equipo equiste.
        #si existe obtenemos el id del torneo
        cursor.execute(
            "SELECT id_torneo FROM equipo WHERE id_equipo = %s",
            (id_equipo,)
        )
        equipo = cursor.fetchone()

        if equipo is None:
            return jsonify({"error": "No se encontró el equipo"}), 404

        #vemos si está en estado de inscripción
        cursor.execute(
            "SELECT estado FROM torneo WHERE id_torneo = %s",
            (equipo[0],)
        )
        torneo = cursor.fetchone()

        if torneo[0] != "inscripción":
            return jsonify({"error": "Solo se pueden eliminar equipos durante la inscripción"}), 400

        #eliminamos sus jugadores del plantel primero
        cursor.execute(
            "DELETE FROM equipo_jugador_torneo WHERE id_equipo = %s",
            (id_equipo,)
        )

        #finalmente eliminamos el equipo
        cursor.execute(
            "DELETE FROM equipo WHERE id_equipo = %s",
            (id_equipo,)
        )

        conexion.commit()

        return jsonify({"mensaje": "Equipo eliminado correctamente"}), 200

    except mysql.connector.IntegrityError:
        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "No se puede eliminar el equipo porque tiene partidos u otros registros asociados"
        }), 409

    except mysql.connector.Error:
        if conexion:
            conexion.rollback()

        return jsonify({"error": "Ocurrió un error al eliminar el equipo"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#>>>Consula de todos los equipos
@equipos_bp.route("/equipos", methods=["GET"])
def obtener_equipos():

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                e.id_equipo,
                e.nombre,
                e.id_torneo,
                t.nombre AS nombre_torneo,
                e.id_facultad,
                f.nombre AS nombre_facultad,
                e.ci_capitan,
                j.nombre AS nombre_capitan,
                j.apellido AS apellido_capitan
            FROM equipo e
            JOIN torneo t ON e.id_torneo = t.id_torneo
            JOIN facultad f ON e.id_facultad = f.id_facultad
            JOIN jugador j ON e.ci_capitan = j.ci
            ORDER BY e.id_equipo
        """

        cursor.execute(consulta)
        equipos = cursor.fetchall()

        return jsonify(equipos), 200

    except mysql.connector.Error:
        return jsonify({"error": "No se pudieron obtener los equipos"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()

#>>>Consultar equipo por id
@equipos_bp.route("/equipos/<int:id_equipo>", methods=["GET"])
def obtener_equipo(id_equipo):

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        consulta = """
            SELECT
                e.id_equipo,
                e.nombre,
                e.id_torneo,
                t.nombre AS nombre_torneo,
                e.id_facultad,
                f.nombre AS nombre_facultad,
                e.ci_capitan,
                j.nombre AS nombre_capitan,
                j.apellido AS apellido_capitan
            FROM equipo e
            JOIN torneo t ON e.id_torneo = t.id_torneo
            JOIN facultad f ON e.id_facultad = f.id_facultad
            JOIN jugador j ON e.ci_capitan = j.ci
            WHERE e.id_equipo = %s
        """

        cursor.execute(consulta, (id_equipo,))
        equipo = cursor.fetchone()

        if equipo is None:
            return jsonify({"error": "No se encontró el equipo"}), 404

        return jsonify(equipo), 200

    except mysql.connector.Error:
        return jsonify({"error": "No se pudo obtener el equipo"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()