"""
Tests pour le module de stéganographie PDF.
"""

import pytest
import io
from PyPDF2 import PdfWriter, PdfReader
from stego.pdf_meta import PDFSteganography


@pytest.fixture
def test_pdf():
    """Crée un PDF de test."""
    # Créer un PDF simple
    writer = PdfWriter()
    
    # Ajouter une page vide (PyPDF2 nécessite au moins une page)
    from PyPDF2.pdf import PageObject
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    # Sauvegarder en mémoire
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


@pytest.fixture
def stego_instance():
    """Instance de PDFSteganography."""
    return PDFSteganography()


def test_hide_and_extract_without_password(stego_instance, test_pdf):
    """Test de base : cacher et extraire des données sans mot de passe."""
    test_data = "Hello, PDF World!"
    
    # Cacher les données
    modified_pdf = stego_instance.hide_data(test_pdf, test_data)
    
    # Extraire les données
    extracted_data = stego_instance.extract_data(modified_pdf)
    
    assert extracted_data == test_data


def test_hide_and_extract_with_password(stego_instance, test_pdf):
    """Test avec mot de passe : cacher et extraire des données avec chiffrement."""
    test_data = "Secret PDF message"
    password = "pdf_secret"
    
    # Cacher les données
    modified_pdf = stego_instance.hide_data(test_pdf, test_data, password)
    
    # Extraire les données
    extracted_data = stego_instance.extract_data(modified_pdf, password)
    
    assert extracted_data == test_data


def test_hide_with_wrong_password(stego_instance, test_pdf):
    """Test avec mauvais mot de passe."""
    test_data = "Secret PDF data"
    correct_password = "correct"
    wrong_password = "wrong"
    
    # Cacher avec le bon mot de passe
    modified_pdf = stego_instance.hide_data(test_pdf, test_data, correct_password)
    
    # Essayer d'extraire avec le mauvais mot de passe
    with pytest.raises(Exception):
        stego_instance.extract_data(modified_pdf, wrong_password)


def test_no_hidden_data(stego_instance, test_pdf):
    """Test d'extraction sur un PDF sans données cachées."""
    with pytest.raises(ValueError, match="Aucune donnée cachée trouvée"):
        stego_instance.extract_data(test_pdf)


def test_no_metadata(stego_instance):
    """Test d'extraction sur un PDF sans métadonnées."""
    # Créer un PDF sans métadonnées
    writer = PdfWriter()
    from PyPDF2.pdf import PageObject
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    buffer = io.BytesIO()
    writer.write(buffer)
    pdf_without_metadata = buffer.getvalue()
    
    with pytest.raises(ValueError, match="Aucune métadonnée trouvée"):
        stego_instance.extract_data(pdf_without_metadata)


def test_get_capacity(stego_instance, test_pdf):
    """Test du calcul de capacité."""
    capacity = stego_instance.get_capacity(test_pdf)
    
    # La capacité des métadonnées PDF est fixée à 64KB
    assert capacity == 65536


def test_unicode_data(stego_instance, test_pdf):
    """Test avec des données Unicode."""
    test_data = "PDF 世界! 📄"
    
    modified_pdf = stego_instance.hide_data(test_pdf, test_data)
    extracted_data = stego_instance.extract_data(modified_pdf)
    
    assert extracted_data == test_data


def test_empty_data(stego_instance, test_pdf):
    """Test avec des données vides."""
    test_data = ""
    
    modified_pdf = stego_instance.hide_data(test_pdf, test_data)
    extracted_data = stego_instance.extract_data(modified_pdf)
    
    assert extracted_data == test_data


def test_large_data(stego_instance, test_pdf):
    """Test avec des données volumineuses mais dans la limite."""
    # Créer des données proches de la limite
    test_data = "x" * 1000  # 1KB, bien dans la limite de 64KB
    
    modified_pdf = stego_instance.hide_data(test_pdf, test_data)
    extracted_data = stego_instance.extract_data(modified_pdf)
    
    assert extracted_data == test_data


def test_multiline_data(stego_instance, test_pdf):
    """Test avec des données multilignes."""
    test_data = """Ligne 1
Ligne 2
Ligne 3 avec des caractères spéciaux: éàçù
Et des symboles: !@#$%^&*()"""
    
    modified_pdf = stego_instance.hide_data(test_pdf, test_data)
    extracted_data = stego_instance.extract_data(modified_pdf)
    
    assert extracted_data == test_data
