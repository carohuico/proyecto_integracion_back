from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
from flask_cors import CORS
import xmltodict
import dicttoxml
from token_required import token_required

app = Flask(__name__)
CORS(app)  # Configuración simplificada de CORS

def xml_to_dict(xml_data):
    try:
        return xmltodict.parse(xml_data)
    except Exception as e:
        raise ValueError(f"Error al procesar XML: {str(e)}")

def dict_to_xml(data):
    return dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)

@app.route('/api/creditos/<int:id_credito>/actualizar', methods=['PUT'])
@token_required
def actualizar_credito(id_credito, user_data):
    content_type = request.headers.get('Content-Type')
    try:
        if content_type == 'application/json':
            data = request.json
        elif content_type == 'application/xml':
            data = xml_to_dict(request.data)['credito']
        else:
            return Response("Unsupported Media Type", status=415)

        valor_pactado = float(data['valor_pactado'])
        valor_pagado = float(data['valor_pagado'])

        if not all(k in data for k in ('valor_pactado', 'valor_pagado')):
            return Response("Faltan datos requeridos", status=400)
        
        print(f"Actualizando crédito con ID {id_credito}: valor_pactado = {valor_pactado}, valor_pagado = {valor_pagado}")

        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE creditos
                SET valor_pactado = %s, valor_pagado = %s
                WHERE id_credito = %s
            """, (valor_pactado, valor_pagado, id_credito))
            connection.commit()
        
        response_data = {"message": "Crédito actualizado con éxito"}
        if content_type == 'application/xml':
            response_xml = dicttoxml.dicttoxml(response_data, custom_root='response', attr_type=False)
            return Response(response_xml, content_type='application/xml')
        else:
            return jsonify(response_data)
    
    except ValueError as e:
        return Response(f"Error procesando datos: {str(e)}", status=400)
    except Exception as e:
        return Response(f"Error interno del servidor: {str(e)}", status=500)
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)