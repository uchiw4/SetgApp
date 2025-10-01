"""
Test de l'API PDF pour debug.
"""

import requests
import io
from PyPDF2 import PdfWriter, PageObject

def create_test_pdf():
    """Crée un PDF de test."""
    writer = PdfWriter()
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()

def test_api_pdf():
    """Test de l'API PDF."""
    
    base_url = "http://localhost:5000"
    
    print("=== Test API PDF ===")
    
    # Créer un PDF de test
    pdf_data = create_test_pdf()
    print(f"PDF de test créé: {len(pdf_data)} bytes")
    
    # Test 1: Capacité
    print("\n--- Test capacité ---")
    try:
        response = requests.post(
            f"{base_url}/api/capacity/pdf",
            files={'file': ('test.pdf', pdf_data, 'application/pdf')}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Erreur capacité: {e}")
    
    # Test 2: Cacher des données
    print("\n--- Test masquage ---")
    test_message = "Message de test pour debug API"
    print(f"Message à cacher: {test_message}")
    
    try:
        response = requests.post(
            f"{base_url}/api/hide/pdf",
            files={'file': ('test.pdf', pdf_data, 'application/pdf')},
            data={'data': test_message}
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            # Sauvegarder le fichier modifié
            with open('hidden_test.pdf', 'wb') as f:
                f.write(response.content)
            print("Fichier modifié sauvegardé: hidden_test.pdf")
            
            # Test 3: Extraire des données
            print("\n--- Test extraction ---")
            with open('hidden_test.pdf', 'rb') as f:
                response = requests.post(
                    f"{base_url}/api/extract/pdf",
                    files={'file': ('hidden_test.pdf', f, 'application/pdf')}
                )
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Vérifier
            if response.status_code == 200:
                result = response.json()
                extracted = result.get('data', '')
                if extracted == test_message:
                    print("✅ SUCCÈS: Message extrait correctement!")
                else:
                    print(f"❌ ÉCHEC: Message extrait: '{extracted}' != '{test_message}'")
            else:
                print(f"❌ ÉCHEC extraction: {response.text}")
                
        else:
            print(f"❌ ÉCHEC masquage: {response.text}")
            
    except Exception as e:
        print(f"Erreur masquage: {e}")

def test_api_with_password():
    """Test avec mot de passe."""
    
    base_url = "http://localhost:5000"
    
    print("\n=== Test API PDF avec mot de passe ===")
    
    pdf_data = create_test_pdf()
    test_message = "Message secret avec mot de passe"
    password = "secret123"
    
    print(f"Message: {test_message}")
    print(f"Mot de passe: {password}")
    
    try:
        # Cacher avec mot de passe
        response = requests.post(
            f"{base_url}/api/hide/pdf",
            files={'file': ('test.pdf', pdf_data, 'application/pdf')},
            data={'data': test_message, 'password': password}
        )
        
        if response.status_code == 200:
            with open('hidden_encrypted_test.pdf', 'wb') as f:
                f.write(response.content)
            print("Fichier chiffré sauvegardé")
            
            # Extraire avec mot de passe
            with open('hidden_encrypted_test.pdf', 'rb') as f:
                response = requests.post(
                    f"{base_url}/api/extract/pdf",
                    files={'file': ('hidden_encrypted_test.pdf', f, 'application/pdf')},
                    data={'password': password}
                )
            
            print(f"Status extraction: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                extracted = result.get('data', '')
                if extracted == test_message:
                    print("✅ SUCCÈS avec chiffrement!")
                else:
                    print(f"❌ ÉCHEC avec chiffrement: '{extracted}' != '{test_message}'")
            else:
                print(f"❌ ÉCHEC extraction chiffrée: {response.text}")
        else:
            print(f"❌ ÉCHEC masquage chiffré: {response.text}")
            
    except Exception as e:
        print(f"Erreur test chiffrement: {e}")

if __name__ == "__main__":
    print("🧪 TEST API PDF")
    print("=" * 40)
    
    test_api_pdf()
    test_api_with_password()
    
    print("\n" + "=" * 40)
    print("Tests terminés")
