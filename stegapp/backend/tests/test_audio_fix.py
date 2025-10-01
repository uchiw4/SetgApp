"""
Test du fix pour l'audio.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import wave
import io
from stego.audio import AudioSteganography

def create_test_audio():
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

def test_audio_fix():
    """Test du fix audio."""
    
    print("🔊 Test du fix audio")
    print("=" * 40)
    
    # Créer un fichier audio de test
    audio_data = create_test_audio()
    print(f"Audio de test créé: {len(audio_data)} bytes")
    
    test_message = "Hello Audio World!"
    print(f"Message à cacher: '{test_message}'")
    
    try:
        stego = AudioSteganography()
        
        # Vérifier la capacité
        capacity = stego.get_capacity(audio_data)
        print(f"Capacité: {capacity} bits")
        
        # Cacher les données
        hidden_audio = stego.hide_data(audio_data, test_message)
        print(f"✅ Données cachées avec succès")
        print(f"Audio modifié: {len(hidden_audio)} bytes")
        
        # Extraire les données
        extracted = stego.extract_data(hidden_audio)
        print(f"Données extraites: '{extracted}'")
        
        if extracted == test_message:
            print("✅ SUCCÈS: Les données correspondent!")
        else:
            print(f"❌ ÉCHEC: '{extracted}' != '{test_message}'")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

def test_audio_with_password():
    """Test avec mot de passe."""
    
    print("\n" + "=" * 40)
    print("Test audio avec mot de passe")
    print("=" * 40)
    
    audio_data = create_test_audio()
    test_message = "Secret audio message"
    password = "audio_secret"
    
    print(f"Message: '{test_message}'")
    print(f"Mot de passe: '{password}'")
    
    try:
        stego = AudioSteganography()
        
        # Cacher avec mot de passe
        hidden_audio = stego.hide_data(audio_data, test_message, password)
        print(f"✅ Données chiffrées cachées avec succès")
        
        # Extraire avec mot de passe
        extracted = stego.extract_data(hidden_audio, password)
        print(f"Données extraites: '{extracted}'")
        
        if extracted == test_message:
            print("✅ SUCCÈS avec chiffrement!")
        else:
            print(f"❌ ÉCHEC avec chiffrement: '{extracted}' != '{test_message}'")
            
    except Exception as e:
        print(f"❌ ERREUR avec chiffrement: {e}")
        import traceback
        traceback.print_exc()

def test_audio_array_modification():
    """Test spécifique de la modification d'array."""
    
    print("\n" + "=" * 40)
    print("Test modification d'array numpy")
    print("=" * 40)
    
    try:
        # Créer un array de test
        test_array = np.array([100, 200, 300, 400, 500], dtype=np.int16)
        print(f"Array original: {test_array}")
        print(f"Array readonly: {test_array.flags.writeable}")
        
        # Essayer de modifier
        test_array[0] = 999
        print(f"Array modifié: {test_array}")
        print("✅ Modification directe fonctionne")
        
        # Test avec frombuffer
        data = test_array.tobytes()
        array_from_buffer = np.frombuffer(data, dtype=np.int16)
        print(f"Array frombuffer readonly: {array_from_buffer.flags.writeable}")
        
        # Créer une copie
        array_copy = array_from_buffer.copy()
        print(f"Array copy readonly: {array_copy.flags.writeable}")
        
        # Modifier la copie
        array_copy[0] = 777
        print(f"Array copy modifié: {array_copy}")
        print("✅ Modification via copie fonctionne")
        
    except Exception as e:
        print(f"❌ ERREUR modification array: {e}")

if __name__ == "__main__":
    test_audio_array_modification()
    test_audio_fix()
    test_audio_with_password()
