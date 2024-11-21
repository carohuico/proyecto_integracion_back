# app/CRUD_clientes/service_d_historial.py
from flask import Flask, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection
 
app = Flask(__name__)
CORS(app)

# DELETE /api/historial-credito/{id}: Eliminar una entrada de crédito y sus pagos asociados.
@app.route('/api/historial-credito/<id>', methods=['DELETE'])
def delete_credit(id):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Eliminar los pagos asociados al crédito
        cursor.execute("""
            DELETE FROM pagos
            WHERE id_credito = %s
        """, (id,))
        
        # Eliminar el crédito
        cursor.execute("""
            DELETE FROM creditos
            WHERE id_credito = %s
        """, (id,))
        
        connection.commit()
    connection.close()
    return jsonify({"message": "Crédito y pagos asociados eliminados."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5015)
