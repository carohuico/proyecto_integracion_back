from flask import Flask, Response, request, jsonify, json
from app.db_config import get_db_connection
import xml.etree.ElementTree as ET
from flask_cors import CORS
from token_required import token_required

app = Flask(__name__)
CORS(app)

@app.route('/api/grafica-clientes-creditos', methods=['POST'])
def get_clientes_creditos():
    connection = get_db_connection()
    try:
        # Leer el XML del body de la petición
        body = request.data
        xml_root = ET.fromstring(body)

        # Extraer fechas del XML
        start_date = xml_root.find('start_date').text if xml_root.find('start_date') is not None else '2000-01-01'
        end_date = xml_root.find('end_date').text if xml_root.find('end_date') is not None else '2025-01-01'

        print(f"Start Date: {start_date}, End Date: {end_date}")

        # Consulta SQL
        query = """
            SELECT 
                DATE_FORMAT(c.fecha_registro, '%%Y-%%m') AS periodo,
                COUNT(DISTINCT c.id_cliente) AS clientes_activos,
                COUNT(cr.id_credito) AS creditos_otorgados
            FROM 
                clientes c
            LEFT JOIN 
                creditos cr ON c.id_cliente = cr.id_cliente
            WHERE 
                c.fecha_registro BETWEEN %s AND %s
            GROUP BY 
                DATE_FORMAT(c.fecha_registro, '%%Y-%%m')
            ORDER BY 
                periodo;
        """

        with connection.cursor() as cursor:
            print("Ejecutando consulta SQL...")
            cursor.execute(query, (start_date, end_date))
            print("Consulta ejecutada.")
            results = cursor.fetchall()

        # Crear el documento XML de respuesta
        root = ET.Element('data')
        for row in results:
            period = ET.SubElement(root, 'period')
            ET.SubElement(period, 'periodo').text = row['periodo']
            ET.SubElement(period, 'clientes_activos').text = str(row['clientes_activos'])
            ET.SubElement(period, 'creditos_otorgados').text = str(row['creditos_otorgados'])

        # Convertir el árbol XML en una cadena
        xml_data = ET.tostring(root, encoding='utf-8', method='xml')
        return Response(xml_data, mimetype='application/xml')

    except Exception as e:
        print("Error en la ejecución:", str(e))
        error_root = ET.Element('error')
        ET.SubElement(error_root, 'message').text = str(e)
        xml_error = ET.tostring(error_root, encoding='utf-8', method='xml')
        return Response(xml_error, mimetype='application/xml', status=500)
    finally:
        connection.close()
        
