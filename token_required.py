from flask import request, jsonify
from functools import wraps
import jwt

SECRET_KEY = "la_llave_mas_secreta_del_mundo"  
ALGORITHM = "HS256"

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"message": "Token faltante"}), 401

        try:
            data = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "El token ha expirado"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token inválido"}), 401

        return f(*args, **kwargs, user_data=data)

    return decorated
