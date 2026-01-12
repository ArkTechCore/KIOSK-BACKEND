from passlib.context import CryptContext
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.models.store import Store

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def main():
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        store = session.get(Store, "S001")
        if not store:
            store = Store(
                id="S001",
                name="Quick Foods Clifton",
                password_hash=pwd.hash("demo1234"),
                active=True,
            )
            session.add(store)
            session.commit()
            print("✅ Created store S001 password=demo1234")
        else:
            print("ℹ️ Store S001 already exists")
    finally:
        session.close()

if __name__ == "__main__":
    main()
