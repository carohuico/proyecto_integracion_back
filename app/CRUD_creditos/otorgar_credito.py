from flask import Flask, request, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection
from token_required import token_required

app = Flask(__name__)
CORS(app)

@app.route('/api/creditos', methods=['POST'])
@token_required
def create_credit_and_payment(user_data):
    data = request.get_json()
    print(f"Datos recibidos: {data}")

    # Validaciones de entrada
    required_fields = ['id_cliente', 'id_viaje', 'valor_pactado', 'valor_pagado', 'fecha_creacion']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Falta el campo requerido: {field}"}), 400
        
    if not isinstance(data['valor_pagado'], (int, float)) or data['valor_pagado'] < 0:
        return jsonify({"error": "El campo valor_pagado debe ser un número positivo"}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            connection.begin()
            
            # Inserción de crédito
            try:
                cursor.execute("""
                    INSERT INTO creditos (id_cliente, id_viaje, estado_credito, valor_pactado, valor_pagado, fecha_creacion)
                    VALUES (%s, %s, 'activo', %s, %s, %s)
                """, (data['id_cliente'], data['id_viaje'], data['valor_pactado'], data['valor_pagado'], data['fecha_creacion']))
                id_credito = cursor.lastrowid
                print(f"Crédito insertado con ID: {id_credito}")
            except Exception as e:
                print(f"Error al insertar crédito: {e}")
                raise

            # Inserción del pago solo si hay un monto_pago
            if data['valor_pagado'] > 0:
                try:
                    cursor.execute("""
                        INSERT INTO pagos (id_credito, fecha_pago, monto_pago)
                        VALUES (%s, %s, %s)
                    """, (id_credito, data['fecha_creacion'], data['valor_pagado']))
                    print(f"Pago insertado para crédito ID: {id_credito}")
                except Exception as e:
                    print(f"Error al insertar pago: {e}")
                    raise
                
            connection.commit()
            
        return jsonify({
            "id_credito": id_credito,
            "id_cliente": data['id_cliente'],
            "estado_credito": 'activo',
            "valor_pactado": data['valor_pactado'],
            "valor_pagado": data['valor_pagado'],
            "fecha_creacion": data['fecha_creacion'],
            "id_viaje": data['id_viaje']
        }), 201
    except Exception as e:
        print(f"Error durante la transacción: {e}")
        connection.rollback()
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
    finally:
        connection.close()
            
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)

