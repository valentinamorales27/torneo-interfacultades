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
7. Configurar la clave secreta de Flask

Para gestionar las sesiones de usuario, Flask necesita una clave secreta.

Dentro del mismo archivo .env creado en el paso anterior, agregar también la siguiente variable:

SECRET_KEY=tu_clave_secreta

Para generar una clave aleatoria, ejecutar en la terminal:

python -c "import secrets; print(secrets.token_hex(32))"

Copiar el resultado obtenido y utilizarlo como valor de SECRET_KEY en el archivo .env.

Importante: El archivo .env contiene información privada y no debe subirse a GitHub. Cada usuario deberá generar su propia clave secreta y configurar sus propias credenciales de MySQL.

8. Iniciar el servidor Flask

Comando: python app.py (ejecuta el backend).

Al ejecutarse, debería mostrarse una dirección local en la terminal. El backend quedará disponible en http://127.0.0.1:5000.

Importante: La terminal en la que se ejecutó este comando debe permanecer abierta mientras se utiliza el backend.

