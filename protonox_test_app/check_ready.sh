#!/bin/bash
# Verificación rápida antes del deployment

echo "⚡ VERIFICACIÓN RÁPIDA - Protonox App Deployment"
echo "==============================================="

# Verificar dispositivo
echo "📱 Dispositivos conectados:"
adb devices -l

# Contar dispositivos
DEVICE_COUNT=$(adb devices | grep -c "device$")
if [ $DEVICE_COUNT -gt 0 ]; then
    echo "✅ $DEVICE_COUNT dispositivo(s) conectado(s) - ¡LISTO!"
    echo ""
    echo "🚀 EJECUTAR DEPLOYMENT:"
    echo "./deploy_wsl.sh all"
else
    echo "❌ No hay dispositivos conectados"
    echo ""
    echo "🔧 VERIFICA:"
    echo "- ¿Celular conectado por USB?"
    echo "- ¿Depuración USB habilitada?"
    echo "- ¿Aceptaste el diálogo en el celular?"
    echo ""
    echo "📶 O usa wireless:"
    echo "adb connect TU_IP:TU_PUERTO"
fi