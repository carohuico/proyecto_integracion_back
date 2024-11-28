import requests
import pymysql as mysql
import time

# Conexión a la base de datos
db = mysql.connect(
    host="localhost",
    user="root",
    password="444",
    database="historial_crediticio"
)
cursor = db.cursor()

# Diccionario para almacenar coordenadas ya consultadas
coordenadas_cache = {}

# Función para normalizar el nombre del lugar
def normalizar_lugar(lugar):
    partes = lugar.split()  # Divide el texto en palabras
    if len(partes) > 1:
        ciudad = ' '.join(partes[:-1]).capitalize() # Todas las palabras menos la última
        departamento = partes[-1].capitalize()  # Última palabra
        return f"{ciudad}, {departamento}"
    return lugar.capitalize()

# Función para obtener coordenadas desde OpenStreetMap
def obtener_coordenadas(lugar):
    # Si ya tenemos las coordenadas en la caché, no hacer la solicitud
    if lugar in coordenadas_cache:
        print(f"Coordenadas para {lugar} encontradas en caché.")
        return coordenadas_cache[lugar]

    lugar_normalizado = normalizar_lugar(lugar)
    url = f"https://nominatim.openstreetmap.org/search?q={lugar_normalizado}&format=json&limit=1"
    print(f"Buscando coordenadas para {lugar_normalizado}...")
    response = requests.get(url, headers={"User-Agent": "CoordenadasScript/1.0"})
    if response.status_code == 200 and response.json():
        data = response.json()[0]
        lat, lon = float(data['lat']), float(data['lon'])
        print(f"Coordenadas encontradas para {lugar_normalizado}: ({lat}, {lon})")
        # Guardar en la caché
        coordenadas_cache[lugar] = (lat, lon)
        return lat, lon

    print(f"No se encontraron coordenadas para {lugar_normalizado}")
    coordenadas_cache[lugar] = (None, None)  # Almacenar como no encontrado
    return None, None

# Obtener todos los lugares únicos sin coordenadas en la tabla descargue
cursor.execute("SELECT DISTINCT descargue FROM descargue WHERE latitud IS NULL OR longitud IS NULL;")
lugares = cursor.fetchall()

# Actualizar todas las filas relacionadas en una sola operación por lugar
for (lugar,) in lugares:
    print(f"Procesando lugar: {lugar}...")
    try:
        lat, lon = obtener_coordenadas(lugar)
        if lat and lon:
            cursor.execute(
                "UPDATE cargue SET latitud = %s, longitud = %s WHERE cargue = %s;",
                (lat, lon, lugar)
            )
            cursor.execute(
                "UPDATE descargue SET latitud = %s, longitud = %s WHERE descargue = %s;",
                (lat, lon, lugar)
            )
            print(f"Coordenadas agregadas para {lugar}: ({lat}, {lon})")
            db.commit()
        else:
            print(f"No se pudieron obtener coordenadas para {lugar}")
    except Exception as e:
        print(f"Error al procesar {lugar}: {e}")
    time.sleep(1)  # Espera 1 segundo entre cada consulta para evitar bloqueos

# Cerrar conexión
cursor.close()
db.close()
