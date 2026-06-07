from app.db.models import PaymentInstructionRecord
from app.db.session import Base, engine


def init_db() -> None:
    _ = PaymentInstructionRecord
    Base.metadata.create_all(bind=engine)
