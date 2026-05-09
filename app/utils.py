"""Utilitaires pour l'application SecretHunter."""
import os
from datetime import datetime
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    """Vérifie si un fichier est autorisé."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def build_text_result(scan_name, original_filename, mode, findings):
    """Construit un rapport textuel des résultats du scan."""
    header = [
        f'Scan Name: {scan_name}',
        f'APK File: {original_filename}',
        f'Mode: {mode.upper()}',
        f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}',
        f'Total Findings: {len(findings)}',
        '-' * 80,
    ]
    lines = header[:]
    for item in findings:
        lines.append(f"Type: {item['type']}")
        lines.append(f"Severity: {item['severity']}")
        lines.append(f"Risk Score: {item.get('risk_score', 'N/A')}")
        lines.append(f"File: {item['file']}")
        lines.append(f"Line: {item['line']}")
        lines.append(f"Value: {item['value']}")
        lines.append(f"Context: {item['context']}")
        lines.append('-' * 80)
    return '\n'.join(lines)


def safe_download_filename(filename):
    """Sécurise un nom de fichier pour le téléchargement."""
    return os.path.basename(secure_filename(filename))


def get_scan_statistics(findings):
    """Calcule les statistiques d'un scan."""
    return {
        'total': len(findings),
        'critical': len([f for f in findings if f.get('severity') == 'CRITICAL']),
        'high': len([f for f in findings if f.get('severity') == 'HIGH']),
        'medium': len([f for f in findings if f.get('severity') == 'MEDIUM']),
        'low': len([f for f in findings if f.get('severity') == 'LOW']),
    }
