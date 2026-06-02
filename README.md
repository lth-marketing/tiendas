# Solicitud de material — La Tienda Home

App interna donde los comerciales de tienda solicitan material al equipo de
marketing. El flujo es:

1. El comercial selecciona **de qué tienda** es (Alfafar, Gandía, …).
2. Elige el **material** del catálogo, indica **unidades** y escribe el
   **motivo**. Puede añadir varias líneas de material.
3. Al enviar, la solicitud se reenvía a un **webhook de N8N** (configurable) y
   se guarda una copia en la base de datos.

## Stack

- **Backend**: Django + Django REST Framework (sirve la API y el SPA).
- **Frontend**: React + Vite.
- **Servidor**: Gunicorn + WhiteNoise (estáticos).
- **Despliegue**: un único contenedor Docker (Easypanel).

## Estructura

```
backend/    Proyecto Django (API + servir el SPA)
  catalog/config.json   Catálogo EDITABLE de tiendas y materiales
frontend/   App React (Vite)
Dockerfile  Build multi-stage (React -> Django runtime)
```

## Editar tiendas y materiales

Edita **`backend/catalog/config.json`**:

```json
{
  "stores": ["Alfafar", "Gandía", "..."],
  "materials": [
    { "id": "folletos", "name": "Folletos" }
  ]
}
```

Tras editarlo, reinicia el contenedor para que los cambios se reflejen.

## Variables de entorno

Ver `.env.example`. La más importante:

- `N8N_WEBHOOK_URL`: URL del webhook de N8N. Si está vacía, la solicitud se
  guarda pero no se reenvía (la app lo indica).
- `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_DEBUG`,
  `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_DB_PATH`.

## Payload enviado al webhook

```json
{
  "store": "Alfafar",
  "requester": "Nombre del comercial",
  "reason": "Motivo de la solicitud",
  "items": [{ "material": "folletos", "units": 100 }],
  "submitted_at": "2026-06-02T10:00:00+00:00"
}
```

## Desarrollo local

Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend (en otra terminal, con proxy al backend):

```bash
cd frontend
npm install
npm run dev
```

## Probar con Docker

```bash
docker build -t tiendas .
docker run -p 8000:8000 -e N8N_WEBHOOK_URL=https://webhook.site/xxxx tiendas
# abre http://localhost:8000
```

## Despliegue en Easypanel

1. Crea una **App** apuntando a este repositorio (rama `main`).
2. Build: **Dockerfile** (en la raíz). Puerto del contenedor: **8000**.
3. En **Environment**, define las variables (al menos `N8N_WEBHOOK_URL`,
   `DJANGO_SECRET_KEY` y `DJANGO_ALLOWED_HOSTS`).
4. (Opcional) Monta un **volumen** en `/data` y define
   `DJANGO_DB_PATH=/data/db.sqlite3` para conservar el histórico de solicitudes.
5. Despliega. El catálogo se edita en `backend/catalog/config.json`.
```
