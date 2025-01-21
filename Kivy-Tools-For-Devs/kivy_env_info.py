import os
import subprocess
import platform
import sys
import webbrowser

# Output file / Archivo de salida
OUTPUT_FILE = "kivy_environment_info.html"

# Detect the operating system
OS_NAME = platform.system().lower()

def escape_html(text):
    """Escape HTML special characters."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\"", "&quot;")
            .replace("'", "&#39;"))

def append_html(content):
    """Append content to the output HTML file."""
    with open(OUTPUT_FILE, "a") as f:
        f.write(content + "\n")

# Initialize HTML file
with open(OUTPUT_FILE, "w") as f:
    f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Kivy Environment Info</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .section { margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px; }
        .title { font-size: 20px; font-weight: bold; color: #333; }
        .hidden-content { display: none; }
        .toggle-button { cursor: pointer; color: #0066cc; text-decoration: underline; }
    </style>
    <script>
        function toggleVisibility(id) {
            const element = document.getElementById(id);
            if (element.style.display === 'none') {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        }
    </script>
</head>
<body>
<h1 style="color: #0066cc;">Kivy Environment Info</h1>
""")

def add_section(title, content, sensitive=False):
    """Add a section to the HTML file."""
    escaped_content = escape_html(content)
    section_id = title.replace(" ", "_").lower()
    if sensitive:
        append_html(f"<div class='section'>")
        append_html(f"<div class='title'>{title}</div>")
        append_html(f"<span class='toggle-button' onclick=\"toggleVisibility('{section_id}')\">Show/Hide</span>")
        append_html(f"<div id='{section_id}' class='hidden-content' style='display:none;'>{escaped_content}</div>")
        append_html("</div>")
    else:
        append_html(f"<div class='section'>")
        append_html(f"<div class='title'>{title}</div>")
        append_html(f"<pre>{escaped_content}</pre>")
        append_html("</div>")

# Add system information
system_info = platform.uname()._asdict().__str__()
add_section("System Information", system_info)

# Python version
add_section("Python Version", sys.version)

# Installed pip packages
try:
    pip_freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    add_section("Installed Pip Packages", pip_freeze)
except Exception as e:
    add_section("Installed Pip Packages", f"Error retrieving pip packages: {e}")

# Buildozer information
try:
    buildozer_version = subprocess.check_output(["buildozer", "-v"], text=True, stderr=subprocess.STDOUT)
    add_section("Buildozer Version", buildozer_version)
except subprocess.CalledProcessError as e:
    add_section("Buildozer Version", f"Buildozer command failed with error code {e.returncode}: {e.output}")
except FileNotFoundError:
    add_section("Buildozer Version", "Buildozer is not installed or there is an error.")

# python-for-android information
try:
    p4a_version = subprocess.check_output(["p4a", "--version"], text=True, stderr=subprocess.STDOUT)
    add_section("python-for-android Version", p4a_version)
except subprocess.CalledProcessError as e:
    add_section("python-for-android Version", f"python-for-android command failed with error code {e.returncode}: {e.output}")
except FileNotFoundError:
    add_section("python-for-android Version", "python-for-android is not installed or there is an error.")

# Android SDK configuration
ANDROIDSDK = os.getenv("ANDROIDSDK")
if not ANDROIDSDK:
    add_section("Android SDK", "ANDROIDSDK is not configured.")
else:
    try:
        sdk_files = os.listdir(ANDROIDSDK)
        add_section("Android SDK", f"ANDROIDSDK: {ANDROIDSDK}\n" + "\n".join(sdk_files), sensitive=True)
    except Exception as e:
        add_section("Android SDK", f"Error accessing ANDROIDSDK: {e}")

# Android NDK configuration
ANDROIDNDK = os.getenv("ANDROIDNDK")
if not ANDROIDNDK:
    add_section("Android NDK", "ANDROIDNDK is not configured.")
else:
    try:
        ndk_files = os.listdir(ANDROIDNDK)
        add_section("Android NDK", f"ANDROIDNDK: {ANDROIDNDK}\n" + "\n".join(ndk_files), sensitive=True)
    except Exception as e:
        add_section("Android NDK", f"Error accessing ANDROIDNDK: {e}")

# Kivy information
try:
    import kivy
    add_section("Kivy Version", kivy.__version__)
except ImportError:
    add_section("Kivy Version", "Kivy is not installed or there is an error.")

# PyJNIus information
try:
    import jnius
    add_section("PyJNIus Version", jnius.__version__)
except ImportError:
    add_section("PyJNIus Version", "PyJNIus is not installed or there is an error.")

# Virtual environment information
VIRTUAL_ENV = os.getenv("VIRTUAL_ENV")
if not VIRTUAL_ENV:
    add_section("Virtual Environment", "No virtual environment is being used.")
else:
    add_section("Virtual Environment", f"Active virtual environment: {VIRTUAL_ENV}", sensitive=True)

# Current environment variables
env_variables = "\n".join([f"{key}={value}" for key, value in os.environ.items()])
add_section("Current Environment Variables", env_variables, sensitive=True)

# Finalize HTML
with open(OUTPUT_FILE, "a") as f:
    f.write("""
</body>
</html>
""")

def install_xdg_open(global_install=True):
    """Install xdg-utils either globally or in the current environment."""
    try:
        if global_install:
            print("Installing xdg-utils globally...")
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "xdg-utils"], check=True)
            print("xdg-utils installed globally.")
        else:
            print("Installing xdg-utils in the current environment...")
            subprocess.run(["apt-get", "update"], check=True)
            subprocess.run(["apt-get", "install", "-y", "xdg-utils"], check=True)
            print("xdg-utils installed in the environment.")
    except Exception as e:
        print(f"Failed to install xdg-utils: {e}")

def open_in_browser():
    """Open the output file in the appropriate browser."""
    try:
        if OS_NAME == "windows":
            file_path = os.path.abspath(OUTPUT_FILE)
            if "microsoft" in platform.release().lower():  # Check if running in WSL
                subprocess.run(["cmd.exe", "/c", "start", file_path], check=True)
            else:
                subprocess.run(["powershell.exe", "Start-Process", file_path], check=True)
        elif OS_NAME == "linux":
            xdg_open_path = "/usr/bin/xdg-open"  # Ruta global típica de xdg-open
            if os.path.exists(xdg_open_path):
                subprocess.run([xdg_open_path, os.path.abspath(OUTPUT_FILE)], check=True)
            else:
                choice = input("xdg-open is not installed. Do you want to install it globally (G) or in the current environment (E)? [G/E]: ").strip().lower()
                if choice == 'g':
                    install_xdg_open(global_install=True)
                elif choice == 'e':
                    install_xdg_open(global_install=False)
                else:
                    print("Skipping xdg-open installation.")
        elif OS_NAME == "darwin":  # macOS
            subprocess.run(["open", os.path.abspath(OUTPUT_FILE)], check=True)
        else:
            print("Unsupported operating system. Please open the file manually.")
    except FileNotFoundError as fnf_error:
        print(f"FileNotFoundError: {fnf_error}")
        print("Please ensure the browser or tool exists.")
    except subprocess.CalledProcessError as cpe:
        print(f"CalledProcessError: {cpe}")
        print("There was an issue running the browser command.")
    except Exception as e:
        print(f"Failed to open the file in a browser: {e}")
        print(f"Please open the file manually: {os.path.abspath(OUTPUT_FILE)}")

# Completion message
if os.path.exists(OUTPUT_FILE):
    print(f"===== Finished =====\nThe information has been saved to {OUTPUT_FILE}")
    open_in_browser()
else:
    print("Error: The output file was not created.")
