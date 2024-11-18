# app/CRUD_clientes/service_r_historial.py
from flask import Flask, jsonify
from flask_cors import CORS
from app.db_config import get_db_connection
 
app = Flask(__name__)
CORS(app)

@app.route('/api/historial-credito', methods=['GET'])
def get_historial():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.id_credito, 
                c.id_viaje, 
                c.id_cliente, 
                c.estado_credito, 
                c.valor_pactado, 
                c.valor_pagado, 
                MAX(p.fecha_pago) AS ultima_fecha_pago
            FROM 
                creditos c
            LEFT JOIN 
                pagos p ON c.id_credito = p.id_credito
            GROUP BY 
                c.id_credito, c.id_viaje, c.id_cliente, c.estado_credito, c.valor_pactado, c.valor_pagado
        """)
        historial = cursor.fetchall()
        print(historial)
    connection.close()
    return jsonify(historial)


@app.route('/api/historial-credito/<clienteId>', methods=['GET'])
def get_historial_cliente(clienteId):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.id_credito, 
                c.id_viaje, 
                c.estado_credito, 
                c.valor_pactado, 
                c.valor_pagado, 
                MAX(p.fecha_pago) AS ultima_fecha_pago
            FROM 
                creditos c
            LEFT JOIN 
                pagos p ON c.id_credito = p.id_credito
            WHERE 
                c.id_cliente = %s
            GROUP BY 
                c.id_credito, c.id_viaje, c.estado_credito, c.valor_pactado, c.valor_pagado
        """, (clienteId,))
        historial = cursor.fetchall()
    connection.close()

    if not historial:
        return jsonify({"error": "No se encontró historial para el cliente con ID proporcionado."}), 404

    return jsonify(historial)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5013)