from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
default_db_path = os.path.join(current_dir, "../sqli_logs.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    prediction = Column(Integer) # 1 for injection, 0 for legitimate
    confidence = Column(Float)
    risk_level = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    blocked = Column(Boolean, default=False)
    
    # New observability fields
    source_ip = Column(String, default="127.0.0.1")
    endpoint = Column(String, default="/predict")
    attack_type = Column(String, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
