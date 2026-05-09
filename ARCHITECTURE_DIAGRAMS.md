# 🏗️ SecretHunter Pro - Architecture Diagrams

**Project**: SecretHunter Pro v2.1 | **Status**: Production Ready

---

## 📊 Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      SECRETHUNTER PRO                           │
│                   Enterprise Flask Application                   │
└─────────────────────────────────────────────────────────────────┘

                            ┌──────────────┐
                            │   app.py     │  ← Entry Point
                            └──────┬───────┘
                                   │
                    ┌──────────────▼─────────────┐
                    │ from app import create_app │
                    └──────────────┬─────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   app/__init__.py           │
                    │  (Application Factory)      │
                    └──────────┬───────┬──────────┘
                               │       │
                ┌──────────────▼─┐  ┌─▼─────────────┐
                │  config.py     │  │  app/main.py  │
                │ (Config        │  │  (Routes)     │
                │  Classes)      │  │  Blueprint    │
                └────────────────┘  └─┬────────┬────┘
                                      │        │
                         ┌────────────▼┐  ┌───▼──────────┐
                         │secrethunter │  │ app/utils.py │
                         │.py          │  │(Utilities)   │
                         │(Scanner)    │  └──────────────┘
                         └─────────────┘

                      ┌─────────────────────────┐
                      │  HTML Templates         │
                      ├─────────────────────────┤
                      │ • base.html (inherited) │
                      │ • index.html (form)     │
                      │ • result.html (display) │
                      └─────────────────────────┘

                      ┌─────────────────────────┐
                      │  Static Files           │
                      ├─────────────────────────┤
                      │ • styles.css (Bootstrap)│
                      └─────────────────────────┘
```

---

## 🔄 Request-Response Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                ┌──────────────▼──────────────┐
                │   GET /                     │
                │   (Homepage Request)        │
                └──────────────┬───────────────┘
                               │
                ┌──────────────▼───────────────────────┐
                │   app/main.py → index() route        │
                │   Returns: templates/index.html      │
                └──────────────┬────────────────────────┘
                               │
                ┌──────────────▼──────────────────┐
                │   Browser displays             │
                │   • Upload form                │
                │   • Mode selector              │
                │   • Drag & drop zone           │
                └──────────────┬─────────────────┘
                               │
                ┌──────────────▼──────────────────┐
                │   User selects APK + mode      │
                │   Clicks "Lancer l'analyse"    │
                └──────────────┬─────────────────┘
                               │
                ┌──────────────▼──────────────────────┐
                │   POST /scan                        │
                │   (Form submission)                 │
                └──────────────┬──────────────────────┘
                               │
        ┌──────────────────────▼──────────────────────┐
        │         app/main.py → scan_apk()            │
        │                                             │
        │  1. Validate file (app/utils.allowed_file) │
        │  2. Save to uploads/                        │
        │  3. Decompile APK (secrethunter.py)        │
        │  4. Scan for secrets (secrethunter.py)     │
        │  5. Build report (app/utils)               │
        │  6. Calculate stats (app/utils)            │
        │  7. Save report to results/                │
        │  8. Render result.html                     │
        └──────────────┬───────────────────────────────┘
                       │
        ┌──────────────▼─────────────────┐
        │   results/report_XXXX.txt      │
        │   (Report generated)           │
        └──────────────┬─────────────────┘
                       │
        ┌──────────────▼─────────────────────────┐
        │   Browser displays result.html         │
        │   • Stats cards                        │
        │   • Results table                      │
        │   • Download link                      │
        └──────────────┬────────────────────────┘
                       │
        ┌──────────────▼──────────────────────┐
        │   GET /download/<filename>          │
        │   (User clicks download)            │
        └──────────────┬──────────────────────┘
                       │
        ┌──────────────▼──────────────────────┐
        │   app/main.py → download_file()     │
        │   Returns: file from results/       │
        └──────────────┬──────────────────────┘
                       │
        ┌──────────────▼──────────────────────┐
        │   Browser downloads report.txt      │
        │   Scan complete!                    │
        └──────────────────────────────────────┘
```

---

## 📁 File System Layout

