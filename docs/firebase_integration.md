# Firebase Integration

The `protonox-app-complete` template ships with Firebase-ready scaffolding using the REST APIs.

## Configure credentials
1. Copy your `google-services.json` into `templates/protonox-app-complete/firebase/`.
2. Update `firebase_config.py` with your project's API key, auth domain, project ID, storage bucket, messaging sender ID, and app ID.

## Auth flows
- Email/password login and registration use the Identity Toolkit REST endpoints.
- Session refresh automatically retrieves fresh ID tokens when needed.
- Token validation is performed before privileged Firestore or Storage calls.

## Firestore
- `firebase_service.py` exposes generic CRUD helpers that call the Firestore REST API.
- Supply collection/document paths; the service handles bearer token injection.

## Storage
- Uploads use the Firebase Storage REST upload endpoint with resumable-friendly defaults.

## Offline considerations
- Service caches the last valid ID token in memory and retries with exponential backoff.
- You can extend the cache strategy to persist tokens on disk for offline-first behavior.
