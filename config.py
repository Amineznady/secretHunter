import os
from datetime import datetime


class Config:
    """Configuration générale de l'application."""
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    RESULTS_FOLDER = os.path.join(BASE_DIR, 'results')
    ALLOWED_EXTENSIONS = {'apk'}
    MAX_CONTENT_LENGTH = 150 * 1024 * 1024  # 150 MB


class DevelopmentConfig(Config):
    """Configuration en développement."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuration en production."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    UPLOAD_FOLDER = os.path.join(Config.BASE_DIR, 'test_uploads')
    RESULTS_FOLDER = os.path.join(Config.BASE_DIR, 'test_results')


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}


def get_config(name=None):
    """Retourne la configuration appropriée."""
    if not name:
        name = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(name, DevelopmentConfig)
