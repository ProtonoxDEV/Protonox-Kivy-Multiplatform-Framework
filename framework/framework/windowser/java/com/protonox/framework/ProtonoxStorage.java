package com.protonox.framework;

import android.app.Activity;
import android.content.Context;
import android.os.Environment;
import android.util.Log;

import java.io.File;

/**
 * ProtonoxStorage
 *
 * Funciones de ayuda para rutas de almacenamiento.
 */
public class ProtonoxStorage {

    private static final String TAG = "ProtonoxStorage";

    public static String getAppStorageDir(Activity activity) {
        if (activity == null) return "";
        Context ctx = activity.getApplicationContext();
        File filesDir = ctx.getFilesDir();
        File protonoxDir = new File(filesDir, "protonox");
        if (!protonoxDir.exists()) {
            boolean created = protonoxDir.mkdirs();
            Log.i(TAG, "Creating app storage dir: " + created);
        }
        return protonoxDir.getAbsolutePath();
    }

    public static String getExternalStorageDir() {
        if (!Environment.MEDIA_MOUNTED.equals(Environment.getExternalStorageState())) {
            return "";
        }
        File ext = Environment.getExternalStorageDirectory();
        File protonoxDir = new File(ext, "Protonox");
        if (!protonoxDir.exists()) {
            boolean created = protonoxDir.mkdirs();
            Log.i(TAG, "Creating external storage dir: " + created);
        }
        return protonoxDir.getAbsolutePath();
    }
}
