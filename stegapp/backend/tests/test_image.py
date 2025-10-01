"""
Tests pour le module de stéganographie d'images.
"""

import pytest
import numpy as np
from PIL import Image
import io
from stego.image import ImageSteganography


@pytest.fixture
def test_image():
    """Crée une image de test."""
    # Créer une image RGB simple
    img_array = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    image = Image.fromarray(img_array)
    
    # Sauvegarder en mémoire
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return buffer.getvalue()


@pytest.fixture
def stego_instance():
    """Instance de ImageSteganography."""
    return ImageSteganography()


def test_hide_and_extract_without_password(stego_instance, test_image):
    """Test de base : cacher et extraire des données sans mot de passe."""
    test_data = "Hello, World!"
    
    # Cacher les données
    modified_image = stego_instance.hide_data(test_image, test_data)
    
    # Extraire les données
    extracted_data = stego_instance.extract_data(modified_image)
    
    assert extracted_data == test_data


def test_hide_and_extract_with_password(stego_instance, test_image):
    """Test avec mot de passe : cacher et extraire des données avec chiffrement."""
    test_data = "Sensitive information"
    password = "secret_password"
    
    # Cacher les données
    modified_image = stego_instance.hide_data(test_image, test_data, password)
    
    # Extraire les données
    extracted_data = stego_instance.extract_data(modified_image, password)
    
    assert extracted_data == test_data


def test_hide_with_wrong_password(stego_instance, test_image):
    """Test avec mauvais mot de passe."""
    test_data = "Secret data"
    correct_password = "correct"
    wrong_password = "wrong"
    
    # Cacher avec le bon mot de passe
    modified_image = stego_instance.hide_data(test_image, test_data, correct_password)
    
    # Essayer d'extraire avec le mauvais mot de passe
    with pytest.raises(Exception):
        stego_instance.extract_data(modified_image, wrong_password)


def test_data_too_large(stego_instance, test_image):
    """Test avec des données trop volumineuses."""
    # Créer des données trop grandes
    large_data = "x" * 100000  # Très grande chaîne
    
    with pytest.raises(ValueError, match="données sont trop volumineuses"):
        stego_instance.hide_data(test_image, large_data)


def test_no_hidden_data(stego_instance, test_image):
    """Test d'extraction sur une image sans données cachées."""
    with pytest.raises(ValueError, match="Aucune donnée cachée trouvée"):
        stego_instance.extract_data(test_image)


def test_get_capacity(stego_instance, test_image):
    """Test du calcul de capacité."""
    capacity = stego_instance.get_capacity(test_image)
    
    # L'image fait 100x100x3 = 30000 pixels
    # Moins la taille du délimiteur
    expected_capacity = 100 * 100 * 3 - len(stego_instance.delimiter)
    
    assert capacity == expected_capacity


def test_unicode_data(stego_instance, test_image):
    """Test avec des données Unicode."""
    test_data = "Hello 世界! 🌍"
    
    modified_image = stego_instance.hide_data(test_image, test_data)
    extracted_data = stego_instance.extract_data(modified_image)
    
    assert extracted_data == test_data


def test_empty_data(stego_instance, test_image):
    """Test avec des données vides."""
    test_data = ""
    
    modified_image = stego_instance.hide_data(test_image, test_data)
    extracted_data = stego_instance.extract_data(modified_image)
    
    assert extracted_data == test_data
