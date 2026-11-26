from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes import auth, chat, inventory, orders, products
from app.config import settings
from app.database import get_db

# Swagger मध्ये गट कसे दिसतील
tags_metadata = [
    {"name": "Health", "description": "Server आणि database चालू आहे का तपासा"},
    {"name": "Auth", "description": "Login आणि registration"},
    {"name": "Products", "description": "Products ची यादी आणि search"},
    {"name": "Inventory", "description": "Stock तपासणी आणि update"},
    {"name": "Orders", "description": "Orders आणि tracking"},
    {"name": "Chat", "description": "AI agents शी संवाद"},
]

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered e-commerce operations platform with specialized agents. "
                "All sample records are DEMO data.",
    version=settings.APP_VERSION,
    openapi_tags=tags_metadata,
    docs_url="/docs",     # Swagger UI
    redoc_url="/redoc",   # ReDoc
)

# React frontend ला backend शी बोलू देण्यासाठी
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "AI E-Commerce Agent",
    }


@app.get("/health/db", tags=["Health"])
def health_check_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}


# सर्व routers जोडा. सर्व पत्ते /api/v1 पासून सुरू होतात.
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=f"{PREFIX}/auth", tags=["Auth"])
app.include_router(products.router, prefix=f"{PREFIX}/products", tags=["Products"])
app.include_router(inventory.router, prefix=f"{PREFIX}/inventory", tags=["Inventory"])
app.include_router(orders.router, prefix=f"{PREFIX}/orders", tags=["Orders"])
app.include_router(chat.router, prefix=f"{PREFIX}/chat", tags=["Chat"])