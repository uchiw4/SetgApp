"""
Module de stéganographie pour les PDF via métadonnées.
"""

import PyPDF2
from typing import Union, Optional
import io
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
        
        # Ajouter les métadonnées (PyPDF2 v3+ syntax)
        # Utiliser /Subject pour stocker les données (plus fiable)
        metadata = {
            '/Title': 'StegApp Document',
            '/Author': 'StegApp',
            '/Subject': data_to_store,  # Stocker directement dans Subject
            '/Creator': 'StegApp Steganography Tool',
            '/Producer': 'StegApp v1.0'
        }
        
        pdf_writer.add_metadata(metadata)
        
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
        # Charger le PDF
        if isinstance(pdf_path, str):
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
        else:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_path))
        
        # Lire les métadonnées (PyPDF2 v3+ syntax)
        metadata = pdf_reader.metadata
        if metadata is None:
            raise ValueError("Aucune métadonnée trouvée dans le PDF")
        
        # Convertir en dictionnaire si nécessaire
        if hasattr(metadata, 'get'):
            metadata_dict = dict(metadata)
        else:
            metadata_dict = metadata
        
        # Chercher directement dans /Subject (méthode fiable)
        data = None
        if '/Subject' in metadata_dict:
            data = metadata_dict['/Subject']
        
        if data is None:
            raise ValueError("Aucune donnée cachée trouvée dans les métadonnées")
        
        # Déchiffrer si nécessaire
        if password:
            data = decrypt_data(data.encode('latin-1'), password).decode()
        
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
