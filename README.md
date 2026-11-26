# Milify

Milify uses Django REST Framework, PostgreSQL, Redis, Next.js and a FastAPI recommendation service. The interface is Persian and right-to-left. The backend dependencies are pinned in `requirements.txt` (Django 5.2) and the frontend dependencies in `frontend/package-lock.json` (Next.js 16).

## Start a clean development instance

Install Docker with Compose, Python 3.12, and Node.js 22. Copy `.env.example` to `.env`. Set `DJANGO_SECRET_KEY` to a fresh random value, set a local `POSTGRES_PASSWORD`, and set `DJANGO_DEBUG=true` only for local development.

```sh
docker compose config -q
docker compose up --build
```

Open the frontend at http://localhost:3000, the API schema at http://localhost:8000/api/docs/, and the recommendation service health endpoint at http://localhost:8001/health. The backend service applies migrations on startup. To create a local admin, run `docker compose exec backend python manage.py createsuperuser`.

Use an empty local PostgreSQL database for a first run. The database role running initial migrations needs permission to install `pg_trgm`, or the database administrator can install it before migration. The user activation migration changes the default for new records. Review legacy inactive accounts individually through the admin workflow.

For development outside Compose, export the environment variables from `.env` and point the PostgreSQL and Redis settings at development instances. Start the backend and frontend in separate terminals.

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

```sh
cd frontend
npm ci
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## External services

- Set the storage bucket and access credentials with the `AWS_*` settings. Provision private read access for subscription-only audio objects in Arvan storage before serving them. The API issues links signed for 15 minutes to eligible subscribers. Previously public objects require an ACL or bucket-policy change at the provider.
- Set SMTP variables to enable password recovery. During local development you can use Django's console email backend in a local settings module.
- Configure the same OAuth client ID in the backend and in `NEXT_PUBLIC_GOOGLE_CLIENT_ID` at frontend build time. Compose forwards `GOOGLE_CLIENT_ID` as the build argument.
- The ML service uses the model under `ml-service/models` inside its Docker volume. The health response indicates whether a model was loaded. Only load model artifacts from a trusted source.
- Replace exposed credentials from the upstream project with freshly issued values before configuring external services.

## Verification

Run backend tests against a local PostgreSQL instance with permission to create the test database and a dedicated Redis instance. Run frontend checks from `frontend`.

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

```sh
npx tsc --noEmit
npm run lint
npm test -- --runInBand
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run build
```

The Next.js production build fetches Vazirmatn from Google Fonts. On systems with a custom trust store, set `NEXT_TURBOPACK_EXPERIMENTAL_USE_SYSTEM_TLS_CERTS=1` to use trusted system certificates.

Simple JWT uses a database blacklist for rotated refresh tokens and logout. Run `python manage.py flushexpiredtokens` periodically to prune expired rows.

For the production proxy configuration, HTTPS environment settings, credential rotation
and advertising accounting, see [Production deployment](deploy/production.md).
Run the development Nginx profile with `docker compose --profile proxy up --build`.
The proxy listens on loopback port 8080.
