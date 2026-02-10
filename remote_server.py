from flask import Flask, request, send_from_directory
from flask_cors import CORS
import pyautogui
from screeninfo import get_monitors
import time
import ctypes
import socket
import threading
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import qrcode
import io

# Windows Mouse Event Constants
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002

app = Flask(__name__)
CORS(app) # Enable CORS for phone-to-PC communication

@app.route("/")
@app.route("/remote.html")
def index():
    return send_from_directory(".", "remote.html")

# CONFIG
DOUBLE_CLICK_DELAY = 0.05
pyautogui.FAILSAFE = False # Prevent accidental locks, though use with caution

def get_screen():
    # Gets the primary monitor
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
    # center click for YouTube play/pause
    click_area(0.5, 0.5)
    return "OK"

@app.route("/back")
def back():
    # left side double click for rewind
    click_area(0.25, 0.5, double=True)
    return "OK"

@app.route("/forward")
def forward():
    # right side double click for fast forward
    click_area(0.75, 0.5, double=True)
    return "OK"

@app.route("/fullscreen")
def fullscreen():
    pyautogui.press("f")  # YouTube fullscreen toggle
    return "OK"

@app.route("/esc")
def exit_fullscreen():
    pyautogui.press("esc")
    return "OK"

@app.route("/arrow_left")
def arrow_left():
    pyautogui.press("left")
    return "OK"

@app.route("/arrow_right")
def arrow_right():
    pyautogui.press("right")
    return "OK"

@app.route("/arrow_up")
def arrow_up():
    pyautogui.press("up")
    return "OK"

@app.route("/arrow_down")
def arrow_down():
    pyautogui.press("down")
    return "OK"

@app.route("/mute")
def mute():
    pyautogui.press("m")
    return "OK"

@app.route("/mouse_move")
def mouse_move():
    dx = float(request.args.get('dx', 0))
    dy = float(request.args.get('dy', 0))
    # Move relative to current position
    pyautogui.moveRel(dx, dy, _pause=False)
    return "OK"

@app.route("/left_click")
def left_click():
    pyautogui.click(button='left')
    return "OK"

@app.route("/right_click")
def right_click():
    pyautogui.click(button='right')
    return "OK"

@app.route("/mouse_down")
def mouse_down():
    button = request.args.get('button', 'left')
    if button == 'x1':
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, XBUTTON1, 0)
    elif button == 'x2':
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XDOWN, 0, 0, XBUTTON2, 0)
    else:
        pyautogui.mouseDown(button=button)
    return "OK"

@app.route("/mouse_up")
def mouse_up():
    button = request.args.get('button', 'left')
    if button == 'x1':
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, XBUTTON1, 0)
    elif button == 'x2':
        ctypes.windll.user32.mouse_event(MOUSEEVENTF_XUP, 0, 0, XBUTTON2, 0)
    else:
        pyautogui.mouseUp(button=button)
    return "OK"

@app.route("/mouse_click")
def mouse_click():
    # Maintain for trackpad tap (default to left)
    return left_click()

@app.route("/scroll")
def scroll():
    # pyautogui.scroll(amount) - positive is up, negative is down
    # Browser scrolling usually feels better with small increments
    dy = int(float(request.args.get('dy', 0)))
    pyautogui.scroll(dy)
    return "OK"

@app.route("/double_click")
def double_click():
    # Double click center (requested for fullscreen toggle)
    click_area(0.5, 0.5, double=True)
    return "OK"

@app.route("/type")
def type_text():
    text = request.args.get('text', '')
    if text:
        pyautogui.write(text)
    return "OK"

@app.route("/press_key")
def press_key():
    key = request.args.get('key', '')
    if key:
        pyautogui.press(key)
    return "OK"

def show_popup(url):
    root = tk.Tk()
    root.title("Video Remote Started")
    root.geometry("350x450")
    root.configure(bg="#121212")

    # Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="white", back_color="#121212")
    
    # Convert PIL image to Tkinter-compatible photo image
    img_qr = img_qr.resize((300, 300))
    photo = ImageTk.PhotoImage(img_qr)

    # UI Elements
    lbl_title = tk.Label(root, text="🚀 Server is live!", font=("Arial", 16, "bold"), fg="#3b82f6", bg="#121212")
    lbl_title.pack(pady=10)

    lbl_qr = tk.Label(root, image=photo, bg="#121212")
    lbl_qr.image = photo # Keep reference
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
    # Get local IP for convenience
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    # Sometimes gethostbyname returns 127.0.0.1, try a trick to get the real local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except:
        pass

    url = f"http://{local_ip}:5000"

    print("\n" + "="*50)
    print("🚀 VIDEO REMOTE SERVER IS STARTING!")
    print(f"📱 Connect your phone to: {url}")
    print("="*50 + "\n")

    # Start the popup in the main thread (Tkinter likes main thread)
    # and the server in a background thread.
    server_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False))
    server_thread.daemon = True
    server_thread.start()

    show_popup(url)
    
    # Keep the main process alive until the server thread ends (it won't unless killed)
    while True:
        time.sleep(1)
