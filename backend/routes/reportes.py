
from flask import Blueprint, jsonify
import mysql.connector
from db import obtener_conexion

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")

#CONSULTAS DEL OBLIGATORIO
#ejecutamos una consulta y devolvemos todos los resultados
#esta funcion nos permite reutilizar la conexion y evitar repetir codigo
def ejecutar_consulta(consulta, parametros=()):
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    try:
        #ejecutamos la consulta utilizando los parametros recibidos
        cursor.execute(consulta, parametros)

        #obtenemos todos los registros encontrados
        resultados = cursor.fetchall()

        return resultados
    finally:
        #cerramos el cursor y la conexion al terminar
        cursor.close()
        conexion.close()


#1.tabla de posiciones
@reportes_bp.route("/tabla-posiciones/<int:id_torneo>", methods=["GET"])
def obtener_tabla_posiciones(id_torneo):

    consulta = """
        SELECT
            e.id_equipo,
            e.nombre AS equipo,

            #calculamos la cantidad de partidos jugados
            CASE
                WHEN SUM(datos.pj) IS NULL THEN 0
                ELSE SUM(datos.pj)
            END AS pj,

            #calculamos la cantidad de partidos ganados
            CASE
                WHEN SUM(datos.pg) IS NULL THEN 0
                ELSE SUM(datos.pg)
            END AS pg,

            #calculamos la cantidad de partidos empatados
            CASE
                WHEN SUM(datos.pe) IS NULL THEN 0
                ELSE SUM(datos.pe)
            END AS pe,

            #calculamos la cantidad de partidos perdidos
            CASE
                WHEN SUM(datos.pp) IS NULL THEN 0
                ELSE SUM(datos.pp)
            END AS pp,

            #calculamos los goles a favor
            CASE
                WHEN SUM(datos.gf) IS NULL THEN 0
                ELSE SUM(datos.gf)
            END AS gf,

            #calculamos los goles en contra
            CASE
                WHEN SUM(datos.gc) IS NULL THEN 0
                ELSE SUM(datos.gc)
            END AS gc,

            #calculamos la diferencia entre goles a favor y en contra
            CASE
                WHEN SUM(datos.gf) IS NULL THEN 0
                ELSE SUM(datos.gf) - SUM(datos.gc)
            END AS dg,

            #calculamos los puntos: 3 por victoria y 1 por empate
            CASE
                WHEN SUM(datos.pg) IS NULL THEN 0
                ELSE SUM(datos.pg) * 3 + SUM(datos.pe)
            END AS puntos

        FROM equipo e

        LEFT JOIN (

            #calculamos las estadisticas de los equipos locales
            SELECT
                p.id_equipo_local AS id_equipo,
                1 AS pj,

                CASE
                    WHEN goles.goles_local > goles.goles_visitante
                    THEN 1 ELSE 0
                END AS pg,

                CASE
                    WHEN goles.goles_local = goles.goles_visitante
                    THEN 1 ELSE 0
                END AS pe,

                CASE
                    WHEN goles.goles_local < goles.goles_visitante
                    THEN 1 ELSE 0
                END AS pp,

                goles.goles_local AS gf,
                goles.goles_visitante AS gc

            FROM partido p

            JOIN (

                #calculamos cuantos goles hizo cada equipo en cada partido
                SELECT
                    p.id_partido,

                    #calculamos los goles del equipo local
                    SUM(
                        CASE
                            WHEN (pp.id_equipo = p.id_equipo_local AND g.autogol = 0)
                            OR (pp.id_equipo = p.id_equipo_visitante AND g.autogol = 1)
                            THEN 1
                            ELSE 0
                        END
                    ) AS goles_local,

                    #calculamos los goles del equipo visitante
                    SUM(
                        CASE
                            WHEN (pp.id_equipo = p.id_equipo_visitante AND g.autogol = 0)
                            OR (pp.id_equipo = p.id_equipo_local AND g.autogol = 1)
                            THEN 1
                            ELSE 0
                        END
                    ) AS goles_visitante

                FROM partido p

                #relacionamos los partidos con sus goles y los jugadores que los hicieron
                LEFT JOIN gol g ON p.id_partido = g.id_partido

                LEFT JOIN planilla_partido pp
                    ON g.id_partido = pp.id_partido
                    AND g.ci_jugador = pp.ci_jugador

                #solo consideramos partidos que ya terminaron
                WHERE p.id_torneo = %s
                AND p.estado = 'jugado'

                GROUP BY p.id_partido

            ) goles ON p.id_partido = goles.id_partido

            WHERE p.id_torneo = %s
            AND p.estado = 'jugado'

            UNION ALL #une los reultados de dos consulats select en una sola tabla
            #junta los de los equipos locales y los visitantes

            #calculamos las estadisticas de los equipos visitantes
            SELECT
                p.id_equipo_visitante AS id_equipo,
                1 AS pj,

                CASE
                    WHEN goles.goles_visitante > goles.goles_local
                    THEN 1 ELSE 0
                END AS pg,

                CASE
                    WHEN goles.goles_visitante = goles.goles_local
                    THEN 1 ELSE 0
                END AS pe,

                CASE
                    WHEN goles.goles_visitante < goles.goles_local
                    THEN 1 ELSE 0
                END AS pp,

                goles.goles_visitante AS gf,
                goles.goles_local AS gc

            FROM partido p

            JOIN (

                #calculamos nuevamente los goles para obtener las estadisticas del visitante
                SELECT
                    p.id_partido,

                    SUM(
                        CASE
                            WHEN (pp.id_equipo = p.id_equipo_local AND g.autogol = 0)
                            OR (pp.id_equipo = p.id_equipo_visitante AND g.autogol = 1)
                            THEN 1
                            ELSE 0
                        END
                    ) AS goles_local,

                    SUM(
                        CASE
                            WHEN (pp.id_equipo = p.id_equipo_visitante AND g.autogol = 0)
                            OR (pp.id_equipo = p.id_equipo_local AND g.autogol = 1)
                            THEN 1
                            ELSE 0
                        END
                    ) AS goles_visitante

                FROM partido p

                LEFT JOIN gol g ON p.id_partido = g.id_partido

                LEFT JOIN planilla_partido pp
                    ON g.id_partido = pp.id_partido
                    AND g.ci_jugador = pp.ci_jugador

                WHERE p.id_torneo = %s
                AND p.estado = 'jugado'

                GROUP BY p.id_partido

            ) goles ON p.id_partido = goles.id_partido

            WHERE p.id_torneo = %s
            AND p.estado = 'jugado'

        ) datos ON e.id_equipo = datos.id_equipo

        #mostramos solamente los equipos del torneo solicitado
        WHERE e.id_torneo = %s

        #agrupamos las estadisticas de cada equipo
        GROUP BY e.id_equipo, e.nombre

        #ordenamos por puntos, diferencia de goles y goles a favor
        ORDER BY puntos DESC, dg DESC, gf DESC, e.nombre ASC
    """

    try:
        resultados = ejecutar_consulta(
            consulta,
            (id_torneo, id_torneo, id_torneo, id_torneo, id_torneo)
        )

        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500


