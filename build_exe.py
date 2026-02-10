import PyInstaller.__main__

PyInstaller.__main__.run([
    "remote_server.py",
    "--onefile",
    "--windowed",
    "--add-data=remote.html;.",
    "--name=PC-Remote",
    "--clean"
])

print("\nBuild complete! Look for 'PC-Remote.exe' in the 'dist' folder.")
