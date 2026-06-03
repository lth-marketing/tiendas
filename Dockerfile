# --- Etapa 1: build del frontend React (Vite) ------------------------------
FROM node:20-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Etapa 2: runtime Django + Gunicorn -------------------------------------
FROM python:3.12-slim AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    DJANGO_DB_PATH=/data/db.sqlite3

WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ ./backend/
# Estáticos del frontend generados en la etapa anterior.
COPY --from=frontend /app/frontend/dist ./frontend/dist

WORKDIR /app/backend

# Recopila los estáticos (incluye el build de React) para servirlos con WhiteNoise.
RUN python manage.py collectstatic --noinput

EXPOSE 8000

# Migra, crea/actualiza el superusuario del admin (si hay credenciales) y arranca Gunicorn.
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py ensure_superuser && gunicorn core.wsgi:application --bind 0.0.0.0:${PORT} --workers 3"]
