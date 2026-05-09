#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecretHunter - Android Security Scanner v2.1 PRO
Scans Android projects or APKs for sensitive information like API keys, tokens, emails, URLs, and hardcoded passwords.
"""

import os
import re
import argparse
import subprocess
import tempfile
import sys
import io
import shutil
from datetime import datetime
from collections import Counter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch
from flask import Flask, render_template_string, request, jsonify, send_file
from werkzeug.utils import secure_filename
import json

# Fix Unicode output on Windows
if sys.platform == 'win32':
    # Reconfigure stdout with UTF-8 encoding
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ============================================
# 🔥 PATTERNS PRO - VERSION 3.0 (Améliorée)
# ============================================

PATTERNS_STRICT = {
    # � Stripe & Payment Keys (CRITIQUES)
    'Stripe Secret Key': r'sk_live_[0-9a-zA-Z]{24}',
    'Stripe Test Key': r'sk_test_[0-9a-zA-Z]{24}',
    'Stripe Publishable Key': r'pk_(?:live|test)_[0-9a-zA-Z]{24}',
    
    # 🐙 GitHub & Git Tokens (CRITIQUES)
    'GitHub Token': r'ghp_[A-Za-z0-9]{36}',
    'GitLab Token': r'glpat-[A-Za-z0-9_-]{20,}',
    
    # 🔐 JWT & Bearer Tokens
    'JWT Token': r'eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+',
    'Bearer Token': r'Bearer\s+[A-Za-z0-9\-._~+/]+=*',
    'OAuth Token': r'ya29\.[0-9A-Za-z\-_]+',
    
    # 💬 Slack Tokens
    'Slack Bot Token': r'xoxb-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24}',
    'Slack User Token': r'xoxp-[0-9]{10,13}-[0-9]{10,13}-[A-Za-z0-9]{24}',
    
    # 🔑 AWS Keys
    'AWS Access Key': r'AKIA[0-9A-Z]{16}',
    'AWS Secret Key': r'(?i)aws_secret_access_key\s*[:=]\s*["\']?([A-Za-z0-9/+=]{40})["\']?',
    
    # 🔑 Private Keys (CRITIQUE)
    'Private Key': r'-----BEGIN (RSA|EC|DSA|OPENSSH) PRIVATE KEY-----',
    'SSH Public Key': r'ssh-(?:rsa|dss|ed25519)\s+[A-Za-z0-9+/=]+',
    
    # 🔒 Firebase (Google ONLY)
    'Firebase URL': r'https://[a-z0-9-]+\.firebaseio\.com',
}

# Mode VULNERABLE - Comprehensive detection
PATTERNS_VULNERABLE = {
    **PATTERNS_STRICT,
    
    # 🔑 API Keys génériques (medium confidence)
    'Google API Key': r'AIza[0-9A-Za-z\-_]{35}',
    'Firebase API Key': r'AIzaSy[A-Za-z0-9\-_]{33}',
    'Generic API Key': r'(?i)(api[_-]?key|apikey)["\'\s:=]+[A-Za-z0-9_\-]{16,}',
    
    # 🔐 Hardcoded Password (amélioré)
    'Hardcoded Password': r'(?i)(password|passwd|pwd)["\'\s:=]+[^\s"\']{4,}',
    
    # 📧 Email
    'Email': r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
    
    # 🌐 Sensitive URL (amélioré)
    'Sensitive URL': r'https?://[^\s"\']+(?:token|auth|key|password|admin|internal)[^\s"\']*',
    
    # 🗄️ Database URLs
    'Database URL': r'(?i)(mysql|postgres|mongodb|oracle|sqlserver|mariadb)://[^\s"\']+:[^\s"\']+@[^\s"\']+',
    
    # 📦 Base64 suspect (tokens encodés)
    'Base64 Data': r'(?:[A-Za-z0-9+/]{40,}={0,2})',
    
    # 🆔 UUID & tokens longs
    'UUID Token': r'[a-f0-9]{32,}',
}

# Patterns complets (par défaut = VULNERABLE)
PATTERNS = PATTERNS_VULNERABLE

def is_false_positive(file_path, value, pattern_type, context):
    """Filtre intelligent des faux positifs (VERSION PRO)."""
    value_lower = value.lower()
    context_lower = context.lower()
    
    # 🚫 Filtre 1: Fichiers système Android (R$, androidx)
    if 'R$' in file_path or 'R.java' in file_path:
        return True
    if 'androidx' in file_path.lower():
        return True
    
    # 🚫 Filtre 2: Longueur minimale
    if len(value) < 6:
        return True
    
    # 🚫 Filtre 3: Pattern par type
    if pattern_type == 'Email':
        # Emails de test/exemple
        test_emails = ['test@example.com', 'user@localhost', 'admin@admin', 'user@test.com', 
                      'noreply@', 'no-reply@', 'info@example']
        if any(test in value_lower for test in test_emails):
            return True
        # Emails documentés
        if 'example.com' in value_lower and ('//' in context_lower or '#' in context_lower):
            return True
    
    elif pattern_type in ['Google API Key', 'AWS Access Key', 'Stripe Secret Key', 'Stripe Test Key']:
        # Placeholders et exemples
        if any(ph in value.upper() for ph in ['EXAMPLE', 'PLACEHOLDER', 'FAKE', 'TEST_', 'XXXX', '0000']):
            return True
    
    elif pattern_type == 'Base64 Data':
        # Filter out base64 strings that are clearly not secrets
        if len(value) < 40 or len(set(value)) < 5:
            return True
    
    elif pattern_type == 'UUID Token':
        # UUID v4 pattern - all zeros is not a secret
        if '00000000-0000-0000-0000-000000000000' in value:
            return True
        # Short UUIDs
        if len(value) < 32:
            return True
    
    elif pattern_type == 'Sensitive URL':
        # URLs publiques/documentation
        public_urls = ['github.com', 'stackoverflow.com', 'docs.', 'example.com', 'localhost', 
                      'api.github.com', 'developer.']
        if any(pub in value_lower for pub in public_urls):
            return True
    
    elif pattern_type in ['Generic API Key', 'Encryption Key']:
        # Clés trop évidentes ou de test
        if len(value) < 16:
            return True
        if value.lower() in ['none', 'null', 'undefined', 'secret', 'password', 'api_key']:
            return True
    
    elif pattern_type == 'Hardcoded Password':
        # Passwords trop courts ou de test
        if len(value) < 4:
            return True
        if value.lower() in ['password', 'pass', '123456', 'admin', 'test', '1234']:
            return True
    
    return False

def calculate_entropy(s):
    """Calculate Shannon entropy of a string (for STRICT mode)."""
    if not s:
        return 0
    entropy = 0
    for c in set(s):
        p = s.count(c) / len(s)
        entropy -= p * (p and __import__('math').log2(p))
    return entropy

def is_high_entropy(value, threshold=3.5):
    """Check if a string has high entropy (likely to be a secret)."""
    return calculate_entropy(value) >= threshold

def scan_file(file_path, findings, debug=False, mode='vulnerable', patterns_dict=None):
    """Scan a single file for secrets with intelligent filtering."""
    if patterns_dict is None:
        patterns_dict = PATTERNS_VULNERABLE if mode == 'vulnerable' else PATTERNS_STRICT
    
    # ✅ Filtrer les dossiers Android système (moins strictement)
    if "\\android\\" in file_path.lower() or "/android/" in file_path.lower():
        if "\\androidx\\" not in file_path.lower():  # Permettre les fichiers Android normaux
            return
    
    # ✅ Ignorer les fichiers R$ (générés automatiquement)
    if "R$" in file_path or "R.java" in file_path:
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            
            # Debug: afficher les fichiers scannés
            if debug and len(lines) > 0:
                print(f"  📄 Scanning: {file_path} ({len(lines)} lines)")
            
            for line_num, line in enumerate(lines, 1):
                for pattern_name, pattern in patterns_dict.items():
                    matches = re.findall(pattern, line)
                    if matches:
                        for match in matches:
                            # Si c'est un tuple (comme pour les groupes de capture), prendre le premier élément
                            if isinstance(match, tuple):
                                match = match[1] if len(match) > 1 else match[0]
                            
                            # Mode STRICT: appliquer filtrage d'entropie supplémentaire
                            if mode == 'strict':
                                # Pour les patterns sensibles, vérifier l'entropie
                                if pattern_name in ['Generic API Key', 'Email', 'Hardcoded Password']:
                                    if not is_high_entropy(match):
                                        continue  # Skip low entropy values
                            
                            # Filtrer les faux positifs (VERSION PRO)
                            if not is_false_positive(file_path, match, pattern_name, line):
                                findings.append({
                                    'file': file_path,
                                    'line': line_num,
                                    'type': pattern_name,
                                    'value': match,
                                    'context': line.strip(),
                                    'severity': get_severity(pattern_name),
                                    'risk_score': get_risk_score(pattern_name),
                                    'mode': mode.upper()
                                })
    except Exception as e:
        print(f"Error scanning {file_path}: {e}")

def get_severity(pattern_type):
    """Détermine la sévérité d'un secret trouvé (SCORE RISQUE PRO)."""
    # 🔴 CRITICAL (Score risque 95-100)
    critical = ['Private Key', 'SSH Public Key', 'AWS Secret Key', 'Stripe Secret Key', 
               'Slack Bot Token', 'GitHub Token']
    
    # 🔴 HIGH (Score risque 80-95)
    high = ['AWS Access Key', 'Firebase API Key', 'Stripe Test Key', 'GitLab Token',
           'JWT Token', 'OAuth Token', 'Encryption Key']
    
    # 🟡 MEDIUM (Score risque 50-80)
    medium = ['Google API Key', 'Firebase URL', 'Bearer Token', 'Generic API Key',
             'Hardcoded Password', 'Database URL', 'Slack User Token']
    
    # 🟢 LOW (Score risque 20-50)
    low = ['Email', 'Sensitive URL', 'Base64 Data', 'UUID Token']
    
    if pattern_type in critical:
        return 'CRITICAL'
    elif pattern_type in high:
        return 'HIGH'
    elif pattern_type in medium:
        return 'MEDIUM'
    else:
        return 'LOW'

