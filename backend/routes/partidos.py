
from flask import Blueprint, request, jsonify
import mysql.connector
from datetime import datetime
from db import obtener_conexion
from datetime import datetime
#agregamos permisos
from auth import requiere_rol

#gestion de los partidos del torneo

partidos_bp = Blueprint("partidos", __name__, url_prefix="/partidos")


#validamos que un identificador sea un entero positivo
def validar_id(valor):

    if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
        return False

    return True


#validamos los datos de un partido
def validar_partido(datos):

    if not isinstance(datos, dict) or not datos:
        return "Se deben enviar los datos del partido"

    id_torneo = datos.get("id_torneo")
    numero_fecha = datos.get("numero_fecha")
    id_equipo_local = datos.get("id_equipo_local")
    id_equipo_visitante = datos.get("id_equipo_visitante")
    dia = datos.get("dia")
    if not isinstance(dia, str):
        return "La fecha debe tener el formato YYYY-MM-DD"

    try:
        fecha = datetime.strptime(dia, "%Y-%m-%d")

        if fecha.strftime("%Y-%m-%d") != dia:
            return "La fecha debe tener el formato YYYY-MM-DD"

    except ValueError:
        return "La fecha debe tener el formato YYYY-MM-DD"
    id_turno = datos.get("id_turno")
    nombre_cancha = datos.get("nombre_cancha")
    id_complejo = datos.get("id_complejo")
    estado = datos.get("estado", "programado")

    if not validar_id(id_torneo):
        return "El identificador del torneo debe ser un entero positivo"

    if not validar_id(numero_fecha):
        return "El número de fecha debe ser un entero positivo"

    if not validar_id(id_equipo_local):
        return "El equipo local debe ser válido"

    if not validar_id(id_equipo_visitante):
        return "El equipo visitante debe ser válido"
    #validamos que sean diferentes los equipos
    if id_equipo_local == id_equipo_visitante:
        return "Un equipo no puede jugar contra sí mismo"

    if not isinstance(dia, str):
        return "La fecha del partido debe ser un texto con formato AAAA-MM-DD"

    try:
        datetime.strptime(dia, "%Y-%m-%d")
    except ValueError:
        return "La fecha debe tener el formato AAAA-MM-DD"

    if not validar_id(id_turno):
        return "El identificador del turno debe ser un entero positivo"

    if not isinstance(nombre_cancha, str) or not nombre_cancha.strip():
        return "El nombre de la cancha es obligatorio"

    if not validar_id(id_complejo):
        return "El identificador del complejo debe ser un entero positivo"

    if estado not in ["programado", "jugado", "postergado", "cancelado"]:
        return "El estado del partido no es válido"

    return None


#validamos que los equipos puedan disputar el partido
def validar_equipos_partido(cursor, datos, id_partido=None):

    id_torneo = datos["id_torneo"]
    equipo_local = datos["id_equipo_local"]
    equipo_visitante = datos["id_equipo_visitante"]
    numero_fecha = datos["numero_fecha"]

    # Verificamos que los equipos sean diferentes
    if equipo_local == equipo_visitante:
        return "Un equipo no puede jugar contra sí mismo"

    #verificamos que los dos equipos pertenezcan al torneo
    cursor.execute(
        """
        SELECT id_equipo
        FROM equipo
        WHERE id_torneo = %s
        AND id_equipo IN (%s, %s)
        """,
        (id_torneo, equipo_local, equipo_visitante)
    )

    equipos = cursor.fetchall()

    if len(equipos) != 2:
        return "Ambos equipos deben pertenecer al torneo indicado"

    #verificamos que ambos equipos tengan al menos cinco jugadores
    for id_equipo in [equipo_local, equipo_visitante]:

        cursor.execute(
            """
            SELECT COUNT(*) AS cantidad
            FROM equipo_jugador_torneo
            WHERE id_equipo = %s AND id_torneo = %s
            """,
            (id_equipo, id_torneo)
        )

        resultado = cursor.fetchone()
        if resultado["cantidad"] < 5:
            return "Ambos equipos deben tener al menos cinco jugadores"

    #verificamos que los equipos no se hayan enfrentado anteriormente
    consulta = """
        SELECT id_partido
        FROM partido
        WHERE id_torneo = %s
        AND estado <> 'cancelado'
        AND (
            (id_equipo_local = %s AND id_equipo_visitante = %s)
            OR
            (id_equipo_local = %s AND id_equipo_visitante = %s)
        )
    """

    valores = [
        id_torneo,
        equipo_local,
        equipo_visitante,
        equipo_visitante,
        equipo_local
    ]

    if id_partido is not None:
        consulta += " AND id_partido <> %s"
        valores.append(id_partido)

    cursor.execute(consulta, tuple(valores))

    resultados = cursor.fetchall()

    if resultados:
        return "Estos equipos ya se enfrentaron en este torneo"

    #verificamos que ningún equipo tenga otro partido en la misma fecha
    consulta = """
        SELECT id_partido
        FROM partido
        WHERE id_torneo = %s
        AND numero_fecha = %s
        AND estado <> 'cancelado'
        AND (
            id_equipo_local IN (%s, %s)
            OR id_equipo_visitante IN (%s, %s)
        )
    """

    valores = [
        id_torneo,
        numero_fecha,
        equipo_local,
        equipo_visitante,
        equipo_local,
        equipo_visitante
    ]

    if id_partido is not None:
        consulta += " AND id_partido <> %s"
        valores.append(id_partido)

    cursor.execute(consulta, tuple(valores))

    resultados = cursor.fetchall()

    if resultados:
        return "Uno de los equipos ya tiene un partido programado en esa fecha"

    return None


