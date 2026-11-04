
from flask import Blueprint, request, jsonify
#blueprint permite que app reconozca archivos de otras rutas
import mysql.connector
from datetime import date
from db import obtener_conexion
#esta parte es para controlar los roles
from auth import requiere_rol

#gestión de jugadores

jugadores_bp = Blueprint("jugadores", __name__, url_prefix="/jugadores")


#verificamos que los datos del jugador sean correctos antes de guardarlos
def validar_jugador(datos):

    campos_obligatorios = [
        "nombre",
        "apellido",
        "email",
        "fecha_nacimiento",
        "tipo",
        "id_facultad"
    ]

    #comprobamos que se hayan enviado todos los campos necesarios
    for campo in campos_obligatorios:
        if campo not in datos or datos[campo] is None:
            return f"Falta el campo obligatorio: {campo}"

    if not str(datos["nombre"]).strip():
        return "El nombre no puede estar vacío"

    if not str(datos["apellido"]).strip():
        return "El apellido no puede estar vacío"

    #verificamos que el email tenga un formato básico válido
    email = str(datos["email"]).strip()

    if "@" not in email or "." not in email.split("@")[-1]:
        return "El email no es válido"

    #el tipo debe coincidir con alguno de los valores permitidos en la tabla
    tipos_validos = ["grado", "posgrado", "docente", "funcionario"]

    if datos["tipo"] not in tipos_validos:
        return "El tipo de jugador no es válido"

    #comprobamos que la fecha tenga el formato correcto y sea antes de hoy
    try:
        fecha_nacimiento = date.fromisoformat(datos["fecha_nacimiento"])

    except (ValueError, TypeError):
        return "La fecha de nacimiento debe tener formato YYYY-MM-DD"

    if fecha_nacimiento >= date.today():
        return "La fecha de nacimiento debe ser anterior a hoy"

    #verificamos que el id de la facultad sea un número positivo
    try:
        id_facultad = int(datos["id_facultad"])

        if id_facultad <= 0:
            return "El id_facultad debe ser positivo"

    except (ValueError, TypeError):
        return "El id_facultad debe ser un número entero"

    return None


#la ci debe contener solo números y como max 8
def validar_ci(ci):

    if not ci:
        return False

    ci = str(ci)
    return ci.isdigit() and len(ci) <= 8


