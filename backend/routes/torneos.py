
from flask import Blueprint, request, jsonify
import mysql.connector
from datetime import datetime
from db import obtener_conexion
from auth import requiere_rol

#este archivo se encarga de gestionar los torneos

torneos_bp = Blueprint("torneos", __name__, url_prefix="/torneos")


#obtenemos todos los torneos
@torneos_bp.route("/", methods=["GET"])
@requiere_rol("administrador", "planillero")
def listar_torneos():

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_torneo,
                nombre,
                anio,
                semestre,
                fecha_inicio,
                fecha_fin,
                estado
            FROM torneo
            ORDER BY anio DESC, semestre DESC
        """)

        torneos = cursor.fetchall()

        return jsonify(torneos), 200

    except mysql.connector.Error as error:
        return jsonify({
            "error": "Error al obtener los torneos",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#obtenemos un torneo específico
@torneos_bp.route("/<int:id_torneo>", methods=["GET"])
@requiere_rol("administrador", "planillero")
def buscar_torneo(id_torneo):

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_torneo,
                nombre,
                anio,
                semestre,
                fecha_inicio,
                fecha_fin,
                estado
            FROM torneo
            WHERE id_torneo = %s
        """, (id_torneo,))

        torneo = cursor.fetchone()

        if torneo is None:
            return jsonify({
                "error": "No se encontró un torneo con ese ID"
            }), 404

        return jsonify(torneo), 200

    except mysql.connector.Error as error:
        return jsonify({
            "error": "Error al buscar el torneo",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()


#creamos un torneo nuevo
@torneos_bp.route("/", methods=["POST"])
@requiere_rol("administrador")
def crear_torneo():

    datos = request.get_json(silent=True)

    if not datos:
        return jsonify({
            "error": "Se debe enviar un JSON válido"
        }), 400

    campos = [
        "nombre",
        "anio",
        "semestre",
        "fecha_inicio",
        "fecha_fin",
        "estado"
    ]

    for campo in campos:
        if campo not in datos or datos[campo] is None:
            return jsonify({
                "error": f"Falta el campo obligatorio: {campo}"
            }), 400

    if not isinstance(datos["nombre"], str) or not datos["nombre"].strip():
        return jsonify({
            "error": "El nombre del torneo no puede estar vacío"
        }), 400

    if len(datos["nombre"].strip()) > 50:
        return jsonify({
            "error": "El nombre no puede superar los 50 caracteres"
        }), 400

    try:
        anio = int(datos["anio"])
        semestre = int(datos["semestre"])
    except (ValueError, TypeError):
        return jsonify({
            "error": "El año y el semestre deben ser números"
        }), 400

    if anio <= 0:
        return jsonify({
            "error": "El año debe ser positivo"
        }), 400

    if semestre not in (1, 2):
        return jsonify({
            "error": "El semestre debe ser 1 o 2"
        }), 400

    if datos["estado"] not in ("inscripción", "en curso", "finalizado"):
        return jsonify({
            "error": "El estado del torneo no es válido"
        }), 400

    try:
        fecha_inicio = datetime.strptime(datos["fecha_inicio"], "%Y-%m-%d").date()
        fecha_fin = datetime.strptime(datos["fecha_fin"], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return jsonify({
            "error": "Las fechas deben tener el formato YYYY-MM-DD"
        }), 400

    if fecha_fin < fecha_inicio:
        return jsonify({
            "error": "La fecha de fin no puede ser anterior a la fecha de inicio"
        }), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO torneo (
                nombre,
                anio,
                semestre,
                fecha_inicio,
                fecha_fin,
                estado
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            datos["nombre"].strip(),
            anio,
            semestre,
            fecha_inicio,
            fecha_fin,
            datos["estado"]
        ))

        id_torneo = cursor.lastrowid

        conexion.commit()

        return jsonify({
            "mensaje": "Torneo creado correctamente",
            "id_torneo": id_torneo
        }), 201

    except mysql.connector.IntegrityError as error:

        if conexion:
            conexion.rollback()

        if error.errno == 1062:
            return jsonify({
                "error": "Ya existe un torneo para ese año y semestre"
            }), 409

        return jsonify({
            "error": "Error de integridad de la base de datos",
            "detalle": str(error)
        }), 400

    except mysql.connector.Error as error:

        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "Error al crear el torneo",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()
    
#modificamos el estado de un torneo
@torneos_bp.route("/<int:id_torneo>/estado", methods=["PUT"])
@requiere_rol("administrador")
def modificar_estado_torneo(id_torneo):
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "estado" not in datos:
        return jsonify({"error": "Se debe indicar el estado del torneo"}), 400

    estado = datos["estado"]
    estados_validos = ("inscripción", "en curso", "finalizado")

    if estado not in estados_validos:
        return jsonify({"error": "El estado del torneo no es válido"}), 400

    conexion = None
    cursor = None

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT estado FROM torneo WHERE id_torneo = %s",
            (id_torneo,)
        )

        torneo = cursor.fetchone()

        if torneo is None:
            return jsonify({"error": "El torneo no existe"}), 404

        cursor.execute(
            "UPDATE torneo SET estado = %s WHERE id_torneo = %s",
            (estado, id_torneo)
        )

        conexion.commit()

        return jsonify({
            "mensaje": "Estado del torneo actualizado correctamente",
            "id_torneo": id_torneo,
            "estado": estado
        }), 200

    except mysql.connector.Error as error:
        if conexion:
            conexion.rollback()

        return jsonify({
            "error": "No se pudo modificar el estado del torneo",
            "detalle": str(error)
        }), 500

    finally:
        if cursor:
            cursor.close()

        if conexion:
            conexion.close()

