# app/CRUD_clientes/service_r_cliente.py
from flask import Flask, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection
from token_required import token_required

#comentarioooo 
app = Flask(__name__)
CORS(app)

@app.route('/get_clientes', methods=['GET'])
def get_clientes():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM clientes
        """)
        clientes = cursor.fetchall()
    connection.close()
    return jsonify(clientes)

@app.route('/get_cliente/<int:id_cliente>', methods=['GET'])
@token_required
def get_cliente(id_cliente, user_data):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT *
            FROM clientes
            WHERE id_cliente = %s
        """, (id_cliente,))
        cliente = cursor.fetchone()
    connection.close()
    return jsonify(cliente)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

