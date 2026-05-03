import os


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "loja.db"))
SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
DEBUG = _as_bool(os.environ.get("FLASK_DEBUG"), default=False)
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "5000"))