#2.top 10 goleadores
@reportes_bp.route("/goleadores/<int:id_torneo>", methods=["GET"])
def obtener_goleadores(id_torneo):

    consulta = """
        SELECT
            j.ci,
            j.nombre,
            j.apellido,
            e.nombre AS equipo,
            COUNT(g.id_gol) AS goles

        FROM gol g

        #relacionamos los goles con la planilla para saber que jugador los hizo y a que equipo pertenece
        JOIN planilla_partido pp
            ON g.id_partido = pp.id_partido
            AND g.ci_jugador = pp.ci_jugador

        JOIN jugador j ON pp.ci_jugador = j.ci
        JOIN equipo e ON pp.id_equipo = e.id_equipo
        JOIN partido p ON g.id_partido = p.id_partido

        #solo contamos goles de partidos jugados y del torneo solicitado
        WHERE p.id_torneo = %s
        AND p.estado = 'jugado'

        #no contamos los autogoles como goles del jugador
        AND g.autogol = 0

        #agrupamos los goles por jugador y equipo
        GROUP BY j.ci, j.nombre, j.apellido, e.nombre

        #ordenamos de mayor a menor cantidad de goles
        ORDER BY goles DESC, j.apellido ASC, j.nombre ASC

        #devolvemos solamente los primeros diez
        LIMIT 10
    """

    try:
        resultados = ejecutar_consulta(consulta, (id_torneo,))
        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500


