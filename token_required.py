from flask import request, jsonify
from functools import wraps
import jwt
import logging

SECRET_KEY = "la_llave_mas_secreta_del_mundo"  
ALGORITHM = "HS256"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            logging.warning("Token faltante")
            return jsonify({"message": "Token faltante"}), 401

        try:
            token = token.split(" ")[1]
            print(f"Token recibido: {token}")
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            logging.warning("El token ha expirado")
            return jsonify({"message": "El token ha expirado"}), 401
        except jwt.InvalidTokenError:
            logging.warning("Token inválido")
            return jsonify({"message": "Token inválido"}), 401
        except Exception as e:
            logging.error(f"Error al decodificar el token: {str(e)}")
            return jsonify({"message": "Error interno del servidor"}), 500

        return f(*args, **kwargs, user_data=data)

    return decorated