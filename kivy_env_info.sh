#!/bin/bash

# Output file / Archivo de salida
OUTPUT_FILE="kivy_environment_info.txt"

# Delete the previous file if it exists / Borrar el archivo anterior si existe
if [ -f $OUTPUT_FILE ]; then
    rm $OUTPUT_FILE
fi

# Add system information / Agregar información del sistema
echo "===== System Information / Información del Sistema =====" >> $OUTPUT_FILE
uname -a >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Python version / Versión de Python
echo "===== Python Version / Versión de Python =====" >> $OUTPUT_FILE
python --version >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Installed pip packages / Paquetes instalados con pip
echo "===== Installed Pip Packages / Paquetes instalados con Pip =====" >> $OUTPUT_FILE
pip freeze >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Buildozer information / Información de Buildozer
echo "===== Buildozer Version / Versión de Buildozer =====" >> $OUTPUT_FILE
buildozer -v >> $OUTPUT_FILE 2>&1 || echo "Buildozer is not installed or there is an error / Buildozer no está instalado o hay un error." >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# python-for-android information / Información de python-for-android
echo "===== python-for-android Version / Versión de python-for-android =====" >> $OUTPUT_FILE
p4a --version >> $OUTPUT_FILE 2>&1 || echo "python-for-android is not installed or there is an error / python-for-android no está instalado o hay un error." >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Android SDK configuration / Configuración del SDK de Android
echo "===== Android SDK =====" >> $OUTPUT_FILE
if [ -z "$ANDROIDSDK" ]; then
    echo "ANDROIDSDK is not configured / ANDROIDSDK no está configurado." >> $OUTPUT_FILE
else
    echo "ANDROIDSDK: $ANDROIDSDK" >> $OUTPUT_FILE
    ls $ANDROIDSDK >> $OUTPUT_FILE 2>&1
fi
echo "" >> $OUTPUT_FILE

# Android NDK configuration / Configuración del NDK de Android
echo "===== Android NDK =====" >> $OUTPUT_FILE
if [ -z "$ANDROIDNDK" ]; then
    echo "ANDROIDNDK is not configured / ANDROIDNDK no está configurado." >> $OUTPUT_FILE
else
    echo "ANDROIDNDK: $ANDROIDNDK" >> $OUTPUT_FILE
    ls $ANDROIDNDK >> $OUTPUT_FILE 2>&1
fi
echo "" >> $OUTPUT_FILE

# Kivy information / Información de Kivy
echo "===== Kivy Version / Versión de Kivy =====" >> $OUTPUT_FILE
python -c "import kivy; print(kivy.__version__)" >> $OUTPUT_FILE 2>&1 || echo "Kivy is not installed or there is an error / Kivy no está instalado o hay un error." >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# PyJNIus information / Información de PyJNIus
echo "===== PyJNIus Version / Versión de PyJNIus =====" >> $OUTPUT_FILE
python -c "import jnius; print(jnius.__version__)" >> $OUTPUT_FILE 2>&1 || echo "PyJNIus is not installed or there is an error / PyJNIus no está instalado o hay un error." >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Virtual environment information / Información del entorno virtual
echo "===== Virtual Environment / Entorno Virtual =====" >> $OUTPUT_FILE
if [ -z "$VIRTUAL_ENV" ]; then
    echo "No virtual environment is being used / No se está utilizando un entorno virtual." >> $OUTPUT_FILE
else
    echo "Active virtual environment: $VIRTUAL_ENV / Entorno virtual activo: $VIRTUAL_ENV" >> $OUTPUT_FILE
fi
echo "" >> $OUTPUT_FILE

# Current environment variables / Variables de entorno actuales
echo "===== Current Environment Variables / Variables de Entorno Actuales =====" >> $OUTPUT_FILE
printenv >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Completion message / Mensaje de finalización
echo "===== Finished / Finalizado ====="
echo "The information has been saved to $OUTPUT_FILE / La información se ha guardado en $OUTPUT_FILE"
