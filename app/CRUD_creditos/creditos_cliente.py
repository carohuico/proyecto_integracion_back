from flask import Flask, request, jsonify, Response
import xmltodict
from app.db_config import get_db_connection
from flask_cors import CORS
from token_required import token_required

app = Flask(__name__)
CORS(app)

@app.route('/api/creditos/<int:cliente_id>', methods=['GET'])
@token_required
def obtener_creditos_cliente(cliente_id, user_data):  # Recibe cliente_id como argumento
    if not cliente_id:
        return jsonify({"message": "ID de cliente es necesario"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT c.id_credito, c.id_viaje, c.id_cliente, cl.nombre_1 AS nombre, c.estado_credito, c.valor_pactado, c.valor_pagado
FROM creditos c
JOIN clientes cl ON c.id_cliente = cl.id_cliente
WHERE c.id_cliente = %s AND c.estado_credito = 'activo';
            """
            cursor.execute(query, (cliente_id,))
            creditos = cursor.fetchall()

        # Si no hay créditos activos
        if not creditos:
            return jsonify({"message": "No se encontraron créditos activos para este cliente."}), 404

        return jsonify(creditos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006)

