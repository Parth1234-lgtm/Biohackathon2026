# PCOS Diagnostic Tool — React Frontend

Vite + React frontend for the PCOS diagnostic API.

## Run

```bash
cd pcos-frontend
npm install
npm run dev
```

Start the backend first (`uvicorn` on `http://127.0.0.1:8000`).

## Pages

- `/` — Patient intake form with demo auto-fill buttons
- `/results` — AI diagnostic summary, pathway flowchart, 3D protein viewer

## Stack

- Vite + React
- Tailwind CSS v4
- React Router
- axios
- 3Dmol.js (CDN in `index.html`)
