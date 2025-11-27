package com.protonox.framework;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import android.util.Log;

import androidx.annotation.Nullable;

/**
 * ProtonoxService
 *
 * Servicio genérico para ser invocado desde Python.
 * De momento solo registra logs y se puede extender más adelante.
 */
public class ProtonoxService extends Service {

    private static final String TAG = "ProtonoxService";

    @Override
    public void onCreate() {
        super.onCreate();
        Log.i(TAG, "ProtonoxService created");
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        String serviceName = "";
        if (intent != null && intent.hasExtra("service_name")) {
            serviceName = intent.getStringExtra("service_name");
        }
        Log.i(TAG, "ProtonoxService started: " + serviceName);
        // NOT STICKY por ahora
        return START_NOT_STICKY;
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        Log.i(TAG, "ProtonoxService destroyed");
    }

    @Nullable
    @Override
    public IBinder onBind(Intent intent) {
        return null; // no binding
    }
}
