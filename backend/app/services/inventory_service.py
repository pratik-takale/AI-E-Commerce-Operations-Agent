from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import inventory_repository, product_repository
from app.schemas.inventory import InventoryOut, InventoryUpdate


def check_inventory(quantity: int) -> str:
    """ business logic: stock """
    if quantity > 0:
        return "In Stock"
    return "Out of Stock"


def is_low_stock(quantity: int, reorder_level: int) -> bool:
    return quantity <= reorder_level


def get_inventory_status(db: Session, product_id: int) -> InventoryOut:
    """ function पुढे Inventory Agent tool ."""
    product = product_repository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    inv = inventory_repository.get_by_product_id(db, product_id)
    if not inv:
        inv = inventory_repository.create(db, product_id)

    return InventoryOut(
        product_id=product.id,
        product_name=product.name,
        quantity=inv.quantity,
        reorder_level=inv.reorder_level,
        status=check_inventory(inv.quantity),
        in_stock=inv.quantity > 0,
        low_stock=is_low_stock(inv.quantity, inv.reorder_level),
        updated_at=inv.updated_at,
    )


def update_inventory(db: Session, product_id: int, body: InventoryUpdate) -> InventoryOut:
    data = body.model_dump(exclude_none=True)
    if not data:
        raise HTTPException(status_code=400, detail="Send quantity or reorder_level")

    product = product_repository.get_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    inv = inventory_repository.get_by_product_id(db, product_id)
    if not inv:
        inv = inventory_repository.create(db, product_id)

    inventory_repository.update(db, inv, data)
    return get_inventory_status(db, product_id)