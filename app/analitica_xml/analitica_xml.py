# app/analitica_xml/analitica_xml.py
from flask import Flask, Response
from flask_cors import CORS
from app.db_config import get_db_connection
import xml.etree.ElementTree as ET

app = Flask(__name__)
CORS(app)

@app.route('/api/cierre-vial-analitica', methods=['GET'])
def get_cierre_vial_analitica():
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("""
            WITH viajes_no_afectados AS (
                SELECT 
                    DISTINCT v2.id_viaje,
                    v2.horas_viaje,
                    v2.departamento,
                    v2.via_afectada
                FROM 
                    viajes v2
                WHERE 
                    v2.id_viaje NOT IN (SELECT id_viaje FROM viajes_cierres)
            ),
            viajes_comparados AS (
                SELECT 
                    DISTINCT v1.id_viaje AS viaje_afectado,
                    v1.horas_viaje AS horas_afectado,
                    v2.id_viaje AS viaje_no_afectado,
                    v2.horas_viaje AS horas_no_afectado,
                    (v1.horas_viaje - v2.horas_viaje) AS duracion_cierre_horas,
                    v1.departamento,
                    v1.via_afectada
                FROM 
                    viajes v1
                JOIN 
                    viajes_cierres vc ON v1.id_viaje = vc.id_viaje
                JOIN 
                    viajes_no_afectados v2 ON v1.departamento = v2.departamento 
                    AND v1.via_afectada = v2.via_afectada
                WHERE 
                    v1.horas_viaje > v2.horas_viaje
            )
            SELECT 
                vc.id_evento AS cierre_vial,
                AVG(cmp.duracion_cierre_horas) AS duracion_cierre_promedio,
                SUM(cr.valor_pagado - cr.valor_pactado) AS impacto_economico_total
            FROM 
                viajes_comparados cmp
            JOIN 
                viajes_cierres vc ON cmp.viaje_afectado = vc.id_viaje
            JOIN 
                creditos cr ON vc.id_viaje = cr.id_viaje
            WHERE 
                (cr.valor_pagado - cr.valor_pactado) > 0
            GROUP BY 
                vc.id_evento;
        """)
        data = cursor.fetchall()
    
    connection.close()

    # Crear la estructura XML
    root = ET.Element("cierres_viales")
    for row in data:
        cierre = ET.SubElement(root, "cierre_vial")
        ET.SubElement(cierre, "id_evento").text = str(row['cierre_vial'])
        ET.SubElement(cierre, "duracion_cierre_promedio").text = f"{row['duracion_cierre_promedio']:.2f}"
        ET.SubElement(cierre, "impacto_economico_total").text = f"{row['impacto_economico_total']:.2f}"

    # Convertir el árbol XML en una cadena
    xml_data = ET.tostring(root, encoding='utf-8', method='xml')

    return Response(xml_data, mimetype='application/xml')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5026)