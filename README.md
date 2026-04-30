# AI Assisted Drive — Backend

Courte documentation pour installer, configurer et lancer le backend.

Pré-requis

**Pré-requis**
- Python 3.10+
- Git

**Installation**
1. Créer et activer un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

**Configuration**
Créer un fichier `.env` à la racine (ou exporter les variables d'environnement). Exemple minimal :

```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
# Peut contenir le JSON complet du token ou le chemin vers un fichier
GOOGLE_TOKEN_JSON='{"token":"..."}'
GOOGLE_DRIVE_ROOT_FOLDER_ID=your-root-folder-id
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
API_BASE_URL=http://127.0.0.1:8000
# CHROMA_PATH par défaut pointe vers backend/chroma_db
# CHROMA_PATH=data/chromadb    # si vous avez une base Chroma existante
```

Remarques :
- `GOOGLE_TOKEN_JSON` peut contenir le JSON complet (exporté depuis l'auth OAuth2) ou une chaîne encodée.
- Pour conserver une base Chroma existante, définissez `CHROMA_PATH` vers `data/chromadb`.

**Lancer le backend**

```bash
# depuis la racine du projet (avec l'environnement virtuel activé)
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Vérifier le health check :

```bash
curl http://127.0.0.1:8000/health
# -> {"status":"ok"}
```

**Utilitaires**
- Le script `scripts/generate_token.py` aide à créer/renouveler `token.json` pour l'authentification Google.
- La configuration est chargée depuis `.env` par `backend/config.py`.

# AI Assisted Drive — Backend

Courte documentation : installer, configurer et lancer le backend.

**Pré-requis**
- Python 3.10+
- Git

**Installation**
1. Créer et activer un environnement virtuel :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

**Configuration**
Créer un fichier `.env` à la racine (ou exporter les variables d'environnement). Exemple minimal :

```env
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
# Peut contenir le JSON complet du token ou le chemin vers un fichier
GOOGLE_TOKEN_JSON='{"token":"..."}'
GOOGLE_DRIVE_ROOT_FOLDER_ID=your-root-folder-id
GEMINI_API_KEY=your-gemini-key
GROQ_API_KEY=your-groq-key
API_BASE_URL=http://127.0.0.1:8000
# CHROMA_PATH par défaut pointe vers backend/chroma_db
# CHROMA_PATH=data/chromadb    # si vous avez une base Chroma existante
```

Remarques :
- `GOOGLE_TOKEN_JSON` peut contenir le JSON complet (exporté depuis l'auth OAuth2) ou une chaîne encodée.
- Pour conserver une base Chroma existante, définissez `CHROMA_PATH` vers `data/chromadb`.

**Lancer le backend**

```bash
# depuis la racine du projet (avec l'environnement virtuel activé)
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Vérifier le health check :

```bash
curl http://127.0.0.1:8000/health
# -> {"status":"ok"}
```

**Utilitaires**
- Le script `scripts/generate_token.py` aide à créer/renouveler `token.json` pour l'authentification Google.
- La configuration est chargée depuis `.env` par `backend/config.py`.
   http://127.0.0.1:8000/docs

Notes
- Le script `scripts/generate_token.py` va aider à créer/renouveler `token.json` pour l'authentification Google.
- Le code lit par défaut la configuration depuis un fichier `.env` si présent.
