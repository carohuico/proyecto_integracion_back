from flask import Flask, request, jsonify
from app.db_config import get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/pagos/<int:cliente_id>', methods=['GET'])
def obtener_pagos_cliente(cliente_id):
    if not cliente_id:
        return jsonify({"message": "ID de cliente es necesario"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT p.id_pago, p.id_credito, c.id_cliente, cl.nombre_1 AS nombre_cliente, p.fecha_pago, p.monto_pago
                FROM pagos p
                JOIN creditos c ON p.id_credito = c.id_credito
                JOIN clientes cl ON c.id_cliente = cl.id_cliente
                WHERE c.id_cliente = %s
            """
            cursor.execute(query, (cliente_id,))
            pagos = cursor.fetchall()

        # Si no hay pagos para el cliente
        if not pagos:
            return jsonify({"message": "No se encontraron pagos para este cliente."}), 404

        return jsonify(pagos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5017)