#3.fair play
@reportes_bp.route("/fair-play/<int:id_torneo>", methods=["GET"])
def obtener_fair_play(id_torneo):

    consulta = """
        SELECT
            j.ci,
            j.nombre,
            j.apellido,
            e.nombre AS equipo,

            #si el jugador no tiene tarjetas, mostramos cero puntos
            CASE
                WHEN totales.puntos_fair_play IS NULL THEN 0
                ELSE totales.puntos_fair_play
            END AS puntos_fair_play

        FROM equipo_jugador_torneo ej
        JOIN jugador j ON ej.ci_jugador = j.ci
        JOIN equipo e
            ON ej.id_equipo = e.id_equipo
            AND ej.id_torneo = e.id_torneo

        #relacionamos los jugadores con sus puntos de fair play
        LEFT JOIN (
            SELECT
                pp.ci_jugador,
                pp.id_equipo,
                p.id_torneo,
                #cada amarilla suma un punto y cada roja suma tres
                SUM(
                    CASE
                        WHEN t.color = 'amarilla' THEN 1
                        WHEN t.color = 'roja' THEN 3
                        ELSE 0
                    END
                ) AS puntos_fair_play

            FROM tarjeta t
            JOIN planilla_partido pp
                ON t.id_partido = pp.id_partido
                AND t.ci_jugador = pp.ci_jugador

            JOIN partido p ON t.id_partido = p.id_partido
            WHERE p.id_torneo = %s
            AND p.estado = 'jugado'
            GROUP BY pp.ci_jugador, pp.id_equipo, p.id_torneo

        ) totales
            ON ej.ci_jugador = totales.ci_jugador
            AND ej.id_equipo = totales.id_equipo
            AND ej.id_torneo = totales.id_torneo

        WHERE ej.id_torneo = %s
        #el menor puntaje representa el mejor fair play
        ORDER BY puntos_fair_play ASC, j.apellido ASC, j.nombre ASC
    """

    try:
        resultados = ejecutar_consulta(consulta, (id_torneo, id_torneo))
        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500


#4.promedio de goles por fecha
@reportes_bp.route("/promedio-goles/<int:id_torneo>", methods=["GET"])
def obtener_promedio_goles(id_torneo):

    consulta = """
        SELECT
            p.id_torneo,
            p.numero_fecha,
            #contamos todos los goles registrados en los partidos de esa fecha
            COUNT(g.id_gol) AS goles_totales,
            #contamos la cantidad de partidos distintos que se jugaron
            COUNT(DISTINCT p.id_partido) AS partidos_jugados,
            #calculamos el promedio de goles por partido
            ROUND(
                COUNT(g.id_gol) / COUNT(DISTINCT p.id_partido),
                2
            ) AS promedio_goles

        FROM partido p
        LEFT JOIN gol g ON p.id_partido = g.id_partido
        WHERE p.id_torneo = %s
        AND p.estado = 'jugado'
        #agrupamos los resultados por torneo y numero de fecha
        GROUP BY p.id_torneo, p.numero_fecha
        ORDER BY p.numero_fecha
    """

    try:
        resultados = ejecutar_consulta(consulta, (id_torneo,))
        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500


#5.canchas y turnos mas utilizados
@reportes_bp.route("/uso-canchas-turnos/<int:id_torneo>", methods=["GET"])
def obtener_uso_canchas_turnos(id_torneo):

    consulta = """
        SELECT
            c.nombre_cancha,
            c.id_complejo,
            co.nombre AS complejo,
            t.hora_inicio,
            t.hora_fin,
            #contamos cuantos partidos se jugaron en cada cancha y turno
            COUNT(p.id_partido) AS partidos_jugados

        FROM partido p
        JOIN cancha c
            ON p.nombre_cancha = c.nombre_cancha
            AND p.id_complejo = c.id_complejo
        JOIN complejo co ON c.id_complejo = co.id_complejo
        JOIN turno t ON p.id_turno = t.id_turno
        WHERE p.id_torneo = %s
        AND p.estado = 'jugado'
        #agrupamos por cancha, complejo y turno
        GROUP BY
            c.nombre_cancha,
            c.id_complejo,
            co.nombre,
            t.hora_inicio,
            t.hora_fin
        #mostramos primero las canchas y turnos mas utilizados
        ORDER BY partidos_jugados DESC
    """

    try:
        resultados = ejecutar_consulta(consulta, (id_torneo,))
        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500


