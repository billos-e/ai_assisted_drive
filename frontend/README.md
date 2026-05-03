# AI Assisted Drive — Frontend

L'interface utilisateur de l'assistant AI Assisted Drive, construite avec Vue.js 3 et Vite.

## 📋 Pré-requis

- **Node.js 18+**
- **npm** (ou yarn)

## 🛠️ Installation

1. **Naviguer dans le dossier frontend :**
   ```bash
   cd frontend
   ```

2. **Installer les dépendances :**
   ```bash
   npm install
   ```

3. **Configuration (Optionnel) :**
   Le frontend est configuré pour communiquer avec le backend sur `http://127.0.0.1:8000`. Si vous devez changer cela, créez un fichier `.env.local` :
   ```env
   VITE_API_URL=http://votre-url-api
   ```

## 🚀 Lancement

Pour lancer l'application en mode développement :
```bash
npm run dev
```

L'application sera accessible sur : **[http://localhost:5173](http://localhost:5173)**

## 📦 Build (Production)

Pour générer les fichiers statiques optimisés :
```bash
npm run build
```
Le résultat sera dans le dossier `dist/`.

## 📁 Structure

- `src/pages/` : Les vues principales (Repository, Chat, Settings).
- `src/components/` : Composants UI réutilisables.
- `src/services/` : Client API et utilitaires.
- `src/style.css` : Design system et styles globaux.
