# ¿Cómo crear la base de datos de forma remota?
## Pasos para la creación de la base de datos y la inserción de los datos de prueba
### 1. Crear la base de datos
- Abrir DataGrip (o cualquier herramienta que permita conectarse a MySQL y ejecutar scripts SQL.
### 2. Crear una nueva conexión SQL en el caso de no tener una
- Completar los datos de la conexión: host, user, password
- Comprobar si fue exitosa mediante Test Connection
- Cuando ya esté establecida **abrimos una consola SQL**
### 3. Ejecución del script 1 (creación de la base y sus tablas)
- Abrir el archivo *1_creacion_tablas.sql* y ejecutar su contenido según se detalla a continuación:
  1. Crear la BD y usarla: primeras 3 líneas
  2. Tablas independientes: **login**, **facultad**, **torneo**, **complejo** y **turno** (líneas 7-48).
  3. Tablas dependientes (ejecutarlas de a 1 en el orden dado): **jugador**, **cancha** y **equipo** (líneas 50-81).
  4. Tabla **equipo_jugador_torneo**: líneas 83-99.
  5. Tabla de **partido**: líneas 101-131.
  6. Tabla de **planilla_partido**: líneas 133-142.
  7. Tablas de **gol** y **tarjeta**: se pueden ejecutar juntas (líneas 144-162).
  8. Por último, tabla **sancion_jugador**: líneas 164- 177.
### 4. Ejecución del script 2 /inserción de los datos de prueba)
- Abrir el archivo *2_inserción_datos_prueba.sql* y ejecutar sus líenas respetando el mismo orden de las instrucciones 2-8 del paso anterior (la ejecución del script 1).
- !Aclaración: el número de las líneas no coincidirá.

- Luego de haber seguido estos 4 pasos ya deberías de tener la Base de Datos creada y con sus datos. Ahora ya puedes ir a la carpeta /backend y seguir con los pasos para correr la aplicación de forma local.
