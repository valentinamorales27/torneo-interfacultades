
import mysql.connector
import os
from dotenv import load_dotenv

#cargamos las variables de entorno del archivo .env
load_dotenv()

#este archivo define la conexión con la base de datos de MySQL

def obtener_conexion():

    conexion = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "torneo_interfacultades")
    )

    return conexion


#probamos si la conexión con MySQL funciona
if __name__ == "__main__":
    try:
        conexion = obtener_conexion()

        print("¡Conexión a MySQL exitosa!")

        conexion.close()

    except mysql.connector.Error as error:
        print("Error al conectar con MySQL:", error)
