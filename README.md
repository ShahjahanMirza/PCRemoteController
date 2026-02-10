# PC Remote Controller

Turn your phone into a wireless remote for your PC. Control media playback, move your mouse, scroll, type, and more — all from your phone's browser. No app install needed on your phone.

---

## What It Does

PC Remote lets you control your computer from your phone over your local WiFi network. It works entirely in your browser — no phone app to download, no accounts to create, no cloud servers involved.

**Controls include:**
- Play / Pause / Skip (media playback)
- Volume up / down / mute
- Virtual trackpad (move your mouse by swiping)
- Left click, right click, double click
- Scroll bar
- Mouse 4 & 5 buttons (browser back/forward)
- On-screen keyboard (type from your phone)
- Fullscreen toggle and Escape

---

## How It Works

1. **Download** `PC-Remote.exe` on your Windows PC
2. **Run it** — a small window appears showing a QR code and your local IP address
3. **Open the website** on your phone (same WiFi network)
4. **Scan the QR code** or enter the IP manually
5. **You're connected** — the remote control panel appears on your phone

That's it. Your phone sends commands to your PC over your local network. The PC executes them (mouse moves, key presses, clicks) using the local server running on your machine.

### Technical Flow

```
Phone (browser) → WiFi → PC (local Flask server on port 5000) → executes input
```

- The `.exe` starts a lightweight HTTP server on your PC (Flask, port 5000)
- Your phone's browser sends simple HTTP requests to that server
- The server translates those requests into mouse/keyboard actions using `pyautogui`
- Everything happens on your local network — nothing leaves your WiFi

---

## Requirements

- **PC:** Windows 10 or later
- **Phone:** Any phone with a modern browser (Chrome, Safari, Firefox)
- **Network:** Both devices must be on the same WiFi network
- **Firewall:** You may need to allow the app through Windows Firewall when prompted

---

## Security & Privacy

### Does this collect my data?

**No.** Zero data is collected, stored, or transmitted anywhere.

- There are no analytics, no tracking, no telemetry
- There is no account system — nothing to sign up for
- No data is sent to any external server, ever
- The source code is fully open — you can verify this yourself

### Is my PC at risk?

The app runs a local HTTP server that only listens on your WiFi network. Here's what that means:

- **Only devices on your WiFi** can send commands to your PC. Nobody on the internet can reach it.
- **The server only accepts predefined commands** — it can move the mouse, press keys, click, scroll, and type. It cannot access your files, read your screen, install software, or do anything beyond simulating input.
- **No remote access from outside your network.** The server binds to your local IP (like `192.168.1.x`), which is not reachable from the internet.
- **When you close the app, the server doesnt stop.** The PC-Remote.exe keeps running in the background. MAKE SURE TO CLOSE IT.

### What about the .exe — is it safe?

The `.exe` is built from the Python source code in this repository using PyInstaller. You can:

1. Read every line of code in `remote_server.py` — it's all here
2. Build the `.exe` yourself from source if you prefer (see below)
3. Scan it with any antivirus — some may flag PyInstaller executables as false positives, which is a [known issue](https://github.com/pyinstaller/pyinstaller/issues/6754) with PyInstaller, not a sign of malware

### Can someone on my WiFi hijack this?

If someone is already on your WiFi network, they could theoretically send commands to the server. This is the same trust model as any local network tool (Chromecast, AirPlay, etc.). If you're on a public or shared network, be cautious — only run the app on networks you trust.

---

## Building From Source

If you'd rather not use the prebuilt `.exe`, you can run it directly from Python:

```bash
# Clone the repo
git clone https://github.com/ShahjahanMirza/PCRemoteController.git
cd PCRemoteController

# Install dependencies
pip install flask flask-cors pyautogui screeninfo pillow qrcode

# Run the server
python remote_server.py
```

To build your own `.exe`:

```bash
pip install pyinstaller
python build_exe.py
```

The output will be in the `dist/` folder.

---

## FAQ

**Q: Do I need to install an app on my phone?**
No. The remote runs entirely in your phone's browser.

**Q: Does this work over the internet / mobile data?**
No. Both your phone and PC must be on the same WiFi network. This is by design — it keeps things fast, simple, and secure.

**Q: Why does Windows Firewall ask me to allow the app?**
The app starts a local server so your phone can talk to your PC. Windows needs your permission to allow incoming connections on your local network. This is normal and safe — it only allows connections from your WiFi, not the internet.

**Q: My antivirus flagged the .exe — is it a virus?**
No. This is a common false positive with PyInstaller-built executables. The source code is fully open for inspection. You can also build the `.exe` yourself from source to be sure.

**Q: Can I use this to control someone else's PC?**
Only if you're on the same WiFi network and they're running the app. There's no remote access capability — this is a local network tool only.

**Q: Does it work on Mac or Linux?**
Currently Windows only. The mouse/keyboard control uses Windows-specific APIs. Mac/Linux support may come in the future.

**Q: Can I customize the controls?**
Not yet in the UI, but the source code is straightforward to modify. You can add new routes in `remote_server.py` for any key or action you want.

**Q: The connection isn't working — what should I check?**
1. Make sure both devices are on the same WiFi network
2. Check that Windows Firewall allowed the app
3. Try entering the IP address manually instead of scanning the QR
4. Make sure no other app is using port 5000

**Q: Is this project still maintained?**
Yes. Check the [releases page](https://github.com/ShahjahanMirza/PCRemoteController/releases) for the latest version.

---

## License

This project is open source. Feel free to use, modify, and distribute it.

---

Built by [@ShahjahanMirza](https://github.com/ShahjahanMirza)
