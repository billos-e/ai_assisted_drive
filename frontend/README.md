# AI Assisted Drive — Frontend

Frontend application built with Vue.js and Vite for the AI Assisted Drive project.

## Prerequisites

- Node.js 18+ and npm

## Installation

```bash
cd frontend
npm install
```

## Configuration

Create a `.env.local` file (optional) to override the API URL:

```
VITE_API_URL=http://127.0.0.1:8000
```

## Development

```bash
npm run dev
```

The app will be available at `http://localhost:5173` with hot module reloading.

The dev server proxies API calls from `/api/*` to `http://127.0.0.1:8000`.

## Build

```bash
npm run build
```

The optimized production build is output to `dist/`.

## Architecture

### Pages
- **Repository** — File/folder browser and uploader
- **Chat** — AI chat interface with streaming responses
- **Settings** — Configuration (account, repository, chat settings)

### Components
- **Sidebar** — Navigation between pages

### Services
- **api.js** — API client for backend endpoints
- **icons.js** — File type icon utilities

### Styles
All styles use CSS variables for theming (`style.css`).

## Notes

- The app communicates with the backend API at `http://127.0.0.1:8000`
- Streaming chat responses are handled via the Fetch API
- File uploads support progress tracking
- The UI follows the specifications in `ui-specifications.md`
