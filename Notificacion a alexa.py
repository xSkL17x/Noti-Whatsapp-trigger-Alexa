import requests, time, os, threading
import tkinter as tk
from wintoastlistener import ToastListener
import pystray
from PIL import Image, ImageDraw

CSV_FILE = "config.csv"
ultimo_aviso = 0

def estado(texto): root.after(0, lambda: lbl_estado.config(text=texto))

def notificacion(ev, payload):
    global ultimo_aviso
    if "whatsapp" in (str(ev) + str(payload)).lower() and time.time() - ultimo_aviso > 10:
        estado("Enviar Notificacion a Alexa...")
        try:
            if requests.get(entry_url.get().strip(), timeout=5).status_code == 200:
                ultimo_aviso = time.time()
                estado("  Noti Activada en Alexa con éxito.")
            else: estado("Error en el URL.")
        except: estado(" Error de conexión.")

def iniciar():
    with open(CSV_FILE, "w") as f: f.write(entry_url.get().strip())
    estado("Esperando Mensajes...")
    btn_iniciar.config(state=tk.DISABLED)
    threading.Thread(target=lambda: ToastListener(notificacion).listen(), daemon=True).start()

def crear_icono():
    img = Image.new('RGB', (64, 64), color=(0, 0, 0))
    ImageDraw.Draw(img).rectangle((16, 16, 48, 48), fill=(0, 255, 0))
    return img

def ocultar_bandeja(event=None):
    if event and root.state() != 'iconic': return
    root.withdraw()
    menu = pystray.Menu(pystray.MenuItem("Mostrar", lambda i, j: (i.stop(), root.after(0, root.deiconify))), pystray.MenuItem("Salir", lambda i, j: (i.stop(), root.destroy())))
    threading.Thread(target=pystray.Icon("Notificador", crear_icono(), "Notificador Alexa", menu).run, daemon=True).start()

root = tk.Tk()
root.title("Notificador Alexa")
root.geometry("450x150")
root.bind('<Unmap>', ocultar_bandeja)

tk.Label(root, text="URL de Alexa:").pack(pady=5)
entry_url = tk.Entry(root, width=65)

if os.path.exists(CSV_FILE):
    with open(CSV_FILE, "r") as f: entry_url.insert(0, f.read().strip())
    
entry_url.pack(pady=5)

btn_iniciar = tk.Button(root, text="Guardar e Iniciar", command=iniciar)
btn_iniciar.pack(pady=5)
lbl_estado = tk.Label(root, text="Esperando inicio...", font=("Arial", 10, "bold"), fg="blue")
lbl_estado.pack(pady=10)

try: root.mainloop()
except KeyboardInterrupt: root.destroy()