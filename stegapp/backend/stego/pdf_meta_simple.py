"""
Module de stéganographie PDF simplifié (approche alternative).
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


class PDFSteganographySimple:
    """Classe simplifiée pour la stéganographie PDF."""
    
    def __init__(self):
        self.metadata_key = "StegData"
    
    def hide_data(self, pdf_path: Union[str, bytes], data: str, password: Optional[str] = None) -> bytes:
        """
        Cache des données dans les métadonnées d'un PDF.
        Utilise une approche plus simple et robuste.
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 n'est pas installé.")
        
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
        
        # Approche simplifiée : stocker dans un champ texte
        try:
            # Méthode 1: Dans le titre
            pdf_writer.add_metadata({
                '/Title': f'StegApp Document - {data_to_store[:50]}...',
                '/Author': 'StegApp',
                '/Subject': 'Document with hidden data',
                '/Creator': 'StegApp Steganography Tool',
                '/Producer': 'StegApp v1.0',
                '/Keywords': data_to_store  # Stocker dans les mots-clés
            })
        except Exception:
            # Méthode 2: Dans les métadonnées personnalisées
            try:
                pdf_writer.add_metadata({
                    '/Title': 'StegApp Document',
                    '/Author': 'StegApp',
                    '/Subject': data_to_store,
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
        """
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 n'est pas installé.")
        
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
        
        # Chercher les données dans différents champs
        data = None
        
        # Méthode 1: Chercher dans Keywords
        try:
            if hasattr(metadata, 'get'):
                data = metadata.get('/Keywords')
            elif isinstance(metadata, dict):
                data = metadata.get('/Keywords')
        except Exception:
            pass
        
        # Méthode 2: Chercher dans Subject
        if data is None:
            try:
                if hasattr(metadata, 'get'):
                    data = metadata.get('/Subject')
                elif isinstance(metadata, dict):
                    data = metadata.get('/Subject')
            except Exception:
                pass
        
        # Méthode 3: Chercher dans Title (partie après le préfixe)
        if data is None:
            try:
                title = None
                if hasattr(metadata, 'get'):
                    title = metadata.get('/Title')
                elif isinstance(metadata, dict):
                    title = metadata.get('/Title')
                
                if title and title.startswith('StegApp Document - '):
                    data = title[19:]  # Enlever le préfixe
                    if data.endswith('...'):
                        data = data[:-3]  # Enlever les points de suspension
            except Exception:
                pass
        
        # Méthode 4: Parcourir tous les champs
        if data is None:
            try:
                # Convertir en dict si nécessaire
                if hasattr(metadata, 'items'):
                    metadata_dict = dict(metadata)
                else:
                    metadata_dict = metadata
                
                # Chercher dans tous les champs
                for key, value in metadata_dict.items():
                    if isinstance(value, str) and len(value) > 10:  # Ignorer les champs courts
                        # Vérifier si c'est potentiellement nos données
                        try:
                            # Essayer de déchiffrer pour voir si c'est nos données
                            if password:
                                try:
                                    test_decrypt = decrypt_data(value.encode('latin-1'), password)
                                    data = test_decrypt.decode()
                                    break
                                except:
                                    pass
                            else:
                                # Si pas de mot de passe, prendre la première chaîne longue
                                if not value.startswith('StegApp') and not value.startswith('Document'):
                                    data = value
                                    break
                        except:
                            pass
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
        """Retourne la capacité maximale."""
        return 65536  # 64KB