def get_risk_score(pattern_type):
    """Retourne un score de risque numérique (0-100)."""
    scores = {
        # Critical
        'Private Key': 100,
        'SSH Public Key': 99,
        'AWS Secret Key': 98,
        'Stripe Secret Key': 97,
        'GitHub Token': 96,
        'Slack Bot Token': 95,
        # High
        'AWS Access Key': 90,
        'Firebase API Key': 88,
        'Stripe Test Key': 87,
        'GitLab Token': 85,
        'JWT Token': 84,
        'OAuth Token': 83,
        'Encryption Key': 82,
        # Medium
        'Google API Key': 75,
        'Firebase URL': 70,
        'Bearer Token': 68,
        'Generic API Key': 65,
        'Hardcoded Password': 60,
        'Database URL': 58,
        'Slack User Token': 55,
        # Low
        'Email': 35,
        'Sensitive URL': 30,
        'Base64 Data': 25,
        'UUID Token': 20,
    }
    return scores.get(pattern_type, 50)

def scan_directory(directory_path, findings, debug=False, mode='vulnerable'):
    """Recursively scan a directory for secrets."""
    patterns_dict = PATTERNS_VULNERABLE if mode == 'vulnerable' else PATTERNS_STRICT
    extensions = ('.java', '.kt', '.xml', '.smali', '.txt', '.json', '.properties', '.gradle', '.py', '.js', '.md', '.sh', '.cpp', '.c', '.h')
    
    files_scanned = 0
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith(extensions):
                file_path = os.path.join(root, file)
                scan_file(file_path, findings, debug=debug, mode=mode, patterns_dict=patterns_dict)
                files_scanned += 1
    
    if debug:
        print(f"✓ Scanned {files_scanned} files in {mode.upper()} mode")

