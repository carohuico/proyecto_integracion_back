from flask import Flask, request, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/api/historial-credito', methods=['POST'])
def create_credit_and_payment():
    data = request.get_json()
    print(data)

    # Validaciones mejoradas
    id_cliente = data.get('id_cliente')
    id_viaje = data.get('id_viaje', None)
    estado_credito = data.get('estado_credito', 'activo')
    valor_pactado = data.get('valor_pactado')
    monto_pago = data.get('monto_pago', 0.00)

    if not id_cliente or not valor_pactado:
        return jsonify({"error": "id_cliente y valor_pactado son obligatorios"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            connection.begin()

            # Inserción de crédito
            cursor.execute("""
                INSERT INTO creditos (id_cliente, id_viaje, estado_credito, valor_pactado, valor_pagado)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_cliente, id_viaje, estado_credito, valor_pactado, monto_pago))

            id_credito = cursor.lastrowid

            # Inserción del pago
            cursor.execute("""
                INSERT INTO pagos (id_credito, fecha_pago, monto_pago)
                VALUES (%s, NOW(), %s)
            """, (id_credito, monto_pago))

            connection.commit()

        return jsonify({
            "id_credito": id_credito,
            "id_cliente": id_cliente,
            "estado_credito": estado_credito,
            "valor_pactado": valor_pactado,
            "monto_pago": monto_pago
        }), 201
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5012)