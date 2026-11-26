from sqlalchemy.orm import Session

from app.models import Inventory


def get_by_product_id(db: Session, product_id: int) -> Inventory | None:
    return db.query(Inventory).filter(Inventory.product_id == product_id).first()


def create(db: Session, product_id: int) -> Inventory:
    inv = Inventory(product_id=product_id, quantity=0, reorder_level=10)
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


def update(db: Session, inv: Inventory, data: dict) -> Inventory:
    for field, value in data.items():
        setattr(inv, field, value)
    db.commit()
    db.refresh(inv)
    return inv