# ¿Cómo levantar el frontend?
- El frontend de la aplicación se hizo con React y Vite. Esta parte del proyecto es la que va a permitir interactuar con el sistema del Torneo Interfacultades de Fútbol 5.
### Para levantar el frontend de forma local será necesario tener instalados:
- Git, para clonar el repositorio.
- Node.js y npm, para instalar las dependencias y ejecutar la aplicación.
- **Haber seguido los pasos para levantar la base de datos y el backend** (sino ir a leer esos README's antes porfas)
## Pasos a seguir:
### 1. Clonar el repositorio de GitHub
- Si aún no clonaste el repositorio clonalo ejecutando:
- Comando 1: git clone <url del repo> (clonamos el repositorio).
- Comando 2: cd torneo_interfacultades (nos paramos en el proyecto).
#### Si ya se clonó el repositorio para levantar el backend, como debería de haber pasado, no es necesario volver a clonarlo.
### 2. Acceder a la carpeta del frontend
- Desde la carpeta principal del proyecto (torneo_interfacultades), ejecutar: *cd frontend* (para pararnos ahí)
- El resto de los comandos se ejecutarán dentro de esta carpeta.
### 3. Instalar las dependencias
- Ejecutar el siguiente comando: *npm install* (instala todas las dependencias necesarias).
### 4. Iniciar el servidor de desarrollo
- Para levantar la aplicación, ejecutar: *npm run dev*
- Si todo está configurado correctamente, Vite te va a mostrar una dirección local en la terminal, suponé: *http://localhost:5173/*
- Abrí ese link en el navegador, podes copiar y pegarlo.
### 5. Verificar que el backend esté funcionando
- Para que el frontend pueda realizar consultas y gestionar la información del torneo, es necesario que el backend Flask también esté levantado.
- El backend debe estar funcionando en: **http://localhost:5000**, esto debería de haber quedado funcionando de la lista de pasos del README del back, si no es así volvé a leerlo.
- (en nuestro caso lo corrimos todo usando VScode entonces teníamos 2 terminales simultáneas corriendo, una con el back y otra con el front)
### 6. Utilizar la aplicación
- Una vez levantados el frontend y el backend, ya se podes usar la aplicación desde el navegador.
- Se puede iniciar sesión con alguno de los usuarios de prueba que ingresamos ya usando los scripts.
- Serían estos: *mail: admin_torneo@gmail.com contraseña: admin1234* y *mail: planillero_torneo@gmail.com contraseña: planillero1234*

-**!!!Importante**: La terminal donde se ejecutó npm run dev tiene que quedarse abierta mientras se usa la página al igual que la del back. Para parar el servidor, te parás en la terminal como para escribir una nueva cosa y apretás Ctrl + C.
