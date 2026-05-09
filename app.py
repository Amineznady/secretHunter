"""Point d'entrée de l'application SecretHunter Pro."""
import os
from app import create_app

# Créer l'application
app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG'],
        use_reloader=False
    )
