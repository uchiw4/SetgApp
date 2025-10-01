"""
Module de stéganographie pour les PDF via métadonnées (version alternative robuste).
"""

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    PyPDF2 = None

from typing import Union, Optional
import io
import json
from .utils import encrypt_data, decrypt_data


class PDFSteganography:
    """Classe pour la stéganographie PDF via métadonnées."""
    
    def __init__(self):
        self.metadata_key = "StegData"
    
    def hide_data(self, pdf_path: Union[str, bytes], data: str, password: Optional[str] = None) -> bytes:
        """
        Cache des données dans les métadonnées d'un PDF.
        
        Args:
            pdf_path: Chemin vers le PDF ou données PDF
            data: Données à cacher
            password: Mot de passe optionnel pour chiffrer les données
        
        Returns:
            Données du PDF modifié
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 n'est pas installé. Installez PyPDF2 pour utiliser la stéganographie PDF.")
        
        # Charger le PDF
        if isinstance(pdf_path, str):
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                pdf_writer = PyPDF2.PdfWriter()
        else:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_path))
            pdf_writer = PyPDF2.PdfWriter()
        
        # Copier toutes les pages
        for page in pdf_reader.pages:
            pdf_writer.add_page(page)
        
        # Préparer les données
        if password:
            encrypted_data = encrypt_data(data.encode(), password)
            data_to_store = encrypted_data.decode('latin-1')
        else:
            data_to_store = data
        
        # Ajouter les métadonnées (méthode robuste)
        # Utiliser /Subject qui est plus fiable
        try:
            pdf_writer.add_metadata({
                '/Title': 'StegApp Document',
                '/Author': 'StegApp',
                '/Subject': data_to_store,  # Stocker dans Subject
                '/Creator': 'StegApp Steganography Tool',
                '/Producer': 'StegApp v1.0'
            })
        except Exception as e:
            raise ValueError(f"Impossible d'ajouter les métadonnées: {e}")
        
        # Sauvegarder
        output = io.BytesIO()
        pdf_writer.write(output)
        return output.getvalue()
    
    def extract_data(self, pdf_path: Union[str, bytes], password: Optional[str] = None) -> str:
        """
        Extrait des données cachées des métadonnées d'un PDF.
        
        Args:
            pdf_path: Chemin vers le PDF ou données PDF
            password: Mot de passe optionnel pour déchiffrer les données
        
        Returns:
            Données extraites
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 n'est pas installé. Installez PyPDF2 pour utiliser la stéganographie PDF.")
        
        # Charger le PDF
        if isinstance(pdf_path, str):
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
        else:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_path))
        
        # Lire les métadonnées
        metadata = pdf_reader.metadata
        if metadata is None:
            raise ValueError("Aucune métadonnée trouvée dans le PDF")
        
        # Convertir en dictionnaire et chercher les données
        data = None
        
        # Méthode 1: Accès direct à /Subject (PRIORITÉ)
        try:
            if hasattr(metadata, 'get'):
                data = metadata.get('/Subject')
            elif isinstance(metadata, dict):
                data = metadata.get('/Subject')
        except Exception:
            pass
        
        # Méthode 2: Parcourir tous les champs pour trouver /Subject
        if data is None:
            try:
                metadata_dict = dict(metadata) if hasattr(metadata, 'items') else metadata
                # Chercher dans /Subject
                if '/Subject' in metadata_dict:
                    data = metadata_dict['/Subject']
                else:
                    # Sinon chercher dans les autres champs
                    for key, value in metadata_dict.items():
                        if key == '/Subject':
                            data = value
                            break
            except Exception:
                pass
        
        # Méthode 3: Recherche dans les champs texte
        if data is None:
            try:
                # Chercher dans tous les champs possibles
                for attr in dir(metadata):
                    if not attr.startswith('_') and hasattr(metadata, attr):
                        try:
                            value = getattr(metadata, attr)
                            if isinstance(value, str) and value.startswith('StegData'):
                                data = value
                                break
                        except Exception:
                            continue
            except Exception:
                pass
        
        if data is None:
            raise ValueError("Aucune donnée cachée trouvée dans les métadonnées")
        
        # Déchiffrer si nécessaire
        if password:
            try:
                data = decrypt_data(data.encode('latin-1'), password).decode()
            except Exception as e:
                raise ValueError(f"Erreur lors du déchiffrement: {str(e)}")
        
        return data
    
    def get_capacity(self, pdf_path: Union[str, bytes]) -> int:
        """
        Retourne la capacité maximale en caractères pour un PDF.
        Les métadonnées PDF ont une limite pratique d'environ 64KB.
        
        Args:
            pdf_path: Chemin vers le PDF ou données PDF
        
        Returns:
            Capacité en caractères
        """
        # Limite pratique des métadonnées PDF
        return 65536  # 64KB
