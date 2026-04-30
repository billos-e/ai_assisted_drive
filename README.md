# AI Assisted Drive — Backend

Courte documentation pour installer, configurer et lancer le backend.

Pré-requis
- Python 3.10+
- Git

Installation
1. Créer et activer un environnement virtuel:

   python3 -m venv .venv
   source .venv/bin/activate

2. Installer les dépendances:

   pip install -r requirements.txt

Configuration
1. Fournir les variables d'environnement (ou créer un fichier `.env` à la racine):

   GOOGLE_CLIENT_ID
   GOOGLE_CLIENT_SECRET
   GOOGLE_TOKEN_JSON    # contenu JSON du token OAuth2 (ou chemin vers le fichier)
   GOOGLE_DRIVE_ROOT_FOLDER_ID
   GEMINI_API_KEY
   GROQ_API_KEY
   API_BASE_URL         # optionnel, défaut: http://127.0.0.1:8000
   CHROMA_PATH          # optionnel, chemin vers la base Chroma (ex: data/chromadb)

2. Si vous avez déjà une base Chroma existante dans `data/chromadb`, définissez `CHROMA_PATH` sur ce dossier pour conserver les index.

Lancer le backend
1. Depuis la racine du projet (env virtuel activé):

   uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000

2. Vérifier l'état:

   GET http://127.0.0.1:8000/health

Notes
- Le script `scripts/generate_token.py` peut aider à créer/renouveler `token.json` pour l'authentification Google.
- Le code lit par défaut la configuration depuis un fichier `.env` si présent.
