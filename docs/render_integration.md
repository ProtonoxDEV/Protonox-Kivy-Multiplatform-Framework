# Render (FastAPI) Integration

Use the backend service helper to communicate with a Render-hosted FastAPI instance.

## Configure base URL
Set `API_BASE_URL` in `templates/protonox-app-complete/app/services/backend_service.py` to your deployed backend URL.

## Supported methods
- `get`, `post`, `put`, and `delete` wrap `requests` with retry and logging support.
- Optional bearer tokens can be provided for authenticated endpoints.

## Error handling
- HTTP errors raise descriptive exceptions with response context.
- Network errors trigger retry with exponential backoff (configurable per call).

## Tips
- Enable CORS for your mobile/desktop origins in FastAPI.
- For long-running operations, use background tasks and poll with `get_payment_status` in `payment_service.py`.
