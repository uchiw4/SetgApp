"""
API Flask pour la stéganographie.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
from stego.image import ImageSteganography
from stego.audio import AudioSteganography
from stego.audio_alt import AudioSteganographyAlt
from stego.pdf_meta import PDFSteganography
from stego.pdf_meta_alt import PDFSteganography as PDFSteganographyAlt
from stego.pdf_meta_simple import PDFSteganographySimple
import base64
import io

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'bmp', 'tiff'},
    'audio': {'wav'},
    'pdf': {'pdf'}
}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

# Instances des classes de stéganographie
image_stego = ImageSteganography()
audio_stego = AudioSteganography()

# PDF avec fallback en cas d'erreur
try:
    pdf_stego = PDFSteganography()
except Exception:
    pdf_stego = PDFSteganographyAlt()


def allowed_file(filename, file_type):
    """Vérifie si le fichier est autorisé."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, set())


def get_file_type(filename):
    """Détermine le type de fichier."""
    extension = filename.rsplit('.', 1)[1].lower()
    for file_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return file_type
    return None


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de vérification de santé."""
    return jsonify({'status': 'healthy', 'message': 'StegApp API is running'})


@app.route('/api/capacity/<file_type>', methods=['POST'])
def get_capacity(file_type):
    """Retourne la capacité maximale d'un fichier."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename, file_type):
            return jsonify({'error': 'Type de fichier non supporté'}), 400
        
        # Lire le fichier
        file_data = file.read()
        
        # Calculer la capacité
        try:
            if file_type == 'image':
                capacity = image_stego.get_capacity(file_data)
            elif file_type == 'audio':
                capacity = audio_stego.get_capacity(file_data)
            elif file_type == 'pdf':
                capacity = pdf_stego.get_capacity(file_data)
            else:
                return jsonify({'error': 'Type de fichier non supporté'}), 400
        except Exception as e:
            if file_type == 'audio':
                # Essayer la version alternative pour l'audio
                try:
                    audio_stego_alt = AudioSteganographyAlt()
                    capacity = audio_stego_alt.get_capacity(file_data)
                except Exception:
                    return jsonify({'error': f'Erreur lors du traitement de l\'audio: {str(e)}'}), 500
            elif file_type == 'pdf':
                # Essayer la version alternative
                try:
                    pdf_stego_alt = PDFSteganographyAlt()
                    capacity = pdf_stego_alt.get_capacity(file_data)
                except Exception:
                    # Dernier recours : version simplifiée
                    try:
                        pdf_stego_simple = PDFSteganographySimple()
                        capacity = pdf_stego_simple.get_capacity(file_data)
                    except Exception:
                        return jsonify({'error': f'Erreur lors du traitement du PDF: {str(e)}'}), 500
            else:
                return jsonify({'error': f'Erreur lors du traitement du fichier: {str(e)}'}), 500
        
        return jsonify({
            'capacity': capacity,
            'capacity_bits': capacity,
            'capacity_bytes': capacity // 8,
            'capacity_chars': capacity // 8  # Approximation pour le texte
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/hide/<file_type>', methods=['POST'])
def hide_data(file_type):
    """Cache des données dans un fichier."""
    try:
        # Vérifier les paramètres requis
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        if 'data' not in request.form:
            return jsonify({'error': 'Aucune donnée fournie'}), 400
        
        file = request.files['file']
        data = request.form['data']
        password = request.form.get('password', '')
        
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename, file_type):
            return jsonify({'error': 'Type de fichier non supporté'}), 400
        
        # Lire le fichier
        file_data = file.read()
        
        # Cacher les données
        try:
            if file_type == 'image':
                result_data = image_stego.hide_data(file_data, data, password if password else None)
                mimetype = 'image/png'
                extension = 'png'
            elif file_type == 'audio':
                result_data = audio_stego.hide_data(file_data, data, password if password else None)
                mimetype = 'audio/wav'
                extension = 'wav'
            elif file_type == 'pdf':
                result_data = pdf_stego.hide_data(file_data, data, password if password else None)
                mimetype = 'application/pdf'
                extension = 'pdf'
            else:
                return jsonify({'error': 'Type de fichier non supporté'}), 400
        except Exception as e:
            if file_type == 'audio':
                # Essayer la version alternative pour l'audio
                try:
                    audio_stego_alt = AudioSteganographyAlt()
                    result_data = audio_stego_alt.hide_data(file_data, data, password if password else None)
                    mimetype = 'audio/wav'
                    extension = 'wav'
                except Exception as alt_e:
                    return jsonify({'error': f'Erreur lors du traitement de l\'audio: {str(e)}'}), 500
            elif file_type == 'pdf':
                # Essayer la version alternative
                try:
                    pdf_stego_alt = PDFSteganographyAlt()
                    result_data = pdf_stego_alt.hide_data(file_data, data, password if password else None)
                    mimetype = 'application/pdf'
                    extension = 'pdf'
                except Exception as alt_e:
                    # Dernier recours : version simplifiée
                    try:
                        pdf_stego_simple = PDFSteganographySimple()
                        result_data = pdf_stego_simple.hide_data(file_data, data, password if password else None)
                        mimetype = 'application/pdf'
                        extension = 'pdf'
                    except Exception as simple_e:
                        return jsonify({'error': f'Erreur lors du traitement du PDF: {str(e)}'}), 500
            else:
                return jsonify({'error': f'Erreur lors du traitement du fichier: {str(e)}'}), 500
        
        # Retourner le fichier modifié
        return send_file(
            io.BytesIO(result_data),
            mimetype=mimetype,
            as_attachment=True,
            download_name=f'hidden_data.{extension}'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/extract/<file_type>', methods=['POST'])
def extract_data(file_type):
    """Extrait des données d'un fichier."""
    try:
        # Vérifier les paramètres requis
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        file = request.files['file']
        password = request.form.get('password', '')
        
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        if not allowed_file(file.filename, file_type):
            return jsonify({'error': 'Type de fichier non supporté'}), 400
        
        # Lire le fichier
        file_data = file.read()
        
        # Extraire les données
        try:
            if file_type == 'image':
                extracted_data = image_stego.extract_data(file_data, password if password else None)
            elif file_type == 'audio':
                extracted_data = audio_stego.extract_data(file_data, password if password else None)
            elif file_type == 'pdf':
                extracted_data = pdf_stego.extract_data(file_data, password if password else None)
            else:
                return jsonify({'error': 'Type de fichier non supporté'}), 400
        except Exception as e:
            if file_type == 'audio':
                # Essayer la version alternative pour l'audio
                try:
                    audio_stego_alt = AudioSteganographyAlt()
                    extracted_data = audio_stego_alt.extract_data(file_data, password if password else None)
                except Exception as alt_e:
                    return jsonify({'error': f'Erreur lors de l\'extraction de l\'audio: {str(e)}'}), 500
            elif file_type == 'pdf':
                # Essayer la version alternative
                try:
                    pdf_stego_alt = PDFSteganographyAlt()
                    extracted_data = pdf_stego_alt.extract_data(file_data, password if password else None)
                except Exception as alt_e:
                    # Dernier recours : version simplifiée
                    try:
                        pdf_stego_simple = PDFSteganographySimple()
                        extracted_data = pdf_stego_simple.extract_data(file_data, password if password else None)
                    except Exception as simple_e:
                        return jsonify({'error': f'Erreur lors de l\'extraction du PDF: {str(e)}'}), 500
            else:
                return jsonify({'error': f'Erreur lors de l\'extraction: {str(e)}'}), 500
        
        return jsonify({
            'data': extracted_data,
            'success': True
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/supported-formats', methods=['GET'])
def get_supported_formats():
    """Retourne les formats supportés."""
    return jsonify({
        'image': list(ALLOWED_EXTENSIONS['image']),
        'audio': list(ALLOWED_EXTENSIONS['audio']),
        'pdf': list(ALLOWED_EXTENSIONS['pdf'])
    })


@app.errorhandler(413)
def too_large(e):
    """Gestionnaire d'erreur pour les fichiers trop volumineux."""
    return jsonify({'error': 'Fichier trop volumineux (max 100MB)'}), 413


@app.errorhandler(404)
def not_found(e):
    """Gestionnaire d'erreur pour les routes non trouvées."""
    return jsonify({'error': 'Endpoint non trouvé'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Gestionnaire d'erreur interne."""
    return jsonify({'error': 'Erreur interne du serveur'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
