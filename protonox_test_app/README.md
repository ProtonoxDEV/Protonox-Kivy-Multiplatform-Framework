# Protonox App Complete Template

A production-ready Kivy template with Firebase (Auth, Firestore, Storage) and Render (FastAPI) integrations.

## How to run
```bash
python app/main.py
```

## How to package
- Android: `bash ../../tools/build_android.sh`
- Desktop: `bash ../../tools/build_linux.sh` or `bash ../../tools/build_windows.sh`

Update `firebase/firebase_config.py` and `firebase/google-services.json` with your project settings before building.
