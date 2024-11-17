# app/CRUD_clientes/service_r_cliente.py
from flask import Flask, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection

#comentarioooo 
app = Flask(__name__)
CORS(app)

@app.route('/get_clientes', methods=['GET'])
def get_clientes():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Consultar solo los campos necesarios y concatenar nombre_1 y nombre_2
        cursor.execute("""
            SELECT *
            FROM clientes
        """)
        clientes = cursor.fetchall()
    connection.close()
    return jsonify(clientes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

