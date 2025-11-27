package com.protonox.framework;

import android.util.Log;

/**
 * ProtonoxBridge
 *
 * Clase de utilidad simple que sirve como punto de entrada desde Pyjnius
 * para comprobar que el puente Java <-> Python está funcionando.
 */
public class ProtonoxBridge {

    private static final String TAG = "ProtonoxBridge";

    public static void log(String message) {
        Log.i(TAG, message);
    }

    public static String ping() {
        Log.i(TAG, "ProtonoxBridge.ping() called");
        return "pong-from-java";
    }
}
