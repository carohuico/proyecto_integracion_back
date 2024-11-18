from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
import pymysql
from flask_cors import CORS
import dicttoxml  # Para convertir a XML

app = Flask(__name__)
CORS(app)

@app.route('/api/pagos/<int:id_cliente>', methods=['GET'])
def historial_pagos(id_cliente):
    try:
        # Conexión a la base de datos
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Consulta para obtener los pagos del cliente
            cursor.execute("""
                SELECT p.id_pago, p.id_credito, p.fecha_pago, p.monto_pago
                FROM pagos p
                JOIN creditos c ON p.id_credito = c.id_credito
                WHERE c.id_cliente = %s
            """, (id_cliente,))
            pagos = cursor.fetchall()

        connection.close()

        # Si no se encuentran pagos, retornamos un mensaje de error
        if not pagos:
            return jsonify({"message": f"No se encontraron pagos para el cliente con ID {id_cliente}."}), 404

        # Detectar el formato solicitado por el cliente
        accept_header = request.headers.get('Accept', 'application/json')  # JSON por defecto

        if 'application/xml' in accept_header:  # Si el cliente solicita XML
            xml_data = dicttoxml.dicttoxml(pagos, custom_root='pagos', ids=False)
            # La función dicttoxml ya incluye la declaración XML correctamente
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
    app.run(host='0.0.0.0', port=5007)