@app.route('/api/grafica-creditos-atrasados', methods=['GET'])
def get_creditos_atrasados():
    connection = get_db_connection()
    try:
        query = """
            SELECT 
                DATE_FORMAT(c.fecha_creacion, '%Y-%m') AS periodo,
                COUNT(c.id_credito) AS creditos_atrasados,
                SUM(GREATEST(c.valor_pactado - IFNULL(p.total_pagado, 0), 0)) AS monto_adeudado
            FROM 
                creditos c
            LEFT JOIN (
                SELECT 
                    id_credito, 
                    SUM(monto_pago) AS total_pagado
                FROM 
                    pagos
                GROUP BY 
                    id_credito
            ) p ON c.id_credito = p.id_credito
            WHERE 
                c.estado_credito = 'activo' -- Solo créditos activos (no pagados)
            GROUP BY 
                DATE_FORMAT(c.fecha_creacion, '%Y-%m')
            ORDER BY 
                periodo;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        # Crear XML de respuesta
        root = ET.Element('data')
        for row in results:
            period = ET.SubElement(root, 'period')
            ET.SubElement(period, 'periodo').text = row['periodo']
            ET.SubElement(period, 'creditos_atrasados').text = str(row['creditos_atrasados'])
            ET.SubElement(period, 'monto_adeudado').text = f"{row['monto_adeudado']:.2f}"

        # Convertir el árbol XML a una cadena
        xml_data = ET.tostring(root, encoding='utf-8', method='xml')
        return Response(xml_data, mimetype='application/xml')

    except Exception as e:
        error_root = ET.Element('error')
        ET.SubElement(error_root, 'message').text = str(e)
        xml_error = ET.tostring(error_root, encoding='utf-8', method='xml')
        return Response(xml_error, mimetype='application/xml', status=500)
    
    finally:
        connection.close()
        
@app.route('/api/resumen_financiero', methods=['GET'])
def get_resumen_financiero():
    connection = get_db_connection()
    try:
        # Query para obtener el resumen financiero
        query = """
            SELECT 
                COUNT(*) AS total_creditos,
                AVG(valor_pactado) AS monto_promedio_otorgado,
                (COUNT(CASE WHEN estado_credito = 'activo' THEN 1 END) / COUNT(*)) * 100 AS porcentaje_creditos_en_demora
            FROM 
                creditos;
        """

        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()  # Solo necesitamos un resultado

        # Crear el documento XML de respuesta
        root = ET.Element('data')
        ET.SubElement(root, 'total_creditos').text = str(result['total_creditos'])
        ET.SubElement(root, 'monto_promedio_otorgado').text = f"{result['monto_promedio_otorgado']:.2f}"
        ET.SubElement(root, 'porcentaje_creditos_en_demora').text = f"{result['porcentaje_creditos_en_demora']:.2f}"

        # Convertir el árbol XML en una cadena
        xml_data = ET.tostring(root, encoding='utf-8', method='xml')
        return Response(xml_data, mimetype='application/xml')

    except Exception as e:
        error_root = ET.Element('error')
        ET.SubElement(error_root, 'message').text = str(e)
        xml_error = ET.tostring(error_root, encoding='utf-8', method='xml')
        return Response(xml_error, mimetype='application/xml', status=500)
    
    finally:
        connection.close()

@app.route('/api/grafica-analisis-clientes', methods=['GET'])
@token_required
def get_analisis_clientes_json(user_data):
    print("Obteniendo análisis de clientes...")
    connection = get_db_connection()
    try:
        query = """
                SELECT 
                    (SELECT COUNT(DISTINCT id_cliente) 
                    FROM creditos 
                    WHERE estado_credito = 'activo') AS clientes_activos,
                    (SELECT COUNT(DISTINCT c.id_cliente)
                    FROM creditos c
                    LEFT JOIN (
                        SELECT id_credito, SUM(monto_pago) AS total_pagado
                        FROM pagos
                        GROUP BY id_credito
                    ) p ON c.id_credito = p.id_credito
                    WHERE c.estado_credito = 'activo' AND c.valor_pactado > IFNULL(p.total_pagado, 0)
                    ) AS clientes_en_demora,
                    (SELECT COUNT(DISTINCT id_cliente) 
                    FROM creditos 
                    WHERE estado_credito = 'pagado') AS clientes_pagados;
            """
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchone()

        # Crear respuesta JSON
        response = {
            "clientes_activos": result["clientes_activos"],
            "clientes_en_demora": result["clientes_en_demora"],
            "clientes_pagados": result["clientes_pagados"]
        }
        return Response(json.dumps(response), mimetype="application/json")

    except Exception as e:
        error_response = {"error": str(e)}
        return Response(json.dumps(error_response), mimetype="application/json", status=500)
    finally:
        connection.close()

@app.route('/api/creditos-atrasados-grupo', methods=['GET'])
@token_required
def creditos_atrasados_por_grupo(user_data):
    query = """
        SELECT 
            IFNULL(c.grupo_clientes, 'Sin Grupo') AS grupo_cliente,
            COUNT(DISTINCT cred.id_credito) AS creditos_atrasados
        FROM 
            clientes c
        JOIN 
            creditos cred ON c.id_cliente = cred.id_cliente
        LEFT JOIN 
            (SELECT 
                 id_credito, 
                 SUM(monto_pago) AS total_pagado 
             FROM pagos 
             GROUP BY id_credito) p ON cred.id_credito = p.id_credito
        WHERE 
            cred.estado_credito = 'activo' 
            AND cred.valor_pactado > IFNULL(p.total_pagado, 0)
        GROUP BY 
            grupo_cliente
        ORDER BY 
            creditos_atrasados DESC;
    """
    
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()
        connection.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011, debug=True)
