"""
Utilitaires pour la stéganographie.
"""

import hashlib
from cryptography.fernet import Fernet
from typing import Union, Tuple
import base64


def generate_key_from_password(password: str) -> bytes:
    """Génère une clé de chiffrement à partir d'un mot de passe."""
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())


def encrypt_data(data: bytes, password: str) -> bytes:
    """Chiffre des données avec un mot de passe."""
    key = generate_key_from_password(password)
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_data(encrypted_data: bytes, password: str) -> bytes:
    """Déchiffre des données avec un mot de passe."""
    key = generate_key_from_password(password)
    f = Fernet(key)
    return f.decrypt(encrypted_data)


def text_to_binary(text: str) -> str:
    """Convertit un texte en binaire."""
    return ''.join(format(ord(char), '08b') for char in text)


def binary_to_text(binary: str) -> str:
    """Convertit du binaire en texte."""
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))


def add_padding(data: str, length: int) -> str:
    """Ajoute du padding pour atteindre une longueur donnée."""
    return data.ljust(length, '0')


def remove_padding(data: str) -> str:
    """Supprime le padding ajouté."""
    return data.rstrip('0')


def calculate_lsb_capacity(image_size: Tuple[int, int]) -> int:
    """Calcule la capacité maximale pour LSB sur une image."""
    width, height = image_size
    return width * height * 3  # 3 canaux RGB


def validate_file_type(filename: str, allowed_extensions: list) -> bool:
    """Valide le type de fichier."""
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)
