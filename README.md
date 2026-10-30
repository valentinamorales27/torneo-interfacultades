# Torneo Interfacultades de Fútbol 5
## Obligatorio de Bases de datos
- Integrantes: Valentina Morales y Rodrigo Montiel.

## Tecnologías utilizadas
- Python: lenguaje utilizado para el backend.
- Flask: framework utilizado para crear los endpoints y gestionar las peticiones HTTP del frontend.
- MySQL: utilizado para crear la base de datos relacional.
- mysql-connector-python: biblioteca para conectar Python con MySQL y poder ejecutar las consultas SQL.
- React: biblioteca utilizada para desarrollar la interfaz de usuario del frontend.
- JavaScript, HTML y CSS: tecnologías utilizadas para implementar la interacción, la estructura y los estilos de la interfaz del frontend.

## Estructura de este repo
- /backend
    - app.py
    - db.py
    - README.md
      
- /docs
    - Diagrama de relaciones
    - Instructivo completo de cómo correr la aplicación de forma local
    - Informe

- /database
    - 1_creación_tablas
    - 2_inserción_datos_prueba
      
## Informe:
### o Fundamentar decisiones de implementación
- Clave primaria de partido es solo id_partido
- Uso de checks, uniques, not null y indexs
- Verificación de tipos (enum) tanto en SQL como el el backend. La idea de repetirnos en el backend es poder detectar esos errores lo antes posible y así poder evitar establecer una conexión que no será exitosa con la base de datos.
### o Mejoras implementadas o consideradas en el modelo de datos
- Jueces
- Relación usuarios/partidos
### o Bitácora del trabajo realizado
### o Bibliografía