#6.jugadores por facultad y tipo
@reportes_bp.route("/jugadores-facultad-tipo/<int:id_torneo>", methods=["GET"])
def obtener_jugadores_facultad_tipo(id_torneo):

    consulta = """
        SELECT
            f.id_facultad,
            f.nombre AS facultad,
            j.tipo,
            #contamos la cantidad de jugadores de cada tipo y facultad
            COUNT(DISTINCT j.ci) AS cantidad_jugadores
        FROM equipo_jugador_torneo ej
        JOIN jugador j ON ej.ci_jugador = j.ci
        JOIN facultad f ON j.id_facultad = f.id_facultad
        WHERE ej.id_torneo = %s
        #agrupamos por facultad y tipo de jugador
        GROUP BY f.id_facultad, f.nombre, j.tipo
        ORDER BY f.nombre, j.tipo
    """

    try:
        resultados = ejecutar_consulta(consulta, (id_torneo,))
        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500


#7.jugadores inscriptos que nunca aparecieron en una planilla
@reportes_bp.route("/jugadores-sin-planilla/<int:id_torneo>", methods=["GET"])
def obtener_jugadores_sin_planilla(id_torneo):

    consulta = """
        SELECT
            j.ci,
            j.nombre,
            j.apellido,
            j.tipo,
            e.nombre AS equipo
        FROM equipo_jugador_torneo ej
        JOIN jugador j ON ej.ci_jugador = j.ci
        JOIN equipo e
            ON ej.id_equipo = e.id_equipo
            AND ej.id_torneo = e.id_torneo
        WHERE ej.id_torneo = %s
        #buscamos jugadores para los que no exista ninguna planilla en ese torneo
        AND NOT EXISTS (
            SELECT 1 #seleccionamos un valor, no necesitamos datos de la subconsulta, solo saber si existe alguno o no
            FROM planilla_partido pp
            JOIN partido p ON pp.id_partido = p.id_partido
            WHERE pp.ci_jugador = ej.ci_jugador
            AND p.id_torneo = ej.id_torneo
        )
        ORDER BY e.nombre, j.apellido, j.nombre
    """

    try:
        resultados = ejecutar_consulta(consulta, (id_torneo,))
        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500


#8.sanciones por equipo y motivo
@reportes_bp.route("/sanciones-equipo/<int:id_torneo>", methods=["GET"])
def obtener_sanciones_equipo(id_torneo):

    consulta = """
        SELECT
            e.id_equipo,
            e.nombre AS equipo,
            s.motivo,
            #contamos cuantas sanciones tiene cada equipo por motivo
            COUNT(s.id_sancion) AS cantidad_sanciones
        FROM sancion_jugador s
        #buscamos el equipo al que pertenece el jugador sancionado
        JOIN equipo_jugador_torneo ej
            ON s.ci_jugador = ej.ci_jugador
            AND s.id_torneo = ej.id_torneo
        JOIN equipo e
            ON ej.id_equipo = e.id_equipo
            AND ej.id_torneo = e.id_torneo
        WHERE s.id_torneo = %s
        #agrupamos las sanciones por equipo y motivo
        GROUP BY e.id_equipo, e.nombre, s.motivo
        ORDER BY e.nombre, cantidad_sanciones DESC
    """

    try:
        resultados = ejecutar_consulta(consulta, (id_torneo,))
        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500


