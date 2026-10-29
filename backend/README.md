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
## 5. Crear la basse de datos
- Para poder continuar debe de ir a la carpeta de *database* del GitHub y seguir los pasos del README.md para poder crear e insertar los datos de prueba en la base de datos.
## 6. Configurar la conexión con SQL
- Dentro de la carpeta del *backend* en la que usted está parado en VSCode puede ver el dile db.py. Este archivo se encarga de las consiguraciones de conexión con SQL, para poder utilizarlo usted debe de configurar el usuario, la contraseña y el nombre de la base de datos. Estos valores deben coincidir con la instalación local de MySQL del paso 5 (cuando creo la BD).
- Para checkear que la conexión quedó establecida use el comando *python db.py*, si funciona debería de ver en la consola un mensaje indicando lo mismo.
## 7. Iniciar el servidor Flask
- Comando: *python app.py* (ejecuta el backend). Al ejecutarse debería de mostarle una dirección local en la terminal. COn esa dirección puede acceder al servidor desde la computadora.
- !! La terminal en la que se ejecutó este comando debe de quedar abierta para que se pueda utilizar el backend.

