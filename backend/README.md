# ¿Cómo levantar el backend?
- El backend se desarrolló en Python, utilizando tanto Flask como MySQL para gestionar la base de datos. Flask es quién nos permitió hacer los endpoint que utilizará el front para realizar las consultas mientras que MySQL almacena los datos.
- Para poder levantar el backend de manera local será necesario tener instalados: **Git**, **Python**(se utilizó Visual Studio Code con la extensión de Pyton de Microsoft) y **MySQL server**.
  
## Lista de pasos a seguir
### 1. Clonar el repositorio de GitHub desde *la terminal* del equipo y abrir el proyecto
- Comando 1: *git clone <url del repo>* (clonamos el respositorio)
- Comando 2: *cd torneo_interfacultades* (accedemos a la carpeta del torneo)
- Comando 3: *code .* (en el caso de que el comando para abrir VSCode desde la terminal no funcione abrir desde VSCode seleccioanndo la carpeta clonada)
## 2. Accedemos a la carpeta del backend
- Comando: *cd backend* (el resto de comandos se ejecutarán dentro de esta carpeta)
## 3. Crear y activar el entorno
- Comando 1: *python -m venv .venv* (es necesario tener instalado Python, en el caso de no tenerlo se puede descargar Python de Microsoft desde la sección de extensiones de VSCode
- Comando 2: ```.\.venv\Scripts\Activate.ps1``` (luego de ejecutarlo debería de aparecer un (.venv) frente a la línea de la terminal)
## 4. Instalar las dependencias
- Comando: *python -m pip install -r requirements.txt* (instala las bibliotecas necesarias para poder correr el backend.
## 5. Crear la base de datos
- Para poder continuar ya debe de tener creada la BD de forma local, si no lo ha hecho aún debe de ir a la carpeta de *database* de este remo y seguir los pasos del README.md para poder crear e insertar los datos de prueba en la base de datos. Una vez creada puede seguir con el paso siguiente.
## 6. Configurar la conexión con MySQL

- Dentro de la carpeta `backend` se encuentra el archivo `db.py`, que se encarga de establecer la conexión con MySQL.
- Para que funcione correctamente, cada usuario debe configurar sus propios datos de conexión.
- Existen dos alternativas para configurar la conexión con la base de datos.

### Opción 1: Conexión utilizando root

Esta es la configuración tradicional de MySQL, utilizando el usuario `root`.

Dentro de la carpeta `backend`, crear un archivo llamado `.env` con el siguiente contenido:

MYSQL_HOST=localhost

MYSQL_USER=root

MYSQL_PASSWORD=tu_contraseña

MYSQL_DATABASE=torneo_interfacultades

FRONTEND_ORIGIN=http://localhost:5173

- Se deben reemplazar los valores por los correspondientes a la instalación local de MySQL.
- Si el usuario `root` no tiene contraseña, se puede dejar `MYSQL_PASSWORD` vacío.

### Opción 2: Conexión utilizando un usuario con permisos limitados

Como alternativa, se puede utilizar un usuario exclusivo para la aplicación llamado `torneo_app`, que tiene permisos limitados sobre la base de datos del torneo.

Esta opción permite conectarse sin utilizar directamente la cuenta `root`, que tiene permisos de administración sobre MySQL.

Primero se debe crear el usuario `torneo_app` siguiendo las instrucciones del README de la carpeta `database`.

Una vez creado, configurar el archivo `.env` de la carpeta `backend` con los siguientes valores:

MYSQL_HOST=localhost

MYSQL_USER=torneo_app

MYSQL_PASSWORD=tu_contraseña_segura

MYSQL_DATABASE=torneo_interfacultades

FRONTEND_ORIGIN=http://localhost:5173

- Se debe utilizar la contraseña que se estableció al crear el usuario `torneo_app`.
- Este usuario tiene permisos para consultar, insertar, modificar y eliminar registros de la base de datos, pero no para crear o eliminar tablas ni administrar usuarios de MySQL.

### Comprobar la conexión

Independientemente de la opción elegida, para verificar que la conexión quedó establecida correctamente, ejecutar desde la carpeta `backend`:

`python db.py`

Si funciona, debería aparecer un mensaje indicando que la conexión con MySQL fue exitosa.

El archivo `.env` contiene información privada y no debe subirse a GitHub.

**Aclaración:** las dos opciones permiten utilizar la aplicación. Los permisos del administrador y del planillero se controlan desde Flask mediante `requiere_rol`. El usuario `torneo_app` representa una restricción adicional a nivel de MySQL.
## 7. Configurar la clave secreta de Flask
- Para gestionar las sesiones de usuario, Flask necesita una clave secreta.
- Dentro del mismo archivo `.env` del paso anterior, agregar la siguiente línea: `SECRET_KEY=tu_clave_secreta`.
- Para generar una clave aleatoria, ejecutar el siguiente comando en la terminal:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
- Copiar el resultado y utilizarlo como valor de `SECRET_KEY`.

## 8. Iniciar el servidor Flask
- Por último, ejecutar el comando `python app.py` para iniciar el backend.
- Si todo está configurado correctamente, Flask mostrará una dirección local en la terminal, por ejemplo: `http://127.0.0.1:5000`.
- Con esa dirección se puede acceder al servidor desde la computadora.
- **Importante:** La terminal en la que se ejecutó este comando debe permanecer abierta para que el backend continúe funcionando.