```
SecretHunter/
│
├── Entry Point
│   └── app.py ........................ Starts Flask app
│
├── Configuration
│   ├── config.py ..................... Config classes
│   └── .env.example .................. Environment template
│
├── Application Package
│   └── app/
│       ├── __init__.py ............... App factory
│       ├── main.py ................... Routes blueprint
│       └── utils.py .................. Utility functions
│
├── Templates (Jinja2)
│   └── templates/
│       ├── base.html ................. Base template
│       ├── index.html ................ Upload form
│       └── result.html ............... Results display
│
├── Static Assets
│   └── static/
│       └── styles.css ................ CSS styles
│
├── Scanner Engine
│   └── secrethunter.py ............... Security scanner
│
├── Data Directories (Runtime)
│   ├── uploads/ ...................... Temporary APK storage
│   └── results/ ...................... Generated reports
│
├── Documentation
│   ├── README.md ..................... User guide
│   ├── STRUCTURE.md .................. Architecture
│   ├── COMPLETION.md ................. Detailed summary
│   ├── PROJECT_SUMMARY.md ............ Quick overview
│   ├── VERIFICATION_CHECKLIST.md .... Verification
│   └── Architecture/Diagrams.md ..... This file
│
├── Project Configuration
│   ├── requirements.txt .............. Dependencies
│   ├── .gitignore .................... Git ignore rules
│   └── __pycache__/ .................. Python cache
│
└── Legacy (From Previous Work)
    ├── versions_archive/ ............. Old versions
    ├── vulnerable_app/ ............... Test data
    ├── reports/ ....................... Old reports
    └── output/ ........................ Old outputs
```

---

## 🔗 Module Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                       IMPORT GRAPH                          │
└─────────────────────────────────────────────────────────────┘

                          ┌──────────┐
                          │  app.py  │
                          └─────┬────┘
                                │
                   ┌────────────▼────────────┐
                   │  app/__init__.py        │
                   │  from app import       │
                   │  - create_app()        │
                   └────┬─────────────┬─────┘
                        │             │
         ┌──────────────▼──┐  ┌──────▼──────────────┐
         │   config.py     │  │   app/main.py       │
         │   from config   │  │   from secrethunter │
         │   - get_config()│  │   - decompile_apk() │
         │                 │  │   - scan_directory()│
         └─────────────────┘  │   from app.utils    │
                              │   - allowed_file()  │
                              │   - build_text_...()│
                              │   - get_scan_...()  │
                              │   - safe_download..()
                              └──────┬──────────────┘
                                     │
                    ┌────────────────▼───────────────┐
                    │     app/utils.py               │
                    │     Utility functions:         │
                    │     - allowed_file()           │
                    │     - build_text_result()      │
                    │     - get_scan_statistics()    │
                    │     - safe_download_filename() │
                    └────────────────────────────────┘

                    ┌──────────────────────────────┐
                    │    secrethunter.py           │
                    │    Scanner functions:        │
                    │    - decompile_apk()        │
                    │    - scan_directory()       │
                    │    - scan_file()            │
                    │    - get_severity()         │
                    │    - get_risk_score()       │
                    └──────────────────────────────┘

                    ┌──────────────────────────────┐
                    │    External Dependencies:    │
                    │    - Flask                  │
                    │    - werkzeug.security      │
                    │    - datetime               │
                    └──────────────────────────────┘
```

---

## 🔀 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        DATA FLOW                             │
└──────────────────────────────────────────────────────────────┘

USER BROWSER
    │
    ├─→ GET / ──────────────────→ app/main.py → index()
    │                                │
    │                                ├─→ render index.html
    │                                │
    │←──────────────────────────────┘
    │
    ├─→ POST /scan
    │   (with APK file + mode)      
    │                                
    │                                ↓
    │                          app/main.py → scan_apk()
    │                                │
    │                    ┌───────────┼────────────┐
    │                    │           │            │
    │                    ▼           ▼            ▼
    │          File Validation  Save File   Load Config
    │          (app/utils)       (uploads/)  (config.py)
    │                    │           │            │
    │                    └───────────┼────────────┘
    │                                │
    │                                ▼
    │                      Decompile APK
    │                   (secrethunter.py)
    │                     (java -jar)
    │                                │
    │                                ▼
    │                      Scan for Secrets
    │                   (secrethunter.py)
    │                   (20+ patterns)
    │                                │
    │                                ▼
    │                    Build Report
    │                 (app/utils.py)
    │                                │
    │                                ▼
    │                   Calculate Statistics
    │                 (app/utils.py)
    │                                │
    │                                ▼
    │                    Save Report File
    │                   (results/ folder)
    │                                │
    │                                ▼
    │                   Render result.html
    │                                │
    │←───────────────────────────────┘
    │
    └─→ GET /download/<filename>
                                     │
                                     ▼
                              app/main.py →
                            download_file()
                                     │
                                     ▼
                           Read from results/
                                     │
                                     ▼
                           Send to browser
                                     │
                                     ▼
                           Downloaded to disk
```

