
from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion

#este archivo se encarga de gestionar los equipos del torneo

equipos_bp = Blueprint("equipos", __name__, url_prefix="/equipos")


#verificamos que los IDs sean números positivos
def validar_id(valor):

    try:
        valor = int(valor)
        return valor > 0

    except (ValueError, TypeError):
        return False


#verificamos que se hayan enviado los datos necesarios para crear un equipo
def validar_equipo(datos):

    campos_obligatorios = [
        "nombre",
        "id_torneo",
        "id_facultad",
        "ci_capitan",
        "numero_camiseta_capitan"
    ]

    for campo in campos_obligatorios:
        if campo not in datos or datos[campo] is None:
            return f"Falta el campo obligatorio: {campo}"

    if not str(datos["nombre"]).strip():
        return "El nombre del equipo no puede estar vacío"

    #comprobamos que los IDs sean positivos
    if not validar_id(datos["id_torneo"]):
        return "El id_torneo debe ser un número positivo"

    if not validar_id(datos["id_facultad"]):
        return "El id_facultad debe ser un número positivo"

    #el número de camiseta debe ser un entero positivo
    if not validar_id(datos["numero_camiseta_capitan"]):
        return "El número de camiseta debe ser positivo"

    if not str(datos["ci_capitan"]).isdigit() or len(str(datos["ci_capitan"])) > 8:
        return "La CI del capitán debe contener solamente números y tener hasta 8 dígitos"

    return None


