"""
Debug spécifique pour les métadonnées PDF.
"""

import io
from PyPDF2 import PdfReader, PdfWriter, PageObject
from stego.pdf_meta import PDFSteganography

def debug_metadata_reading():
    """Debug de la lecture des métadonnées."""
    
    print("🔍 Debug lecture métadonnées PDF")
    print("=" * 50)
    
    # Créer un PDF avec métadonnées
    writer = PdfWriter()
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    # Ajouter les métadonnées exactement comme dans le code
    test_data = "test"
    metadata = {
        '/Title': 'StegApp Document',
        '/Author': 'StegApp',
        '/Subject': 'Document with hidden data',
        '/Creator': 'StegApp Steganography Tool',
        '/Producer': 'StegApp v1.0',
        'StegData': test_data
    }
    
    print(f"Métadonnées ajoutées:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    writer.add_metadata(metadata)
    
    # Sauvegarder
    output = io.BytesIO()
    writer.write(output)
    pdf_data = output.getvalue()
    
    # Lire le PDF
    reader = PdfReader(io.BytesIO(pdf_data))
    metadata_read = reader.metadata
    
    print(f"\nMétadonnées lues:")
    if metadata_read:
        # Convertir en dictionnaire
        if hasattr(metadata_read, 'items'):
            metadata_dict = dict(metadata_read)
        else:
            metadata_dict = metadata_read
            
        for key, value in metadata_dict.items():
            print(f"  {key}: {value}")
        
        # Test de récupération
        print(f"\nTest de récupération:")
        steg_data = metadata_dict.get('StegData')
        print(f"  StegData via .get(): {steg_data}")
        
        # Test avec notre module
        print(f"\nTest avec notre module:")
        try:
            stego = PDFSteganography()
            extracted = stego.extract_data(pdf_data)
            print(f"  Données extraites: '{extracted}'")
            print(f"  Correspond à 'test': {extracted == 'test'}")
        except Exception as e:
            print(f"  Erreur: {e}")
            
    else:
        print("  Aucune métadonnée trouvée!")

def test_different_metadata_keys():
    """Test avec différentes clés de métadonnées."""
    
    print("\n" + "=" * 50)
    print("Test avec différentes clés")
    print("=" * 50)
    
    writer = PdfWriter()
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    # Test 1: Clé exacte
    metadata1 = {'StegData': 'test1'}
    writer.add_metadata(metadata1)
    
    output = io.BytesIO()
    writer.write(output)
    pdf1 = output.getvalue()
    
    # Test 2: Clé avec slash
    writer2 = PdfWriter()
    page2 = PageObject.create_blank_page(width=612, height=792)
    writer2.add_page(page2)
    metadata2 = {'/StegData': 'test2'}
    writer2.add_metadata(metadata2)
    
    output2 = io.BytesIO()
    writer2.write(output2)
    pdf2 = output2.getvalue()
    
    # Lire les deux
    reader1 = PdfReader(io.BytesIO(pdf1))
    reader2 = PdfReader(io.BytesIO(pdf2))
    
    print("PDF 1 (clé sans slash):")
    if reader1.metadata:
        metadata_dict1 = dict(reader1.metadata)
        print(f"  Clés: {list(metadata_dict1.keys())}")
        print(f"  StegData: {metadata_dict1.get('StegData')}")
    
    print("PDF 2 (clé avec slash):")
    if reader2.metadata:
        metadata_dict2 = dict(reader2.metadata)
        print(f"  Clés: {list(metadata_dict2.keys())}")
        print(f"  /StegData: {metadata_dict2.get('/StegData')}")

if __name__ == "__main__":
    debug_metadata_reading()
    test_different_metadata_keys()
