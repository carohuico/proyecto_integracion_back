from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
import dicttoxml
from flask_cors import CORS
import pymysql

app = Flask(__name__)
CORS(app)

# Endpoint para obtener créditos con pagos atrasados
@app.route('/api/pagos-atrasados', methods=['GET'])
def obtener_creditos_atrasados():
    try:
        # Conexión a la base de datos
        connection = get_db_connection()
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            # Consulta para obtener los créditos con pagos atrasados
            cursor.execute("""
                SELECT 
                    c.id_credito,
                    c.id_cliente,
                    cl.nombre_1 AS nombre_cliente, -- Se añade el nombre del cliente
                    c.estado_credito,
                    c.valor_pactado,
                    c.valor_pagado,
                    (c.valor_pactado - c.valor_pagado) AS monto_pendiente,
                    MIN(p.fecha_pago) AS fecha_ultimo_pago,
                    DATEDIFF(CURDATE(), MIN(p.fecha_pago)) AS dias_desde_inicio,
                    FLOOR(DATEDIFF(CURDATE(), MIN(p.fecha_pago)) / 30) AS periodos_transcurridos,
                    (FLOOR(DATEDIFF(CURDATE(), MIN(p.fecha_pago)) / 30) * 1000) AS monto_esperado
                FROM 
                    creditos c
                LEFT JOIN 
                    pagos p ON c.id_credito = p.id_credito
                LEFT JOIN 
                    clientes cl ON c.id_cliente = cl.id_cliente -- Unión con la tabla clientes
                WHERE 
                    c.estado_credito = 'activo'
                    AND c.valor_pagado < c.valor_pactado
                GROUP BY 
                    c.id_credito, cl.nombre_1; 

            """)
            creditos_atrasados = cursor.fetchall()

        connection.close()

        # Validación: Si no se encontraron créditos atrasados
        if not creditos_atrasados:
            return jsonify({"message": "No se encontraron créditos con pagos atrasados."}), 404

        # Detectar el formato solicitado por el cliente
        accept_header = request.headers.get('Accept', 'application/json')  # JSON por defecto

        if 'application/xml' in accept_header:  # Si el cliente solicita XML
            xml_data = dicttoxml.dicttoxml(creditos_atrasados, custom_root='creditos_atrasados', attr_type=False)
            return Response(xml_data, content_type='application/xml; charset=utf-8')
        else:  # Por defecto, responder con JSON
            return jsonify(creditos_atrasados)

    except pymysql.MySQLError as e:
        return jsonify({"error": "Error en la base de datos.", "details": str(e)}), 500
    except Exception as e:
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
    app.run(host='0.0.0.0', port=5019)

