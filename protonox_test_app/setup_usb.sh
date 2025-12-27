#!/bin/bash
# Configuración USB para WSL usando usbipd

echo "🔌 CONFIGURACIÓN USB PARA WSL"
echo "============================="

echo "Este script te ayudará a configurar USB forwarding con usbipd."
echo "Necesitas instalar usbipd en Windows primero."
echo ""

echo "PASO 1 - INSTALAR USBIPD EN WINDOWS:"
echo "===================================="
echo "1. Descarga usbipd-win desde: https://github.com/dorssel/usbipd-win/releases"
echo "2. Instala el MSI como administrador"
echo "3. Reinicia tu terminal WSL"
echo ""

echo "PASO 2 - CONFIGURAR DISPOSITIVO USB:"
echo "===================================="
echo "En PowerShell (como administrador) ejecuta:"
echo ""
echo "   # Listar dispositivos USB"
echo "   usbipd list"
echo ""
echo "   # Busca tu dispositivo Android (por nombre)"
echo "   # Anota el BUSID (ej: 1-2)"
echo ""
echo "   # Bind el dispositivo"
echo "   usbipd bind -b BUSID"
echo ""
echo "   # Attach a WSL"
echo "   usbipd attach -b BUSID -t wsl"
echo ""

echo "PASO 3 - CONFIGURAR WSL:"
echo "========================"
echo "En WSL ejecuta:"
echo ""
echo "   sudo apt update"
echo "   sudo apt install linux-tools-generic hwdata"
echo "   sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*/usbip 20"
echo ""

echo "PASO 4 - VERIFICAR:"
echo "==================="
echo "   adb devices"
echo ""
echo "Si ves tu dispositivo, ejecuta:"
echo "   ./deploy_wsl.sh all"

echo ""
read -p "¿Ya configuraste usbipd en Windows? (s/n): " CONFIGURED

if [ "$CONFIGURED" = "s" ] || [ "$CONFIGURED" = "S" ]; then
    echo ""
    echo "🔍 Verificando configuración WSL..."
    if command -v usbip >/dev/null 2>&1; then
        echo "✅ usbip instalado"
        usbip list -r 127.0.0.1 2>/dev/null && echo "✅ usbip funcionando" || echo "⚠️ usbip necesita configuración"
    else
        echo "❌ usbip no instalado. Ejecuta:"
        echo "   sudo apt install linux-tools-generic hwdata"
    fi

    echo ""
    echo "📱 Verificando dispositivos:"
    adb devices
else
    echo ""
    echo "📖 Lee las instrucciones arriba y vuelve cuando tengas usbipd configurado."
fi