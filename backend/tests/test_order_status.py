from app.utils.order_status import (
    CancellationDecision, OrderStatus, can_transition, cancellation_decision,
)


def test_normal_flow_is_allowed():
    assert can_transition(OrderStatus.PENDING, OrderStatus.CONFIRMED)
    assert can_transition(OrderStatus.CONFIRMED, OrderStatus.PROCESSING)
    assert can_transition(OrderStatus.PROCESSING, OrderStatus.SHIPPED)
    assert can_transition(OrderStatus.SHIPPED, OrderStatus.DELIVERED)


def test_cannot_skip_or_go_back():
    assert not can_transition(OrderStatus.PENDING, OrderStatus.DELIVERED)
    assert not can_transition(OrderStatus.SHIPPED, OrderStatus.PENDING)


def test_final_states_cannot_change():
    for new in OrderStatus:
        assert not can_transition(OrderStatus.DELIVERED, new)
        assert not can_transition(OrderStatus.CANCELLED, new)


def test_cancellation_rules():
    assert cancellation_decision(OrderStatus.PENDING) == CancellationDecision.DIRECT
    assert cancellation_decision(OrderStatus.CONFIRMED) == CancellationDecision.DIRECT
    assert cancellation_decision(OrderStatus.PROCESSING) == CancellationDecision.NEEDS_APPROVAL
    assert cancellation_decision(OrderStatus.SHIPPED) == CancellationDecision.NEEDS_APPROVAL
    assert cancellation_decision(OrderStatus.DELIVERED) == CancellationDecision.NOT_ALLOWED