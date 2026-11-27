from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.database import get_db
from app.models import User
from app.schemas.order import (
    CancelOut, CancelRequest, OrderCreate, OrderListOut, OrderOut, StatusUpdate,
)
from app.services import order_service
from app.utils.order_status import OrderStatus

router = APIRouter()


@router.post("", response_model=OrderOut, status_code=201, summary="Create order")
def create_order(
    body: OrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return order_service.create_order(db, body, user.id)


# "/my" must be declared before "/{order_id}", otherwise "my" is read as an order id
@router.get("/my", response_model=OrderListOut, summary="My orders")
def get_my_orders(
    status: OrderStatus | None = Query(None, description="Example: shipped"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return order_service.list_user_orders(db, user.id, status, page, page_size)


@router.get("/user/{user_id}", response_model=OrderListOut, summary="Orders of a customer")
def get_user_orders(
    user_id: int,
    status: OrderStatus | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # A customer may only ask for their own id. An admin may ask for anyone.
    if user.role != "admin" and user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail={"code": "FORBIDDEN", "message": "You can only view your own orders"},
        )
    return order_service.list_user_orders(db, user_id, status, page, page_size)


@router.get("/{order_id}", response_model=OrderOut, summary="Order details")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return order_service.get_order_for_user(db, order_id, user)


@router.patch(
    "/{order_id}/status",
    response_model=OrderOut,
    summary="Update status (admin)",
    dependencies=[Depends(require_admin)],
)
def update_status(order_id: int, body: StatusUpdate, db: Session = Depends(get_db)):
    return order_service.update_status(db, order_id, body.status)


@router.post("/{order_id}/cancel", response_model=CancelOut, summary="Request cancellation")
def cancel_order(
    order_id: int,
    body: CancelRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return order_service.cancel_order(db, order_id, body, user)