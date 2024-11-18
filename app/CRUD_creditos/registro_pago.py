from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
from flask_cors import CORS
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

@app.route('/api/pagos', methods=['POST'])
def registrar_pago():
    # Verificar si el cuerpo de la solicitud es JSON
    if request.is_json:
        data = request.json
    else:
        # Si no es JSON, tratar de parsear el XML
        try:
            # Asumir que el contenido está en XML
            data = ET.fromstring(request.data)
            # Convertir el XML a un diccionario (si es necesario)
            data = {
                "id_credito": data.find("id_credito").text,
                "monto_pago": data.find("monto_pago").text
            }
        except ET.ParseError:
            return jsonify({"error": "Formato de solicitud no válido"}), 400

    # Realizar la conexión a la base de datos
    connection = get_db_connection()
    with connection.cursor() as cursor:
        # Registrar el pago
        cursor.execute("""
            INSERT INTO pagos (id_credito, fecha_pago, monto_pago)
            VALUES (%s, CURDATE(), %s)
        """, (data['id_credito'], data['monto_pago']))
        
        # Actualizar el valor pagado en el crédito
        cursor.execute("""
            UPDATE creditos
            SET valor_pagado = valor_pagado + %s
            WHERE id_credito = %s
        """, (data['monto_pago'], data['id_credito']))
        
        connection.commit()
    connection.close()

    # Crear respuesta en XML
    response = ET.Element("response")
    message = ET.SubElement(response, "message")
    message.text = "Pago registrado con éxito"
    
    # Convertir el árbol XML a un string
    xml_response = ET.tostring(response, encoding='utf-8', method='xml')

    # Verificar el formato solicitado por el cliente (XML o JSON)
    if request.headers.get('Accept') == 'application/xml':
        return Response(xml_response, content_type='application/xml')
    else:
        return jsonify({"message": "Pago registrado con éxito"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009)

