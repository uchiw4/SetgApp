/**
 * Application JavaScript pour StegApp
 */

function stegApp() {
    return {
        // State
        activeTab: 'hide',
        fileType: 'image',
        extractFileType: 'image',
        selectedFile: null,
        extractSelectedFile: null,
        dataToHide: '',
        password: '',
        extractPassword: '',
        showPassword: false,
        showExtractPassword: false,
        loading: false,
        message: '',
        messageType: 'info',
        capacity: null,
        extractedData: '',

        // Configuration
        apiBaseUrl: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
            ? 'http://localhost:5000' 
            : '',
        
        // Mode sombre
        darkMode: false,

        // Initialize
        init() {
            this.initializeDarkMode();
            this.checkAPIHealth();
        },

        // Initialiser le mode sombre
        initializeDarkMode() {
            // Vérifier le localStorage ou la préférence système
            const savedTheme = localStorage.getItem('darkMode');
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            
            this.darkMode = savedTheme ? JSON.parse(savedTheme) : prefersDark;
            this.applyDarkMode();
        },

        // Basculer le mode sombre
        toggleDarkMode() {
            this.darkMode = !this.darkMode;
            this.applyDarkMode();
            localStorage.setItem('darkMode', JSON.stringify(this.darkMode));
        },

        // Appliquer le mode sombre
        applyDarkMode() {
            if (this.darkMode) {
                document.documentElement.classList.add('dark');
            } else {
                document.documentElement.classList.remove('dark');
            }
        },

        // API Health Check
        async checkAPIHealth() {
            try {
                const response = await fetch(`${this.apiBaseUrl}/api/health`);
                if (!response.ok) {
                    throw new Error('API non disponible');
                }
            } catch (error) {
                this.showMessage('Erreur: API non disponible. Assurez-vous que le serveur backend est démarré.', 'error');
            }
        },

        // File Upload Handlers
        handleFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                this.selectedFile = file;
                this.checkCapacity();
            }
        },

        handleExtractFileUpload(event) {
            const file = event.target.files[0];
            if (file) {
                this.extractSelectedFile = file;
            }
        },

        // Clear Files
        clearFile() {
            this.selectedFile = null;
            this.capacity = null;
            document.getElementById('file-upload').value = '';
        },

        clearExtractFile() {
            this.extractSelectedFile = null;
            document.getElementById('extract-file-upload').value = '';
        },

        // Get File Type Description
        getFileTypeDescription() {
            const descriptions = {
                image: 'Images PNG, JPG, JPEG, BMP, TIFF supportées',
                audio: 'Fichiers audio WAV supportés (PCM 16-bit)',
                pdf: 'Fichiers PDF supportés'
            };
            return descriptions[this.fileType] || '';
        },

        // Check Capacity
        async checkCapacity() {
            if (!this.selectedFile) return;

            this.loading = true;
            try {
                const formData = new FormData();
                formData.append('file', this.selectedFile);

                const response = await fetch(`${this.apiBaseUrl}/api/capacity/${this.fileType}`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Erreur lors de la vérification de la capacité');
                }

                const result = await response.json();
                this.capacity = result.capacity_bits;

            } catch (error) {
                this.showMessage(`Erreur: ${error.message}`, 'error');
            } finally {
                this.loading = false;
            }
        },

        // Hide Data
        async hideData() {
            if (!this.selectedFile || !this.dataToHide) {
                this.showMessage('Veuillez sélectionner un fichier et saisir des données à cacher.', 'error');
                return;
            }

            this.loading = true;
            try {
                const formData = new FormData();
                formData.append('file', this.selectedFile);
                formData.append('data', this.dataToHide);
                if (this.password) {
                    formData.append('password', this.password);
                }

                const response = await fetch(`${this.apiBaseUrl}/api/hide/${this.fileType}`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Erreur lors du masquage des données');
                }

                // Download the modified file
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = `hidden_data.${this.getFileExtension()}`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);

                this.showMessage('Données cachées avec succès! Le fichier modifié a été téléchargé.', 'success');
                this.resetHideForm();

            } catch (error) {
                this.showMessage(`Erreur: ${error.message}`, 'error');
            } finally {
                this.loading = false;
            }
        },

        // Extract Data
        async extractData() {
            if (!this.extractSelectedFile) {
                this.showMessage('Veuillez sélectionner un fichier.', 'error');
                return;
            }

            this.loading = true;
            try {
                const formData = new FormData();
                formData.append('file', this.extractSelectedFile);
                if (this.extractPassword) {
                    formData.append('password', this.extractPassword);
                }

                const response = await fetch(`${this.apiBaseUrl}/api/extract/${this.extractFileType}`, {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Erreur lors de l\'extraction des données');
                }

                const result = await response.json();
                this.extractedData = result.data;
                this.showMessage('Données extraites avec succès!', 'success');

            } catch (error) {
                this.showMessage(`Erreur: ${error.message}`, 'error');
                this.extractedData = '';
            } finally {
                this.loading = false;
            }
        },

        // Utility Functions
        getFileExtension() {
            const extensions = {
                image: 'png',
                audio: 'wav',
                pdf: 'pdf'
            };
            return extensions[this.fileType] || 'bin';
        },

        resetHideForm() {
            this.dataToHide = '';
            this.password = '';
            this.clearFile();
        },

        showMessage(text, type = 'info') {
            this.message = text;
            this.messageType = type;
            
            // Auto-hide message after 5 seconds
            setTimeout(() => {
                this.message = '';
            }, 5000);
        },

        async copyToClipboard(text) {
            try {
                await navigator.clipboard.writeText(text);
                this.showMessage('Texte copié dans le presse-papiers!', 'success');
            } catch (error) {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                this.showMessage('Texte copié dans le presse-papiers!', 'success');
            }
        }
    };
}

// Drag and drop functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add drag and drop support for file uploads
    const dropZones = document.querySelectorAll('input[type="file"]').forEach(input => {
        const dropZone = input.closest('.border-dashed');
        
        dropZone.addEventListener('dragover', function(e) {
            e.preventDefault();
            dropZone.classList.add('border-indigo-400', 'bg-indigo-50');
        });
        
        dropZone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            dropZone.classList.remove('border-indigo-400', 'bg-indigo-50');
        });
        
        dropZone.addEventListener('drop', function(e) {
            e.preventDefault();
            dropZone.classList.remove('border-indigo-400', 'bg-indigo-50');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                input.files = files;
                input.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
    });
});

// Service Worker for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
    });
}
