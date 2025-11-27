# Troubleshooting

## Buildozer fails to download SDK/NDK
- Ensure `JAVA_HOME` and `ANDROID_HOME` are set.
- Run `sdkmanager --list` to confirm installed packages.
- Clear `.buildozer` and retry.

## Firebase authentication issues
- Verify the `firebase/firebase_config.py` values and `google-services.json` placement.
- Confirm the Web API key is enabled for Email/Password sign-in in Firebase Console.
- Check device time synchronization to avoid token validation errors.

## Render backend unreachable
- Validate `API_BASE_URL` in `backend_service.py`.
- Add proper internet permissions in Android manifests via Buildozer.
- Inspect server logs for rate limiting or CORS rejections.

## App crashes on emoji-heavy text
- The Protonox Kivy fork includes emoji patches; ensure you are using the packaged framework and not system Kivy.

## Slow cold starts
- Preload critical services (Firebase auth refresh, theme) during the splash/loading sequence.
- Use the `optimizations.md` guide to prune assets and reduce APK size.
