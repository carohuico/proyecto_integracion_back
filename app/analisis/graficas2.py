from flask import Flask, jsonify
from app.db_config import get_db_connection
from flask_cors import CORS
from decimal import Decimal

app = Flask(__name__)
CORS(app)

@app.route('/api/impacto-economico-cierres', methods=['GET'])
def get_impacto_economico_cierres():
    print("Obteniendo datos de impacto económico por cierres viales...")
    query = """
        SELECT
            c.tipo_evento AS tipo_cierre,
            SUM(cr.valor_pactado - cr.valor_pagado) AS monto_perdida
        FROM
            cierres c
        JOIN
            viajes_cierres vc ON c.id_evento = vc.id_evento
        JOIN
            viajes v ON vc.id_viaje = v.id_viaje
        JOIN
            creditos cr ON v.id_viaje = cr.id_viaje
        WHERE
            cr.estado_credito = 'activo'
        GROUP BY
            c.tipo_evento;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            print("Ejecutando consulta SQL...")
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Resultados obtenidos: {len(results)} filas.")

        formatted_results = [
            {
                "tipo_cierre": row["tipo_cierre"],
                "monto_perdida": float(row["monto_perdida"]) if isinstance(row["monto_perdida"], Decimal) else None
            }
            for row in results
        ]
        return jsonify(formatted_results)

    except Exception as e:
        print(f"Error encontrado durante la consulta o procesamiento: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()

@app.route('/api/riesgo-credito-rutas', methods=['GET'])
def get_riesgo_credito_rutas():
    print("Obteniendo datos de riesgo de crédito por ruta...")
    query = """
        SELECT
            c.ruta,
            SUM(cr.valor_pactado - cr.valor_pagado) AS monto_pendiente,
            COUNT(DISTINCT cr.id_credito) AS numero_creditos,
            CASE
                WHEN SUM(cr.valor_pactado - cr.valor_pagado) > 100000 THEN 'Alto'
                WHEN SUM(cr.valor_pactado - cr.valor_pagado) BETWEEN 50000 AND 100000 THEN 'Medio'
                ELSE 'Bajo'
            END AS nivel_riesgo
        FROM
            cierres c
        JOIN
            viajes_cierres vc ON c.id_evento = vc.id_evento
        JOIN
            viajes v ON vc.id_viaje = v.id_viaje
        JOIN
            creditos cr ON v.id_viaje = cr.id_viaje
        WHERE
            cr.estado_credito = 'activo'
        GROUP BY
            c.ruta;
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            print("Ejecutando consulta SQL...")
            cursor.execute(query)
            results = cursor.fetchall()
            print(f"Resultados obtenidos: {len(results)} filas.")

        formatted_results = [
            {
                "ruta": row["ruta"],
                "monto_pendiente": float(row["monto_pendiente"]) if isinstance(row["monto_pendiente"], Decimal) else None,
                "numero_creditos": row["numero_creditos"],
                "nivel_riesgo": row["nivel_riesgo"]
            }
            for row in results
        ]
        return jsonify(formatted_results)

    except Exception as e:
        print(f"Error encontrado durante la consulta o procesamiento: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5025, debug=True)

