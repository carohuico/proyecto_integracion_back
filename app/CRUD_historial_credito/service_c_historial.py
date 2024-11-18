from flask import Flask, request, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection

app = Flask(__name__)
CORS(app)

@app.route('/api/historial-credito', methods=['POST'])
def create_credit_and_payment():
    data = request.get_json()

    # Extraer datos del cuerpo de la solicitud
    id_cliente = data.get('id_cliente')
    estado_credito = data.get('estado_credito', 'activo')
    valor_pactado = data.get('valor_pactado')
    valor_pagado = data.get('valor_pagado', 0.00)
    monto_pago = data.get('monto_pago')  # Puede ser None si no hay pago inicial

    if not id_cliente or not valor_pactado:
        return jsonify({"error": "id_cliente y valor_pactado son obligatorios"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Iniciar una transacción
            connection.begin()

            # Insertar el crédito
            cursor.execute("""
                INSERT INTO creditos (id_cliente, estado_credito, valor_pactado, valor_pagado)
                VALUES (%s, %s, %s, %s)
            """, (id_cliente, estado_credito, valor_pactado, valor_pagado))
            
            # Obtener el ID del crédito recién creado
            id_credito = cursor.lastrowid

            # Si hay un monto de pago, registrar el pago asociado
            if monto_pago:
                cursor.execute("""
                    INSERT INTO pagos (id_credito, fecha_pago, monto_pago)
                    VALUES (%s, NOW(), %s)
                """, (id_credito, monto_pago))

            # Confirmar la transacción
            connection.commit()

        return jsonify({"message": "Crédito y pago creados exitosamente", "id_credito": id_credito}), 201

    except Exception as e:
        # Revertir la transacción en caso de error
        connection.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5012)