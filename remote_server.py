from flask import Flask, request, send_from_directory, Response
from flask_cors import CORS
import pyautogui
from screeninfo import get_monitors
import time
import ctypes
import socket
import threading
import tkinter as tk
from PIL import Image, ImageTk
import qrcode

# Windows Mouse Event Constants
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/")
@app.route("/remote.html")
def index():
    return send_from_directory(".", "remote.html")

# 1x1 transparent GIF for image-based ping/commands
PIXEL = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'

def pixel_response():
    return Response(PIXEL, mimetype='image/gif', headers={
        'Cache-Control': 'no-store',
        'Access-Control-Allow-Origin': '*'
    })

@app.route("/ping")
def ping():
    return pixel_response()

# CONFIG
DOUBLE_CLICK_DELAY = 0.05
pyautogui.FAILSAFE = False

def get_screen():
    m = get_monitors()[0]
    return m.width, m.height

def click_area(x_ratio, y_ratio, double=False):
    w, h = get_screen()
    x = int(w * x_ratio)
    y = int(h * y_ratio)
    print(f"Clicking at {x}, {y} (ratio: {x_ratio}, {y_ratio})")
    pyautogui.moveTo(x, y, duration=0.05)
    if double:
        pyautogui.click(clicks=2, interval=DOUBLE_CLICK_DELAY)
    else:
        pyautogui.click()

@app.route("/play")
def play_pause():
    click_area(0.5, 0.5)
    return pixel_response()

@app.route("/back")
def back():
    click_area(0.25, 0.5, double=True)
    return pixel_response()

@app.route("/forward")
def forward():
    click_area(0.75, 0.5, double=True)
    return pixel_response()

@app.route("/fullscreen")
def fullscreen():
    pyautogui.press("f")
    return pixel_response()

@app.route("/esc")
def exit_fullscreen():
    pyautogui.press("esc")
    return pixel_response()

@app.route("/arrow_left")
def arrow_left():
    pyautogui.press("left")
    return pixel_response()

@app.route("/arrow_right")
def arrow_right():
    pyautogui.press("right")
    return pixel_response()

@app.route("/arrow_up")
def arrow_up():
    pyautogui.press("up")
    return pixel_response()

@app.route("/arrow_down")
def arrow_down():
    pyautogui.press("down")
    return pixel_response()

@app.route("/mute")
def mute():
    pyautogui.press("m")
    return pixel_response()

@app.route("/mouse_move")
def mouse_move():
    dx = float(request.args.get('dx', 0))
    dy = float(request.args.get('dy', 0))
    pyautogui.moveRel(dx, dy, _pause=False)
    return pixel_response()

@app.route("/left_click")
def left_click():
    pyautogui.click(button='left')
    return pixel_response()

@app.route("/right_click")
def right_click():
    pyautogui.click(button='right')
    return pixel_response()

@app.route("/mouse_down")
def mouse_down():
    button = request.args.get('button', 'left')
    if button == 'x1':
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, XBUTTON1, 0)
    elif button == 'x2':
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, XBUTTON2, 0)
    else:
        pyautogui.mouseDown(button=button)
    return pixel_response()

@app.route("/mouse_up")
def mouse_up():
    button = request.args.get('button', 'left')
    if button == 'x1':
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, XBUTTON1, 0)
    elif button == 'x2':
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, XBUTTON2, 0)
    else:
        pyautogui.mouseUp(button=button)
    return pixel_response()

@app.route("/mouse_click")
def mouse_click():
    return left_click()

@app.route("/scroll")
def scroll():
    dy = int(float(request.args.get('dy', 0)))
    pyautogui.scroll(dy)
    return pixel_response()

@app.route("/double_click")
def double_click():
    click_area(0.5, 0.5, double=True)
    return pixel_response()

@app.route("/type")
def type_text():
    text = request.args.get('text', '')
    if text:
        pyautogui.write(text)
    return pixel_response()

@app.route("/press_key")
def press_key():
    key = request.args.get('key', '')
    if key:
        pyautogui.press(key)
    return pixel_response()

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return socket.gethostbyname(socket.gethostname())


def show_popup(url):
    root = tk.Tk()
    root.title("PC Remote")
    root.geometry("350x450")
    root.configure(bg="#121212")

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="white", back_color="#121212")
    img_qr = img_qr.resize((300, 300))
    photo = ImageTk.PhotoImage(img_qr)

    lbl_title = tk.Label(root, text="🚀 Server is live!", font=("Arial", 16, "bold"), fg="#3b82f6", bg="#121212")
    lbl_title.pack(pady=10)

    lbl_qr = tk.Label(root, image=photo, bg="#121212")
    lbl_qr.image = photo
    lbl_qr.pack(pady=5)

    lbl_info = tk.Label(root, text="Scan to connect your phone:", font=("Arial", 10), fg="white", bg="#121212")
    lbl_info.pack(pady=5)

    entry_url = tk.Entry(root, font=("Consolas", 10), fg="#94a3b8", bg="#1a1a1a", relief="flat", justify="center", width=35)
    entry_url.insert(0, url)
    entry_url.config(state="readonly")
    entry_url.pack(pady=5)

    btn_ok = tk.Button(root, text="Close Window", command=root.destroy, bg="#3b82f6", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=20, pady=5)
    btn_ok.pack(pady=15)

    root.mainloop()


if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 5000
    url = f"http://{local_ip}:{port}"

    print("\n" + "="*50)
    print("🚀 PC REMOTE SERVER IS STARTING!")
    print(f"📱 Connect your phone to: {url}")
    print("="*50 + "\n")

    server_thread = threading.Thread(
        target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()

    show_popup(url)

    while True:
        time.sleep(1)
