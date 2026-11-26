from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.models import Inventory, Product


def get_by_id(db: Session, product_id: int) -> Product | None:
    return (
        db.query(Product)
        .options(joinedload(Product.inventory))
        .filter(Product.id == product_id, Product.is_active.is_(True))
        .first()
    )


def list_products(
    db: Session,
    category: str | None,
    q: str | None,
    min_price: float | None,
    max_price: float | None,
    in_stock: bool,
    page: int,
    page_size: int,
) -> tuple[list[Product], int]:
    query = db.query(Product).filter(Product.is_active.is_(True))

    # Category filter 
    if category:
        query = query.filter(func.lower(Product.category) == category.lower())

    # Search: 
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Product.name.ilike(like), Product.description.ilike(like)))

    # filter
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    
    if in_stock:
        query = query.join(Inventory).filter(Inventory.quantity > 0)

    total = query.count()  # pagination 

    items = (
        query.options(joinedload(Product.inventory))
        .order_by(Product.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def create(db: Session, data: dict, initial_stock: int, reorder_level: int) -> Product:
    product = Product(**data)
    db.add(product)
    db.flush()  # product.id 
    db.add(Inventory(product_id=product.id, quantity=initial_stock, reorder_level=reorder_level))
    db.commit()
    db.refresh(product)
    return product


def update(db: Session, product: Product, data: dict) -> Product:
    for field, value in data.items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


def soft_delete(db: Session, product: Product) -> None:
    product.is_active = False
    db.commit()
def get_active_by_ids(db: Session, product_ids: list[int]) -> list[Product]:
    return (
        db.query(Product)
        .filter(Product.id.in_(product_ids), Product.is_active.is_(True))
        .all()
    )