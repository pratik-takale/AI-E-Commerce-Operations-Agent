from sqlalchemy.orm import Session, selectinload

from app.models import Order, OrderItem, SupportTicket


def get_by_id(db: Session, order_id: int) -> Order | None:
   
    return (
        db.query(Order)
        .options(selectinload(Order.items).selectinload(OrderItem.product))
        .filter(Order.id == order_id)
        .first()
    )


def get_for_update(db: Session, order_id: int) -> Order | None:
  
    return db.query(Order).filter(Order.id == order_id).with_for_update().first()


def list_by_user(
    db: Session, user_id: int, status: str | None, page: int, page_size: int
) -> tuple[list[Order], int]:
    query = db.query(Order).filter(Order.user_id == user_id)
    if status:
        query = query.filter(Order.status == status)

    total = query.count()
    items = (
        query.options(selectinload(Order.items))
        .order_by(Order.created_at.desc(), Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def find_pending_cancellation(db: Session, order_id: int) -> SupportTicket | None:
    return (
        db.query(SupportTicket)
        .filter(
            SupportTicket.order_id == order_id,
            SupportTicket.ticket_type == "cancellation",
            SupportTicket.status == "pending_approval",
        )
        .first()
    )


def create_cancellation_ticket(db: Session, order: Order, reason: str) -> SupportTicket:
    ticket = SupportTicket(
        user_id=order.user_id,
        order_id=order.id,
        ticket_type="cancellation",
        issue=reason,
        status="pending_approval",
        priority="medium",
    )
    db.add(ticket)
    db.flush()  # ticket.id 
    return ticket


def close_pending_cancellations(db: Session, order_id: int, new_status: str) -> None:
    tickets = (
        db.query(SupportTicket)
        .filter(
            SupportTicket.order_id == order_id,
            SupportTicket.ticket_type == "cancellation",
            SupportTicket.status == "pending_approval",
        )
        .all()
    )
    for t in tickets:
        t.status = new_status