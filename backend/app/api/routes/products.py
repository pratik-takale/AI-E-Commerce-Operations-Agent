from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Product

router = APIRouter()


@router.get("")
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.is_active.is_(True)).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "category": p.category,
            "in_stock": bool(p.inventory and p.inventory.quantity > 0),
            "is_demo": p.is_demo,
        }
        for p in products
    ]