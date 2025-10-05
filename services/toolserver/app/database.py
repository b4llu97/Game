from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Fact
import os
from typing import Optional, List

FACTS_DB_PATH = os.getenv("FACTS_DB_PATH", "/app/data/facts.db")

engine = create_engine(f"sqlite:///{FACTS_DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def set_fact(db: Session, key: str, value: str) -> Fact:
    fact = db.query(Fact).filter(Fact.key == key).first()
    if fact:
        fact.value = value
    else:
        fact = Fact(key=key, value=value)
        db.add(fact)
    
    db.commit()
    db.refresh(fact)
    return fact

def get_fact(db: Session, key: str) -> Optional[Fact]:
    return db.query(Fact).filter(Fact.key == key).first()

def list_all_facts(db: Session) -> List[Fact]:
    return db.query(Fact).all()

def delete_fact(db: Session, key: str) -> bool:
    fact = db.query(Fact).filter(Fact.key == key).first()
    if fact:
        db.delete(fact)
        db.commit()
        return True
    return False
