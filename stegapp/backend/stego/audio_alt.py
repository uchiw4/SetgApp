"""
Module de stéganographie audio alternatif (version robuste).
"""

import wave
import numpy as np
from typing import Union, Optional
import io
from .utils import text_to_binary, binary_to_text, encrypt_data, decrypt_data


class AudioSteganographyAlt:
    """Classe alternative pour la stéganographie audio utilisant LSB."""
    
    def __init__(self):
        self.delimiter = "1111111111111110"  # Marqueur de fin
    
    def hide_data(self, audio_path: Union[str, bytes], data: str, password: Optional[str] = None) -> bytes:
        """
        Cache des données dans un fichier audio en utilisant LSB.
        Version alternative plus robuste.
        """
        # Charger le fichier audio
        if isinstance(audio_path, str):
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
                params = audio_file.getparams()
        else:
            with wave.open(io.BytesIO(audio_path), 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
                params = audio_file.getparams()
        
        # Vérifier que c'est du PCM 16-bit
        if params.sampwidth != 2:
            raise ValueError("Seuls les fichiers audio PCM 16-bit sont supportés")
        
        # Préparer les données
        if password:
            data = encrypt_data(data.encode(), password).decode('latin-1')
        
        # Convertir en binaire
        binary_data = text_to_binary(data)
        binary_data += self.delimiter
        
        # Vérifier la capacité
        if len(binary_data) > len(frames) // 2:  # 2 bytes par sample
            raise ValueError("Les données sont trop volumineuses pour ce fichier audio")
        
        # Méthode alternative : modification byte par byte
        frames_list = list(frames)
        
        # Masquer les données
        for i in range(len(binary_data)):
            byte_index = i * 2  # 2 bytes par sample (16-bit)
            if byte_index + 1 < len(frames_list):
                # Modifier le LSB du premier byte du sample
                frames_list[byte_index] = (frames_list[byte_index] & 0xFE) | int(binary_data[i])
        
        # Convertir en bytes
        modified_frames = bytes(frames_list)
        
        # Créer le nouveau fichier audio
        output = io.BytesIO()
        with wave.open(output, 'wb') as output_file:
            output_file.setparams(params)
            output_file.writeframes(modified_frames)
        
        return output.getvalue()
    
    def extract_data(self, audio_path: Union[str, bytes], password: Optional[str] = None) -> str:
        """
        Extrait des données cachées d'un fichier audio.
        Version alternative plus robuste.
        """
        # Charger le fichier audio
        if isinstance(audio_path, str):
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
        else:
            with wave.open(io.BytesIO(audio_path), 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
        
        # Extraire les bits LSB
        binary_data = ""
        for i in range(0, len(frames), 2):  # 2 bytes par sample
            if i < len(frames):
                # Extraire le LSB du premier byte du sample
                binary_data += str(frames[i] & 1)
        
        # Trouver la fin des données
        delimiter_index = binary_data.find(self.delimiter)
        if delimiter_index == -1:
            raise ValueError("Aucune donnée cachée trouvée dans le fichier audio")
        
        # Extraire les données
        data_binary = binary_data[:delimiter_index]
        data = binary_to_text(data_binary)
        
        # Déchiffrer si nécessaire
        if password:
            data = decrypt_data(data.encode('latin-1'), password).decode()
        
        return data
    
    def get_capacity(self, audio_path: Union[str, bytes]) -> int:
        """
        Retourne la capacité maximale en bits pour un fichier audio.
        """
        if isinstance(audio_path, str):
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.getnframes()
        else:
            with wave.open(io.BytesIO(audio_path), 'rb') as audio_file:
                frames = audio_file.getnframes()
        
        # Capacité = nombre de samples (frames / 2 pour 16-bit) - délimiteur
        return (frames // 2) - len(self.delimiter)
