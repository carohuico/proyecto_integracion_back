import threading
import os
import sys

def run_service(file, port):
    """
    Ejecuta servicios usando threads en el puerto especificado
    """
    filepath = os.path.join("app", "CRUD_clientes", f"{file}.py")
    os.system(f"python3 {filepath}")

# Lista de servicios CRUD con el archivo y puerto correspondiente
services = [
    {"file": "service_c_cliente", "port": 5001},
    {"file": "service_r_cliente", "port": 5002},
    {"file": "service_u_cliente", "port": 5003},
    {"file": "service_d_cliente", "port": 5004},
]

threads = []

# Iniciar un thread por cada servicio
for service in services:
    thread = threading.Thread(target=run_service, args=(service["file"], service["port"]))
    threads.append(thread)
    thread.start()
    print(f"Servicio {service['file']} iniciado en el puerto {service['port']}")

# Esperar a que todos los threads terminen
for thread in threads:
    thread.join()
    print("Todos los servicios han terminado.")

