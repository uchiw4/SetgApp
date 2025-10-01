"""
Script de debug pour la stéganographie PDF.
"""

import io
from PyPDF2 import PdfReader, PdfWriter
from stego.pdf_meta import PDFSteganography
from stego.pdf_meta_alt import PDFSteganographyAlt

def debug_pdf_metadata():
    """Debug des métadonnées PDF."""
    
    # Créer un PDF de test
    print("=== Création d'un PDF de test ===")
    writer = PdfWriter()
    
    # Ajouter une page vide
    from PyPDF2.pdf import PageObject
    page = PageObject.create_blank_page(width=612, height=792)
    writer.add_page(page)
    
    # Ajouter des métadonnées
    test_data = "Hello, World! Test message"
    metadata = {
        '/Title': 'Test PDF',
        '/Author': 'StegApp',
        '/Subject': 'Debug Test',
        '/Creator': 'StegApp Debug',
        '/Producer': 'StegApp v1.0',
        'StegData': test_data
    }
    
    print(f"Métadonnées à ajouter: {metadata}")
    writer.add_metadata(metadata)
    
    # Sauvegarder en mémoire
    output = io.BytesIO()
    writer.write(output)
    pdf_data = output.getvalue()
    
    print(f"PDF créé, taille: {len(pdf_data)} bytes")
    
    # Lire le PDF
    print("\n=== Lecture du PDF ===")
    reader = PdfReader(io.BytesIO(pdf_data))
    
    print(f"Nombre de pages: {len(reader.pages)}")
    
    # Examiner les métadonnées
    metadata = reader.metadata
    print(f"Métadonnées trouvées: {metadata}")
    print(f"Type des métadonnées: {type(metadata)}")
    
    if metadata:
        print("\n=== Détail des métadonnées ===")
        for key, value in metadata.items():
            print(f"  {key}: {value} (type: {type(value)})")
            
        # Chercher StegData
        steg_data = None
        if hasattr(metadata, 'get'):
            steg_data = metadata.get('StegData')
            print(f"StegData via .get(): {steg_data}")
        
        # Essayer d'accéder directement
        try:
            steg_data = metadata['StegData']
            print(f"StegData via []: {steg_data}")
        except KeyError:
            print("StegData non trouvé via []")
        
        # Parcourir tous les éléments
        print("\n=== Parcours complet ===")
        try:
            for key, value in metadata.items():
                if 'Steg' in str(key) or 'Steg' in str(value):
                    print(f"  TROUVÉ: {key} = {value}")
        except Exception as e:
            print(f"Erreur lors du parcours: {e}")
    
    return pdf_data

def test_steganography():
    """Test de la stéganographie PDF."""
    
    print("\n=== Test de stéganographie ===")
    
    # Test avec le module principal
    try:
        stego = PDFSteganography()
        print("Module principal chargé avec succès")
        
        test_data = "Message de test pour debug"
        print(f"Données à cacher: {test_data}")
        
        # Créer un PDF de test
        writer = PdfWriter()
        from PyPDF2.pdf import PageObject
        page = PageObject.create_blank_page(width=612, height=792)
        writer.add_page(page)
        
        output = io.BytesIO()
        writer.write(output)
        pdf_data = output.getvalue()
        
        # Cacher les données
        print("Tentative de masquage...")
        modified_pdf = stego.hide_data(pdf_data, test_data)
        print(f"PDF modifié créé, taille: {len(modified_pdf)} bytes")
        
        # Extraire les données
        print("Tentative d'extraction...")
        extracted_data = stego.extract_data(modified_pdf)
        print(f"Données extraites: {extracted_data}")
        
        if extracted_data == test_data:
            print("✅ SUCCÈS: Les données correspondent!")
        else:
            print("❌ ÉCHEC: Les données ne correspondent pas")
            
    except Exception as e:
        print(f"❌ ERREUR avec le module principal: {e}")
        import traceback
        traceback.print_exc()
        
        # Essayer la version alternative
        try:
            print("\n--- Essai avec le module alternatif ---")
            stego_alt = PDFSteganographyAlt()
            modified_pdf = stego_alt.hide_data(pdf_data, test_data)
            extracted_data = stego_alt.extract_data(modified_pdf)
            print(f"Module alternatif - Données extraites: {extracted_data}")
            
            if extracted_data == test_data:
                print("✅ SUCCÈS avec le module alternatif!")
            else:
                print("❌ ÉCHEC avec le module alternatif")
                
        except Exception as e2:
            print(f"❌ ERREUR avec le module alternatif: {e2}")
            import traceback
            traceback.print_exc()

def debug_pypdf2_version():
    """Debug de la version PyPDF2."""
    import PyPDF2
    print(f"\n=== Version PyPDF2 ===")
    print(f"Version: {PyPDF2.__version__}")
    
    # Tester les méthodes disponibles
    print("\nMéthodes PdfWriter:")
    writer = PdfWriter()
    methods = [method for method in dir(writer) if not method.startswith('_')]
    print(f"  {methods}")
    
    # Tester les méthodes PdfReader
    print("\nMéthodes PdfReader:")
    reader = PdfReader(io.BytesIO(b''))
    methods = [method for method in dir(reader) if not method.startswith('_')]
    print(f"  {methods}")
    
    # Tester les métadonnées
    print("\nTest métadonnées:")
    try:
        writer = PdfWriter()
        writer.add_metadata({'/Test': 'valeur'})
        print("  add_metadata() fonctionne")
    except Exception as e:
        print(f"  add_metadata() échoue: {e}")

if __name__ == "__main__":
    print("🔍 DEBUG PDF STEGANOGRAPHY")
    print("=" * 50)
    
    debug_pypdf2_version()
    debug_pdf_metadata()
    test_steganography()
    
    print("\n" + "=" * 50)
    print("Debug terminé")