---

## 🔐 Security Layers

```
┌────────────────────────────────────────────────────┐
│              SECURITY ARCHITECTURE                 │
└────────────────────────────────────────────────────┘

Layer 1: Input Validation
├─ File extension check (.apk only)
├─ Filename sanitization (secure_filename)
└─ File size limit (150 MB max)
        │
        ▼
Layer 2: File Handling
├─ Secure temporary folder (uploads/)
├─ No path traversal (basename + secure_filename)
└─ Automatic cleanup after processing
        │
        ▼
Layer 3: Configuration Security
├─ Sensitive data in .env (not committed)
├─ Environment-specific configs (dev/prod/test)
└─ No hardcoded secrets in code
        │
        ▼
Layer 4: Template Security
├─ Jinja2 auto-escaping enabled
├─ Proper URL encoding (url_for)
└─ CSRF token support ready
        │
        ▼
Layer 5: Error Handling
├─ Graceful error messages
├─ No sensitive info in errors
└─ Flash messages for user feedback
        │
        ▼
SECURE APPLICATION
```

---

## 🚀 Deployment Architecture

```
┌──────────────────────────────────────────────────────┐
│          PRODUCTION DEPLOYMENT ARCHITECTURE          │
└──────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  CLIENT BROWSER                                    │
│  http://example.com:443 (HTTPS)                   │
└──────────────┬─────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────┐
│  REVERSE PROXY (Nginx/Apache)                     │
│  • Port 443 (HTTPS)                               │
│  • Rate limiting                                  │
│  • Load balancing                                 │
│  • Static file serving                            │
└──────────────┬─────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────┐
│  WSGI APPLICATION SERVER (Gunicorn)               │
│  • Port 5000 (internal)                           │
│  • Multiple worker processes                      │
│  • Process management                             │
└──────────────┬─────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────┐
│  FLASK APPLICATION                                │
│  SecretHunter Pro v2.1                            │
│  • Factory pattern initialization                 │
│  • Environment-specific config                    │
│  • Blueprint routing                              │
└──────────────┬─────────────────────────────────────┘
               │
┌──────────────▼─────────────────────────────────────┐
│  DATA & STORAGE                                   │
│  • /uploads → Temporary APK files                 │
│  • /results → Generated reports                   │
│  • .env → Configuration & secrets                 │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Configuration Hierarchy

```
┌────────────────────────────────────────────────┐
│     CONFIGURATION MANAGEMENT SYSTEM            │
└────────────────────────────────────────────────┘

Environment Variable: FLASK_ENV
        │
        ├─→ "development"
        │        │
        │        ├─→ DEBUG = True
        │        ├─→ TESTING = False
        │        ├─→ Auto-reload: ON
        │        ├─→ Error details: FULL
        │        └─→ config.py:DevelopmentConfig
        │
        ├─→ "production"
        │        │
        │        ├─→ DEBUG = False
        │        ├─→ TESTING = False
        │        ├─→ Auto-reload: OFF
        │        ├─→ Error details: MINIMAL
        │        └─→ config.py:ProductionConfig
        │
        └─→ "testing"
                 │
                 ├─→ DEBUG = False
                 ├─→ TESTING = True
                 ├─→ Test folders: test_uploads/
                 ├─→ Error details: FULL
                 └─→ config.py:TestingConfig

