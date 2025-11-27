package com.protonox.framework;

import android.app.Activity;
import android.content.pm.PackageManager;
import android.util.Log;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

/**
 * ProtonoxPermissions
 *
 * Utilidades para trabajar con permisos desde Pyjnius.
 */
public class ProtonoxPermissions {

    private static final String TAG = "ProtonoxPermissions";

    public static boolean hasPermission(Activity activity, String permission) {
        if (activity == null) return false;
        int result = ContextCompat.checkSelfPermission(activity, permission);
        return result == PackageManager.PERMISSION_GRANTED;
    }

    public static void requestPermissions(Activity activity, String[] permissions, int requestCode) {
        if (activity == null) {
            Log.w(TAG, "requestPermissions: activity is null");
            return;
        }
        ActivityCompat.requestPermissions(activity, permissions, requestCode);
    }
}