def is_valid_apk(apk_path):
    try:
        with open(apk_path, 'rb') as f:
            return f.read(2) == b'PK'
    except Exception:
        return False


def decompile_apk(apk_path):
    """Decompile APK using apktool."""
    if not is_valid_apk(apk_path):
        return None, 'APK invalide ou corrompu : le fichier n\'est pas un zip APK valide.'

    apktool_path = shutil.which('apktool') or shutil.which('apktool.bat')
    java_path = shutil.which('java')

    if not apktool_path and not java_path:
        return None, 'apktool et Java sont introuvables. Installez apktool et ajoutez Java au PATH.'

    output_dir = os.path.join(tempfile.mkdtemp(), 'apktool_out')
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    def run_command(cmd):
        try:
            return subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        except subprocess.TimeoutExpired:
            return None

    def format_error(result):
        return (result.stderr or result.stdout or '').strip()

    apktool_dir = os.path.dirname(apktool_path) if apktool_path else None
    jar_candidate = None
    if apktool_dir and os.path.isdir(apktool_dir):
        jars = [f for f in os.listdir(apktool_dir) if f.lower().startswith('apktool') and f.lower().endswith('.jar')]
        if jars:
            jars.sort(reverse=True)
            jar_candidate = os.path.join(apktool_dir, jars[0])

    if jar_candidate and java_path:
        result = run_command([java_path, '-jar', jar_candidate, 'd', apk_path, '-o', output_dir, '-f'])
        if result and result.returncode == 0:
            return output_dir, None
        if result is None:
            return None, 'Décompilation APK avec apktool.jar timed out. Vérifiez Java et apktool.jar.'
        return None, f"apktool.jar a échoué : {format_error(result)}"

    if apktool_path:
        if apktool_path.lower().endswith('.bat'):
            result = run_command([apktool_path, 'd', apk_path, '-o', output_dir, '-f'])
        else:
            result = run_command([apktool_path, 'd', apk_path, '-o', output_dir, '-f'])

        if result and result.returncode == 0:
            return output_dir, None
        if result is None:
            return None, 'Décompilation APK avec apktool timed out. Vérifiez l\'installation de apktool.'
        return None, f"apktool a échoué : {format_error(result)}"

    return None, 'Impossible de trouver un exécutable apktool valide.'