#9.porcentaje de partidos por estado
@reportes_bp.route("/estado-partidos/<int:id_torneo>", methods=["GET"])
def obtener_estado_partidos(id_torneo):

    consulta = """
        SELECT
            estado,
            #contamos cuantos partidos hay en cada estado
            COUNT(*) AS cantidad,
            #calculamos el porcentaje que representan sobre el total de partidos
            CASE
                WHEN (
                    SELECT COUNT(*)
                    FROM partido
                    WHERE id_torneo = %s
                ) = 0
                THEN 0
                ELSE ROUND(
                    COUNT(*) * 100.0 /
                    (
                        SELECT COUNT(*)
                        FROM partido
                        WHERE id_torneo = %s
                    ),
                    2
                )
            END AS porcentaje

        FROM partido
        WHERE id_torneo = %s
        #agrupamos los partidos segun su estado
        GROUP BY estado
        ORDER BY estado
    """

    try:
        resultados = ejecutar_consulta(
            consulta,
            (id_torneo, id_torneo, id_torneo)
        )

        return jsonify(resultados), 200

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 500

##CONSULTAS ADICIONALES-3
#obtenemos los partidos cancelados y postergados de un torneo
@reportes_bp.route("/partidos-cancelados-postergados/<int:id_torneo>", methods=["GET"])
def partidos_cancelados_postergados(id_torneo):

    consulta = """
        SELECT
            p.id_partido,
            p.numero_fecha,
            p.dia,
            el.nombre AS equipo_local,
            ev.nombre AS equipo_visitante,
            p.estado,
            t.hora_inicio,
            t.hora_fin,
            c.nombre_cancha,
            co.nombre AS complejo

        FROM partido p

        JOIN equipo el ON p.id_equipo_local = el.id_equipo
        JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
        JOIN turno t ON p.id_turno = t.id_turno
        JOIN cancha c ON p.nombre_cancha = c.nombre_cancha
                     AND p.id_complejo = c.id_complejo
        JOIN complejo co ON c.id_complejo = co.id_complejo

        WHERE p.id_torneo = %s
        AND p.estado IN ('cancelado', 'postergado')

        ORDER BY p.dia, t.hora_inicio
    """

    resultados = ejecutar_consulta(consulta, (id_torneo,))

    return jsonify(resultados), 200
#obtenemos los proximos 3 partidos de un torneo
@reportes_bp.route("/proximos-partidos/<int:id_torneo>", methods=["GET"])
def proximos_partidos(id_torneo):

    consulta = """
        SELECT
            p.id_partido,
            p.numero_fecha,
            p.dia,
            el.nombre AS equipo_local,
            ev.nombre AS equipo_visitante,
            t.hora_inicio,
            t.hora_fin,
            c.nombre_cancha,
            co.nombre AS complejo,
            p.estado

        FROM partido p

        JOIN equipo el ON p.id_equipo_local = el.id_equipo
        JOIN equipo ev ON p.id_equipo_visitante = ev.id_equipo
        JOIN turno t ON p.id_turno = t.id_turno
        JOIN cancha c ON p.nombre_cancha = c.nombre_cancha
                     AND p.id_complejo = c.id_complejo
        JOIN complejo co ON c.id_complejo = co.id_complejo

        WHERE p.id_torneo = %s
        AND p.estado = 'programado'
        AND TIMESTAMP(p.dia, t.hora_inicio) > NOW()

        ORDER BY p.dia, t.hora_inicio
        LIMIT 3
    """

    resultados = ejecutar_consulta(consulta, (id_torneo,))

    return jsonify(resultados), 200

#obtenemos los jugadores que disputaron mas partidos de un torneo
@reportes_bp.route("/jugadores-mas-partidos/<int:id_torneo>", methods=["GET"])
def jugadores_mas_partidos(id_torneo):

    consulta = """
        SELECT
            j.ci,
            j.nombre,
            j.apellido,
            e.nombre AS equipo,
            f.nombre AS facultad,
            COUNT(DISTINCT pp.id_partido) AS partidos_disputados

        FROM planilla_partido pp

        JOIN partido p ON pp.id_partido = p.id_partido
        JOIN jugador j ON pp.ci_jugador = j.ci
        JOIN equipo e ON pp.id_equipo = e.id_equipo
        JOIN facultad f ON j.id_facultad = f.id_facultad

        WHERE p.id_torneo = %s
        AND p.estado = 'jugado'

        GROUP BY
            j.ci,
            j.nombre,
            j.apellido,
            e.nombre,
            f.nombre

        ORDER BY partidos_disputados DESC, j.apellido, j.nombre
    """

    resultados = ejecutar_consulta(consulta, (id_torneo,))

    return jsonify(resultados), 200