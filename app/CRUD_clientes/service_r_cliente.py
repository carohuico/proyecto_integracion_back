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

@app.route('/get_cliente/<int:id_cliente>', methods=['GET'])
def get_cliente(id_cliente):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                id_cliente,
                CONCAT(nombre_1, ' ', nombre_2) AS nombre_completo,
                num_identificacion_fiscal,
                grupo_clientes,
                distrito,
                limite_credito
            FROM clientes
            WHERE id_cliente = %s
        """, (id_cliente,))
        cliente = cursor.fetchone()
    connection.close()
    if cliente:
        return jsonify(cliente)
    else:
        return jsonify({"error": "Cliente no encontrado"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)