def generate_pdf_report(findings, output_file, target_path, mode='vulnerable'):
    """Génère un rapport PDF professionnel."""
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Styles personnalisés
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Centré
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=20
    )
    
    normal_style = styles['Normal']
    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leftIndent=20
    )
    
    story = []
    
    # Titre
    story.append(Paragraph("🔍 SecretHunter - Rapport d'Analyse de Sécurité", title_style))
    story.append(Spacer(1, 12))
    
    # Informations générales
    story.append(Paragraph("Informations Générales", subtitle_style))
    story.append(Paragraph(f"<b>Date du scan:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    story.append(Paragraph(f"<b>Cible analysée:</b> {target_path}", normal_style))
    story.append(Paragraph(f"<b>Mode de détection:</b> {mode.upper()}", normal_style))
    story.append(Paragraph(f"<b>Nombre total de secrets trouvés:</b> {len(findings)}", normal_style))
    story.append(Spacer(1, 20))
    
    if findings:
        # Statistiques
        story.append(Paragraph("📊 Statistiques", subtitle_style))
        
        # Compter par type
        types_count = Counter(f['type'] for f in findings)
        severity_count = Counter(f['severity'] for f in findings)
        
        # Tableau des types
        type_data = [['Type de Secret', 'Nombre']]
        for secret_type, count in types_count.most_common():
            type_data.append([secret_type, str(count)])
        
        type_table = Table(type_data)
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(type_table)
        story.append(Spacer(1, 20))
        
        # Détails des findings
        story.append(Paragraph("🔍 Détails des Secrets Trouvés", subtitle_style))
        
        for i, finding in enumerate(findings, 1):
            # Nouvelle page tous les 20 findings
            if i > 1 and (i-1) % 20 == 0:
                story.append(PageBreak())
            
            severity_color = {'CRITICAL': colors.darkred, 'HIGH': colors.red, 'MEDIUM': colors.orange, 'LOW': colors.green}.get(finding['severity'], colors.gray)
            
            story.append(Paragraph(f"<b>{i}. {finding['type']}</b> <font color='{severity_color}'>[{finding['severity']}]</font>", normal_style))
            story.append(Paragraph(f"<b>Fichier:</b> {finding['file']}", normal_style))
            story.append(Paragraph(f"<b>Ligne:</b> {finding['line']}", normal_style))
            story.append(Paragraph("<b>Valeur détectée:</b>", normal_style))
            story.append(Paragraph(f"<code>{finding['value'][:100]}{'...' if len(finding['value']) > 100 else ''}</code>", code_style))
            story.append(Paragraph("<b>Contexte:</b>", normal_style))
            story.append(Paragraph(f"<code>{finding['context'][:200]}{'...' if len(finding['context']) > 200 else ''}</code>", code_style))
            story.append(Spacer(1, 15))
    
    else:
        story.append(Paragraph("✅ Aucun secret détecté", subtitle_style))
        story.append(Paragraph("L'application analysée semble respecter les bonnes pratiques de sécurité.", normal_style))
    
    # Recommandations
    story.append(PageBreak())
    story.append(Paragraph("💡 Recommandations de Sécurité", subtitle_style))
    recommendations = [
        "• Évitez de hardcoder les clés API et tokens dans le code source",
        "• Utilisez des variables d'environnement ou des services de gestion de secrets",
        "• Ne commitez jamais de fichiers contenant des informations sensibles",
        "• Utilisez des outils de scan automatique dans votre pipeline CI/CD",
        "• Effectuez des audits de sécurité réguliers de vos applications"
    ]
    
    for rec in recommendations:
        story.append(Paragraph(rec, normal_style))
        story.append(Spacer(1, 5))
    
    # Générer le PDF
    doc.build(story)
    print(f"📄 Rapport PDF généré: {output_file}")

def start_dashboard(findings, target_path, mode='strict'):
    """Démarre le dashboard web Flask."""
    app = Flask(__name__)
    upload_dir = os.path.join(os.getcwd(), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    dashboard_state = {
        'findings': findings,
        'target_path': target_path,
        'scan_date': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
        'message': 'Analyse initiale effectuée.',
        'mode': mode,
        'pdf_path': None,
        'json_path': None,
    }

    dashboard_html = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SecretHunter Pro Dashboard</title>
        <style>
            body { font-family: 'Inter', Arial, sans-serif; margin: 0; padding: 0; background: #eef2ff; color: #111827; }
            .container { max-width: 1300px; margin: 0 auto; padding: 30px 20px; }
            .topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; flex-wrap: wrap; gap: 15px; }
            .brand { display: flex; align-items: center; gap: 15px; }
            .brand h1 { margin: 0; font-size: 2rem; }
            .brand span { font-size: 1rem; color: #6b7280; }
            .header-card { background: linear-gradient(135deg, #4338ca 0%, #2563eb 100%); color: white; padding: 30px; border-radius: 24px; box-shadow: 0 20px 60px rgba(15, 23, 42, 0.12); }
            .header-card p { margin: 10px 0 0; color: #dbeafe; }
            .grid { display: grid; gap: 20px; }
            .stats { grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); }
            .stat-card, .panel { background: white; padding: 25px; border-radius: 24px; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08); border: 1px solid #e5e7eb; }
            .panel h2 { margin-top: 0; font-size: 1.4rem; }
            .status { padding: 18px; border-radius: 16px; background: #f3f4f6; color: #111827; margin-bottom: 20px; border: 1px solid #d1d5db; }
            .form-row { display: grid; grid-template-columns: 1.7fr 0.9fr 0.9fr; gap: 15px; align-items: end; }
            input[type="file"], select { width: 100%; padding: 14px 18px; border-radius: 16px; border: 1px solid #d1d5db; background: #f9fafb; font-size: 0.95rem; }
            .action-btn, .secondary-btn { display: inline-flex; justify-content: center; align-items: center; gap: 10px; padding: 14px 20px; border-radius: 16px; border: none; cursor: pointer; font-weight: 600; }
            .action-btn { background: #4338ca; color: white; }
            .action-btn:hover { background: #3730a3; }
            .secondary-btn { background: #eef2ff; color: #4338ca; }
            .secondary-btn:hover { background: #e0e7ff; }
            .stat-card h3 { margin: 0 0 8px; font-size: 0.95rem; color: #6b7280; }
            .stat-card .number { font-size: 2.5rem; font-weight: 700; color: #111827; }
            .stat-card .badge { display: inline-flex; padding: 6px 12px; border-radius: 999px; font-size: 0.8rem; font-weight: 700; }
            .badge.strict { background: #ede9fe; color: #4f46e5; }
            .badge.vulnerable { background: #fee2e2; color: #b91c1c; }
            .data-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .data-table th, .data-table td { padding: 16px 14px; text-align: left; border-bottom: 1px solid #e5e7eb; }
            .data-table th { color: #6b7280; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 0.02em; }
            .severity-chip { display: inline-flex; align-items: center; gap: 8px; padding: 8px 12px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; }
            .severity-chip.high { background: #fee2e2; color: #b91c1c; }
            .severity-chip.medium { background: #fef9c3; color: #b45309; }
            .severity-chip.low { background: #dcfce7; color: #166534; }
            .search-row { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 20px; }
            .search-row input { flex: 1; padding: 14px 18px; border-radius: 16px; border: 1px solid #d1d5db; background: #f9fafb; }
            .file-label { color: #dbeafe; font-weight: 700; }
            @media (max-width: 900px) { .form-row { grid-template-columns: 1fr; } }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="topbar">
                <div class="brand">
                    <div style="font-size: 2rem;">🔍</div>
                    <div>
                        <h1>SecretHunter Pro</h1>
                        <span>Interface de scan APK professionnelle</span>
                    </div>
                </div>
                <div style="display:flex; gap:10px; flex-wrap: wrap;">
                    <a class="secondary-btn" href="/download_json">📄 Télécharger JSON</a>
                    <a class="secondary-btn" href="/download_pdf">📁 Télécharger PDF</a>
                </div>
            </div>

            <div class="header-card">
                <h2>Tableau de bord de sécurité</h2>
                <p>Analyse des APK et rapports rapides pour pentest ou audit de sécurité mobile.</p>
                <p class="small-text">Fichier sélectionné : <span class="file-label">{{ target_path }}</span> • Mode : <span class="badge {{ mode }}">{{ mode.upper() }}</span></p>
            </div>

            <div class="grid stats">
                <div class="stat-card">
                    <h3>Nombre de findings</h3>
                    <div class="number">{{ findings|length }}</div>
                    <p class="small-text">Total des secrets détectés</p>
                </div>
                <div class="stat-card">
                    <h3>Haute sévérité</h3>
                    <div class="number high">{{ high_count }}</div>
                    <p class="small-text">Secrets critiques à traiter en priorité</p>
                </div>
                <div class="stat-card">
                    <h3>Moyenne sévérité</h3>
                    <div class="number medium">{{ medium_count }}</div>
                    <p class="small-text">Secrets sensibles nécessitant revue</p>
                </div>
                <div class="stat-card">
                    <h3>Basse sévérité</h3>
                    <div class="number low">{{ low_count }}</div>
                    <p class="small-text">Informations moins critiques</p>
                </div>
            </div>

            <div class="panel">
                <h2>📤 Importer un APK</h2>
                <div class="status">{{ message }}</div>
                <form action="/analyze" method="post" enctype="multipart/form-data">
                    <div class="form-row">
                        <input type="file" name="apk_file" accept=".apk" required>
                        <select name="mode">
                            <option value="strict" {% if mode == 'strict' %}selected{% endif %}>STRICT</option>
                            <option value="vulnerable" {% if mode == 'vulnerable' %}selected{% endif %}>VULNERABLE</option>
                        </select>
                        <button class="action-btn" type="submit">Démarrer l'analyse</button>
                    </div>
                </form>
            </div>

            <div class="panel">
                <div class="search-row">
                    <input id="search-input" type="text" placeholder="Chercher par type, fichier ou contexte" oninput="searchFindings()" />
                    <button class="secondary-btn" type="button" onclick="showAll()">Réinitialiser</button>
                </div>
                <table class="data-table" id="findings-table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Fichier</th>
                            <th>Ligne</th>
                            <th>Sévérité</th>
                            <th>Contexte</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for finding in findings %}
                        <tr class="finding-row">
                            <td>{{ finding.type }}</td>
                            <td>{{ finding.file }}</td>
                            <td>{{ finding.line }}</td>
                            <td><span class="severity-chip {{ finding.severity.lower() }}">{{ finding.severity }}</span></td>
                            <td>{{ finding.context[:120] }}{% if finding.context|length > 120 %}...{% endif %}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% if not findings %}
                <div style="text-align: center; padding: 40px; color: #4b5563;">Aucun secret détecté. Lancez une analyse pour voir les résultats.</div>
                {% endif %}
            </div>
        </div>

        <script>
            function searchFindings() {
                const query = document.getElementById('search-input').value.toLowerCase();
                const rows = document.querySelectorAll('.finding-row');
                rows.forEach(row => {
                    const text = row.innerText.toLowerCase();
                    row.style.display = text.includes(query) ? '' : 'none';
                });
            }

            function showAll() {
                document.getElementById('search-input').value = '';
                searchFindings();
            }
        </script>
    </body>
    </html>
    """

    def scan_and_update(path, mode):
        new_findings = []
        if path.endswith('.apk'):
            decompiled_dir, error = decompile_apk(path)
            if not decompiled_dir:
                return None, error
            scan_directory(decompiled_dir, new_findings, debug=False, mode=mode)
        else:
            scan_directory(path, new_findings, debug=False, mode=mode)
        return new_findings, None

    @app.route('/')
    def dashboard():
        high_count = len([f for f in dashboard_state['findings'] if f['severity'] == 'HIGH'])
        medium_count = len([f for f in dashboard_state['findings'] if f['severity'] == 'MEDIUM'])
        low_count = len([f for f in dashboard_state['findings'] if f['severity'] == 'LOW'])

        return render_template_string(dashboard_html,
                                    findings=dashboard_state['findings'],
                                    target_path=dashboard_state['target_path'],
                                    scan_date=dashboard_state['scan_date'],
                                    high_count=high_count,
                                    medium_count=medium_count,
                                    low_count=low_count,
                                    message=dashboard_state['message'],
                                    mode=dashboard_state['mode'])

    @app.route('/analyze', methods=['POST'])
    def analyze():
        file = request.files.get('apk_file')
        mode = request.form.get('mode', 'strict')

        if not file or file.filename == '':
            dashboard_state['message'] = 'Aucun fichier APK sélectionné. Veuillez choisir un fichier .apk.'
            return dashboard()

        if not file.filename.lower().endswith('.apk'):
            dashboard_state['message'] = 'Seuls les fichiers .apk sont supportés.'
            return dashboard()

        filename = secure_filename(file.filename)
        saved_path = os.path.join(upload_dir, filename)
        file.save(saved_path)

        dashboard_state['target_path'] = saved_path
        dashboard_state['mode'] = mode
        dashboard_state['scan_date'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        dashboard_state['message'] = f'Analyse en cours pour {filename}...'

        new_findings, error = scan_and_update(saved_path, mode)
        if error:
            dashboard_state['message'] = error
            dashboard_state['findings'] = []
        else:
            dashboard_state['findings'] = new_findings
            dashboard_state['message'] = f'Analyse terminée pour {filename} ({len(new_findings)} findings).'
            dashboard_state['pdf_path'] = None
            dashboard_state['json_path'] = None

        return dashboard()

    @app.route('/download_pdf')
    def download_pdf():
        if not dashboard_state['findings']:
            dashboard_state['message'] = 'Aucune analyse disponible pour générer un PDF.'
            return dashboard()

        pdf_name = f"secret_hunter_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(upload_dir, pdf_name)
        generate_pdf_report(dashboard_state['findings'], pdf_path, dashboard_state['target_path'], mode=dashboard_state['mode'])
        dashboard_state['pdf_path'] = pdf_path
        return send_file(pdf_path, as_attachment=True, download_name=pdf_name)

    @app.route('/download_json')
    def download_json():
        if not dashboard_state['findings']:
            dashboard_state['message'] = 'Aucune analyse disponible pour générer un JSON.'
            return dashboard()

        json_name = f"secret_hunter_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        json_path = os.path.join(upload_dir, json_name)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_state['findings'], f, ensure_ascii=False, indent=2)
        dashboard_state['json_path'] = json_path
        return send_file(json_path, as_attachment=True, download_name=json_name)

    @app.route('/api/findings')
    def api_findings():
        return jsonify(dashboard_state['findings'])

    print('🚀 Dashboard démarré sur http://localhost:5000')
    print('📊 Ouvrez votre navigateur pour voir les résultats')
    app.run(debug=True, host='0.0.0.0', port=5000)

def main():
    parser = argparse.ArgumentParser(description='SecretHunter - Android Security Scanner')
    parser.add_argument('path', nargs='?', help='Path to Android project directory or APK file (optional with --dashboard)')
    parser.add_argument('--output', '-o', help='Output file for findings (optional)')
    parser.add_argument('--pdf', help='Generate PDF report')
    parser.add_argument('--dashboard', action='store_true', help='Start web dashboard (no scanning if no path provided)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose mode - show all scanned files')
    parser.add_argument('--mode', choices=['strict', 'vulnerable'], default='vulnerable',
                       help='Detection mode: strict (API keys + tokens only) or vulnerable (includes passwords + emails)')
    
    args = parser.parse_args()
    
    # Lancer le dashboard si demandé
    if args.dashboard:
        import os
        import subprocess

        msg = (
            "🚀 SecretHunter Pro - Dashboard Web\n"
            "==================================================\n"
            "📊 Interface moderne et professionnelle\n"
            "🌐 URL: http://localhost:5000\n\n"
            "💡 Le dashboard web s'ouvre automatiquement.\n"
            "  Si l'auto-lancement échoue, utilisez : python app.py\n\n"
        )
        sys.stderr.write(msg)

        try:
            from app import create_app

            def terminal_supports_flask():
                try:
                    return sys.stdout.isatty() and sys.stderr.isatty()
                except Exception:
                    return False

            if terminal_supports_flask():
                app = create_app()
                app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
            else:
                sys.stderr.write("🔁 Environnement sans console directe, démarrage via app.py...\n")
                subprocess.run(
                    [sys.executable, 'app.py'],
                    cwd=os.path.dirname(__file__),
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as e:
            sys.stderr.write(f"❌ Erreur lors du lancement du dashboard: {e}\n")
            sys.stderr.write("💡 Essayez manuellement: python app.py\n")
            sys.exit(1)
        return
    
    # Vérifier qu'un chemin est fourni si pas en mode dashboard
    if not args.path:
        print("❌ Erreur: Veuillez spécifier un chemin vers un APK ou un répertoire de projet.")
        print("💡 Utilisation: python secrethunter.py <chemin>")
        print("💡 Ou pour le dashboard seul: python secrethunter.py --dashboard")
        sys.exit(1)
    
    # Afficher le mode sélectionné
    if args.mode == 'strict':
        print(f"🔴 STRICT MODE - High confidence secrets only (API keys, tokens, private keys)")
        print(f"   Patterns: {len(PATTERNS_STRICT)} (with entropy analysis)")
    else:
        print(f"🟢 VULNERABLE MODE - Comprehensive detection (includes passwords, emails, URLs)")
        print(f"   Patterns: {len(PATTERNS_VULNERABLE)}")
    print()
    
    if not os.path.exists(args.path):
        print(f"Path does not exist: {args.path}")
        sys.exit(1)
    
    findings = []
    
    if args.path.endswith('.apk'):
        print("Detected APK file. Attempting to decompile...")
        decompiled_dir, error = decompile_apk(args.path)
        if decompiled_dir:
            print(f"Scanning decompiled APK...")
            if args.verbose:
                print(f"Verbose mode enabled - showing all scanned files:")
            scan_directory(decompiled_dir, findings, debug=args.verbose, mode=args.mode)
        else:
            print(f"Cannot proceed without decompiling APK: {error}")
            sys.exit(1)
    else:
        print(f"Scanning directory: {args.path}")
        if args.verbose:
            print(f"Verbose mode enabled - showing all scanned files:")
        scan_directory(args.path, findings, debug=args.verbose, mode=args.mode)
    
    # Output results
    if findings:
        print(f"\n🔍 Found {len(findings)} potential secrets ({args.mode.upper()} mode):\n")
        
        # Grouper par sévérité
        high_severity = [f for f in findings if f['severity'] == 'HIGH']
        medium_severity = [f for f in findings if f['severity'] == 'MEDIUM']
        low_severity = [f for f in findings if f['severity'] == 'LOW']
        
        for severity, color, findings_list in [
            ('HIGH', '🔴', high_severity),
            ('MEDIUM', '🟡', medium_severity),
            ('LOW', '🟢', low_severity)
        ]:
            if findings_list:
                print(f"{color} {severity} SEVERITY ({len(findings_list)} findings):")
                for finding in findings_list[:5]:  # Afficher seulement les 5 premiers
                    print(f"  📁 {finding['file']}:{finding['line']}")
                    print(f"  🔍 {finding['type']}: {finding['value'][:50]}{'...' if len(finding['value']) > 50 else ''}")
                    print(f"  📝 {finding['context'][:80]}{'...' if len(finding['context']) > 80 else ''}")
                    print()
        
        if len(findings) > 15:
            print(f"⚠️  {len(findings) - 15} more findings not shown. Use --output to see all.")
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(f"SecretHunter Scan Results - {len(findings)} findings ({args.mode.upper()} mode)\n\n")
                for finding in findings:
                    f.write(f"File: {finding['file']}\n")
                    f.write(f"Line: {finding['line']}\n")
                    f.write(f"Type: {finding['type']}\n")
                    f.write(f"Severity: {finding['severity']}\n")
                    f.write(f"Value: {finding['value']}\n")
                    f.write(f"Context: {finding['context']}\n")
                    f.write(f"Detection Mode: {finding.get('mode', 'UNKNOWN')}\n")
                    f.write("-" * 50 + "\n")
            print(f"\n📄 Results saved to: {args.output}")
        
        # Générer le rapport PDF si demandé
        if args.pdf:
            pdf_filename = args.pdf if args.pdf.endswith('.pdf') else f"{args.pdf}.pdf"
            generate_pdf_report(findings, pdf_filename, args.path, mode=args.mode)
    
    else:
        print(f"\n✅ No secrets found! ({args.mode.upper()} mode)")
        if not args.verbose:
            print("💡 Tip: Use --verbose to see all scanned files")

if __name__ == '__main__':
    main()
