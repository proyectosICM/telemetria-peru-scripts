import argparse
from socket_server import start_server
from gui import run_gui  # Asume que importas la GUI aquí
from threading import Event

def run_from_console():
    stop_event = Event()  # Crea el evento stop_event
    start_server(stop_event)  # Pasa el evento a start_server
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inicia el servidor en modo consola o GUI.")
    parser.add_argument('--gui', action='store_true', help="Ejecutar en modo gráfico")
    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        run_from_console()