#validamos que la cancha esté disponible en ese día y turno
def validar_disponibilidad_cancha(cursor, datos, id_partido=None):

    consulta = """
        SELECT id_partido
        FROM partido
        WHERE dia = %s
        AND id_turno = %s
        AND nombre_cancha = %s
        AND id_complejo = %s
        AND estado NOT IN ('cancelado', 'postergado')
    """

    valores = [
        datos["dia"],
        datos["id_turno"],
        datos["nombre_cancha"],
        datos["id_complejo"]
    ]
    #cuando modificamos un partido, osea ya tenía un id que no es none
    #sacamos ese id de los resultados de la consulta pq ese partido no cuenta.
    if id_partido is not None:
        consulta += " AND id_partido <> %s"
        valores.append(id_partido)

    cursor.execute(consulta, tuple(valores))

    resultados = cursor.fetchall()

    if resultados:
        return "La cancha ya está ocupada en ese día y turno"
    return None


#obtenemos todos los partidos
@partidos_bp.route("/", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_partidos():

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT p.id_partido, p.id_torneo, p.numero_fecha, p.dia,
                   p.id_equipo_local, el.nombre AS equipo_local,
                   p.id_equipo_visitante, ev.nombre AS equipo_visitante,
                   p.id_turno, p.nombre_cancha, p.id_complejo,
                   p.estado
            FROM partido p
            JOIN equipo el ON p.id_equipo_local = el.id_equipo
            JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
            ORDER BY p.id_torneo, p.numero_fecha, p.dia
        """

        cursor.execute(consulta)
        partidos = cursor.fetchall()

        return jsonify(partidos), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#obtenemos los partidos de un torneo
@partidos_bp.route("/torneo/<int:id_torneo>", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_partidos_torneo(id_torneo):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT p.id_partido, p.id_torneo, p.numero_fecha, p.dia,
                   p.id_equipo_local, el.nombre AS equipo_local,
                   p.id_equipo_visitante, ev.nombre AS equipo_visitante,
                   p.id_turno, p.nombre_cancha, p.id_complejo,
                   p.estado
            FROM partido p
            JOIN equipo el ON p.id_equipo_local = el.id_equipo
            JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
            WHERE p.id_torneo = %s
            ORDER BY p.numero_fecha, p.dia
        """

        cursor.execute(consulta, (id_torneo,))
        partidos = cursor.fetchall()

        return jsonify(partidos), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#obtenemos un partido por su identificador
@partidos_bp.route("/<int:id_partido>", methods=["GET"])
@requiere_rol("administrador", "planillero")
def obtener_partido(id_partido):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        consulta = """
            SELECT p.id_partido, p.id_torneo, p.numero_fecha, p.dia,
                   p.id_equipo_local, el.nombre AS equipo_local,
                   p.id_equipo_visitante, ev.nombre AS equipo_visitante,
                   p.id_turno, p.nombre_cancha, p.id_complejo,
                   p.estado
            FROM partido p
            JOIN equipo el ON p.id_equipo_local = el.id_equipo
            JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
            WHERE p.id_partido = %s
        """

        cursor.execute(consulta, (id_partido,))
        partido = cursor.fetchone()

        if not partido:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

        return jsonify(partido), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#registramos un nuevo partido
@partidos_bp.route("/", methods=["POST"])
@requiere_rol("administrador")
def crear_partido():

    datos = request.get_json(silent=True)

    error_validacion = validar_partido(datos)

    if error_validacion:
        return jsonify({"error": error_validacion}), 400
    if datos.get("estado", "programado") != "programado":
        return jsonify({
            "error": "Un partido nuevo debe crearse en estado programado"
        }), 400
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        error_equipos = validar_equipos_partido(cursor, datos)

        if error_equipos:
            return jsonify({"error": error_equipos}), 409

        error_cancha = validar_disponibilidad_cancha(cursor, datos)

        if error_cancha:
            return jsonify({"error": error_cancha}), 409

        consulta = """
            INSERT INTO partido (
                id_torneo, numero_fecha,
                id_equipo_local, id_equipo_visitante,
                dia, id_turno, nombre_cancha, id_complejo, estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            datos["id_torneo"],
            datos["numero_fecha"],
            datos["id_equipo_local"],
            datos["id_equipo_visitante"],
            datos["dia"],
            datos["id_turno"],
            datos["nombre_cancha"].strip(),
            datos["id_complejo"],
            "programado" #los partidos nuevos solo pueden ser programados
        )

        cursor.execute(consulta, valores)
        id_partido = cursor.lastrowid

        conexion.commit()

        return jsonify({
            "mensaje": "Partido creado correctamente",
            "id_partido": id_partido
        }), 201

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1452:
            return jsonify({
                "error": "Alguno de los equipos, el turno o la cancha indicada no existe"
            }), 404

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#modificamos los datos de un partido
@partidos_bp.route("/<int:id_partido>", methods=["PUT"])
@requiere_rol("administrador")
def modificar_partido(id_partido):

    datos = request.get_json(silent=True)

    error_validacion = validar_partido(datos)

    if error_validacion:
        return jsonify({"error": error_validacion}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        cursor.execute(
            "SELECT id_partido, estado FROM partido WHERE id_partido = %s",
            (id_partido,)
        )

        partido_actual = cursor.fetchone()

        if not partido_actual:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

        #verificamos que el estado del partido pueda modificarse
        estado_actual = partido_actual["estado"]
        nuevo_estado = datos.get("estado", estado_actual)

        estados_permitidos = {
            "programado": ["jugado", "postergado", "cancelado"],
            "postergado": ["programado", "cancelado"],
            "cancelado": [],
            "jugado": []
        }

        if nuevo_estado != estado_actual and nuevo_estado not in estados_permitidos[estado_actual]:
            return jsonify({
                "error": "No se puede cambiar el partido de ese estado al nuevo estado"
            }), 409

        # verificamos que el partido ya haya terminado antes de marcarlo como jugado
        if nuevo_estado == "jugado":

            cursor.execute(
                """
                SELECT TIMESTAMP(%s, hora_fin) <= NOW() AS horario_finalizado
                FROM turno
                WHERE id_turno = %s
                """,
                (datos["dia"], datos["id_turno"])
            )

            resultado = cursor.fetchone()

            if not resultado:
                return jsonify({
                    "error": "No existe el turno indicado"
                }), 404

            if not resultado["horario_finalizado"]:
                return jsonify({
                    "error": "No se puede marcar el partido como jugado antes de que finalice su horario"
                }), 409
        error_equipos = validar_equipos_partido(cursor, datos, id_partido)

        if error_equipos:
            return jsonify({"error": error_equipos}), 409

        error_cancha = validar_disponibilidad_cancha(cursor, datos, id_partido)

        if error_cancha:
            return jsonify({"error": error_cancha}), 409

        consulta = """
            UPDATE partido
            SET id_torneo = %s,
                numero_fecha = %s,
                id_equipo_local = %s,
                id_equipo_visitante = %s,
                dia = %s,
                id_turno = %s,
                nombre_cancha = %s,
                id_complejo = %s,
                estado = %s
            WHERE id_partido = %s
        """

        valores = (
            datos["id_torneo"],
            datos["numero_fecha"],
            datos["id_equipo_local"],
            datos["id_equipo_visitante"],
            datos["dia"],
            datos["id_turno"],
            datos["nombre_cancha"].strip(),
            datos["id_complejo"],
            datos.get("estado", partido_actual["estado"]),
            id_partido
        )

        cursor.execute(consulta, valores)
        conexion.commit()

        return jsonify({"mensaje": "Partido modificado correctamente"}), 200

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1452:
            return jsonify({
                "error": "Alguno de los equipos, el turno o la cancha indicada no existe"
            }), 404

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()


#eliminamos un partido
@partidos_bp.route("/<int:id_partido>", methods=["DELETE"])
@requiere_rol("administrador")
def eliminar_partido(id_partido):

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        #verificamos que exista el partido
        cursor.execute(
            "SELECT id_partido, estado FROM partido WHERE id_partido = %s",
            (id_partido,)
        )

        partido = cursor.fetchone()

        if not partido:
            return jsonify({"error": "No existe un partido con ese identificador"}), 404

        if partido["estado"] != "programado":
            return jsonify({
                "error": "Solamente se pueden eliminar partidos programados"
            }), 409

        cursor.execute(
            "DELETE FROM partido WHERE id_partido = %s",
            (id_partido,)
        )

        conexion.commit()

        return jsonify({"mensaje": "Partido eliminado correctamente"}), 200

    except mysql.connector.Error as error:
        conexion.rollback()

        if error.errno == 1451:
            return jsonify({
                "error": "No se puede eliminar el partido porque tiene registros asociados"
            }), 409

        return jsonify({"error": str(error)}), 500

    finally:
        cursor.close()
        conexion.close()
