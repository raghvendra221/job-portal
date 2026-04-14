# Celery is not used in this project.
# Background tasks run via Python threading (see account/tasks.py).
# This file is kept as a no-op so existing imports don't break.

class _FakeCeleryApp:
    """Stub so `from jobportal.celery import app` still works."""
    pass

app = _FakeCeleryApp()
