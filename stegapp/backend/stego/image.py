"""
Module de stéganographie pour les images (LSB).
"""

import numpy as np
from PIL import Image
from typing import Union, Optional
import io
from .utils import text_to_binary, binary_to_text, add_padding, remove_padding, encrypt_data, decrypt_data


class ImageSteganography:
    """Classe pour la stéganographie d'images utilisant LSB."""
    
    def __init__(self):
        self.delimiter = "1111111111111110"  # Marqueur de fin
    
    def hide_data(self, image_path: Union[str, bytes], data: str, password: Optional[str] = None) -> bytes:
        """
        Cache des données dans une image en utilisant LSB.
        
        Args:
            image_path: Chemin vers l'image ou données d'image
            data: Données à cacher
            password: Mot de passe optionnel pour chiffrer les données
        
        Returns:
            Données de l'image modifiée
        """
        # Charger l'image
        if isinstance(image_path, str):
            image = Image.open(image_path)
        else:
            image = Image.open(io.BytesIO(image_path))
        
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Préparer les données
        if password:
            data = encrypt_data(data.encode(), password).decode('latin-1')
        
        # Convertir en binaire
        binary_data = text_to_binary(data)
        binary_data += self.delimiter
        
        # Vérifier la capacité
        width, height = image.size
        capacity = width * height * 3
        if len(binary_data) > capacity:
            raise ValueError("Les données sont trop volumineuses pour cette image")
        
        # Convertir l'image en tableau numpy
        img_array = np.array(image)
        
        # Masquer les données
        data_index = 0
        for row in img_array:
            for pixel in row:
                for channel in range(3):  # R, G, B
                    if data_index < len(binary_data):
                        # Modifier le LSB
                        pixel[channel] = (pixel[channel] & 0xFE) | int(binary_data[data_index])
                        data_index += 1
                    else:
                        break
                if data_index >= len(binary_data):
                    break
            if data_index >= len(binary_data):
                break
        
        # Sauvegarder l'image modifiée
        result_image = Image.fromarray(img_array)
        output = io.BytesIO()
        result_image.save(output, format='PNG')
        return output.getvalue()
    
    def extract_data(self, image_path: Union[str, bytes], password: Optional[str] = None) -> str:
        """
        Extrait des données cachées d'une image.
        
        Args:
            image_path: Chemin vers l'image ou données d'image
            password: Mot de passe optionnel pour déchiffrer les données
        
        Returns:
            Données extraites
        """
        # Charger l'image
        if isinstance(image_path, str):
            image = Image.open(image_path)
        else:
            image = Image.open(io.BytesIO(image_path))
        
        # Convertir en RGB si nécessaire
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convertir l'image en tableau numpy
        img_array = np.array(image)
        
        # Extraire les bits LSB
        binary_data = ""
        for row in img_array:
            for pixel in row:
                for channel in range(3):  # R, G, B
                    binary_data += str(pixel[channel] & 1)
        
        # Trouver la fin des données
        delimiter_index = binary_data.find(self.delimiter)
        if delimiter_index == -1:
            raise ValueError("Aucune donnée cachée trouvée dans l'image")
        
        # Extraire les données
        data_binary = binary_data[:delimiter_index]
        data = binary_to_text(data_binary)
        
        # Déchiffrer si nécessaire
        if password:
            data = decrypt_data(data.encode('latin-1'), password).decode()
        
        return data
    
    def get_capacity(self, image_path: Union[str, bytes]) -> int:
        """
        Retourne la capacité maximale en bits pour une image.
        
        Args:
            image_path: Chemin vers l'image ou données d'image
        
        Returns:
            Capacité en bits
        """
        if isinstance(image_path, str):
            image = Image.open(image_path)
        else:
            image = Image.open(io.BytesIO(image_path))
        
        width, height = image.size
        return width * height * 3 - len(self.delimiter)  # Moins la taille du délimiteur
