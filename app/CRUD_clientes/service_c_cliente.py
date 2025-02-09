from flask import Flask, request, jsonify
import random
from app.db_config import get_db_connection
from flask_cors import CORS
from token_required import token_required

app = Flask(__name__)
CORS(app)
CORS(app)

@app.route('/create_cliente', methods=['POST'])
def create_cliente():
    print("create_cliente")
    print("create_cliente")
    data = request.json
    print("--------------------")
    print(data)
    connection = get_db_connection()
    #create random id 
    id = random.randint(10000, 99999) 
    with connection.cursor() as cursor:
        
        cursor.execute("""
            INSERT INTO clientes (id_cliente, nombre_1, nombre_2, calle, telefono_1, num_identificacion_fiscal, ofvta, poblacion, grupo_clientes, canal_distribucion, tipo_canal, gr_1, clasificacion, digito_control, bloqueo_pedido, cpag, c_distribucion, distrito, zona, central, fecha_registro, limite_credito)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (id, data.get('nombre_1'), data.get('nombre_2'), data.get('calle'), data.get('telefono_1'), data.get('num_identificacion_fiscal'), data.get('ofvta'), data.get('poblacion'), data.get('grupo_clientes'), data.get('canal_distribucion'), data.get('tipo_canal'), data.get('gr_1'), data.get('clasificacion'), data.get('digito_control'), data.get('bloqueo_pedido'), data.get('cpag'), data.get('c_distribucion'), data.get('distrito'), data.get('zona'), data.get('central'), data.get('fecha_registro'), data.get('limite_credito')))
        connection.commit()
    connection.close()
    return jsonify({"message": "Cliente creado con éxito"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)