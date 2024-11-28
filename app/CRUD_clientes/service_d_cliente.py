# app/CRUD_clientes/service_d_cliente.py
from flask import Flask, jsonify
from app.db_config import get_db_connection
from flask_cors import CORS
from token_required import token_required

app = Flask(__name__)
CORS(app)

@app.route('/delete_cliente/<int:id_cliente>', methods=['DELETE'])
@token_required
def delete_cliente(id_cliente, user_data):
    print("delete_cliente", id_cliente)
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        connection.commit()
    connection.close()
    return jsonify({"message": "Cliente eliminado con éxito"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