#obtenemos todos los equipos registrados
@equipos_bp.route("", methods=["GET"])
def listar_equipos():

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #consultamos los equipos junto con el nombre del torneo y de la facultad
        sql = """
            SELECT
                e.id_equipo,
                e.nombre,
                e.id_torneo,
                t.nombre AS torneo,
                e.id_facultad,
                f.nombre AS facultad,
                e.ci_capitan,
                j.nombre AS nombre_capitan,
                j.apellido AS apellido_capitan
            FROM equipo e
            JOIN torneo t ON e.id_torneo = t.id_torneo
            JOIN facultad f ON e.id_facultad = f.id_facultad
            JOIN jugador j ON e.ci_capitan = j.ci
            ORDER BY e.nombre
        """

        cursor.execute(sql)
        equipos = cursor.fetchall()

        return jsonify(equipos), 200

    except mysql.connector.Error as error:
        return jsonify({
            "error": "Error al obtener los equipos",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#obtenemos los datos de un equipo específico
@equipos_bp.route("/<int:id_equipo>", methods=["GET"])
def buscar_equipo(id_equipo):

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                e.id_equipo,
                e.nombre,
                e.id_torneo,
                t.nombre AS torneo,
                t.estado AS estado_torneo,
                e.id_facultad,
                f.nombre AS facultad,
                e.ci_capitan,
                j.nombre AS nombre_capitan,
                j.apellido AS apellido_capitan
            FROM equipo e
            JOIN torneo t ON e.id_torneo = t.id_torneo
            JOIN facultad f ON e.id_facultad = f.id_facultad
            JOIN jugador j ON e.ci_capitan = j.ci
            WHERE e.id_equipo = %s
        """

        cursor.execute(sql, (id_equipo,))
        equipo = cursor.fetchone()

        if equipo is None:
            return jsonify({
                "error": "No se encontró un equipo con ese ID"
            }), 404

        return jsonify(equipo), 200

    except mysql.connector.Error as error:
        return jsonify({
            "error": "Error al buscar el equipo",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#creamos un nuevo equipo y agregamos automáticamente a su capitán al plantel
@equipos_bp.route("", methods=["POST"])
def crear_equipo():

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Se debe enviar un JSON válido"
        }), 400

    #verificamos que los datos recibidos sean correctos
    error_validacion = validar_equipo(datos)

    if error_validacion:
        return jsonify({
            "error": error_validacion
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #verificamos que el torneo exista y que todavía esté en inscripción
        cursor.execute(
            """
            SELECT estado
            FROM torneo
            WHERE id_torneo = %s
            """,
            (datos["id_torneo"],)
        )

        torneo = cursor.fetchone()

        if torneo is None:
            return jsonify({
                "error": "No existe un torneo con ese ID"
            }), 404

        if torneo["estado"] != "inscripción":
            return jsonify({
                "error": "Solo se pueden crear equipos durante la inscripción"
            }), 400

        #verificamos que el capitán exista y que pertenezca a la facultad del equipo
        cursor.execute(
            """
            SELECT ci, id_facultad
            FROM jugador
            WHERE ci = %s
            """,
            (datos["ci_capitan"],)
        )

        capitan = cursor.fetchone()

        if capitan is None:
            return jsonify({
                "error": "No existe un jugador con la CI indicada para el capitán"
            }), 404

        if capitan["id_facultad"] != int(datos["id_facultad"]):
            return jsonify({
                "error": "El capitán debe pertenecer a la misma facultad que el equipo"
            }), 400

        #creamos el equipo
        cursor.execute(
            """
            INSERT INTO equipo (
                nombre,
                id_torneo,
                id_facultad,
                ci_capitan
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                datos["nombre"].strip(),
                int(datos["id_torneo"]),
                int(datos["id_facultad"]),
                datos["ci_capitan"]
            )
        )

        #obtenemos el ID generado para el nuevo equipo
        id_equipo = cursor.lastrowid

        #agregamos al capitán como integrante del plantel
        cursor.execute(
            """
            INSERT INTO equipo_jugador_torneo (
                id_equipo,
                ci_jugador,
                id_torneo,
                numero_camiseta
            )
            VALUES (%s, %s, %s, %s)
            """,
            (
                id_equipo,
                datos["ci_capitan"],
                int(datos["id_torneo"]),
                int(datos["numero_camiseta_capitan"])
            )
        )

        #confirmamos las dos inserciones juntas
        conexion.commit()

        return jsonify({
            "mensaje": "Equipo creado correctamente",
            "id_equipo": id_equipo
        }), 201

    except mysql.connector.IntegrityError as error:

        #si falla alguna inserción deshacemos también la anterior
        if conexion:
            conexion.rollback()

        #1062 significa que se intentó ingresar un valor duplicado
        if error.errno == 1062:
            return jsonify({
                "error": "El capitán ya pertenece a un equipo de este torneo o el número de camiseta ya está utilizado"
            }), 409

        #1452 significa que alguna clave foránea no existe
        if error.errno == 1452:
            return jsonify({
                "error": "Alguno de los datos indicados no existe en la base de datos"
            }), 400

        return jsonify({
            "error": "Error de integridad de la base de datos",
            "detalle": str(error)
        }), 400

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al crear el equipo",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#modificamos el nombre de un equipo
@equipos_bp.route("/<int:id_equipo>", methods=["PUT"])
def modificar_equipo(id_equipo):

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Se debe enviar un JSON válido"
        }), 400

    if "nombre" not in datos or not str(datos["nombre"]).strip():
        return jsonify({
            "error": "Se debe indicar un nombre válido para el equipo"
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #verificamos que el equipo exista y obtenemos el estado de su torneo
        cursor.execute(
            """
            SELECT t.estado
            FROM equipo e
            JOIN torneo t ON e.id_torneo = t.id_torneo
            WHERE e.id_equipo = %s
            """,
            (id_equipo,)
        )

        equipo = cursor.fetchone()

        if equipo is None:
            return jsonify({
                "error": "No se encontró un equipo con ese ID"
            }), 404
        #VERIFICACIÓN DEL ESTADO DEL TORNEO
        #los equipos solo se pueden modificar durante la inscripción
        if equipo["estado"] != "inscripción":
            return jsonify({
                "error": "Solo se pueden modificar equipos durante la inscripción"
            }), 400

        cursor.execute(
            """
            UPDATE equipo
            SET nombre = %s
            WHERE id_equipo = %s
            """,
            (datos["nombre"].strip(), id_equipo)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Equipo modificado correctamente"
        }), 200

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al modificar el equipo",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#eliminamos un equipo y sus integrantes del plantel
@equipos_bp.route("/<int:id_equipo>", methods=["DELETE"])
def eliminar_equipo(id_equipo):

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #verificamos que el equipo exista y que su torneo esté en inscripción
        cursor.execute(
            """
            SELECT t.estado
            FROM equipo e
            JOIN torneo t ON e.id_torneo = t.id_torneo
            WHERE e.id_equipo = %s
            """,
            (id_equipo,)
        )

        equipo = cursor.fetchone()

        if equipo is None:
            return jsonify({
                "error": "No se encontró un equipo con ese ID"
            }), 404

        if equipo["estado"] != "inscripción":
            return jsonify({
                "error": "Solo se pueden eliminar equipos durante la inscripción"
            }), 400

        #primero eliminamos los integrantes porque dependen del equipo
        cursor.execute(
            """
            DELETE FROM equipo_jugador_torneo
            WHERE id_equipo = %s
            """,
            (id_equipo,)
        )

        #después eliminamos el equipo
        cursor.execute(
            """
            DELETE FROM equipo
            WHERE id_equipo = %s
            """,
            (id_equipo,)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Equipo eliminado correctamente"
        }), 200

    except mysql.connector.IntegrityError as error:

        if conexion:
            conexion.rollback()

        #1451 significa que otra tabla referencia al equipo mediante una clave foránea
        if error.errno == 1451:
            return jsonify({
                "error": "No se puede eliminar el equipo porque está relacionado con partidos o planillas"
            }), 409

        return jsonify({
            "error": "Error de integridad de la base de datos",
            "detalle": str(error)
        }), 400

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al eliminar el equipo",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
