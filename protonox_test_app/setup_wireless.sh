#!/bin/bash
# Configuración rápida de Wireless ADB

echo "📶 CONFIGURACIÓN WIRELESS ADB"
echo "============================="

echo "PASOS EN TU CELULAR:"
echo "1. Ve a Configuración > Acerca del teléfono"
echo "2. Toca 'Número de compilación' 7 veces (hasta ver 'Eres desarrollador')"
echo "3. Ve a Configuración > Opciones de desarrollador"
echo "4. Habilita 'Depuración inalámbrica'"
echo "5. Toca 'Depuración inalámbrica' para activarla"
echo "6. Anota la IP y puerto que aparezca (ejemplo: 192.168.1.100:12345)"
echo ""

read -p "Ingresa la IP y puerto de tu celular (ej: 192.168.1.100:12345): " DEVICE_IP

if [ -z "$DEVICE_IP" ]; then
    echo "❌ No se proporcionó IP. Intenta nuevamente."
    exit 1
fi

echo ""
echo "🔌 Conectando a $DEVICE_IP..."

# Conectar wireless
adb connect "$DEVICE_IP"

# Verificar conexión
sleep 2
echo ""
echo "📱 Verificando conexión:"
adb devices -l

# Contar dispositivos conectados
CONNECTED_DEVICES=$(adb devices | grep -c "device$")
if [ $CONNECTED_DEVICES -gt 0 ]; then
    echo ""
    echo "✅ ¡CONEXIÓN EXITOSA!"
    echo "🎉 Ahora puedes ejecutar: ./deploy_wsl.sh all"
else
    echo ""
    echo "❌ No se pudo conectar. Verifica:"
    echo "- Que la IP y puerto sean correctos"
    echo "- Que el celular esté en la misma red WiFi"
    echo "- Que la depuración inalámbrica esté activada"
    echo ""
    echo "💡 Intenta nuevamente o usa USB con usbipd"
fi