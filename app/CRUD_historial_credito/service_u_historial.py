from flask import Flask, request, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection

app = Flask(__name__)
CORS(app)

# PUT /api/historial-credito/{id}: Actualizar una entrada de crédito.
@app.route('/api/historial-credito/<int:id>', methods=['PUT'])
def update_historial_credito(id):
    db_connection = get_db_connection()
    cursor = db_connection.cursor()
    try:
        # Obtener los datos enviados por el cliente
        data = request.get_json()
        print(f"ID recibido en la ruta: {id}")
        print(f"Datos recibidos: {data}")
        # Validar los campos requeridos
        if not all(key in data for key in ['id_cliente', 'id_viaje', 'valor_pactado', 'valor_pagado', 'fecha_creacion']):
            return jsonify({'message': 'Faltan campos obligatorios'}), 400

        # Actualizar solo los campos permitidos
        cursor.execute(
            """
            UPDATE creditos
            SET 
                id_cliente = %s, 
                id_viaje = %s, 
                valor_pactado = %s, 
                valor_pagado = %s, 
                fecha_creacion = %s
            WHERE id_credito = %s
            """,
            (data['id_cliente'], data['id_viaje'], data['valor_pactado'], data['valor_pagado'], data['fecha_creacion'], id)
        )

        db_connection.commit()
        return jsonify({'message': 'Crédito actualizado correctamente'}), 200
    except Exception as e:
        db_connection.rollback()
        print(f"Error: {e}")  # Log de error
        return jsonify({'message': 'Error al actualizar el crédito'}), 500
    finally:
        cursor.close()
        db_connection.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5014)