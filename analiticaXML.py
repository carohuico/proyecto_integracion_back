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
    {"folder": "analisis", "file": "graficas_json", "port": 5023},
    {"folder": "analisis", "file": "graficas2", "port": 5025},
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
