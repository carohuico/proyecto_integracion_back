from flask import Flask, request, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/api/historial-credito', methods=['POST'])
def create_credit_and_payment():
    data = request.get_json()
    print(data)

    # Validaciones de entrada
    id_cliente = data.get('id_cliente')
    id_viaje = data.get('id_viaje')
    estado_credito = data.get('estado_credito', 'activo')
    valor_pactado = data.get('valor_pactado')
    monto_pago = data.get('monto_pago', 0.00)
    fecha_creacion = data.get('fecha_creacion')

    if not id_cliente or not valor_pactado or not id_viaje or not estado_credito or not fecha_creacion:
        return jsonify({"error": "id_cliente, valor_pactado, id_viaje, estado_credito y fecha_creacion son obligatorios"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            connection.begin()

            # Inserción de crédito
            cursor.execute("""
                INSERT INTO creditos (id_cliente, id_viaje, estado_credito, valor_pactado, valor_pagado, fecha_creacion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (id_cliente, id_viaje, estado_credito, valor_pactado, monto_pago, fecha_creacion))

            id_credito = cursor.lastrowid

            # Inserción del pago solo si hay un monto_pago
            if monto_pago > 0:
                cursor.execute("""
                    INSERT INTO pagos (id_credito, fecha_pago, monto_pago)
                    VALUES (%s, %s, %s)
                """, (id_credito, fecha_creacion, monto_pago))

            connection.commit()

        return jsonify({
            "id_credito": id_credito,
            "id_cliente": id_cliente,
            "estado_credito": estado_credito,
            "valor_pactado": valor_pactado,
            "monto_pago": monto_pago,
            "fecha_creacion": fecha_creacion
        }), 201
    except Exception as e:
        connection.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5012)
