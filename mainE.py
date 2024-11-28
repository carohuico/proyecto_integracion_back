import threading
import os

def run_service(folder, file, port):
    """
    Ejecuta servicios usando threads en el puerto especificado.
    """
    filepath = os.path.join("app", folder, f"{file}.py")
    os.system(f"python3 {filepath}")

# Lista de servicios CRUD con el archivo, carpeta y puerto correspondiente
services = [
    # Servicios de CRUD_reportess
    {"folder": "CRUD_reportes", "file": "creditos_activos", "port": 5018},
    {"folder": "CRUD_reportes", "file": "pagos_atrasados", "port": 5019},
    {"folder": "CRUD_reportes", "file": "reporte_cliente", "port": 5020},
    {"folder": "CRUD_reportes", "file": "resumen_financiero", "port": 5021},
    {"folder": "CRUD_reportes", "file": "creditos_totales", "port": 5022},
]

threads = []

# Iniciar un thread por cada servicio
for service in services:
    thread = threading.Thread(target=run_service, args=(service["folder"], service["file"], service["port"]))
    threads.append(thread)
    thread.start()
    print(f"Servicio {service['file']} iniciado en la carpeta {service['folder']} en el puerto {service['port']}")

# Esperar a que todos los threads terminen
for thread in threads:
    thread.join()
    print("Todos los servicios han terminado.")

