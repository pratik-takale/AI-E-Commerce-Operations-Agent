"""Create an admin user. Run from the backend folder: python scripts/create_admin.py"""
import getpass
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models import User
from app.utils.security import hash_password


def main() -> None:
    name = input("Admin name: ").strip()
    email = input("Admin email: ").strip().lower()
    password = getpass.getpass("Password (min 8 characters, letters and digits): ")

    if len(name) < 2 or "@" not in email or len(password) < 8:
        print("Invalid input. Nothing was created.")
        return

    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            print("A user with this email already exists.")
            return
        db.add(User(name=name, email=email, password_hash=hash_password(password), role="admin"))
        db.commit()
        print(f"Admin created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()