#obtenemos todos los jugadores registrados en la base de datos
@jugadores_bp.route("", methods=["GET"])
@requiere_rol("administrador", "planillero")
def listar_jugadores():

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        #usamos dictionary=True para obtener los resultados como diccionarios para poder acceder más fácil
        cursor = conexion.cursor(dictionary=True)

        #consultamos los jugadores junto con el nombre de su facultad
        sql = """
            SELECT
                j.ci,
                j.nombre,
                j.apellido,
                j.email,
                j.fecha_nacimiento,
                j.tipo,
                j.id_facultad,
                f.nombre AS facultad
            FROM jugador j
            JOIN facultad f ON j.id_facultad = f.id_facultad
            ORDER BY j.apellido, j.nombre
        """

        cursor.execute(sql)
        jugadores = cursor.fetchall()
        return jsonify(jugadores), 200

    except mysql.connector.Error as error:
        return jsonify({
            "error": "Error al obtener los jugadores",
            "detalle": str(error)
        }), 500

    finally:
        #cerramos el cursor y la conexión para liberar recursos
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#buscamos un jugador utilizando su CI
@jugadores_bp.route("/<ci>", methods=["GET"])
@requiere_rol("administrador", "planillero")
def buscar_jugador(ci):

    if not validar_ci(ci):
        return jsonify({
            "error": "La CI debe contener solamente números y tener hasta 8 dígitos"
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        sql = """
            SELECT
                j.ci,
                j.nombre,
                j.apellido,
                j.email,
                j.fecha_nacimiento,
                j.tipo,
                j.id_facultad,
                f.nombre AS facultad
            FROM jugador j
            JOIN facultad f ON j.id_facultad = f.id_facultad
            WHERE j.ci = %s
        """

        #el %s se reemplaza por la CI de forma segura
        cursor.execute(sql, (ci,))
        jugador = cursor.fetchone()

        #si no encontramos al jugador devolvemos un error
        if jugador is None:
            return jsonify({
                "error": "No se encontró un jugador con esa CI"
            }), 404

        return jsonify(jugador), 200

    except mysql.connector.Error as error:
        return jsonify({
            "error": "Error al buscar el jugador",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#registramos un nuevo jugador en la base de datos
@jugadores_bp.route("", methods=["POST"])
@requiere_rol("administrador")
def crear_jugador():

    #obtenemos los datos enviados desde el frontend
    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Se debe enviar un JSON válido"
        }), 400

    #la CI es obligatoria porque es la clave primaria de jugador
    if "ci" not in datos:
        return jsonify({
            "error": "Falta el campo obligatorio: ci"
        }), 400

    if not validar_ci(datos["ci"]):
        return jsonify({
            "error": "La CI debe contener solamente números y tener hasta 8 dígitos"
        }), 400

    #validamos el resto de los datos del jugador
    error_validacion = validar_jugador(datos)

    if error_validacion:
        return jsonify({
            "error": error_validacion
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        sql = """
            INSERT INTO jugador (
                ci,
                nombre,
                apellido,
                email,
                fecha_nacimiento,
                tipo,
                id_facultad
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        valores = (
            str(datos["ci"]),
            datos["nombre"].strip(),
            datos["apellido"].strip(),
            datos["email"].strip(),
            datos["fecha_nacimiento"],
            datos["tipo"],
            int(datos["id_facultad"])
        )

        cursor.execute(sql, valores)

        #confirmamos que el jugador quede guardado
        conexion.commit()

        return jsonify({
            "mensaje": "Jugador creado correctamente",
            "ci": str(datos["ci"])
        }), 201

    except mysql.connector.IntegrityError as error:

        #si ocurre un error deshacemos los cambios
        if conexion:
            conexion.rollback()

        #1062 significa que se intentó ingresar un valor duplicado
        if error.errno == 1062:
            return jsonify({
                "error": "Ya existe un jugador con esa CI o email"
            }), 409

        #1452 significa que la clave foránea indicada no existe
        if error.errno == 1452:
            return jsonify({
                "error": "La facultad indicada no existe"
            }), 400

        return jsonify({
            "error": "Error de integridad de la base de datos",
            "detalle": str(error)
        }), 400

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al crear el jugador",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#modificamos los datos de un jugador existente
@jugadores_bp.route("/<ci>", methods=["PUT"])
@requiere_rol("administrador")
def modificar_jugador(ci):

    if not validar_ci(ci):
        return jsonify({
            "error": "La CI debe contener solamente números y tener hasta 8 dígitos"
        }), 400

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Se debe enviar un JSON válido"
        }), 400

    error_validacion = validar_jugador(datos)

    if error_validacion:
        return jsonify({
            "error": error_validacion
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        #primero verificamos que el jugador exista
        cursor.execute(
            "SELECT ci FROM jugador WHERE ci = %s",
            (ci,)
        )

        jugador = cursor.fetchone()

        if jugador is None:
            return jsonify({
                "error": "No se encontró un jugador con esa CI"
            }), 404

        #actualizamos los datos sin modificar la ci
        sql = """
            UPDATE jugador
            SET
                nombre = %s,
                apellido = %s,
                email = %s,
                fecha_nacimiento = %s,
                tipo = %s,
                id_facultad = %s
            WHERE ci = %s
        """

        valores = (
            datos["nombre"].strip(),
            datos["apellido"].strip(),
            datos["email"].strip(),
            datos["fecha_nacimiento"],
            datos["tipo"],
            int(datos["id_facultad"]),
            ci
        )

        cursor.execute(sql, valores)
        conexion.commit()

        return jsonify({
            "mensaje": "Jugador modificado correctamente"
        }), 200

    except mysql.connector.IntegrityError as error:

        if conexion:
            conexion.rollback()
        #los números de errores los sacmamos de la página de sql
        #1062 significa que el email ya pertenece a otro jugador
        if error.errno == 1062:
            return jsonify({
                "error": "Ya existe otro jugador con ese email"
            }), 409

        #1452 significa que la facultad indicada no existe
        if error.errno == 1452:
            return jsonify({
                "error": "La facultad indicada no existe"
            }), 400

        return jsonify({
            "error": "Error de integridad de la base de datos",
            "detalle": str(error)
        }), 400

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al modificar el jugador",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#eliminamos un jugador de la base de datos
@jugadores_bp.route("/<ci>", methods=["DELETE"])
@requiere_rol("administrador")
def eliminar_jugador(ci):

    if not validar_ci(ci):
        return jsonify({
            "error": "La CI debe contener solamente números y tener hasta 8 dígitos"
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        #verificamos que el jugador exista antes de eliminarlo
        cursor.execute(
            "SELECT ci FROM jugador WHERE ci = %s",
            (ci,)
        )

        jugador = cursor.fetchone()

        if jugador is None:
            return jsonify({
                "error": "No se encontró un jugador con esa CI"
            }), 404

        cursor.execute(
            "DELETE FROM jugador WHERE ci = %s",
            (ci,)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Jugador eliminado correctamente"
        }), 200

    except mysql.connector.IntegrityError as error:

        if conexion:
            conexion.rollback()

        #1451 significa que otra tabla utiliza al jugador mediante una clave foránea
        if error.errno == 1451:
            return jsonify({
                "error": "No se puede eliminar el jugador porque está relacionado con equipos, planillas o sanciones"
            }), 409

        return jsonify({
            "error": "Error de integridad de la base de datos",
            "detalle": str(error)
        }), 400

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al eliminar el jugador",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
