import os
import sys
import PyInstaller.__main__

# The name of your script
script_name = "remote_server.py"

# Include the remote.html file
add_data = "--add-data=remote.html;."

# Path to PyInstaller executable
PyInstaller.__main__.run([
    script_name,
    "--onefile",
    "--windowed", # Use this if you don't want a console window, but for debugging keep it console-less by removing this if needed
    add_data,
    "--name=VideoRemote",
    "--clean"
])

print("\nBuild complete! Look for 'VideoRemote.exe' in the 'dist' folder.")
