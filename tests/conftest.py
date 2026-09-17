import pytest
import os
import tempfile
import shutil
from pathlib import Path
from backend.app import create_app
from backend.database.db import init_db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test with isolated temp database and upload folder."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test_chroma.db')
    upload_path = os.path.join(temp_dir, 'uploads')
    os.makedirs(upload_path, exist_ok=True)

    test_config = {
        'TESTING': True,
        'DATABASE_PATH': db_path,
        'UPLOAD_FOLDER': upload_path,
        'SECRET_KEY': 'test-secret-key-12345',
        'GEMINI_API_KEY': ''
    }

    app = create_app(test_config)

    with app.app_context():
        init_db(app)

    yield app

    # Cleanup temp directory
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()
