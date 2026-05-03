# AI Assisted Drive — Backend

Le backend est une API FastAPI qui gère l'indexation des fichiers Google Drive et le moteur de recherche RAG.

## 📋 Pré-requis

- **Python 3.10+**
- Un compte **Google Cloud** (pour les credentials Drive API)
- Une clé API **Groq** ou **Google AI** (Gemini)

## 🛠️ Installation

1. **Créer l'environnement virtuel :**
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configuration :**
   Copiez le fichier d'exemple :
   ```bash
   cp .env.example .env
   ```
   Remplissez les variables dans le `.env` :
   - Les clés **Google** (`GOOGLE_CLIENT_ID` et `GOOGLE_CLIENT_SECRET`) se trouvent dans le fichier **`credentials.json`** que vous téléchargez depuis la Google Cloud Console (OAuth 2.0 Client ID).
   - Une fois ces deux clés renseignées, lancez `python scripts/generate_token.py` pour générer automatiquement le `GOOGLE_TOKEN_JSON` dans votre `.env`.

## 🚀 Lancement

Pour démarrer le serveur de développement :
```bash
uvicorn main:app --reload
```

Le serveur sera disponible sur : **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
- **Documentation API** : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check** : [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

## 📁 Structure Clé

- `main.py` : Point d'entrée de l'API.
- `drive/` : Client pour l'interaction avec Google Drive.
- `vectorstore/` : Gestion de la base de données vectorielle (ChromaDB).
- `chat/` : Logique de communication avec les LLMs.