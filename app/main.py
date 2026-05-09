"""Routes principales de l'application SecretHunter."""
import os
import shutil
from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, request, send_from_directory, url_for, current_app
from secrethunter import decompile_apk, scan_directory
from app.utils import allowed_file, build_text_result, safe_download_filename, get_scan_statistics

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Page d'accueil - upload APK."""
    return render_template('index.html')


@main_bp.route('/scan', methods=['POST'])
def scan_apk():
    """Traite l'upload et le scan d'un APK."""
    # Vérifier le fichier
    apk_file = request.files.get('apk_file')
    if not apk_file or apk_file.filename == '':
        flash('Aucun fichier sélectionné. Choisissez un fichier APK.', 'danger')
        return redirect(url_for('main.index'))

    if not allowed_file(apk_file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        flash('Seuls les fichiers APK sont autorisés.', 'danger')
        return redirect(url_for('main.index'))

    # Sauvegarder le fichier
    from werkzeug.utils import secure_filename
    filename = secure_filename(apk_file.filename)
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    apk_file.save(upload_path)

    # Récupérer le mode
    scan_mode = request.form.get('mode', 'strict').lower()
    if scan_mode not in ['strict', 'vulnerable']:
        scan_mode = 'strict'

    # Décompiler l'APK
    decoded_path, decode_error = decompile_apk(upload_path)
    if decode_error:
        flash(f'Erreur lors de la décompilation : {decode_error}', 'danger')
        return redirect(url_for('main.index'))

    # Scanner le dossier décompilé
    findings = []
    scan_directory(decoded_path, findings, mode=scan_mode)

    # Nettoyer le dossier décompilé
    try:
        shutil.rmtree(decoded_path, ignore_errors=True)
    except Exception:
        pass

    # Calculer les statistiques
    stats = get_scan_statistics(findings)

    # Générer et sauvegarder le rapport
    scan_name = f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    result_filename = f"{scan_name}.txt"
    result_path = os.path.join(current_app.config['RESULTS_FOLDER'], result_filename)
    result_text = build_text_result(scan_name, filename, scan_mode, findings)
    with open(result_path, 'w', encoding='utf-8') as result_file:
        result_file.write(result_text)

    # Rendre la page de résultats
    return render_template(
        'result.html',
        findings=findings,
        stats=stats,
        filename=filename,
        mode=scan_mode,
        result_file=result_filename,
        total_findings=len(findings),
        scan_date=datetime.now().strftime('%d/%m/%Y à %H:%M:%S'),
    )


@main_bp.route('/download/<path:filename>')
def download_result(filename):
    """Télécharge un rapport de scan."""
    safe_name = safe_download_filename(filename)
    return send_from_directory(current_app.config['RESULTS_FOLDER'], safe_name, as_attachment=True)
