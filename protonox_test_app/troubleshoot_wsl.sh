#!/bin/bash
# Script de troubleshooting para WSL + Android USB

echo "🔧 TROUBLESHOOTING: WSL + Android USB"
echo "====================================="

# Detectar WSL
if [ -n "$WSL_DISTRO_NAME" ]; then
    echo "✅ WSL Detectado: $WSL_DISTRO_NAME"
else
    echo "❌ No se detectó WSL"
    exit 1
fi

echo ""
echo "1️⃣ VERIFICANDO ADB..."
echo "   Linux ADB: $(which adb 2>/dev/null || echo 'NO ENCONTRADO')"
echo "   Windows ADB: $([ -f /mnt/c/Windows/System32/adb.exe ] && echo 'ENCONTRADO' || echo 'NO ENCONTRADO')"

echo ""
echo "2️⃣ ESTADO DEL SERVIDOR ADB..."
adb kill-server 2>/dev/null
sleep 1
adb start-server 2>/dev/null
sleep 2
adb devices

echo ""
echo "3️⃣ DISPOSITIVOS USB DETECTADOS..."
lsusb 2>/dev/null | grep -i android || echo "   No se detectan dispositivos Android"

echo ""
echo "4️⃣ PERMISOS USB..."
if [ -d "/dev/bus/usb" ]; then
    echo "   ✅ Acceso a USB devices disponible"
    ls -la /dev/bus/usb/ | head -3
else
    echo "   ❌ No hay acceso a USB devices"
fi

echo ""
echo "📋 INSTRUCCIONES PARA CONECTAR TU CELULAR:"
echo "=========================================="
echo ""
echo "EN TU CELULAR ANDROID:"
echo "1. Ve a Configuración > Acerca del teléfono"
echo "2. Toca 'Número de compilación' 7 veces hasta ver 'Eres desarrollador'"
echo "3. Ve a Configuración > Opciones de desarrollador"
echo "4. Habilita 'Depuración USB'"
echo "5. Conecta tu celular por USB al computador"
echo ""
echo "EN WINDOWS:"
echo "6. Abre 'Configuración' > 'Dispositivos' > 'Dispositivos Bluetooth y otros'"
echo "7. Busca tu dispositivo Android y selecciona 'Conectar'"
echo ""
echo "EN WSL:"
echo "8. Ejecuta: ./deploy_wsl.sh"
echo ""
echo "Si aún no funciona:"
echo "- Desconecta y reconecta el USB"
echo "- Reinicia el servidor ADB: adb kill-server && adb start-server"
echo "- Verifica que no haya otras apps usando el puerto USB"
echo ""
echo "🔄 Una vez conectado, ejecuta:"
echo "   ./deploy_wsl.sh all    # Construir, instalar y ejecutar"