
from flask import Blueprint, request, jsonify
import mysql.connector
from db import obtener_conexion

#este archivo se encarga de gestionar los planteles de los equipos

planteles_bp = Blueprint("planteles", __name__, url_prefix="/equipos")


#verificamos que la ci tenga solamente números y hasta 8 dígitos
def validar_ci(ci):

    if not ci:
        return False

    ci = str(ci)

    return ci.isdigit() and len(ci) <= 8


#verificamos que el equipo exista y que su torneo esté en inscripción
def obtener_equipo_en_inscripcion(cursor, id_equipo):

    sql = """
        SELECT
            e.id_equipo,
            e.id_torneo,
            e.id_facultad,
            e.ci_capitan,
            t.estado
        FROM equipo e
        JOIN torneo t ON e.id_torneo = t.id_torneo
        WHERE e.id_equipo = %s
        FOR UPDATE
    """

    cursor.execute(sql, (id_equipo,))
    equipo = cursor.fetchone()

    if equipo is None:
        return None, "No se encontró un equipo con ese id"

    if equipo["estado"] != "inscripción":
        return None, "No se puede modificar el plantel porque el torneo no está en inscripción"

    return equipo, None


#obtenemos los jugadores que integran un equipo
@planteles_bp.route("/<int:id_equipo>/plantel", methods=["GET"])
def listar_plantel(id_equipo):

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #verificamos que el equipo exista
        cursor.execute(
            "SELECT id_equipo FROM equipo WHERE id_equipo = %s",
            (id_equipo,)
        )

        equipo = cursor.fetchone()

        if equipo is None:
            return jsonify({
                "error": "No se encontró un equipo con ese id"
            }), 404

        #obtenemos los integrantes junto con sus datos personales
        #decidimos que se ordene por número de remera pensando en el front
        sql = """
            SELECT
                ej.id_equipo,
                ej.ci_jugador,
                ej.id_torneo,
                ej.numero_camiseta,
                j.nombre,
                j.apellido,
                j.email,
                j.tipo,
                j.id_facultad
            FROM equipo_jugador_torneo ej
            JOIN jugador j ON ej.ci_jugador = j.ci
            WHERE ej.id_equipo = %s
            ORDER BY ej.numero_camiseta
        """

        cursor.execute(sql, (id_equipo,))
        jugadores = cursor.fetchall()

        return jsonify(jugadores), 200

    except mysql.connector.Error as error:
        return jsonify({
            "error": "Error al obtener el plantel",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#agregamos un jugador al plantel de un equipo
@planteles_bp.route("/<int:id_equipo>/plantel", methods=["POST"])
def agregar_jugador_plantel(id_equipo):

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Se debe enviar un JSON válido"
        }), 400

    #verificamos que se hayan enviado los datos necesarios
    if "ci_jugador" not in datos or "numero_camiseta" not in datos:
        return jsonify({
            "error": "Se deben enviar ci_jugador y numero_camiseta"
        }), 400

    ci = datos["ci_jugador"]

    if not validar_ci(ci):
        return jsonify({
            "error": "La CI debe contener solamente números y tener hasta 8 dígitos"
        }), 400

    #verificamos que el número de camiseta sea un entero positivo
    try:
        numero_camiseta = int(datos["numero_camiseta"])

        if numero_camiseta <= 0:
            return jsonify({
                "error": "El número de camiseta debe ser positivo"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "error": "El número de camiseta debe ser un entero"
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #verificamos que el equipo exista y que el torneo esté en inscripción
        equipo, error_equipo = obtener_equipo_en_inscripcion(
            cursor,
            id_equipo
        )

        if error_equipo:
            conexion.rollback()

            if equipo is None:
                return jsonify({
                    "error": error_equipo
                }), 404

            return jsonify({
                "error": error_equipo
            }), 409

        #buscamos al jugador que queremos agregar
        cursor.execute(
            """
            SELECT ci, nombre, apellido, tipo, id_facultad
            FROM jugador
            WHERE ci = %s
            """,
            (str(ci),)
        )

        jugador = cursor.fetchone()

        if jugador is None:
            conexion.rollback()

            return jsonify({
                "error": "No se encontró un jugador con esa CI"
            }), 404

        #todos los integrantes deben pertenecer a la facultad del equipo
        if jugador["id_facultad"] != equipo["id_facultad"]:
            conexion.rollback()

            return jsonify({
                "error": "El jugador no pertenece a la facultad del equipo"
            }), 400

        #obtenemos los integrantes actuales del equipo
        sql = """
            SELECT
                ej.ci_jugador,
                ej.numero_camiseta,
                j.tipo
            FROM equipo_jugador_torneo ej
            JOIN jugador j ON ej.ci_jugador = j.ci
            WHERE ej.id_equipo = %s
            AND ej.id_torneo = %s
        """

        cursor.execute(
            sql,
            (id_equipo, equipo["id_torneo"])
        )

        integrantes = cursor.fetchall()

        #un equipo no puede tener más de 10 integrantes
        if len(integrantes) >= 10:
            conexion.rollback()

            return jsonify({
                "error": "El equipo ya tiene el máximo de 10 jugadores"
            }), 409

        #verificamos que el jugador no esté ya en otro equipo del torneo
        cursor.execute(
            """
            SELECT id_equipo
            FROM equipo_jugador_torneo
            WHERE ci_jugador = %s
            AND id_torneo = %s
            """,
            (str(ci), equipo["id_torneo"])
        )

        ya_inscripto = cursor.fetchone()

        if ya_inscripto is not None:
            conexion.rollback()

            return jsonify({
                "error": "El jugador ya integra un equipo de este torneo"
            }), 409

        #contamos los docentes y funcionarios que ya tiene el equipo
        cantidad_docentes_funcionarios = 0

        for integrante in integrantes:
            if integrante["tipo"] in ["docente", "funcionario"]:
                cantidad_docentes_funcionarios += 1

        #docentes y funcionarios cuentan juntos para el límite de 2
        if jugador["tipo"] in ["docente", "funcionario"]:
            cantidad_docentes_funcionarios += 1

        if cantidad_docentes_funcionarios > 2:
            conexion.rollback()

            return jsonify({
                "error": "El equipo no puede tener más de 2 docentes y funcionarios en total"
            }), 409

        #insertamos al jugador en el plantel
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
                str(ci),
                equipo["id_torneo"],
                numero_camiseta
            )
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Jugador agregado al plantel correctamente",
            "ci_jugador": str(ci),
            "id_equipo": id_equipo
        }), 201

    except mysql.connector.IntegrityError as error:

        if conexion:
            conexion.rollback()

        #1062 significa que se intentó ingresar un valor duplicado
        if error.errno == 1062:
            return jsonify({
                "error": "El jugador ya está en el plantel o el número de camiseta ya está utilizado"
            }), 409

        #1452 significa que alguna clave foránea indicada no existe
        if error.errno == 1452:
            return jsonify({
                "error": "El jugador o el equipo indicado no existe"
            }), 400

        return jsonify({
            "error": "Error de integridad de la base de datos",
            "detalle": str(error)
        }), 400

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al agregar el jugador al plantel",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#quitamos un jugador del plantel de un equipo
@planteles_bp.route("/<int:id_equipo>/plantel/<ci>", methods=["DELETE"])
def quitar_jugador_plantel(id_equipo, ci):

    if not validar_ci(ci):
        return jsonify({
            "error": "La CI debe contener solamente números y tener hasta 8 dígitos"
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #verificamos que el equipo exista y que el torneo esté en inscripción
        equipo, error_equipo = obtener_equipo_en_inscripcion(
            cursor,
            id_equipo
        )

        if error_equipo:
            conexion.rollback()

            if equipo is None:
                return jsonify({
                    "error": error_equipo
                }), 404

            return jsonify({
                "error": error_equipo
            }), 409

        #verificamos que el jugador forme parte de este plantel
        cursor.execute(
            """
            SELECT ci_jugador
            FROM equipo_jugador_torneo
            WHERE id_equipo = %s
            AND id_torneo = %s
            AND ci_jugador = %s
            """,
            (id_equipo, equipo["id_torneo"], ci)
        )

        integrante = cursor.fetchone()

        if integrante is None:
            conexion.rollback()

            return jsonify({
                "error": "El jugador no forma parte del plantel de este equipo"
            }), 404

        #el capitán debe permanecer en el plantel
        if str(equipo["ci_capitan"]) == str(ci):
            conexion.rollback()

            return jsonify({
                "error": "No se puede quitar al capitán del plantel"
            }), 409

        #contamos cuántos integrantes tiene actualmente el equipo
        cursor.execute(
            """
            SELECT COUNT(*) AS cantidad
            FROM equipo_jugador_torneo
            WHERE id_equipo = %s
            AND id_torneo = %s
            """,
            (id_equipo, equipo["id_torneo"])
        )

        cantidad = cursor.fetchone()["cantidad"]

        #un equipo debe tener al menos 5 jugadores
        if cantidad <= 5:
            conexion.rollback()

            return jsonify({
                "error": "El equipo debe tener al menos 5 jugadores"
            }), 409

        #eliminamos al jugador del plantel
        cursor.execute(
            """
            DELETE FROM equipo_jugador_torneo
            WHERE id_equipo = %s
            AND id_torneo = %s
            AND ci_jugador = %s
            """,
            (id_equipo, equipo["id_torneo"], ci)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Jugador quitado del plantel correctamente"
        }), 200

    except mysql.connector.IntegrityError as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "No se puede quitar al jugador porque está relacionado con otros registros",
            "detalle": str(error)
        }), 409

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al quitar el jugador del plantel",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()

