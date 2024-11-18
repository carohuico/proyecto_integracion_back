# app/CRUD_clientes/service_d_cliente.py
from flask import Flask, jsonify
from app.db_config import get_db_connection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/delete_cliente/<int:id_cliente>', methods=['DELETE'])
def delete_cliente(id_cliente):
    print("delete_cliente", id_cliente)
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM clientes WHERE id_cliente = %s", (id_cliente,))
        connection.commit()
    connection.close()
    return jsonify({"message": "Cliente eliminado con éxito"})

if __name__ == '__main__':
    app.run(port=5004)
