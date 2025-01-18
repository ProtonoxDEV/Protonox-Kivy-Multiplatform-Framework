Kivy Environment Diagnostic Tool

Descripción

Este repositorio contiene un script de diagnóstico para entornos de desarrollo con Kivy. El script recopila información detallada del entorno, como:

🐍 Versión de Python y paquetes instalados.

🖥️ Detalles del sistema operativo.

🛠️ Configuración de herramientas de desarrollo como Buildozer y python-for-android.

📂 Rutas y configuraciones de Android SDK y NDK.

🌐 Variables de entorno activas.

🎨 Versión de Kivy y PyJNIus.

🧪 Estado del entorno virtual (si aplica).

El archivo generado puede ser utilizado para depuración, compartir configuraciones del entorno o resolver problemas al compilar aplicaciones Kivy para Android.

Description

This repository contains a diagnostic script for Kivy development environments. The script collects detailed information about the environment, such as:

🐍 Python version and installed packages.

🖥️ Operating system details.

🛠️ Development tools configuration, including Buildozer and python-for-android.

📂 Android SDK and NDK paths and configurations.

🌐 Active environment variables.

🎨 Kivy and PyJNIus versions.

🧪 Virtual environment status (if applicable).

The generated file can be used for debugging, sharing environment configurations, or resolving issues when building Kivy applications for Android.

Uso / Usage

En Español:

🔄 Clona el repositorio:

git clone https://github.com/ProtonoxDEV/Kivy-Tools-For-Devs.git
cd Kivy-Tools-For-Devs

🛠️ Haz el script ejecutable:

chmod +x kivy_env_info_with_env_vars.sh

▶️ Ejecuta el script:

./kivy_env_info_with_env_vars.sh

📄 Revisa el archivo generado:
El script generará un archivo llamado kivy_environment_info.txt con toda la información relevante del entorno.

In English:

🔄 Clone the repository:

git clone https://github.com/ProtonoxDEV/Kivy-Tools-For-Devs.git
cd Kivy-Tools-For-Devs

🛠️ Make the script executable:

chmod +x kivy_env_info_with_env_vars.sh

▶️ Run the script:

./kivy_env_info_with_env_vars.sh

📄 Check the generated file:
The script will generate a file named kivy_environment_info.txt with all relevant environment information.

Requisitos / Requirements

Python 3.x 🐍

Kivy 🎨

Opcional: Buildozer, python-for-android, Android SDK/NDK 🛠️

Contribuciones / Contributions

💡 Las contribuciones son bienvenidas. Si deseas agregar nuevas características o mejorar el script, abre un pull request o reporta un problema en la sección de issues.

💡 Contributions are welcome. If you want to add new features or improve the script, please open a pull request or report an issue in the issues section.
