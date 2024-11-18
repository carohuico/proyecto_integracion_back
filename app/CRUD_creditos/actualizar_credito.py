from flask import Flask, request, jsonify, Response
from app.db_config import get_db_connection
from flask_cors import CORS
import xmltodict
import dicttoxml

app = Flask(__name__)
# Configuración explícita de CORS
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

def xml_to_dict(xml_data):
    try:
        return xmltodict.parse(xml_data)
    except Exception as e:
        raise ValueError(f"Error al procesar XML: {str(e)}")

def dict_to_xml(data):
    return dicttoxml.dicttoxml(data, custom_root='response', attr_type=False)

@app.route('/api/creditos/<int:id_credito>/actualizar', methods=['OPTIONS', 'PUT'])
def actualizar_credito(id_credito):
    # Manejo de preflight para CORS
    if request.method == 'OPTIONS':
        response = Response(status=204)  # Cambiado a 204 sin contenido
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "PUT, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    # Detectar el tipo de contenido
    content_type = request.headers.get('Content-Type')
    try:
        if content_type == 'application/json':
            data = request.json
        elif content_type == 'application/xml':
            data = xml_to_dict(request.data)['credito']
        else:
            return Response("Unsupported Media Type", status=415)
        
        # Validar datos requeridos
        if not all(k in data for k in ('valor_pactado', 'estado_credito')):
            return Response("Faltan datos requeridos", status=400)
        
        # Conexión y actualización
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("""
                UPDATE creditos
                SET valor_pactado = %s, estado_credito = %s
                WHERE id_credito = %s
            """, (data['valor_pactado'], data['estado_credito'], id_credito))
            connection.commit()
        
        # Responder en el formato solicitado
        response_data = {"message": "Crédito actualizado con éxito"}
        if content_type == 'application/xml':
            response_xml = dict_to_xml(response_data)
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

