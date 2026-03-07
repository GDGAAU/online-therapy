# Online Therapy Platform

This repository contains a full-stack online therapy platform with a Django REST backend and a SvelteKit frontend. 

## Repository structure

- `back-end/`: Django REST API (Djoser + SimpleJWT)
- `front-end/`: SvelteKit web app (Tailwind CSS, shadcn-style UI components)
- `docker-compose.yml`: Optional multi-service setup

## Requirements

### Backend

- Python 3.11+ (recommended)
- `pip` or a compatible package manager

### Frontend

- Bun (recommended) or Node.js 18+

## Environment configuration

Both apps include example environment files you can copy and adjust.

Backend:

```bash
cp back-end/.env.example back-end/.env
```

Frontend:

```bash
cp front-end/.env.example front-end/.env
```

Update the values in each `.env` file to match your local setup (database URL, API base URL, and any keys required by third-party services).

## Backend setup (Django)

From the repository root:

```bash
cd back-end
```

Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
python manage.py migrate
```

Start the API server:

```bash
python manage.py runserver
```

## Frontend setup (SvelteKit)

From the repository root:

```bash
cd front-end
```

Install dependencies:

```bash
bun install
```

Start the dev server:

```bash
bun run dev
```

Build for production:

```bash
bun run build
```

Preview the production build:

```bash
bun run preview
```

## Docker (optional)

You can also run the project with Docker Compose if you prefer containerized workflows.

```bash
docker compose up --build
```

## Key features

- Custom user model and profile data
- Djoser-based authentication with JWT access and refresh tokens
- Logout endpoint that clears refresh cookies
- Auth-aware frontend navigation and profile routing
- Modern login and signup UI

## Useful scripts

Backend tests:

```bash
cd back-end
python manage.py test
```

Frontend typecheck/lint (if configured):

```bash
cd front-end
bun run check
```

## Notes

- If you use Node.js instead of Bun, replace `bun` commands with `npm` or `pnpm` equivalents.
- If you do not have a `requirements.txt` in `back-end/`, install from `pyproject.toml` using your preferred tool (e.g., `pip install -e .`).
