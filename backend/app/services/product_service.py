import math

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Product
from app.repositories import product_repository
from app.schemas.product import ProductCreate, ProductListOut, ProductOut, ProductUpdate
from app.services.inventory_service import check_inventory


def to_out(product: Product) -> ProductOut:
    """Database object response"""
    quantity = product.inventory.quantity if product.inventory else 0
    return ProductOut(
        id=product.id,
        name=product.name,
        description=product.description,
        price=float(product.price),
        category=product.category,
        is_active=product.is_active,
        is_demo=product.is_demo,
        quantity=quantity,
        stock_status=check_inventory(quantity),
    )


def list_products(
    db: Session, category, q, min_price, max_price, in_stock, page, page_size
) -> ProductListOut:
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(status_code=400, detail="min_price cannot be greater than max_price")

    items, total = product_repository.list_products(
        db, category, q, min_price, max_price, in_stock, page, page_size
    )
    return ProductListOut(
        items=[to_out(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


def get_product(db: Session, product_id: int) -> ProductOut:
    product = product_repository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return to_out(product)


def create_product(db: Session, body: ProductCreate) -> ProductOut:
    data = body.model_dump(exclude={"initial_stock", "reorder_level"})
    product = product_repository.create(db, data, body.initial_stock, body.reorder_level)
    return to_out(product)


def update_product(db: Session, product_id: int, body: ProductUpdate) -> ProductOut:
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="Send at least one field to update")
    product = product_repository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return to_out(product_repository.update(db, product, data))


def delete_product(db: Session, product_id: int) -> None:
    product = product_repository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product_repository.soft_delete(db, product)