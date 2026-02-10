from flask import Flask, request, send_from_directory, jsonify
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
import ssl
import os
import tempfile

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

# Ping endpoint so the website can verify connection
@app.route("/ping")
def ping():
    return jsonify({"status": "ok", "name": socket.gethostname()})

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
    return "OK"

@app.route("/back")
def back():
    click_area(0.25, 0.5, double=True)
    return "OK"

@app.route("/forward")
def forward():
    click_area(0.75, 0.5, double=True)
    return "OK"

@app.route("/fullscreen")
def fullscreen():
    pyautogui.press("f")
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
    return left_click()

@app.route("/scroll")
def scroll():
    dy = int(float(request.args.get('dy', 0)))
    pyautogui.scroll(dy)
    return "OK"

@app.route("/double_click")
def double_click():
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

def generate_ssl_cert():
    """Generate a self-signed SSL certificate for HTTPS."""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime

        # Generate key
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

        # Get local IP
        local_ip = get_local_ip()

        # Build certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "PC Remote"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "PC Remote"),
        ])

        # Add the local IP as a Subject Alternative Name so browsers accept it
        san = x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.IPv4Address(local_ip)),
        ])

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
            .add_extension(san, critical=False)
            .sign(key, hashes.SHA256())
        )

        # Write to temp files
        cert_dir = os.path.join(tempfile.gettempdir(), "pc_remote_ssl")
        os.makedirs(cert_dir, exist_ok=True)
        cert_path = os.path.join(cert_dir, "cert.pem")
        key_path = os.path.join(cert_dir, "key.pem")

        with open(cert_path, "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        with open(key_path, "wb") as f:
            f.write(key.private_bytes(
                serialization.Encoding.PEM,
                serialization.PrivateFormat.TraditionalOpenSSL,
                serialization.NoEncryption()
            ))

        return cert_path, key_path

    except ImportError:
        print("⚠️  'cryptography' package not found. Install with: pip install cryptography")
        print("    Falling back to HTTP mode.")
        return None, None


def get_local_ip():
    """Get the real local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return socket.gethostbyname(socket.gethostname())


import ipaddress

def show_popup(url, is_https=False):
    root = tk.Tk()
    root.title("PC Remote")
    root.geometry("350x500")
    root.configure(bg="#121212")

    # Generate QR Code
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

    if is_https:
        lbl_ssl = tk.Label(root, text="🔒 Running with HTTPS", font=("Arial", 9), fg="#22c55e", bg="#121212")
        lbl_ssl.pack(pady=2)

    btn_ok = tk.Button(root, text="Close Window", command=root.destroy, bg="#3b82f6", fg="white", font=("Arial", 10, "bold"), relief="flat", padx=20, pady=5)
    btn_ok.pack(pady=15)

    root.mainloop()


if __name__ == "__main__":
    local_ip = get_local_ip()
    port = 5000

    # Try to generate SSL cert
    cert_path, key_path = generate_ssl_cert()
    use_ssl = cert_path is not None

    if use_ssl:
        url = f"https://{local_ip}:{port}"
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert_path, key_path)
    else:
        url = f"http://{local_ip}:{port}"
        ssl_context = None

    print("\n" + "="*50)
    print("🚀 PC REMOTE SERVER IS STARTING!")
    print(f"📱 Connect your phone to: {url}")
    if use_ssl:
        print("🔒 HTTPS enabled (self-signed certificate)")
    print("="*50 + "\n")

    # Start server in background thread
    def run_server():
        if ssl_context:
            app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False, ssl_context=ssl_context)
        else:
            app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    show_popup(url, is_https=use_ssl)

    while True:
        time.sleep(1)
