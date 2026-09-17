from pathlib import Path
from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS

from backend.config import Config
from backend.database.db import close_db, init_db
from backend.utils.responses import error_response

# Import Blueprints
from backend.routes.auth import auth_bp
from backend.routes.tasks import tasks_bp
from backend.routes.notes import notes_bp
from backend.routes.planner import planner_bp
from backend.routes.private_access import private_bp
from backend.routes.safety import safety_bp
from backend.routes.documents import documents_bp
from backend.routes.contacts import contacts_bp
from backend.routes.emergency import emergency_bp

def create_app(test_config=None):
    """Application factory for Chroma Blend."""
    app = Flask(
        __name__,
        static_folder=None # We will handle frontend static files explicitly
    )
    
    # Load configuration
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    # Enable CORS with credentials
    CORS(app, supports_credentials=True)

    # Database connection teardown
    app.teardown_appcontext(close_db)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(notes_bp)
    app.register_blueprint(planner_bp)
    app.register_blueprint(private_bp)
    app.register_blueprint(safety_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(emergency_bp)

    # Resolve frontend path
    frontend_dir = (Path(__file__).resolve().parent.parent / 'frontend').resolve()

    # Serve static assets
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(frontend_dir / 'css', filename)

    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(frontend_dir / 'js', filename)

    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(frontend_dir / 'assets', filename)

    # Serve HTML views
    @app.route('/')
    def index():
        return send_from_directory(frontend_dir, 'index.html')

    @app.route('/login')
    @app.route('/login.html')
    def login_page():
        return send_from_directory(frontend_dir, 'login.html')

    @app.route('/register')
    @app.route('/register.html')
    def register_page():
        return send_from_directory(frontend_dir, 'register.html')

    @app.route('/planner')
    @app.route('/planner.html')
    def planner_page():
        return send_from_directory(frontend_dir, 'planner.html')

    @app.route('/private')
    @app.route('/private.html')
    def private_page():
        return send_from_directory(frontend_dir, 'private.html')

    # Global error handling
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return error_response("The requested API resource was not found.", 404)
        return send_from_directory(frontend_dir, 'index.html')

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return error_response("Uploaded file exceeds the maximum allowed size (16 MB).", 413)

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f"Internal server error: {e}")
        return error_response("An internal server error occurred. Please try again later.", 500)

    # Initialize database automatically on startup if it doesn't exist
    with app.app_context():
        init_db(app)

    return app

if __name__ == '__main__':
    application = create_app()
    port = application.config.get('PORT', 5000)
    debug = application.config.get('DEBUG', True)
    print(f" * Chroma Blend running at http://127.0.0.1:{port}/")
    application.run(host='0.0.0.0', port=port, debug=debug)
