#!/usr/bin/env bash
set -euo pipefail

# Configuración principal (API34, NDK28c, Kivy 3 fork, arm64-only)
BUILD_TYPE="${1:-debug}"          # debug | release
SPEC_FILE="${SPEC_FILE:-buildozer_native_bridge.spec}"
PACKAGE_NAME="${PACKAGE_NAME:-dev.protonox.protonoxbridge}"
LOG_FILE="${LOG_FILE:-build_output.log}"
SKIP_DEPLOY="${SKIP_DEPLOY:-0}"    # 1 para solo compilar
SKIP_LOGCAT="${SKIP_LOGCAT:-0}"    # 1 para no abrir logcat
BUILDOZER_BIN="${BUILDOZER_BIN:-}"

# Detectar archivo principal
CANDIDATE_MAIN_FILES=(main.py protonox_native_demo.py protonox_native_bridge_template.py)
MAIN_FILE=""
for f in "${CANDIDATE_MAIN_FILES[@]}"; do
	if [[ -f "$f" ]]; then
		MAIN_FILE="$f"
		break
	fi
done

info() { echo "[INFO] $*"; }
error() { echo "[ERROR] $*" >&2; exit 1; }

# Resolver binario buildozer
if [[ -z "$BUILDOZER_BIN" ]]; then
	if command -v buildozer >/dev/null 2>&1; then
		BUILDOZER_BIN=$(command -v buildozer)
	elif [[ -x "$HOME/.local/bin/buildozer" ]]; then
		BUILDOZER_BIN="$HOME/.local/bin/buildozer"
	fi
fi

[[ -n "$BUILDOZER_BIN" ]] || error "buildozer no está instalado (intenta pip install buildozer)"
if [[ "$SKIP_DEPLOY" != "1" ]]; then
	command -v adb >/dev/null 2>&1 || error "adb no está instalado"
fi
[[ -f "$SPEC_FILE" ]] || error "$SPEC_FILE no existe"
[[ -n "$MAIN_FILE" ]] || error "No se encontró archivo principal (main.py / protonox_native_demo.py / protonox_native_bridge_template.py)"

info "Objetivo: API34, NDK28c, arm64-only, Kivy 3 fork"
info "Especificación: $SPEC_FILE"
info "APK log: $LOG_FILE"
export BUILDOZER_SPECFILE="$SPEC_FILE"

DEVICE_SERIAL=""
if [[ "$SKIP_DEPLOY" != "1" ]]; then
	DEVICE_SERIAL=$(adb devices | awk '/device$/{print $1; exit}')
	[[ -n "$DEVICE_SERIAL" ]] || error "No hay dispositivo ADB conectado"
	info "Dispositivo: $DEVICE_SERIAL"
fi

info "Limpiando log de build anterior"
: > "$LOG_FILE"

info "Construyendo APK ($BUILD_TYPE)"
if [[ "$BUILD_TYPE" == "release" ]]; then
	"$BUILDOZER_BIN" -v android release 2>&1 | tee -a "$LOG_FILE"
else
	"$BUILDOZER_BIN" -v android debug 2>&1 | tee -a "$LOG_FILE"
fi

info "Buscando APK generado"
if [[ "$BUILD_TYPE" == "release" ]]; then
	APK_PATH=$(find bin/ -name "*-release-*.apk" -o -name "*-release.apk" | head -n1)
else
	APK_PATH=$(find bin/ -name "*-debug.apk" | head -n1)
fi
[[ -n "${APK_PATH:-}" ]] || error "No se encontró el APK en bin/"
info "APK: $APK_PATH"

if [[ "$SKIP_DEPLOY" != "1" ]]; then
	info "Desinstalando versión previa (si existe)"
	adb -s "$DEVICE_SERIAL" uninstall "$PACKAGE_NAME" >/dev/null 2>&1 || true

	info "Instalando APK en dispositivo"
	adb -s "$DEVICE_SERIAL" install -r "$APK_PATH"

	info "Lanzando app"
	adb -s "$DEVICE_SERIAL" shell am start -n "$PACKAGE_NAME/org.kivy.android.PythonActivity"

	if [[ "$SKIP_LOGCAT" != "1" ]]; then
		info "Logcat en vivo (Ctrl+C para salir)"
		adb -s "$DEVICE_SERIAL" logcat -c || true
		adb -s "$DEVICE_SERIAL" logcat | grep -i -E "python|kivy|protonox|error|exception"
	fi
fi

info "Listo"
