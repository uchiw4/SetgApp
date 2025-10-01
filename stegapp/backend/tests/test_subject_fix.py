"""
Test du fix avec /Subject.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stego.pdf_meta import PDFSteganography
from PyPDF2 import PdfWriter, PageObject
import io

def test_subject_fix():
    """Test du fix avec /Subject."""
    
    print("🔧 Test fix /Subject")
    print("=" * 40)
    
    # Créer un PDF simple
    writer = PdfWriter()
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    pdf_data = output.getvalue()
    
    test_message = "test"
    print(f"Message à cacher: '{test_message}'")
    
    try:
        stego = PDFSteganography()
        
        # Cacher les données
        hidden_pdf = stego.hide_data(pdf_data, test_message)
        print(f"✅ Données cachées avec succès")
        
        # Vérifier les métadonnées
        from PyPDF2 import PdfReader
        reader = PdfReader(io.BytesIO(hidden_pdf))
        metadata = reader.metadata
        
        print(f"\nMétadonnées après masquage:")
        if metadata:
            metadata_dict = dict(metadata)
            for key, value in metadata_dict.items():
                print(f"  {key}: {value}")
        
        # Extraire les données
        extracted = stego.extract_data(hidden_pdf)
        print(f"\nDonnées extraites: '{extracted}'")
        
        if extracted == test_message:
            print("✅ SUCCÈS: Les données correspondent!")
        else:
            print(f"❌ ÉCHEC: '{extracted}' != '{test_message}'")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

def test_with_password():
    """Test avec mot de passe."""
    
    print("\n" + "=" * 40)
    print("Test avec mot de passe")
    print("=" * 40)
    
    writer = PdfWriter()
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    pdf_data = output.getvalue()
    
    test_message = "message secret"
    password = "secret123"
    
    print(f"Message: '{test_message}'")
    print(f"Mot de passe: '{password}'")
    
    try:
        stego = PDFSteganography()
        
        # Cacher avec mot de passe
        hidden_pdf = stego.hide_data(pdf_data, test_message, password)
        print(f"✅ Données chiffrées cachées avec succès")
        
        # Extraire avec mot de passe
        extracted = stego.extract_data(hidden_pdf, password)
        print(f"Données extraites: '{extracted}'")
        
        if extracted == test_message:
            print("✅ SUCCÈS avec chiffrement!")
        else:
            print(f"❌ ÉCHEC avec chiffrement: '{extracted}' != '{test_message}'")
            
    except Exception as e:
        print(f"❌ ERREUR avec chiffrement: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_subject_fix()
    test_with_password()
