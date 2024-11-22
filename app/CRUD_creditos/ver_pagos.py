from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
import dicttoxml
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

@app.route('/api/pagos', methods=['GET'])
def obtener_pagos():
    try:
        # Conexión a la base de datos
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:  # Cursor para resultados como diccionarios
            cursor.execute("""
                SELECT p.id_pago, p.id_credito, c.id_cliente, cl.nombre_1 AS nombre_cliente, p.fecha_pago, p.monto_pago 
                FROM pagos p
                JOIN creditos c ON p.id_credito = c.id_credito
                JOIN clientes cl ON c.id_cliente = cl.id_cliente;
            """)
            pagos = cursor.fetchall()

        connection.close()

        # Validación: Si no hay pagos registrados
        if not pagos:
            return jsonify({"message": "No se encontraron pagos."}), 404

        # Detectar el formato solicitado por el cliente
        accept_header = request.headers.get('Accept', 'application/json')  # JSON por defecto

        if 'application/xml' in accept_header:  # Si el cliente solicita XML
            xml_data = dicttoxml.dicttoxml(pagos, custom_root='pagos', attr_type=False)
            return Response(xml_data, content_type='application/xml; charset=utf-8')
        else:  # Por defecto, responder con JSON
            return jsonify(pagos)

    except pymysql.MySQLError as e:
        # Error relacionado con la base de datos
        return jsonify({"error": "Error en la base de datos.", "details": str(e)}), 500

    except Exception as e:
        # Error genérico
        return jsonify({"error": "Ocurrió un error inesperado.", "details": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado."}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Método no permitido."}), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Error interno del servidor."}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5016)
