# TwoCards Demo Stack

Simple FastAPI backend with React (Vite) frontend for demonstrating product listing and order submission.

## Development

Use the bundled helper script (Linux/macOS) to install dependencies, launch both services, and open the browser automatically:

```bash
./run_dev.sh
```

Alternatively start each service manually:

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

## Deployment

- Backend expects `DATABASE_URL` if you want PostgreSQL instead of SQLite.
- Frontend is Netlify-ready via the included `netlify.toml` which builds the Vite project located in `frontend/` and serves the generated `dist` directory.
- Configure `VITE_API_BASE` environment variable in Netlify to point to the deployed backend URL.
