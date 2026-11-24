"""Seed DEMO data. This is sample data only, not real retailer inventory."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import bcrypt

from app.core.database import SessionLocal
from app.models import (
    Conversation, Document, Inventory, Message,
    Order, OrderItem, Product, SupportTicket, User,
)

DEMO_NOTE = "[DEMO DATA] "
DEMO_PASSWORD = "Demo@1234"


def hash_pw(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def make_order(db, user, items, status, address):
    total = sum(p.price * qty for p, qty in items)
    order = Order(
        user_id=user.id, total_amount=total, status=status,
        shipping_address=address, is_demo=True,
    )
    db.add(order)
    db.flush()
    for product, qty in items:
        db.add(OrderItem(order_id=order.id, product_id=product.id,
                         quantity=qty, unit_price=product.price))
    return order


def seed():
    db = SessionLocal()
    try:
        if db.query(User).count() > 0:
            print("Database already has data. Skipping seed.")
            return

        # Users
        admin = User(name="Demo Admin", email="admin@demo.example.com",
                     password_hash=hash_pw(DEMO_PASSWORD), role="admin")
        rahul = User(name="Demo Customer Rahul", email="rahul@demo.example.com",
                     password_hash=hash_pw(DEMO_PASSWORD), role="customer")
        priya = User(name="Demo Customer Priya", email="priya@demo.example.com",
                     password_hash=hash_pw(DEMO_PASSWORD), role="customer")
        db.add_all([admin, rahul, priya])
        db.flush()

        # Products: (name, description, price, category, stock)
        catalog = [
            ("iPhone 16", "Smartphone with a 6.1-inch display and dual camera.", 65000, "Smartphones", 25),
            ("Samsung Galaxy", "Android smartphone with AMOLED display and 5000 mAh battery.", 35000, "Smartphones", 40),
            ("HP Laptop", "14-inch laptop, 16 GB RAM, 512 GB SSD.", 48000, "Laptops", 15),
            ("Dell Laptop", "15.6-inch laptop, 16 GB RAM, 512 GB SSD.", 52000, "Laptops", 8),
            ("Wireless Headphones", "Over-ear Bluetooth headphones with 30-hour battery.", 3499, "Audio", 60),
            ("Smart Watch", "Fitness smartwatch with heart-rate and sleep tracking.", 4999, "Wearables", 5),
        ]
        products = {}
        for name, desc, price, category, stock in catalog:
            p = Product(name=name, description=DEMO_NOTE + desc, price=price,
                        category=category, is_demo=True)
            db.add(p)
            db.flush()
            db.add(Inventory(product_id=p.id, quantity=stock, reorder_level=10))
            products[name] = p

        # Orders
        addr = "Demo Address, Pune, Maharashtra 411001"
        o1 = make_order(db, rahul, [(products["iPhone 16"], 1)], "shipped", addr)
        o2 = make_order(db, priya, [(products["Dell Laptop"], 1)], "delivered", addr)
        make_order(db, rahul, [(products["HP Laptop"], 1), (products["Wireless Headphones"], 2)],
                   "pending", addr)
        make_order(db, priya, [(products["Samsung Galaxy"], 1)], "confirmed", addr)

        # Support tickets
        db.add(SupportTicket(user_id=priya.id, order_id=o2.id, ticket_type="complaint",
                             issue="[DEMO] Laptop arrived with a scratched lid.", priority="high"))
        db.add(SupportTicket(user_id=rahul.id, order_id=o1.id, ticket_type="cancellation",
                             issue="[DEMO] Ordered by mistake, please cancel.", status="pending_approval"))

        # Sample conversation
        conv = Conversation(user_id=rahul.id, session_id="demo-session-001")
        db.add(conv)
        db.flush()
        db.add(Message(conversation_id=conv.id, role="user", content="Where is my order?"))
        db.add(Message(conversation_id=conv.id, role="assistant",
                       content="[DEMO] Your order is on the way.", agent_used="order_tracking"))

        # Documents for RAG (embeddings will be generated later)
        db.add_all([
            Document(title="Demo Return Policy", source="policy",
                     content="[DEMO] Items can be returned within 7 days of delivery if unused."),
            Document(title="Demo Cancellation Policy", source="policy",
                     content="[DEMO] Orders can be cancelled before shipping. Shipped orders need admin approval."),
            Document(title="Demo Warranty FAQ", source="faq",
                     content="[DEMO] Laptops and smartphones include a 1-year manufacturer warranty."),
        ])

        db.commit()
        print("Demo data inserted successfully.")
        print(f"Demo login password for all users: {DEMO_PASSWORD}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()