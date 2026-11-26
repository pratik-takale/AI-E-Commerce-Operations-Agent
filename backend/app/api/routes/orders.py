from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import (
    CancelOut, CancelRequest, OrderCreate, OrderListOut, OrderOut, StatusUpdate,
)
from app.services import order_service
from app.utils.order_status import OrderStatus

router = APIRouter()


@router.post("", response_model=OrderOut, status_code=201, summary="Create order")
def create_order(body: OrderCreate, db: Session = Depends(get_db)):
    return order_service.create_order(db, body)


@router.get("/user/{user_id}", response_model=OrderListOut, summary="Customer orders")
def get_user_orders(
    user_id: int,
    status: OrderStatus | None = Query(None, description="उदा. shipped"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return order_service.list_user_orders(db, user_id, status, page, page_size)


@router.get("/{order_id}", response_model=OrderOut, summary="Order details")
def get_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.get_order(db, order_id)


@router.patch("/{order_id}/status", response_model=OrderOut, summary="Update status")
def update_status(order_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    return order_service.update_status(db, order_id, body.status)


@router.post("/{order_id}/cancel", response_model=CancelOut, summary="Request cancellation")
def cancel_order(order_id: int, body: CancelRequest, db: Session = Depends(get_db)):
    return order_service.cancel_order(db, order_id, body)