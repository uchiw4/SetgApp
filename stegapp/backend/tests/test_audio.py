"""
Tests pour le module de stéganographie audio.
"""

import pytest
import wave
import numpy as np
import io
from stego.audio import AudioSteganography


@pytest.fixture
def test_audio():
    """Crée un fichier audio de test."""
    # Générer des données audio PCM 16-bit
    sample_rate = 44100
    duration = 1  # 1 seconde
    frequency = 440  # Note A4
    
    # Générer une onde sinusoïdale
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    audio_data = np.sin(2 * np.pi * frequency * t)
    
    # Convertir en 16-bit PCM
    audio_data = (audio_data * 32767).astype(np.int16)
    
    # Créer le fichier WAV
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    return buffer.getvalue()


@pytest.fixture
def stego_instance():
    """Instance de AudioSteganography."""
    return AudioSteganography()


def test_hide_and_extract_without_password(stego_instance, test_audio):
    """Test de base : cacher et extraire des données sans mot de passe."""
    test_data = "Hello, Audio World!"
    
    # Cacher les données
    modified_audio = stego_instance.hide_data(test_audio, test_data)
    
    # Extraire les données
    extracted_data = stego_instance.extract_data(modified_audio)
    
    assert extracted_data == test_data


def test_hide_and_extract_with_password(stego_instance, test_audio):
    """Test avec mot de passe : cacher et extraire des données avec chiffrement."""
    test_data = "Secret audio message"
    password = "audio_secret"
    
    # Cacher les données
    modified_audio = stego_instance.hide_data(test_audio, test_data, password)
    
    # Extraire les données
    extracted_data = stego_instance.extract_data(modified_audio, password)
    
    assert extracted_data == test_data


def test_hide_with_wrong_password(stego_instance, test_audio):
    """Test avec mauvais mot de passe."""
    test_data = "Secret audio data"
    correct_password = "correct"
    wrong_password = "wrong"
    
    # Cacher avec le bon mot de passe
    modified_audio = stego_instance.hide_data(test_audio, test_data, correct_password)
    
    # Essayer d'extraire avec le mauvais mot de passe
    with pytest.raises(Exception):
        stego_instance.extract_data(modified_audio, wrong_password)


def test_data_too_large(stego_instance, test_audio):
    """Test avec des données trop volumineuses."""
    # Créer des données trop grandes
    large_data = "x" * 100000
    
    with pytest.raises(ValueError, match="données sont trop volumineuses"):
        stego_instance.hide_data(test_audio, large_data)


def test_no_hidden_data(stego_instance, test_audio):
    """Test d'extraction sur un fichier audio sans données cachées."""
    with pytest.raises(ValueError, match="Aucune donnée cachée trouvée"):
        stego_instance.extract_data(test_audio)


def test_get_capacity(stego_instance, test_audio):
    """Test du calcul de capacité."""
    capacity = stego_instance.get_capacity(test_audio)
    
    # Vérifier que la capacité est positive
    assert capacity > 0
    
    # Vérifier que la capacité est raisonnable pour 1 seconde d'audio
    assert capacity <= 44100  # Max 44100 échantillons par seconde


def test_unicode_data(stego_instance, test_audio):
    """Test avec des données Unicode."""
    test_data = "Audio 世界! 🎵"
    
    modified_audio = stego_instance.hide_data(test_audio, test_data)
    extracted_data = stego_instance.extract_data(modified_audio)
    
    assert extracted_data == test_data


def test_empty_data(stego_instance, test_audio):
    """Test avec des données vides."""
    test_data = ""
    
    modified_audio = stego_instance.hide_data(test_audio, test_data)
    extracted_data = stego_instance.extract_data(modified_audio)
    
    assert extracted_data == test_data


def test_wrong_audio_format():
    """Test avec un format audio non supporté."""
    stego_instance = AudioSteganography()
    
    # Créer des données qui ne sont pas du PCM 16-bit
    fake_audio = b"fake audio data"
    
    with pytest.raises(Exception):
        stego_instance.hide_data(fake_audio, "test data")
