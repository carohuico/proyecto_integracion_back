import threading
import os
import sys

def run_service(folder, file, port):
    """
    Ejecuta servicios usando threads en el puerto especificado
    """
    filepath = os.path.join("app", folder, f"{file}.py")
    os.system(f"python3 {filepath}")

# Lista de servicios CRUD con el archivo y puerto correspondiente
services = [
    # Servicios de CRUD_clientes
    {"folder": "CRUD_clientes", "file": "register", "port": 5100},
    {"folder": "CRUD_clientes", "file": "login", "port": 5000},
    {"folder": "CRUD_clientes", "file": "service_c_cliente", "port": 5001},
    {"folder": "CRUD_clientes", "file": "service_r_cliente", "port": 5002},
    {"folder": "CRUD_clientes", "file": "service_u_cliente", "port": 5003},
    {"folder": "CRUD_clientes", "file": "service_d_cliente", "port": 5004},
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