##ENDPOINT QUE SE NOS OCURRIÓ APARTE

#cambiamos el capitán de un equipo, pq no lo podemos borrar así nomás
#por dependencias, así que hicimos una función para reemplazarlo por otro jugador de ese mismo plantel
@planteles_bp.route("/<int:id_equipo>/capitan", methods=["PUT"])
def cambiar_capitan(id_equipo):
    #si no pudo obtener los datos devuelve none no una excepción
    datos = request.get_json(silent=True)

    if not datos or "ci_capitan" not in datos:
        return jsonify({
            "error": "Se debe enviar la CI del nuevo capitán"
        }), 400

    ci = datos["ci_capitan"]

    if not validar_ci(ci):
        return jsonify({
            "error": "La CI debe contener solamente números y tener hasta 8 dígitos"
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        #verificamos que el equipo exista y que el torneo esté en inscripción
        equipo, error_equipo = obtener_equipo_en_inscripcion(
            cursor,
            id_equipo
        )

        if error_equipo:
            conexion.rollback()

            if equipo is None:
                return jsonify({"error": error_equipo}), 404

            return jsonify({"error": error_equipo}), 409

        #verificamos que el nuevo capitán forme parte del plantel
        cursor.execute(
            """
            SELECT ci_jugador
            FROM equipo_jugador_torneo
            WHERE id_equipo = %s
            AND id_torneo = %s
            AND ci_jugador = %s
            """,
            (id_equipo, equipo["id_torneo"], str(ci))
        )

        integrante = cursor.fetchone()

        if integrante is None:
            conexion.rollback()

            return jsonify({
                "error": "El nuevo capitán debe formar parte del plantel"
            }), 400

        #actualizamos el capitán del equipo
        cursor.execute(
            """
            UPDATE equipo
            SET ci_capitan = %s
            WHERE id_equipo = %s
            """,
            (str(ci), id_equipo)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Capitán cambiado correctamente",
            "ci_capitan": str(ci)
        }), 200

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al cambiar el capitán",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
