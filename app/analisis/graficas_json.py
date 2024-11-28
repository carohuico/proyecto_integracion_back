from flask import Flask, jsonify
from app.db_config import get_db_connection
from flask_cors import CORS
from decimal import Decimal

app = Flask(__name__)
CORS(app)

@app.route('/api/mapa-rutas-impacto', methods=['GET'])
def get_mapa_rutas_impacto():
    print("Obteniendo datos de impacto en rutas...")
    query = """
        SELECT DISTINCT
            v.id_viaje,
            v.via_afectada AS via_afectada_viaje,
            c.via_afectada AS via_afectada_evento,
            c.longitud,
            c.latitud,
            c.descripcion AS descripcion_evento,
            c.tipo_evento,
            c.fecha_evento,
            c.referencia,
            v.cantidad AS impacto_financiero
        FROM
            viajes v
        LEFT JOIN
            viajes_cierres vc ON v.id_viaje = vc.id_viaje
        LEFT JOIN
            cierres c ON vc.id_evento = c.id_evento
        WHERE
            c.id_evento IS NOT NULL;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            print("Ejecutando consulta SQL...")
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Resultados obtenidos: {len(results)} filas.")

        # Transformar los resultados a un formato JSON serializable
        formatted_results = []
        for row in results:
            try:
                formatted_results.append({
                    "id_viaje": row.get("id_viaje"),
                    "via_afectada_viaje": row.get("via_afectada_viaje"),
                    "via_afectada_evento": row.get("via_afectada_evento"),
                    "longitud": float(row["longitud"]) if row["longitud"] is not None else None,
                    "latitud": float(row["latitud"]) if row["latitud"] is not None else None,
                    "descripcion_evento": row.get("descripcion_evento"),
                    "tipo_evento": row.get("tipo_evento"),
                    "fecha_evento": row.get("fecha_evento"),
                    "referencia": row.get("referencia"),
                    "impacto_financiero": float(row["impacto_financiero"]) if isinstance(row["impacto_financiero"], Decimal) else None
                })
            except Exception as e:
                print(f"Error al procesar fila: {row}, Error: {str(e)}")
                formatted_results.append({
                    "id_viaje": row.get("id_viaje"),
                    "error": str(e)
                })

        return jsonify(formatted_results)

    except Exception as e:
        print(f"Error encontrado durante la consulta o procesamiento: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()
        
@app.route('/api/mapa-rutas-eficiencia', methods=['GET'])
def get_mapa_rutas_eficiencia():
    print("Obteniendo datos de eficiencia de rutas...")
    query = """
        SELECT 
            v.id_viaje,
            v.cod_producto,
            c1.cargue AS origen,
            c1.latitud AS latitud_origen,
            c1.longitud AS longitud_origen,
            c2.descargue AS destino,
            c2.latitud AS latitud_destino,
            c2.longitud AS longitud_destino,
            v.cantidad,
            v.horas_viaje,
            COALESCE(c1.horas_espera_cargue, 0) + COALESCE(c2.horas_espera_descargue, 0) AS horas_demora,
            (v.cantidad / NULLIF(v.horas_viaje, 0)) AS eficiencia,
            (v.horas_viaje + COALESCE(c1.horas_espera_cargue, 0) + COALESCE(c2.horas_espera_descargue, 0)) AS tiempo_total
        FROM 
            viajes v
        LEFT JOIN 
            cargue c1 ON v.id_viaje = c1.id_viaje
        LEFT JOIN 
            descargue c2 ON v.id_viaje = c2.id_viaje
        WHERE 
            c1.latitud IS NOT NULL 
            AND c1.longitud IS NOT NULL
            AND c2.latitud IS NOT NULL 
            AND c2.longitud IS NOT NULL;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            print("Ejecutando consulta SQL para eficiencia...")
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Resultados obtenidos: {len(results)} filas.")

        formatted_results = []
        for row in results:
            try:
                formatted_results.append({
                    "id_viaje": row.get("id_viaje"),
                    "cod_producto": row.get("cod_producto"),
                    "origen": row.get("origen"),
                    "latitud_origen": float(row["latitud_origen"]) if row["latitud_origen"] is not None else None,
                    "longitud_origen": float(row["longitud_origen"]) if row["longitud_origen"] is not None else None,
                    "destino": row.get("destino"),
                    "latitud_destino": float(row["latitud_destino"]) if row["latitud_destino"] is not None else None,
                    "longitud_destino": float(row["longitud_destino"]) if row["longitud_destino"] is not None else None,
                    "cantidad": float(row["cantidad"]),
                    "horas_viaje": float(row["horas_viaje"]) if row["horas_viaje"] is not None else None,
                    "horas_demora": float(row["horas_demora"]) if row["horas_demora"] is not None else None,
                    "eficiencia": float(row["eficiencia"]) if row["eficiencia"] is not None else None,
                    "tiempo_total": float(row["tiempo_total"]) if row["tiempo_total"] is not None else None,
                })
            except Exception as e:
                print(f"Error al procesar fila: {row}, Error: {str(e)}")
                formatted_results.append({
                    "id_viaje": row.get("id_viaje"),
                    "error": str(e)
                })

        return jsonify(formatted_results)

    except Exception as e:
        print(f"Error encontrado durante la consulta o procesamiento: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()

@app.route('/api/creditos-pagos', methods=['GET'])
def get_creditos_pagos():
    print("Obteniendo datos de créditos y pagos...")
    query = """
        SELECT 
            DATE_FORMAT(p.fecha_pago, '%Y-%m') AS periodo,
            SUM(c.limite_credito) AS total_creditos,
            SUM(p.monto_pago) AS total_pagos
        FROM 
            clientes c
        JOIN 
            creditos cr ON c.id_cliente = cr.id_cliente
        LEFT JOIN 
            pagos p ON cr.id_credito = p.id_credito
        GROUP BY 
            periodo
        ORDER BY 
            periodo ASC;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        formatted_results = []
        for row in results:
            formatted_results.append({
                "periodo": row.get("periodo"),
                "total_creditos": float(row.get("total_creditos", 0)) if row.get("total_creditos") else 0,
                "total_pagos": float(row.get("total_pagos", 0)) if row.get("total_pagos") else 0,
            })

        return jsonify(formatted_results)
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5023, debug=True)
