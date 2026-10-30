from flask import Blueprint, jsonify, request
#Blueprint lo usamos porque esto permite que Flask
#pueda reconocer las rutas desde archivos diferentes al app
from db import obtener_conexion
import mysql.connector
from datetime import date

jugadores_bp = Blueprint("jugadores", __name__)

#>>> ABM DE JUGADORES
#Alta de un jugador:
@jugadores_bp.route("/jugadores", methods=["POST"])
def crear_jugador():
    datos = request.get_json() #los datos del que este usando la app
    if not datos: return jsonify({"error": "Se deben enviar los datos del jugador"}), 400 #si no hay datos aviso
    #campos que debería de tener la solicitud post
    campos = [
        "ci",
        "nombre",
        "apellido",
        "email",
        "fecha_nacimiento",
        "id_facultad",
        "tipo"
    ]
    #recorremos cada campo y vemos si esta en la solicitud post
    for campo in campos:
        if campo not in datos or datos[campo] is None:
            return jsonify({"error": f"Falta el campo {campo}"}), 400 #si no está aviso
    
    #validamos los datos
    #checkeamos que los valores no sean vacíos o no contengan elementos clave (ej. el @ del mail)
    if not str(datos["ci"]).strip():
        return jsonify({"error": "La CI no puede estar vacía"}), 400

    if not str(datos["nombre"]).strip() or not str(datos["apellido"]).strip():
        return jsonify({"error": "El nombre y el apellido son obligatorios"}), 400

    if "@" not in str(datos["email"]):
        return jsonify({"error": "El email no es válido"}), 400

    tipos_validos = ["grado", "posgrado", "docente", "funcionario"]

    if datos["tipo"] not in tipos_validos:
        return jsonify({"error": "El tipo de jugador no es válido"}), 400

    try: #probamos pasar la fecha y el id facultad a los formatos que deberían de tener
         #para ver si son válidos y verificamos que la fecha de nacimiento sea coherente
        fecha = date.fromisoformat(datos["fecha_nacimiento"])

        if fecha >= date.today():
            return jsonify({"error": "La fecha de nacimiento debe ser anterior a hoy"}), 400

        id_facultad = int(datos["id_facultad"])

    except (ValueError, TypeError): #notificamos los errores
        return jsonify({"error": "La fecha o el ID de facultad no son válidos"}), 400

    #establecemos la conexión
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try: #generamos la consulta SQL
        consulta = """
            INSERT INTO jugador
            (ci, nombre, apellido, email, fecha_nacimiento, id_facultad, tipo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        #los signos de %s indican dónde van los valores que se reciben
        #preparamos los datos obtenidos por el usuario
        valores = (
            datos["ci"],
            datos["nombre"],
            datos["apellido"],
            datos["email"],
            datos["fecha_nacimiento"],
            id_facultad,
            datos["tipo"]
        )
        #ejecutamos la consulta junto a los datos ingresados
        cursor.execute(consulta, valores)
        conexion.commit() #"guardamos" cambios

        return jsonify({"mensaje": "Jugador creado correctamente"}), 201 #comuncamos si fue exitosa o no
    #si da algún error el try lo mostramos
    except mysql.connector.IntegrityError:#restricción de integridad
        conexion.rollback()#cancela los cambios de esta operación
        return jsonify({
            "error": "La CI o el email ya existen, o la facultad no es válida"
        }), 409

    except mysql.connector.Error:
        conexion.rollback()
        return jsonify({"error": "No se pudo crear el jugador"}), 500
    #cerramos la conexión
    finally:
        cursor.close()
        conexion.close()

#Modificar jugador (se identifica con su ci)
@jugadores_bp.route("/jugadores/<ci>", methods=["PUT"])
def modificar_jugador(ci): 
    #mismos controles/verificaciones que el POST
    datos = request.get_json(silent=True)#significa que si da algún error, devuelve none, entonces los podemos tratar acá

    if not datos:
        return jsonify({"error": "Se deben enviar los datos del jugador"}), 400

    campos = [
        "nombre",
        "apellido",
        "email",
        "fecha_nacimiento",
        "id_facultad",
        "tipo"
    ]

    for campo in campos:
        if campo not in datos or datos[campo] is None:
            return jsonify({"error": f"Falta el campo {campo}"}), 400

    if not str(datos["nombre"]).strip() or not str(datos["apellido"]).strip():
        return jsonify({"error": "El nombre y el apellido son obligatorios"}), 400

    if "@" not in str(datos["email"]):
        return jsonify({"error": "El email no es válido"}), 400

    tipos_validos = ["grado", "posgrado", "docente", "funcionario"]

    if datos["tipo"] not in tipos_validos:
        return jsonify({"error": "El tipo de jugador no es válido"}), 400

    try:
        fecha = date.fromisoformat(datos["fecha_nacimiento"])

        if fecha >= date.today():
            return jsonify({"error": "La fecha de nacimiento debe ser anterior a hoy"}), 400

        id_facultad = int(datos["id_facultad"])

    except (ValueError, TypeError):
        return jsonify({"error": "La fecha o el ID de facultad no son válidos"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        #primero vemos si existe
        cursor.execute(
            "SELECT ci FROM jugador WHERE ci = %s",
            (ci,)
        )

        jugador = cursor.fetchone()
        if jugador is None:
            return jsonify({"error": "No se encontró el jugador"}), 404
        
        consulta = """
            UPDATE jugador
            SET nombre = %s,
                apellido = %s,
                email = %s,
                fecha_nacimiento = %s,
                id_facultad = %s,
                tipo = %s
            WHERE ci = %s
        """

        valores = (
            datos["nombre"],
            datos["apellido"],
            datos["email"],
            datos["fecha_nacimiento"],
            id_facultad,
            datos["tipo"],
            ci
        )

        cursor.execute(consulta, valores)
        conexion.commit()

        return jsonify({"mensaje": "Jugador modificado correctamente"}), 200

    except mysql.connector.IntegrityError:
        conexion.rollback()
        return jsonify({
            "error": "El email ya existe o la facultad no es válida"
        }), 409

    except mysql.connector.Error:
        conexion.rollback()
        return jsonify({"error": "No se pudo modificar el jugador"}), 500

    finally:
        cursor.close()
        conexion.close()

#Baja de un jugador (se identifica con el id)
@jugadores_bp.route("/jugadores/<ci>", methods=["DELETE"])
def eliminar_jugador(ci):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    #en esta no tenemos campos ingresados por el usuario además del id
    try:
        cursor.execute(
            "DELETE FROM jugador WHERE ci = %s",
            (ci,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "No se encontró el jugador"}), 404

        conexion.commit()

        return jsonify({"mensaje": "Jugador eliminado correctamente"}), 200

    except mysql.connector.IntegrityError:
        conexion.rollback()
        return jsonify({
            "error": "No se puede eliminar el jugador porque tiene registros asociados"
        }), 409

    except mysql.connector.Error:
        conexion.rollback()
        return jsonify({"error": "No se pudo eliminar el jugador"}), 500

    finally:
        cursor.close()
        conexion.close()

#>>>Consultar todos los jugadores
@jugadores_bp.route("/jugadores", methods=["GET"])
def obtener_jugadores():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM jugador")
        jugadores = cursor.fetchall()

        return jsonify(jugadores), 200

    except mysql.connector.Error:
        return jsonify({"error": "No se pudieron obtener los jugadores"}), 500

    finally:
        cursor.close()
        conexion.close()

#>>>Consultar jugador por ci
@jugadores_bp.route("/jugadores/<ci>", methods=["GET"])
def obtener_jugador(ci):

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)#convierte el resultado en un diccionario para poder devolverlo con jsonify()

        consulta = """
            SELECT
                ci,
                nombre,
                apellido,
                email,
                fecha_nacimiento,
                tipo,
                id_facultad
            FROM jugador
            WHERE ci = %s
        """

        cursor.execute(consulta, (ci,))
        jugador = cursor.fetchone()

        if jugador is None:
            return jsonify({"error": "No se encontró el jugador"}), 404

        return jsonify(jugador), 200

    except mysql.connector.Error:
        return jsonify({"error": "No se pudo obtener el jugador"}), 500

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()