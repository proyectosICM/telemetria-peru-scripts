import tkinter as tk
from threading import Thread, Event
from socket_server import start_server

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Servidor Socket GUI")
        
        # Etiqueta para mostrar el estado del servidor
        self.status_label = tk.Label(root, text="Servidor detenido", fg="red")
        self.status_label.pack(pady=10)

        # Botón para iniciar el servidor
        self.start_button = tk.Button(root, text="Iniciar Servidor", command=self.start_server)
        self.start_button.pack(pady=10)

        # Botón para detener el servidor
        self.stop_button = tk.Button(root, text="Detener Servidor", command=self.stop_server, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.server_thread = None
        self.stop_event = Event()  # Evento para detener el servidor
        self.server_running = False

    def start_server(self):
        if not self.server_running:
            self.server_running = True
            self.stop_event.clear()  # Asegurarse de que el evento esté limpio
            self.server_thread = Thread(target=start_server, args=(self.stop_event,))
            self.server_thread.start()
            self.status_label.config(text="Servidor en ejecución", fg="green")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)

    def stop_server(self):
        if self.server_running:
            self.server_running = False
            self.stop_event.set()  # Enviar la señal para detener el servidor
            self.server_thread.join()  # Esperar a que el hilo del servidor termine
            self.status_label.config(text="Servidor detenido", fg="red")
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

def run_gui():
    root = tk.Tk()
    app = ServerApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()
