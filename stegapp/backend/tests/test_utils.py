"""
Tests pour les utilitaires de stéganographie.
"""

import pytest
from stego.utils import (
    generate_key_from_password,
    encrypt_data,
    decrypt_data,
    text_to_binary,
    binary_to_text,
    add_padding,
    remove_padding,
    calculate_lsb_capacity,
    validate_file_type
)


def test_generate_key_from_password():
    """Test de génération de clé à partir d'un mot de passe."""
    password = "test_password"
    key1 = generate_key_from_password(password)
    key2 = generate_key_from_password(password)
    
    # La même clé doit être générée pour le même mot de passe
    assert key1 == key2
    
    # La clé doit être différente pour un mot de passe différent
    different_key = generate_key_from_password("different_password")
    assert key1 != different_key


def test_encrypt_decrypt_data():
    """Test de chiffrement et déchiffrement."""
    original_data = b"Hello, World!"
    password = "secret_password"
    
    # Chiffrer
    encrypted = encrypt_data(original_data, password)
    
    # Vérifier que les données sont différentes
    assert encrypted != original_data
    
    # Déchiffrer
    decrypted = decrypt_data(encrypted, password)
    
    # Vérifier que les données originales sont récupérées
    assert decrypted == original_data


def test_encrypt_decrypt_wrong_password():
    """Test avec un mauvais mot de passe."""
    original_data = b"Secret data"
    correct_password = "correct"
    wrong_password = "wrong"
    
    encrypted = encrypt_data(original_data, correct_password)
    
    # Essayer de déchiffrer avec le mauvais mot de passe
    with pytest.raises(Exception):
        decrypt_data(encrypted, wrong_password)


def test_text_to_binary():
    """Test de conversion texte vers binaire."""
    text = "Hello"
    binary = text_to_binary(text)
    
    # Vérifier la longueur (8 bits par caractère)
    assert len(binary) == len(text) * 8
    
    # Vérifier que c'est bien du binaire
    assert all(bit in '01' for bit in binary)


def test_binary_to_text():
    """Test de conversion binaire vers texte."""
    text = "Hello"
    binary = text_to_binary(text)
    converted_text = binary_to_text(binary)
    
    assert converted_text == text


def test_text_binary_roundtrip():
    """Test d'aller-retour texte -> binaire -> texte."""
    original_text = "Hello, 世界! 🌍"
    binary = text_to_binary(original_text)
    converted_text = binary_to_text(binary)
    
    assert converted_text == original_text


def test_add_padding():
    """Test d'ajout de padding."""
    data = "1010"
    padded = add_padding(data, 10)
    
    assert len(padded) == 10
    assert padded.startswith(data)
    assert padded.endswith("000000")


def test_remove_padding():
    """Test de suppression de padding."""
    data = "1010"
    padded = add_padding(data, 10)
    unpadded = remove_padding(padded)
    
    assert unpadded == data


def test_padding_roundtrip():
    """Test d'aller-retour avec padding."""
    original_data = "10101010"
    padded = add_padding(original_data, 20)
    unpadded = remove_padding(padded)
    
    assert unpadded == original_data


def test_calculate_lsb_capacity():
    """Test de calcul de capacité LSB."""
    image_size = (100, 200)
    capacity = calculate_lsb_capacity(image_size)
    
    # Capacité = largeur * hauteur * 3 canaux RGB
    expected_capacity = 100 * 200 * 3
    assert capacity == expected_capacity


def test_validate_file_type():
    """Test de validation de type de fichier."""
    # Types valides
    assert validate_file_type("test.png", [".png", ".jpg"])
    assert validate_file_type("test.JPG", [".png", ".jpg"])  # Case insensitive
    assert validate_file_type("test.txt", [".txt", ".doc"])
    
    # Types invalides
    assert not validate_file_type("test.gif", [".png", ".jpg"])
    assert not validate_file_type("test", [".png", ".jpg"])  # Pas d'extension
    assert not validate_file_type("", [".png", ".jpg"])  # Nom vide
