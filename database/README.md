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
### 4. Ejecución del script 2 (inserción de los datos de prueba)
- Abrir el archivo *2_inserción_datos_prueba.sql* y ejecutar sus líenas respetando el mismo orden de las instrucciones 2-8 del paso anterior (la ejecución del script 1).
- !Aclaración: el número de las líneas no coincidirá.
### 5. Ejecución del script 3 (creación de una view para cálculo de goles por aprtido)
- Abrir el archivo *3_creacion_view_goles_partido.sql* y ejecutar todas sus líneas.
  
- Luego de haber seguido estos 5 pasos ya deberías de tener la Base de Datos creada y con sus datos. Ahora ya puedes ir a la carpeta /backend y seguir con los pasos para correr la aplicación de forma local.

## Configuración del usuario de MySQL

Para mejorar la seguridad del sistema, decidimos utilizar un usuario de MySQL exclusivo para la aplicación, llamado `torneo_app`, en lugar de conectarnos directamente con `root`.

Este usuario tiene permisos para consultar, insertar, modificar y eliminar registros de la base de datos `torneo_interfacultades`, pero no puede crear ni eliminar tablas ni administrar usuarios de MySQL.

Una vez creada la base de datos, abrir DataGrip, conectarse con el usuario `root` y ejecutar las siguientes instrucciones en una consola SQL:

create user if not exists 'torneo_app'@'localhost' identified by 'tu_contraseña_segura';

grant select, insert, update, delete on torneo_interfacultades.* to 'torneo_app'@'localhost';

Se debe reemplazar `tu_contraseña_segura` por una contraseña propia y segura. Si el usuario ya existe, no es necesario volver a crearlo y se debe utilizar la contraseña que tenía configurada.

Para comprobar que los permisos fueron asignados correctamente, ejecutar:

show grants for 'torneo_app'@'localhost';

Deberían aparecer los permisos `SELECT`, `INSERT`, `UPDATE` y `DELETE` sobre la base de datos del torneo.

Los roles de administrador y planillero de la aplicación siguen siendo controlados por Flask mediante `requiere_rol`. El usuario `torneo_app` agrega una restricción de seguridad en MySQL, pero no diferencia los roles de la aplicación.

Una vez terminada esta configuración, continuar con el README de la carpeta `backend`.
