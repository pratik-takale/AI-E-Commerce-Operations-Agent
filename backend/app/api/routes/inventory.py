from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.database import get_db
from app.schemas.inventory import InventoryOut, InventoryUpdate
from app.services import inventory_service

router = APIRouter()


@router.get(
    "/{product_id}",
    response_model=InventoryOut,
    summary="Check stock (logged-in users)",
    dependencies=[Depends(get_current_user)],
)
def check_stock(product_id: int, db: Session = Depends(get_db)):
    return inventory_service.get_inventory_status(db, product_id)


@router.patch(
    "/{product_id}",
    response_model=InventoryOut,
    summary="Update stock (admin)",
    dependencies=[Depends(require_admin)],
)
def update_stock(product_id: int, body: InventoryUpdate, db: Session = Depends(get_db)):
    return inventory_service.update_inventory(db, product_id, body)