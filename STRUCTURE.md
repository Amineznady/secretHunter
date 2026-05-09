# 📂 Structure du projet SecretHunter Pro

```
SecretHunter/
│
├── 📄 app.py                          # Point d'entrée principal
├── 📄 config.py                       # Configuration de l'application
├── 📄 secrethunter.py                 # Moteur de scan des secrets
├── 📄 requirements.txt                # Dépendances Python
├── 📄 README.md                       # Documentation (ce fichier)
├── 📄 STRUCTURE.md                    # Cette documentation
├── 📄 .gitignore                      # Fichiers à ignorer
├── 📄 .env.example                    # Variables d'environnement (exemple)
│
├── 📁 app/                            # Package Flask principal
│   ├── __init__.py                    # Fabrique create_app() et configuration Flask
│   ├── main.py                        # Routes principales (/scan, /download, etc.)
│   └── utils.py                       # Fonctions utilitaires (build_text_result, etc.)
│
├── 📁 templates/                      # Templates HTML (Jinja2)
│   ├── base.html                      # Template de base (header, footer, structure)
│   ├── index.html                     # Page d'upload APK et configuration
│   └── result.html                    # Page des résultats détaillés
│
├── 📁 static/                         # Ressources statiques
│   └── styles.css                     # CSS personnalisé et thème
│
├── 📁 uploads/                        # 📂 Dossier des APK uploadés (automatique)
├── 📁 results/                        # 📂 Dossier des rapports générés (automatique)
│
├── 📁 vulnerable_app/                 # Exemple d'application Android vulnérable (test)
├── 📁 output/                         # Rapports générés antérieurement
└── 📁 versions_archive/               # Anciennes versions du projet
```

## 📋 Description des fichiers

### Fichiers de configuration

| Fichier | Rôle |
|---------|------|
| `config.py` | Classes de configuration (Development, Production, Testing) |
| `.env.example` | Modèle de variables d'environnement |
| `requirements.txt` | Liste des dépendances Python |

### Application Flask

| Fichier | Rôle |
|---------|------|
| `app.py` | Point d'entrée principal - crée et démarre l'app |
| `app/__init__.py` | Fabrique d'application et configuration Flask |
| `app/main.py` | Blueprints avec les routes principales |
| `app/utils.py` | Fonctions utilitaires réutilisables |

### Frontend

| Fichier | Rôle |
|---------|------|
| `templates/base.html` | Template parente (héritage HTML) |
| `templates/index.html` | Page d'accueil avec formulaire d'upload |
| `templates/result.html` | Affichage des résultats du scan |
| `static/styles.css` | Styles CSS personnalisés |

### Dossiers de données

| Dossier | Contenu |
|---------|---------|
| `uploads/` | APK envoyés par les utilisateurs (nettoyé après scan) |
| `results/` | Rapports textes générés (accessible au téléchargement) |
| `vulnerable_app/` | Exemple d'application avec secrets pour les tests |

## 🔄 Flux de données

```
1. Utilisateur accède à /
       ↓
2. Frontend: index.html
       ↓
3. Utilisateur upload APK + choisit mode
       ↓
4. POST /scan
       ↓
5. app/main.py:scan_apk()
       ↓
6. Sauvegarde dans uploads/
       ↓
7. decompile_apk() (apktool)
       ↓
8. scan_directory() (secrethunter.py)
       ↓
9. build_text_result() (app/utils.py)
       ↓
10. Rapport généré dans results/
       ↓
11. render_template('result.html')
       ↓
12. Affichage des résultats + download possible
```

## 🔧 Comment ajouter une nouvelle route

1. Créer la fonction dans `app/main.py`
2. Ajouter le décorateur `@main_bp.route()`
3. Créer un template si nécessaire
4. Ajouter le CSS si besoin

Exemple:
```python
@main_bp.route('/stats')
def statistics():
    # Récupérer les stats
    return render_template('stats.html')
```

## 📦 Dépendances et leurs rôles

| Package | Version | Rôle |
|---------|---------|------|
| Flask | >=3.0.0 | Framework web |
| reportlab | >=4.0.0 | Génération PDF |
| Pillow | >=9.0.0 | Traitement d'images |
| Werkzeug | >=3.0.0 | Utilitaires web (secure_filename, etc.) |
| python-dotenv | >=1.0.0 | Gestion des variables d'env (.env) |

## 🔐 Fichiers à ignorer (.gitignore)

```
.env                 # Ne pas commiter les secrets
__pycache__/         # Cache Python
*.pyc                # Bytecode compilé
.DS_Store            # Fichiers système macOS
uploads/             # APK uploadés
results/             # Rapports générés
.venv/               # Environnement virtuel
```

## 🚀 Lancement

### Développement
```bash
python app.py
# Accès: http://127.0.0.1:5000
```

### Production
```bash
FLASK_ENV=production python app.py
```

### Test
```bash
FLASK_ENV=testing python -m pytest
```

## 📊 Modèle de données

### Structure d'un finding

```python
{
    'file': str,        # Chemin du fichier
    'line': int,        # Numéro de ligne
    'type': str,        # Type de secret (ex: "Stripe Secret Key")
    'value': str,       # Valeur détectée
    'context': str,     # Contexte (ligne complète)
    'severity': str,    # CRITICAL, HIGH, MEDIUM, LOW
    'risk_score': int,  # 0-100
    'mode': str,        # STRICT ou VULNERABLE
}
```

### Structure de statistiques

```python
{
    'total': int,      # Total findings
    'critical': int,   # Nombre CRITICAL
    'high': int,       # Nombre HIGH
    'medium': int,     # Nombre MEDIUM
    'low': int,        # Nombre LOW
}
```

## 🔄 Intégration continue (CI/CD)

Structure recommandée pour une CI/CD:

```yaml
test:
  - Linter (flake8)
  - Vérifier syntax
  - Tests unitaires
build:
  - pip install -r requirements.txt
deploy:
  - FLASK_ENV=production
  - Gunicorn ou autre WSGI
```

## 📖 Documentation additionnelle

- `README.md` - Vue d'ensemble et guide d'utilisation
- `secrethunter.py` - Documentation du moteur de scan
- `config.py` - Configuration disponible
- Code Python - Commentaires détaillés dans les fonctions

---

**Dernière mise à jour:** 6 mai 2026
