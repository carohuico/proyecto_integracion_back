from flask import Flask, jsonify, request
from app.db_config import get_db_connection
from flask_cors import CORS
from datetime import datetime, timedelta
import bcrypt


# Configuración de la aplicación
app = Flask(__name__)
CORS(app)

@app.route('/register', methods=['POST'])
@app.route('/register', methods=['POST'])
def register():
    connection = get_db_connection()
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")
        role = data.get("role", "normal")  # Valor predeterminado: "normal"

        if not username or not password:
            return jsonify({"message": "Faltan datos: username y/o password"}), 400

        # Generar hash de la contraseña
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with connection.cursor() as cursor:
            # Verificar si el usuario ya existe
            query = "SELECT username FROM usuarios WHERE username = %s"
            cursor.execute(query, (username,))
            if cursor.fetchone():
                return jsonify({"message": "El usuario ya existe"}), 409

            # Insertar nuevo usuario
            insert_query = """
            INSERT INTO usuarios (username, password_hash, role, estado)
            VALUES (%s, %s, %s, 1)
            """
            cursor.execute(insert_query, (username, password_hash, role))
            connection.commit()

            return jsonify({"message": "Usuario registrado exitosamente"}), 201

    except Exception as e:
        return jsonify({"message": f"Error interno: {str(e)}"}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    # Habilitar el servidor Flask en todas las interfaces
    app.run(host='0.0.0.0', port=5100, debug=True)
