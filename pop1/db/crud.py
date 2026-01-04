from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime
from .models import Flat, PriceHistory, AppState

def get_app_state(db: Session, key: str) -> str | None:
    row = db.query(AppState).filter_by(key=key).first()
    return row.value if row else None

def set_app_state(db: Session, key: str, value: str):
    row = db.query(AppState).filter_by(key=key).first()
    if row:
        row.value = value
    else:
        db.add(AppState(key=key, value=value))
    db.commit()

def get_flat_by_avito_id(db: Session, avito_id: str) -> Flat | None:
    return db.query(Flat).filter_by(avito_id=avito_id).first()

def create_flat(db: Session, data: dict, district: str):
    flat = Flat(
        avito_id=data["avito_id"],
        url=data["url"],
        title=data["title"],
        price=data["price"],
        district=district,
    )
    try:
        db.add(flat)
        db.commit()
    except IntegrityError:
        db.rollback()

def update_price(db: Session, flat: Flat, new_price: int):
    flat.updated_at = datetime.utcnow()
    flat.price = new_price
    db.commit()

def add_price_history(db: Session, flat_id: int, old: int, new: int):
    db.add(
        PriceHistory(
            flat_id=flat_id,
            old_price=old,
            new_price=new,
        )
    )
    db.commit()
