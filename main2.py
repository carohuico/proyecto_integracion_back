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
    # Servicios de CRUD_creditos
    {"folder": "CRUD_creditos", "file": "actualizar_credito", "port": 5005},
    {"folder": "CRUD_creditos", "file": "creditos_cliente", "port": 5006},
    {"folder": "CRUD_creditos", "file": "historial_pagos_cliente", "port": 5007},
    {"folder": "CRUD_creditos", "file": "otorgar_credito", "port": 5008},
    {"folder": "CRUD_creditos", "file": "registro_pago", "port": 5009},
    {"folder": "CRUD_creditos", "file": "ver_creditos", "port": 5010},
    {"folder": "CRUD_creditos", "file": "ver_pagos", "port": 5016},
    {"folder": "CRUD_creditos", "file": "pagos_cliente", "port": 5017},
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