All configs inherit from base Config:
├─ BASE_DIR
├─ UPLOAD_FOLDER
├─ RESULTS_FOLDER
├─ ALLOWED_EXTENSIONS = {apk}
└─ MAX_CONTENT_LENGTH = 150 MB
```

---

## 📊 URL Routing Map

```
┌─────────────────────────────────────────────┐
│            URL ROUTING MAP                  │
└─────────────────────────────────────────────┘

GET /
│
├─→ app/main.py → index()
├─→ Template: templates/index.html
├─→ Status Code: 200 OK
└─→ Content-Type: text/html

POST /scan
│
├─→ app/main.py → scan_apk()
├─→ Input: form-data with apk_file + mode
├─→ Processing: 30-60 seconds
├─→ Output: HTML (result.html)
├─→ Status Code: 200 OK
└─→ Content-Type: text/html

GET /download/<filename>
│
├─→ app/main.py → download_file()
├─→ Parameter: filename (sanitized)
├─→ Location: results/<filename>
├─→ Status Code: 200 OK
└─→ Content-Type: text/plain
```

---

## 🎯 Module Responsibilities

```
┌────────────────────────────────────────────────────┐
│           MODULE RESPONSIBILITY MAP               │
└────────────────────────────────────────────────────┘

config.py
├─ Define Config classes
├─ Manage environment-specific settings
└─ Select appropriate config via get_config()

app/__init__.py (App Factory)
├─ Create Flask instance
├─ Load configuration
├─ Initialize folders
├─ Register blueprints
└─ Return configured app

app/main.py (Routes Blueprint)
├─ Handle GET / (homepage)
├─ Handle POST /scan (analysis)
├─ Handle GET /download (file delivery)
├─ Coordinate workflow
└─ Error handling

app/utils.py (Utilities)
├─ Validate file uploads
├─ Generate text reports
├─ Calculate statistics
└─ Sanitize filenames

secrethunter.py (Scanner Engine)
├─ Decompile APK files
├─ Scan for security patterns
├─ Assign severity levels
└─ Calculate risk scores

templates/*.html (Presentation)
├─ base.html: Layout & navigation
├─ index.html: Upload form
└─ result.html: Results display

static/styles.css (Styling)
└─ Bootstrap 5 customization
```

---

## 📈 Performance Architecture

```
┌──────────────────────────────────────────┐
│        PERFORMANCE OPTIMIZATION          │
└──────────────────────────────────────────┘

Request Processing Timeline:
│
├─ HTTP Request ...................... T+0ms
├─ Route matching .................... T+1ms
├─ File validation ................... T+5ms
├─ File save to disk ................. T+10ms
├─ APK decompilation ................ T+15-30s
├─ Secret scanning .................. T+30-45s
├─ Report generation ................ T+45s
├─ Statistics calculation ........... T+46s
├─ Template rendering ............... T+50s
├─ HTTP Response .................... T+51s

Bottleneck: APK Decompilation (30-45s)
Solution: Async processing (future enhancement)

Current Architecture:
├─ Synchronous processing
├─ Single request per APK
├─ 120-second timeout
└─ Suitable for small teams
```

---

## 🔄 Version Control Structure

```
Git Repository Structure:
│
├── .gitignore (Enhanced)
│   ├─ .env (Secrets)
│   ├─ __pycache__/ (Cache)
│   ├─ uploads/ (Runtime data)
│   ├─ results/ (Generated files)
│   └─ *.log (Logs)
│
├── Tracked Files
│   ├─ app.py
│   ├─ config.py
│   ├─ secrethunter.py
│   ├─ requirements.txt
│   ├─ app/*.py
│   ├─ templates/*.html
│   ├─ static/styles.css
│   └─ README.md, STRUCTURE.md, etc.
│
└── Not Tracked
    ├─ .env (Configuration)
    ├─ uploads/* (Temporary)
    ├─ results/* (Generated)
    └─ __pycache__/ (Cache)
```

---

**Architecture Documentation Complete** ✅

All diagrams and architecture decisions documented.
Ready for team review and implementation.

---

Generated: May 6, 2026
Project: SecretHunter Pro v2.1
Status: Production Ready ✅
