
import requests

BASE_URL = "http://localhost:5000"

# Utilizamos una sesión para conservar las cookies del login
sesion = requests.Session()


# 1. Iniciar sesión como administrador
respuesta_login = sesion.post(
    f"{BASE_URL}/login",
    json={
        "correo": "admin_torneo@gmail.com",
        "contraseña": "admin1234"
    }
)

print("LOGIN:", respuesta_login.status_code)

if respuesta_login.status_code != 200:
    print("No se pudo iniciar sesión.")
    print(respuesta_login.text)
    exit()


# ID del torneo que queremos consultar
id_torneo = 1


# Endpoints de todos los reportes
reportes = [
    ("Tabla de posiciones", f"/reportes/tabla-posiciones/{id_torneo}"),
    ("Top 10 goleadores", f"/reportes/goleadores/{id_torneo}"),
    ("Fair Play", f"/reportes/fair-play/{id_torneo}"),
    ("Promedio de goles por fecha", f"/reportes/promedio-goles/{id_torneo}"),
    ("Uso de canchas y turnos", f"/reportes/uso-canchas-turnos/{id_torneo}"),
    ("Jugadores por facultad y tipo", f"/reportes/jugadores-facultad-tipo/{id_torneo}"),
    ("Jugadores sin planilla", f"/reportes/jugadores-sin-planilla/{id_torneo}"),
    ("Sanciones por equipo", f"/reportes/sanciones-equipo/{id_torneo}"),
    ("Estado de partidos", f"/reportes/estado-partidos/{id_torneo}"),
    ("Partidos cancelados y postergados", f"/reportes/partidos-cancelados-postergados/{id_torneo}"),
    ("Próximos partidos", f"/reportes/proximos-partidos/{id_torneo}"),
    ("Jugadores con más partidos", f"/reportes/jugadores-mas-partidos/{id_torneo}")
]


# Ejecutamos cada reporte
for nombre, endpoint in reportes:

    print("\n" + "=" * 60)
    print("REPORTE:", nombre)

    respuesta = sesion.get(BASE_URL + endpoint)

    print("Código HTTP:", respuesta.status_code)

    if respuesta.status_code == 200:

        print("RESULTADO OK")

        datos = respuesta.json()

        print("Cantidad de registros:", len(datos))
        print("Datos:")

        for registro in datos:
            print(registro)

    else:

        print("ERROR")
        print(respuesta.text)
