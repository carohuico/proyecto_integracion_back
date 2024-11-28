from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
import dicttoxml
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

@app.route('/api/resumen-financiero', methods=['GET'])
def obtener_resumen_financiero():
    try:
        # Conexión a la base de datos
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:  # Cursor para resultados como diccionarios
            cursor.execute("""
                SELECT
                    c.id_cliente,
                    cl.nombre_1 AS nombre,
                    COUNT(c.id_credito) AS total_creditos,  -- Número total de créditos
                    SUM(c.valor_pagado) AS total_pagado,    -- Suma de los valores pagados
                    CASE
                        -- Todos los créditos están en estado 'pagado'
                        WHEN COUNT(c.id_credito) = SUM(CASE WHEN c.estado_credito = 'pagado' THEN 1 ELSE 0 END) THEN 'Completado'
                        
                        -- Hay créditos activos, pero se ha realizado algún pago
                        WHEN SUM(c.valor_pagado) > 0 THEN 'En proceso'
                        
                        -- Si no se ha realizado ningún pago y los créditos están activos
                        ELSE 'Pendiente'
                        END AS estado_general
                FROM creditos c
                JOIN clientes cl ON c.id_cliente = cl.id_cliente
                GROUP BY c.id_cliente, cl.nombre_1;
            """)
            resumen = cursor.fetchall()

        connection.close()

        # Validación: Si no hay registros
        if not resumen:
            return jsonify({"message": "No se encontraron registros."}), 404

        # Detectar el formato solicitado por el cliente
        accept_header = request.headers.get('Accept', 'application/json')  # JSON por defecto

        if 'application/xml' in accept_header:  # Si el cliente solicita XML
            xml_data = dicttoxml.dicttoxml(resumen, custom_root='resumen', ids=False)  # Se eliminó attribute_names
            return Response(xml_data, content_type='application/xml; charset=utf-8')
        else:  # Por defecto, responder con JSON
            return jsonify(resumen)

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
    app.run(host='0.0.0.0', port=5021)

