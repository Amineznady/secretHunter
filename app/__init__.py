import os
from flask import Flask
from config import get_config


def create_app(config_name=None):
    """Fabrique pour créer l'application Flask."""
    package_dir = os.path.abspath(os.path.dirname(__file__))
    app_root = os.path.abspath(os.path.dirname(package_dir))
    template_folder = os.path.join(package_dir, 'templates')
    static_folder = os.path.join(app_root, 'static')

    app = Flask(
        __name__,
        template_folder=template_folder,
        static_folder=static_folder,
        static_url_path='/static'
    )
    config = get_config(config_name)
    app.config.from_object(config)

    # Créer les dossiers nécessaires
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

    # Enregistrer les contextes de template
    from datetime import datetime
    @app.context_processor
    def inject_globals():
        return {
            'current_year': datetime.now().year,
            'app_name': 'SecretHunter Pro',
        }

    # Enregistrer le blueprint main
    from app.main import main_bp
    app.register_blueprint(main_bp)

    return app
