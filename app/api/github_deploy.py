# webhook.py
from fastapi import APIRouter, Request
import subprocess
import hmac
import hashlib
import logging
from dotenv import load_dotenv
import os

load_dotenv()


# Crear un logger para manejar los errores
logger = logging.getLogger(__name__)

# Crear el router
webhook_router = APIRouter(tags=["Webhook"])

# Tu secreto (puedes generarlo en GitHub)
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

@webhook_router.post("/git-webhook")
async def git_webhook(request: Request):
    # 1. Verificar que la solicitud es realmente de GitHub utilizando el secreto
    signature = request.headers.get("X-Hub-Signature-256")
    if signature is None:
        logger.error("No signature found")
        return {"message": "No signature found"}, 400

    body = await request.body()
    expected_signature = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, signature):
        logger.error("Invalid signature")
        return {"message": "Invalid signature"}, 400
    
    # 2. Realizar git pull para traer los cambios
    try:
        subprocess.run(["git", "pull"], cwd="/home/ubuntu/tienda-online-backend", check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Error pulling git changes: {e}")
        return {"message": "Error pulling git changes", "error": str(e)}, 500
    
    # 3. Ejecutar Alembic para aplicar las migraciones (si hay cambios)
    try:
        subprocess.run(["alembic", "upgrade", "head"], cwd="/home/ubuntu/tienda-online-backend", check=True)
        return {"message": "Repositorio actualizado y migraciones aplicadas"}
    except subprocess.CalledProcessError as e:
        logger.error(f"Error applying alembic migrations: {e}")
        return {"message": "Hubo un error al aplicar migraciones", "error": str(e)}, 500
