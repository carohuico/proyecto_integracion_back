from flask import Flask, jsonify, request
from app.db_config import get_db_connection
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
import logging

# Configuración de la aplicación
app = Flask(__name__)
CORS(app)

SECRET_KEY = "la_llave_mas_secreta_del_mundo"  
ALGORITHM = "HS256" 

@app.route('/login', methods=['POST'])
def login():
    connection = get_db_connection()
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"message": "Faltan datos: username y/o password"}), 400

        with connection.cursor() as cursor:
            query = "SELECT * FROM usuarios WHERE username = %s AND estado = 1"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({"message": "Usuario no encontrado o inactivo"}), 404

            # Verificar contraseña con bcrypt
            if not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                return jsonify({"message": "Contraseña incorrecta"}), 401

            # Generar token JWT
            #tiempo mexico
            exp = datetime.now(timezone.utc) + timedelta(hours=1)
            token = jwt.encode(
                {
                    "id_usuario": user["id_usuario"],
                    "username": user["username"],
                    "role": user["role"],
                    "exp": exp
                },
                SECRET_KEY,
                algorithm=ALGORITHM,
            )
            print(f"El token expira en {exp}")
            
            #obtener id_cliente del usuario
            query_id = "SELECT id_cliente FROM usuarios WHERE id_usuario = %s"
            cursor.execute(query_id, (user["id_usuario"],))
            id_cliente = cursor.fetchone()
            print(f"El id_cliente es {id_cliente}")

            # Registrar el último acceso en la base de datos
            update_query = "UPDATE usuarios SET ultimo_acceso = NOW() WHERE id_usuario = %s"
            cursor.execute(update_query, (user["id_usuario"],))
            connection.commit()

            return jsonify({"token": token, "role": user["role"], "id_cliente": id_cliente["id_cliente"]}), 200

    except Exception as e:
        return jsonify({"message": f"Error interno: {str(e)}"}), 500
    finally:
        connection.close()


#prueba curl
if __name__ == '__main__':
    # Habilitar el servidor Flask en todas las interfaces
    app.run(host='0.0.0.0', port=5000, debug=True)
