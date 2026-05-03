# AI Assisted Drive

AI Assisted Drive est un assistant intelligent qui se connecte à votre Google Drive pour indexer vos documents et vous permettre d'interagir avec eux via une interface de chat. Il utilise le **RAG (Retrieval-Augmented Generation)** pour fournir des réponses précises basées sur vos propres fichiers.

## 🌟 Fonctionnalités

- **Synchronisation Drive** : Connectez votre compte Google et sélectionnez un dossier racine.
- **Indexation Intelligente** : Extraction automatique du texte des PDF, Word, Excel, Images (OCR), etc.
- **Chat Contextuel** : Posez des questions à vos documents avec des réponses sourcées.
- **Interface Moderne** : Design premium, minimaliste et réactif.

## 🏗️ Structure du Projet

Le projet est divisé en deux parties principales :

- **`/backend`** : Serveur API construit avec **FastAPI**. Il gère l'authentification Google, le téléchargement des fichiers, l'indexation dans la base de données vectorielle (**ChromaDB**) et la communication avec l'IA (**Groq/Gemini**).
- **`/frontend`** : Application web construite avec **Vue.js 3** et **Vite**. Elle offre une expérience fluide pour naviguer dans vos fichiers et discuter avec l'assistant.

## 🛠️ Stack Technique

### Backend
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![ChromaDB](https://img.shields.io/badge/ChromaDB-white?style=for-the-badge&logo=google-cloud&logoColor=4285F4)
![Google Drive](https://img.shields.io/badge/Google%20Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)

### Frontend
![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)

### AI & LLM
![Groq](https://img.shields.io/badge/Groq-orange?style=for-the-badge)
![Gemini](https://img.shields.io/badge/Google%20Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white)


## 🚀 Démarrage Rapide

Pour lancer le projet, vous devez démarrer le backend et le frontend séparément :

1. Consulter le [README du Backend](./backend/README.md) pour l'installation et la configuration de l'API.
2. Consulter le [README du Frontend](./frontend/README.md) pour lancer l'interface utilisateur.

---

Développé avec ❤️ pour une gestion de fichiers plus intelligente.
