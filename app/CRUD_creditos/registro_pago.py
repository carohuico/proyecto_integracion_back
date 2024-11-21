from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
from flask_cors import CORS
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

@app.route('/api/pagos', methods=['POST'])
def registrar_pago():
    # Intentar procesar JSON primero
    data = None
    if request.is_json:
        try:
            data = request.json
        except Exception as e:
            return jsonify({"error": "Error al procesar JSON"}), 400
    else:
        # Si no es JSON, intentar procesar como XML
        try:
            xml_data = ET.fromstring(request.data)
            data = {
                "id_credito": xml_data.find("id_credito").text,
                "fecha_pago": xml_data.find("fecha_pago").text,
                "monto_pago": xml_data.find("monto_pago").text
            }
        except ET.ParseError:
            return jsonify({"error": "Formato de solicitud no válido"}), 400

    # Validar que los datos necesarios están presentes
    if not data or "id_credito" not in data or "monto_pago" not in data or "fecha_pago" not in data:
        return jsonify({"error": "Datos incompletos"}), 400

    # Validar que la fecha es válida
    from datetime import datetime
    try:
        datetime.strptime(data['fecha_pago'], '%Y-%m-%d')  # Validar formato YYYY-MM-DD
    except ValueError:
        return jsonify({"error": "Formato de fecha no válido, se requiere YYYY-MM-DD"}), 400

    # Procesar los datos y registrar el pago
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO pagos (id_credito, fecha_pago, monto_pago)
            VALUES (%s, %s, %s)
        """, (data['id_credito'], data['fecha_pago'], data['monto_pago']))
        
        cursor.execute("""
            UPDATE creditos
            SET valor_pagado = valor_pagado + %s
            WHERE id_credito = %s
        """, (data['monto_pago'], data['id_credito']))
        
        connection.commit()
    connection.close()

    # Preparar respuesta en ambos formatos
    if request.headers.get('Accept') == 'application/xml':
        response = ET.Element("response")
        message = ET.SubElement(response, "message")
        message.text = "Pago registrado con éxito"
        xml_response = ET.tostring(response, encoding='utf-8', method='xml')
        return Response(xml_response, content_type='application/xml')
    
    return jsonify({"message": "Pago registrado con éxito"})

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
    app.run(host='0.0.0.0', port=5009)

