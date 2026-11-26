import math
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Inventory, Order, OrderItem, User
from app.repositories import inventory_repository, order_repository, product_repository
from app.schemas.order import (
    CancelOut, CancelRequest, OrderCreate, OrderItemOut, OrderListOut,
    OrderOut, OrderSummary,
)
from app.utils.order_status import (
    ALLOWED_TRANSITIONS, CancellationDecision, OrderStatus,
    can_transition, cancellation_decision,
)


def _fail(status_code: int, code: str, message: str, **extra):
    
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message, **extra})


def _to_out(order: Order) -> OrderOut:
    items = [
        OrderItemOut(
            product_id=i.product_id,
            product_name=i.product.name,
            quantity=i.quantity,
            unit_price=float(i.unit_price),
            line_total=float(i.unit_price * i.quantity),
        )
        for i in order.items
    ]
    return OrderOut(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=float(order.total_amount),
        shipping_address=order.shipping_address,
        is_demo=order.is_demo,
        created_at=order.created_at,
        items=items,
    )


def _restore_stock(db: Session, order: Order) -> None:
    
    product_ids = sorted({i.product_id for i in order.items})
    stocks = inventory_repository.get_many_for_update(db, product_ids)
    for item in order.items:
        inv = stocks.get(item.product_id)
        if inv:
            inv.quantity += item.quantity
        else:
            db.add(Inventory(product_id=item.product_id, quantity=item.quantity))


# ---------- Create ----------

def create_order(db: Session, body: OrderCreate) -> OrderOut:
    user = db.get(User, body.user_id)
    if not user:
        _fail(404, "USER_NOT_FOUND", "User not found")

    
    wanted: dict[int, int] = {}
    for it in body.items:
        wanted[it.product_id] = wanted.get(it.product_id, 0) + it.quantity
    ids = sorted(wanted)

    try:
        # 1) Products active check
        products = {p.id: p for p in product_repository.get_active_by_ids(db, ids)}
        missing = [i for i in ids if i not in products]
        if missing:
            _fail(404, "PRODUCT_NOT_FOUND", f"Products not found: {missing}")

        #2
        stocks = inventory_repository.get_many_for_update(db, ids)
        problems = []
        for pid in ids:
            available = stocks[pid].quantity if pid in stocks else 0
            if available < wanted[pid]:
                problems.append(
                    f"{products[pid].name}: requested {wanted[pid]}, available {available}"
                )
        if problems:
            _fail(400, "INSUFFICIENT_STOCK", "Not enough stock", items=problems)

        
        order = Order(
            user_id=body.user_id,
            total_amount=Decimal("0"),
            status=OrderStatus.PENDING.value,
            shipping_address=body.shipping_address,
        )
        db.add(order)
        db.flush()  

        total = Decimal("0")
        for pid in ids:
            price = Decimal(str(products[pid].price))  
            qty = wanted[pid]
            total += price * qty
            db.add(OrderItem(order_id=order.id, product_id=pid, quantity=qty, unit_price=price))
            stocks[pid].quantity -= qty
        order.total_amount = total

        db.commit()  
    except Exception:
        db.rollback()  
        raise

    return get_order(db, order.id)


# ---------- Read ----------

def get_order(db: Session, order_id: int) -> OrderOut:
    order = order_repository.get_by_id(db, order_id)
    if not order:
        _fail(404, "ORDER_NOT_FOUND", "Order not found")
    return _to_out(order)


def list_user_orders(
    db: Session, user_id: int, status: OrderStatus | None, page: int, page_size: int
) -> OrderListOut:
    if not db.get(User, user_id):
        _fail(404, "USER_NOT_FOUND", "User not found")

    items, total = order_repository.list_by_user(
        db, user_id, status.value if status else None, page, page_size
    )
    return OrderListOut(
        items=[
            OrderSummary(
                id=o.id,
                status=o.status,
                total_amount=float(o.total_amount),
                item_count=sum(i.quantity for i in o.items),
                is_demo=o.is_demo,
                created_at=o.created_at,
            )
            for o in items
        ],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
    )


# ---------- Status update (admin) ----------

def update_status(db: Session, order_id: int, new_status: OrderStatus) -> OrderOut:
    try:
        order = order_repository.get_for_update(db, order_id)
        if not order:
            _fail(404, "ORDER_NOT_FOUND", "Order not found")

        current = OrderStatus(order.status)
        if current == new_status:
            _fail(400, "STATUS_UNCHANGED", f"Order is already {current.value}")

        if not can_transition(current, new_status):
            allowed = sorted(s.value for s in ALLOWED_TRANSITIONS[current])
            if current == OrderStatus.DELIVERED:
                msg = "Delivered orders are final. Use the return/refund process instead."
            elif current == OrderStatus.CANCELLED:
                msg = "Cancelled orders are final."
            else:
                msg = f"Cannot change status from {current.value} to {new_status.value}."
            _fail(400, "INVALID_STATUS_TRANSITION", msg, allowed_next=allowed)

        if new_status == OrderStatus.CANCELLED:
            _restore_stock(db, order)
            order_repository.close_pending_cancellations(db, order.id, "approved")

        order.status = new_status.value
        db.commit()
    except Exception:
        db.rollback()
        raise

    return get_order(db, order_id)


# ---------- Cancellation ----------

def cancel_order(db: Session, order_id: int, body: CancelRequest) -> CancelOut:
    try:
        order = order_repository.get_for_update(db, order_id)
        if not order:
            _fail(404, "ORDER_NOT_FOUND", "Order not found")

        current = OrderStatus(order.status)

        if current == OrderStatus.CANCELLED:
            _fail(400, "ALREADY_CANCELLED", "This order is already cancelled.")

        decision = cancellation_decision(current)

        if decision == CancellationDecision.NOT_ALLOWED:
            _fail(
                400,
                "CANCEL_NOT_ALLOWED",
                "Delivered orders cannot be cancelled. "
                "Please raise a return or refund request instead.",
            )

        if decision == CancellationDecision.DIRECT:
            _restore_stock(db, order)
            order.status = OrderStatus.CANCELLED.value
            db.commit()
            return CancelOut(
                order_id=order.id,
                result="cancelled",
                order_status=OrderStatus.CANCELLED.value,
                message="Order cancelled and stock restored.",
            )

      
        if order_repository.find_pending_cancellation(db, order.id):
            _fail(
                400,
                "CANCELLATION_ALREADY_REQUESTED",
                "A cancellation request for this order is already waiting for admin approval.",
            )

        ticket = order_repository.create_cancellation_ticket(db, order, body.reason)
        db.commit()
        return CancelOut(
            order_id=order.id,
            result="pending_approval",
            order_status=current.value,
            message="Cancellation request sent to admin for approval.",
            ticket_id=ticket.id,
        )
    except Exception:
        db.rollback()
        raise