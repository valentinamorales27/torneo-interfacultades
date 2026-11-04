USE torneo_interfacultades;

#Esta view es una tabla que se encarga de calcular las diferentes
#estadísticas de goles por partido. Se usa para facilitar la consulta sobre
#la tabal de posiciones.
create or replace view vista_goles_partido as

select
    p.id_partido,
    p.id_torneo,
    #goles del equipo local
    SUM(
        CASE
            WHEN (pp.id_equipo = p.id_equipo_local AND g.autogol = 0)
            OR (pp.id_equipo = p.id_equipo_visitante AND g.autogol = 1)
            THEN 1
            ELSE 0
        END
    ) AS goles_local,
    #goles del equipo visitante
    SUM(
        CASE
            WHEN (pp.id_equipo = p.id_equipo_visitante AND g.autogol = 0)
            OR (pp.id_equipo = p.id_equipo_local AND g.autogol = 1)
            THEN 1
            ELSE 0
        END
    ) AS goles_visitante

FROM partido p
#unimos los partidos con los goles
LEFT JOIN gol g
    ON p.id_partido = g.id_partido
#unimos los partidos con su planilla
LEFT JOIN planilla_partido pp
    ON g.id_partido = pp.id_partido
    AND g.ci_jugador = pp.ci_jugador
#solo partidos ya termiados, osea jugados
WHERE p.estado = 'jugado'
#agrupamos por partido estas estadísticas
GROUP BY p.id_partido, p.id_torneo;
