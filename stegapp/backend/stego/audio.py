"""
Module de stéganographie pour les fichiers audio (LSB).
"""

import wave
import numpy as np
from typing import Union, Optional
import io
from .utils import text_to_binary, binary_to_text, encrypt_data, decrypt_data


class AudioSteganography:
    """Classe pour la stéganographie audio utilisant LSB."""
    
    def __init__(self):
        self.delimiter = "1111111111111110"  # Marqueur de fin
    
    def hide_data(self, audio_path: Union[str, bytes], data: str, password: Optional[str] = None) -> bytes:
        """
        Cache des données dans un fichier audio en utilisant LSB.
        
        Args:
            audio_path: Chemin vers le fichier audio ou données audio
            data: Données à cacher
            password: Mot de passe optionnel pour chiffrer les données
        
        Returns:
            Données du fichier audio modifié
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
        
        # Convertir les frames en array numpy
        audio_array = np.frombuffer(frames, dtype=np.int16)
        
        # Créer une copie modifiable
        audio_array = audio_array.copy()
        
        # Préparer les données
        if password:
            data = encrypt_data(data.encode(), password).decode('latin-1')
        
        # Convertir en binaire
        binary_data = text_to_binary(data)
        binary_data += self.delimiter
        
        # Vérifier la capacité
        if len(binary_data) > len(audio_array):
            raise ValueError("Les données sont trop volumineuses pour ce fichier audio")
        
        # Masquer les données
        for i in range(len(binary_data)):
            # Modifier le LSB
            audio_array[i] = (audio_array[i] & 0xFFFE) | int(binary_data[i])
        
        # Convertir en bytes
        modified_frames = audio_array.astype(np.int16).tobytes()
        
        # Créer le nouveau fichier audio
        output = io.BytesIO()
        with wave.open(output, 'wb') as output_file:
            output_file.setparams(params)
            output_file.writeframes(modified_frames)
        
        return output.getvalue()
    
    def extract_data(self, audio_path: Union[str, bytes], password: Optional[str] = None) -> str:
        """
        Extrait des données cachées d'un fichier audio.
        
        Args:
            audio_path: Chemin vers le fichier audio ou données audio
            password: Mot de passe optionnel pour déchiffrer les données
        
        Returns:
            Données extraites
        """
        # Charger le fichier audio
        if isinstance(audio_path, str):
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
        else:
            with wave.open(io.BytesIO(audio_path), 'rb') as audio_file:
                frames = audio_file.readframes(audio_file.getnframes())
        
        # Convertir les frames en array numpy
        audio_array = np.frombuffer(frames, dtype=np.int16)
        
        # Extraire les bits LSB
        binary_data = ""
        for sample in audio_array:
            binary_data += str(sample & 1)
        
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
        
        Args:
            audio_path: Chemin vers le fichier audio ou données audio
        
        Returns:
            Capacité en bits
        """
        if isinstance(audio_path, str):
            with wave.open(audio_path, 'rb') as audio_file:
                frames = audio_file.getnframes()
        else:
            with wave.open(io.BytesIO(audio_path), 'rb') as audio_file:
                frames = audio_file.getnframes()
        
        return frames - len(self.delimiter)  # Moins la taille du délimiteur
