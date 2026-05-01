# AI Assisted Drive — Backend

Courte documentation pour installer, configurer et lancer le backend.

Pré-requis

**Pré-requis**
- Python 3.10+
- Git

**Installation**
1. Créer et activer un environnement virtuel :

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

2. Installer les dépendances :

```bash
pip install -r requirements.txt
```

**Configuration**
Créer un fichier `.env` à la racine à partir de l'environement :

```bash
cp .env.example .env
```

Remarques :
- `GOOGLE_TOKEN_JSON` peut contenir le JSON complet (exporté depuis l'auth OAuth2) ou une chaîne encodée.
- Pour conserver une base Chroma existante, définissez `CHROMA_PATH` vers `data/chromadb`.

**Lancer le backend**

```bash
# depuis la racine du projet (avec l'environnement virtuel activé)
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Vérifier le health check :

```bash
curl http://127.0.0.1:8000/health
# -> {"status":"ok"}
```

Acceder à la documentation interactive : http://127.0.0.1:8000/docs

**Notes**
- Le script `scripts/generate_token.py` va aider à créer/renouveler `token.json` pour l'authentification Google.
- La configuration est chargée depuis `.env` par `backend/config.py`.