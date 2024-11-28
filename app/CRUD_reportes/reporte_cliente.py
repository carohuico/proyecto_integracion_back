from flask import Flask, request, jsonify, Response
import xmltodict
from app.db_config import get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

@app.route('/api/reporte-cliente/<int:cliente_id>', methods=['GET'])
@token_requiered
def obtener_creditos_cliente(cliente_id, user_data):
    if not cliente_id:
        return jsonify({"message": "ID de cliente es necesario"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            query = """
                SELECT * FROM creditos
                WHERE id_cliente = %s
            """
            cursor.execute(query, (cliente_id,))
            result = cursor.fetchall()

        # Si no hay créditos activos
        if not creditos:
            return jsonify({"message": "No se encontraron créditos activos para este cliente."}), 404

        return jsonify(creditos)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5020)
