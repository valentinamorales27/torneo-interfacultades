import mysql.connector

#Este archivo define la conexión con las base de datos de MySQL

def obtener_conexion():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="TU_CONTRASEÑA",
        database="torneo_interfacultades"
    )

    return conexion

if __name__ == "__main__":
    try:
        conexion = obtener_conexion()

        print("¡Conexión a MySQL exitosa!")

        conexion.close()

    except mysql.connector.Error as error:
        print("Error al conectar con MySQL:", error)