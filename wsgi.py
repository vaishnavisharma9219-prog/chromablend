"""WSGI entry point for production servers (gunicorn, etc.)."""
from backend.app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()
