#!/bin/bash
# Script de deployment para WSL - Protonox App

echo "🚀 DEPLOYMENT DE PROTONOX APP EN WSL"
echo "===================================="

# Detectar WSL
if [ -n "$WSL_DISTRO_NAME" ]; then
    echo "✅ Detectado WSL: $WSL_DISTRO_NAME"
else
    echo "❌ No se detectó WSL"
    exit 1
fi

# Función para usar ADB de Windows o Linux
setup_adb() {
    WINDOWS_ADB="/mnt/c/Windows/System32/adb.exe"
    LINUX_ADB="/usr/bin/adb"

    if [ -f "$WINDOWS_ADB" ] && "$WINDOWS_ADB" devices >/dev/null 2>&1; then
        echo "✅ Usando ADB de Windows: $WINDOWS_ADB"
        alias adb="$WINDOWS_ADB"
        export ADB="$WINDOWS_ADB"
        return 0
    elif [ -f "$LINUX_ADB" ] && "$LINUX_ADB" devices >/dev/null 2>&1; then
        echo "✅ Usando ADB de Linux: $LINUX_ADB"
        alias adb="$LINUX_ADB"
        export ADB="$LINUX_ADB"
        return 0
    else
        echo "❌ Ningún ADB funcional encontrado"
        echo "💡 Asegúrate de que:"
        echo "   - Tu celular esté conectado por USB"
        echo "   - La depuración USB esté habilitada"
        echo "   - Hayas aceptado el diálogo de depuración en el celular"
        return 1
    fi
}

# Verificar dispositivo conectado
check_device() {
    echo ""
    echo "📱 Verificando dispositivo Android..."
    if adb devices | grep -q "device$"; then
        echo "✅ Dispositivo Android conectado:"
        adb devices -l
        return 0
    else
        echo "❌ No se detecta dispositivo Android"
        echo ""
        echo "🔧 Instrucciones para conectar tu celular:"
        echo "1. Habilita 'Opciones de desarrollador' en Android:"
        echo "   - Ve a Configuración > Acerca del teléfono"
        echo "   - Toca 'Número de compilación' 7 veces"
        echo "2. Habilita 'Depuración USB':"
        echo "   - Configuración > Opciones de desarrollador > Depuración USB"
        echo "3. Conecta tu celular por USB"
        echo "4. Acepta el diálogo de 'Permitir depuración USB' en tu celular"
        echo "5. Ejecuta este script nuevamente"
        return 1
    fi
}

# Función para build APK
build_apk() {
    echo ""
    echo "🔨 Construyendo APK..."
    if [ -f "buildozer.spec" ]; then
        echo "✅ buildozer.spec encontrado"
        echo "🏗️  Ejecutando: buildozer android debug"
        source venv_buildozer/bin/activate && buildozer android debug
        if [ $? -eq 0 ]; then
            echo "✅ APK construido exitosamente"
            find . -name "*.apk" -type f -printf "📦 APK encontrado: %p (%s bytes)\n" | tail -1
            return 0
        else
            echo "❌ Error al construir APK"
            return 1
        fi
    else
        echo "❌ buildozer.spec no encontrado"
        return 1
    fi
}

# Función para instalar APK
install_apk() {
    echo ""
    echo "📥 Instalando APK en dispositivo..."
    APK_FILE=$(find . -name "*.apk" -type f | head -1)
    if [ -n "$APK_FILE" ]; then
        echo "📦 Instalando: $APK_FILE"
        adb install -r "$APK_FILE"
        if [ $? -eq 0 ]; then
            echo "✅ APK instalado exitosamente"
            return 0
        else
            echo "❌ Error al instalar APK"
            return 1
        fi
    else
        echo "❌ No se encontró archivo APK"
        return 1
    fi
}

# Función para ejecutar app
run_app() {
    echo ""
    echo "▶️  Ejecutando app en dispositivo..."
    PACKAGE_NAME="org.protonox.protonox_app_complete"
    ACTIVITY_NAME=".MainActivity"

    adb shell am start -n "$PACKAGE_NAME/$PACKAGE_NAME$ACTIVITY_NAME"
    if [ $? -eq 0 ]; then
        echo "✅ App ejecutada exitosamente"
        echo "📱 Revisa tu celular - la app debería estar ejecutándose"
        return 0
    else
        echo "❌ Error al ejecutar app"
        return 1
    fi
}

# Main
cd "/home/protonox/Protonox-Kivy-Multiplatform-Framework/protonox_test_app"

# Configurar ADB
if ! setup_adb; then
    exit 1
fi

# Verificar dispositivo
if ! check_device; then
    echo ""
    echo "💡 Una vez conectado el dispositivo, ejecuta:"
    echo "   $0 build    # Para construir APK"
    echo "   $0 install  # Para instalar APK"
    echo "   $0 run      # Para ejecutar app"
    exit 1
fi

# Procesar argumentos
case "${1:-all}" in
    "build")
        build_apk
        ;;
    "install")
        install_apk
        ;;
    "run")
        run_app
        ;;
    "all")
        if build_apk && install_apk; then
            run_app
        fi
        ;;
    *)
        echo "Uso: $0 [build|install|run|all]"
        echo "  build  - Construir APK"
        echo "  install - Instalar APK en dispositivo"
        echo "  run    - Ejecutar app en dispositivo"
        echo "  all    - Hacer todo (default)"
        ;;
esac