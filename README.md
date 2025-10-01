# StegApp - Application de Stéganographie Web

![StegApp](https://img.shields.io/badge/StegApp-v1.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.11+-green)
![Flask](https://img.shields.io/badge/Flask-3.0.0-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

StegApp est une application web complète de stéganographie qui permet de cacher et extraire des données dans différents types de médias (images, audio, vidéo, PDF) avec une interface moderne et sécurisée.

## 🌟 Fonctionnalités

### Types de médias supportés
- **Images** : PNG, JPG, JPEG, BMP, TIFF (LSB)
- **Audio** : WAV PCM 16-bit (LSB)
- **Vidéo** : MP4, AVI, MOV (LSB sur frames)
- **PDF** : Métadonnées



## 🏗️ Architecture

```
stegapp/
├── backend/                 # API Flask
│   ├── stego/              # Modules de stéganographie
│   │   ├── image.py        # Stéganographie d'images
│   │   ├── audio.py        # Stéganographie audio
│   │   ├── video.py        # Stéganographie vidéo
│   │   ├── pdf_meta.py     # Stéganographie PDF
│   │   └── utils.py        # Utilitaires communs
│   ├── api.py              # API REST Flask
│   ├── requirements.txt    # Dépendances Python
│   └── tests/              # Tests pytest
├── frontend/               # Interface web
│   ├── index.html          # Page principale
│   └── app.js             # JavaScript Alpine.js
├── docker/                 # Configuration Docker
│   ├── Dockerfile          # Image de production
│   ├── Dockerfile.dev      # Image de développement
│   ├── docker-compose.yml  # Orchestration
│   └── nginx.conf          # Configuration Nginx
└── README.md              # Documentation
```

## 🚀 Installation et Démarrage

### Prérequis
- Docker et Docker Compose
- Python 3.11+ (pour le développement local)
- Node.js (optionnel, pour les outils de développement)

### Démarrage rapide avec Docker

```bash
# Cloner le projet
git clone <repository-url>
cd stegapp

# Démarrer l'application
docker-compose up -d

# L'application sera accessible sur http://localhost
```

### Développement local

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python api.py
```

#### Frontend
```bash
cd frontend
# Servir avec un serveur HTTP simple
python -m http.server 8000
# ou utiliser nginx/apache
```

### Mode développement avec Docker

```bash
# Démarrer avec les profils de développement
docker-compose --profile dev up

# Backend de développement sur http://localhost:5001
# Frontend sur http://localhost
```

## 🧪 Tests

```bash
cd backend
pytest tests/ -v --cov=stego
```

### Couverture de tests
- Tests unitaires pour chaque module
- Tests d'intégration pour l'API
- Tests de sécurité pour le chiffrement
- Tests de validation des fichiers

## 📖 Utilisation

### Interface web

1. **Cacher des données** :
   - Sélectionnez le type de fichier support
   - Uploadez votre fichier
   - Saisissez les données à cacher
   - Optionnel : ajoutez un mot de passe
   - Téléchargez le fichier modifié

2. **Extraire des données** :
   - Sélectionnez le type de fichier
   - Uploadez le fichier contenant des données cachées
   - Saisissez le mot de passe si nécessaire
   - Consultez les données extraites

### API REST

#### Endpoints disponibles

- `GET /api/health` - Vérification de santé
- `GET /api/supported-formats` - Formats supportés
- `POST /api/capacity/{type}` - Capacité d'un fichier
- `POST /api/hide/{type}` - Cacher des données
- `POST /api/extract/{type}` - Extraire des données

#### Exemple d'utilisation API

```bash
# Vérifier la santé de l'API
curl http://localhost:5000/api/health

# Obtenir la capacité d'une image
curl -X POST -F "file=@image.png" http://localhost:5000/api/capacity/image

# Cacher des données dans une image
curl -X POST \
  -F "file=@image.png" \
  -F "data=Hello World" \
  -F "password=secret" \
  http://localhost:5000/api/hide/image \
  --output hidden_image.png

# Extraire des données
curl -X POST \
  -F "file=@hidden_image.png" \
  -F "password=secret" \
  http://localhost:5000/api/extract/image
```

## 🔧 Configuration

### Variables d'environnement

```bash
# Backend
FLASK_ENV=production          # Environnement Flask
FLASK_DEBUG=0                 # Mode debug
MAX_CONTENT_LENGTH=104857600  # Taille max des fichiers (100MB)

# Docker
COMPOSE_PROJECT_NAME=stegapp  # Nom du projet Docker
```

### Nginx

Le fichier `docker/nginx.conf` configure :
- Proxy vers l'API Flask
- Compression gzip
- Rate limiting (10 req/s)
- Headers de sécurité
- Limite de taille de fichier (100MB)

## 🔒 Sécurité

### Chiffrement
- **Algorithme** : Fernet (AES 128 en mode CBC)
- **Dérivation de clé** : SHA-256 du mot de passe
- **Salt** : Géré automatiquement par Fernet

### Sécurité web
- **Headers de sécurité** : X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **Rate limiting** : 10 requêtes/seconde par IP
- **Validation des fichiers** : Types et tailles contrôlés
- **Utilisateur non-root** : Dans les conteneurs Docker

### Bonnes pratiques
- Utilisez des mots de passe forts
- Ne partagez jamais vos mots de passe
- Vérifiez l'intégrité des fichiers téléchargés
- Sauvegardez vos fichiers originaux

## 📊 Performance

### Capacités approximatives

| Type de fichier | Capacité maximale |
|----------------|------------------|
| Image 1000x1000 | ~3M bits (~375KB) |
| Audio 1 minute | ~44K bits (~5.5KB) |
| Vidéo 1 minute | Variable selon résolution |
| PDF | 64KB dans métadonnées |

### Optimisations
- Traitement en mémoire pour les petits fichiers
- Compression gzip pour les réponses API
- Cache des capacités de fichiers
- Rate limiting pour éviter les abus

## 🐛 Dépannage

### Problèmes courants

1. **"API non disponible"**
   - Vérifiez que le backend est démarré
   - Contrôlez les logs : `docker-compose logs backend`

2. **"Données trop volumineuses"**
   - Réduisez la taille des données
   - Utilisez un fichier support plus grand
   - Vérifiez la capacité avec `/api/capacity`

3. **"Aucune donnée cachée trouvée"**
   - Vérifiez le type de fichier
   - Assurez-vous que le fichier contient des données
   - Vérifiez le mot de passe si utilisé

### Logs

```bash
# Logs de l'application
docker-compose logs -f

# Logs du backend uniquement
docker-compose logs -f backend

# Logs de Nginx
docker-compose logs -f nginx
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

### Standards de code
- **Python** : PEP 8, type hints
- **JavaScript** : ES6+, Alpine.js patterns
- **Tests** : Couverture > 80%
- **Documentation** : Docstrings et commentaires

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- **Flask** - Framework web Python
- **Alpine.js** - Framework JavaScript léger
- **TailwindCSS** - Framework CSS utilitaire
- **Pillow** - Traitement d'images Python
- **OpenCV** - Traitement vidéo
- **PyPDF2** - Manipulation PDF
- **Cryptography** - Chiffrement Python

## 📞 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation
- Vérifiez les logs d'erreur

---

**StegApp** - Stéganographie sécurisée et moderne 🌟
