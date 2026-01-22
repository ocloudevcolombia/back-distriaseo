from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.auth.routers import auth_router
from app.api.users.users import user_router
from app.api.store.products.categories import categories_router
from app.api.store.products.products import products_router
from app.api.store.sales.api import sales_router
from app.api.store.customers.api import customers_router
from app.api.store.debt.api import debts_router
from app.api.store.orders.orders import orders_router
from app.api.store.returns.api import returns_router
from app.api.store.services.router import services_router
from app.api.github_deploy import webhook_router

# Middleware para evitar el cache en Swagger y ReDoc
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, proxy-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

# Configuración de logging detallada
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(title="Tienda Online API", debug=True)

# 🌍 CORS
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://distriaseo.vercel.app",
    "https://distriaseo.ocloudxx.lat"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True
)

# Middleware para evitar cache
app.add_middleware(NoCacheMiddleware)

# Manejador de excepciones global
@app.exception_handler(Exception)
async def validation_exception_handler(request, exc):
    logger.error(f"Error al procesar la solicitud: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

# 📦 Routers

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(sales_router)
app.include_router(debts_router)
app.include_router(returns_router)
app.include_router(services_router)
app.include_router(webhook_router)
