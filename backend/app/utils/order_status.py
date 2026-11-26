from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"



ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.PENDING: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.PROCESSING, OrderStatus.CANCELLED},
    OrderStatus.PROCESSING: {OrderStatus.SHIPPED, OrderStatus.CANCELLED},
    OrderStatus.SHIPPED: {OrderStatus.DELIVERED, OrderStatus.CANCELLED},
    OrderStatus.DELIVERED: set(),   
    OrderStatus.CANCELLED: set(),   
}


def can_transition(current: OrderStatus, new: OrderStatus) -> bool:
    return new in ALLOWED_TRANSITIONS[current]


class CancellationDecision(str, Enum):
    DIRECT = "direct"                  
    NEEDS_APPROVAL = "needs_approval" 
    NOT_ALLOWED = "not_allowed"        


def cancellation_decision(status: OrderStatus) -> CancellationDecision:
    if status in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
        return CancellationDecision.DIRECT
    if status in (OrderStatus.PROCESSING, OrderStatus.SHIPPED):
        return CancellationDecision.NEEDS_APPROVAL
    return CancellationDecision.NOT_ALLOWED