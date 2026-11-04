
from functools import wraps
from flask import session, jsonify


#verifica que el usuario haya iniciado sesion
def requiere_sesion(funcion):

    @wraps(funcion)
    def decorador(*args, **kwargs):

        #comprobamos si hay un usuario conectado
        if "correo" not in session:
            return jsonify({"error": "Debe iniciar sesion"}), 401

        return funcion(*args, **kwargs)

    return decorador


#verifica que el usuario tenga uno de los roles permitidos
def requiere_rol(*roles_permitidos):

    def decorador(funcion):

        @wraps(funcion)
        def funcion_protegida(*args, **kwargs):

            #comprobamos si hay un usuario conectado
            if "correo" not in session:
                return jsonify({"error": "Debe iniciar sesion"}), 401

            #comprobamos si su rol tiene permiso
            if session.get("rol") not in roles_permitidos:
                return jsonify({"error": "No tiene permisos para realizar esta operacion"}), 403

            return funcion(*args, **kwargs)

        return funcion_protegida

    return decorador
