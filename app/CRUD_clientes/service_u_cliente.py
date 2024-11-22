# app/CRUD_clientes/service_u_cliente.py
from flask import Flask, request, jsonify
from app.db_config import get_db_connection
from flask_cors import CORS
from token_required import token_required

app = Flask(__name__)
CORS(app)

@app.route('/update_cliente/<int:id_cliente>', methods=['PATCH'])
@token_required
def update_cliente(id_cliente, user_data):
    data = request.json
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE clientes
            SET nombre_1 = %s, nombre_2 = %s, calle = %s, telefono_1 = %s, num_identificacion_fiscal = %s, ofvta = %s, poblacion = %s, grupo_clientes = %s, canal_distribucion = %s, tipo_canal = %s, gr_1 = %s, clasificacion = %s, digito_control = %s, bloqueo_pedido = %s, cpag = %s, c_distribucion = %s, distrito = %s, zona = %s, central = %s, limite_credito = %s
            WHERE id_cliente = %s
        """, (data.get('nombre_1'), data.get('nombre_2'), data.get('calle'), data.get('telefono_1'), data.get('num_identificacion_fiscal'), data.get('ofvta'), data.get('poblacion'), data.get('grupo_clientes'), data.get('canal_distribucion'), data.get('tipo_canal'), data.get('gr_1'), data.get('clasificacion'), data.get('digito_control'), data.get('bloqueo_pedido'), data.get('cpag'), data.get('c_distribucion'), data.get('distrito'), data.get('zona'), data.get('central'), data.get('limite_credito'), id_cliente))
        connection.commit()
    connection.close()
    return jsonify({"message": "Cliente actualizado con éxito"})

if __name__ == '__main__':
    app.run(port=5003)