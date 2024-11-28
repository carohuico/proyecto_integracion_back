from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
import dicttoxml
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

@app.route('/api/creditos-activos', methods=['GET'])
def obtener_creditos():
    try:
        # Conexión a la base de datos
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:  # Cursor para resultados como diccionarios
            cursor.execute("""
                SELECT c.id_credito, c.id_viaje, c.id_cliente, cl.nombre_1 AS nombre, c.estado_credito, c.valor_pactado, c.valor_pagado
                FROM creditos c
                JOIN clientes cl
                WHERE c.id_cliente = cl.id_cliente and c.estado_credito = 'activo';

            """)
            creditos = cursor.fetchall()

        connection.close()

        # Validación: Si no hay créditos registrados
        if not creditos:
            return jsonify({"message": "No se encontraron créditos."}), 404

        # Detectar el formato solicitado por el cliente
        accept_header = request.headers.get('Accept', 'application/json')  # JSON por defecto

        if 'application/xml' in accept_header:  # Si el cliente solicita XML
            xml_data = dicttoxml.dicttoxml(creditos, custom_root='creditos', attr_type=False)
            return Response(xml_data, content_type='application/xml; charset=utf-8')
        else:  # Por defecto, responder con JSON
            return jsonify(creditos)

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
    app.run(host='0.0.0.0',port=5018)


