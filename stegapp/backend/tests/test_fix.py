"""
Test du fix pour l'extraction PDF.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stego.pdf_meta import PDFSteganography
from PyPDF2 import PdfWriter, PageObject
import io

def test_fix():
    """Test du fix pour l'extraction."""
    
    print("🔧 Test du fix PDF")
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
        
        # Extraire les données
        extracted = stego.extract_data(hidden_pdf)
        print(f"Données extraites: '{extracted}'")
        
        if extracted == test_message:
            print("✅ SUCCÈS: Les données correspondent!")
        else:
            print(f"❌ ÉCHEC: '{extracted}' != '{test_message}'")
            
            # Debug: examiner les métadonnées
            from PyPDF2 import PdfReader
            reader = PdfReader(io.BytesIO(hidden_pdf))
            metadata = reader.metadata
            
            print(f"\nDebug métadonnées:")
            if metadata:
                metadata_dict = dict(metadata)
                for key, value in metadata_dict.items():
                    print(f"  {key}: {value}")
                    
                steg_data = metadata_dict.get('StegData')
                subject_data = metadata_dict.get('/Subject')
                print(f"\n  StegData: {steg_data}")
                print(f"  Subject: {subject_data}")
                
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fix()
