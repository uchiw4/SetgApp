"""
Test rapide pour debugger les PDFs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stego.pdf_meta import PDFSteganography
from stego.pdf_meta_simple import PDFSteganographySimple
from PyPDF2 import PdfWriter, PageObject
import io

def quick_test():
    """Test rapide des modules PDF."""
    
    print("🔍 Test rapide des modules PDF")
    print("=" * 40)
    
    # Créer un PDF simple
    writer = PdfWriter()
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    output = io.BytesIO()
    writer.write(output)
    pdf_data = output.getvalue()
    
    test_message = "Hello World Test"
    print(f"Message à cacher: {test_message}")
    
    # Test module principal
    print("\n--- Module principal ---")
    try:
        stego = PDFSteganography()
        hidden = stego.hide_data(pdf_data, test_message)
        extracted = stego.extract_data(hidden)
        print(f"✅ Principal: '{extracted}' == '{test_message}' ? {extracted == test_message}")
    except Exception as e:
        print(f"❌ Principal: {e}")
    
    # Test module simplifié
    print("\n--- Module simplifié ---")
    try:
        stego_simple = PDFSteganographySimple()
        hidden = stego_simple.hide_data(pdf_data, test_message)
        extracted = stego_simple.extract_data(hidden)
        print(f"✅ Simplifié: '{extracted}' == '{test_message}' ? {extracted == test_message}")
    except Exception as e:
        print(f"❌ Simplifié: {e}")
    
    # Test avec mot de passe
    print("\n--- Test avec mot de passe ---")
    password = "secret123"
    try:
        stego_simple = PDFSteganographySimple()
        hidden = stego_simple.hide_data(pdf_data, test_message, password)
        extracted = stego_simple.extract_data(hidden, password)
        print(f"✅ Avec mot de passe: '{extracted}' == '{test_message}' ? {extracted == test_message}")
    except Exception as e:
        print(f"❌ Avec mot de passe: {e}")

if __name__ == "__main__":
    quick_test()
