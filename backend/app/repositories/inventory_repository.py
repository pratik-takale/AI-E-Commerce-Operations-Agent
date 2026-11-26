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

def get_many_for_update(db: Session, product_ids: list[int]) -> dict[int, Inventory]:
    
    rows = (
        db.query(Inventory)
        .filter(Inventory.product_id.in_(product_ids))
        .order_by(Inventory.product_id)
        .with_for_update()
        .all()
    )
    return {r.product_id: r for r in rows}