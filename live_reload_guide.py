#!/usr/bin/env python3
"""
Protonox Live Reload - Pair Nativo Android + WebSocket
Instrucciones completas para usar live reload en tu celular.
"""

print("🚀 Protonox Live Reload - Guía Completa")
print("=" * 60)

print("\n📱 PASO 1: Conectar tu celular")
print("-" * 30)
print("1. Conecta tu celular por USB al PC")
print("2. Habilita 'Depuración USB' en Ajustes > Opciones de desarrollador")
print("3. Asegúrate de que esté conectado a la misma WiFi que tu PC")

print("\n🔧 PASO 2: Ejecutar el servidor")
print("-" * 30)
print("Ejecuta este comando en la terminal:")
print("source venv_protonox_studio/bin/activate && python simple_wireless_server.py")

print("\n📊 Qué hace el servidor:")
print("• Busca dispositivos Android conectados por USB")
print("• Habilita ADB wireless automáticamente")
print("• Conecta tu celular por WiFi (sin cables)")
print("• Inicia servidor WebSocket para live reload")
print("• Muestra QR code para conexión fácil")

print("\n📱 PASO 3: Conectar desde tu celular")
print("-" * 30)
print("1. Escanea el QR code que aparece en la terminal")
print("2. O usa una app WebSocket como 'WebSocket King'")
print("3. Conecta a: ws://[IP_PC]:8765")

print("\n🔄 PASO 4: Probar live reload")
print("-" * 30)
print("1. Modifica ejemplos/wireless_debug_example.py")
print("2. Los cambios se verán automáticamente en tu celular")
print("3. ¡Sin necesidad de recompilar!")

print("\n🛠️  HERRAMIENTAS NECESARIAS:")
print("-" * 30)
print("• Android SDK Platform Tools (para ADB)")
print("• App WebSocket en tu celular (WebSocket King, etc.)")
print("• Celular y PC en la misma red WiFi")

print("\n💡 TIPS:")
print("-" * 30)
print("• Si no tienes ADB: solo usa websocket_server.py")
print("• Si no tienes celular físico: usa un emulador Android")
print("• Para debugging avanzado: revisa los logs en la terminal")

print("\n🎯 RESULTADO:")
print("-" * 30)
print("✅ Desarrollo móvil ultra-rápido")
print("✅ Cambios instantáneos en tu celular")
print("✅ Sin cables después de la configuración inicial")
print("✅ Compatible con Android 16")

print("\n🚀 ¡Listo para el futuro del desarrollo móvil!")
print("=" * 60)