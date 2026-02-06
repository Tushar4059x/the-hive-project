from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

DATABASE_URL = "sqlite:///./hive_memory.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class LogModel(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    level = Column(String, index=True)  # INFO, SUCCESS, ERROR, CRITICAL
    message = Column(Text)
    agent_id = Column(String, index=True)
    
    # Economy / Metadata Fields
    forks = Column(Integer, default=0)
    hashrate = Column(String, default="0 H/s")
    strategy_name = Column(String, default="Unknown")
    
    payload_json = Column(Text, default="{}") # Store extra fields as JSON

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "message": self.message,
            "agent_id": self.agent_id,
            "forks": self.forks,
            "hashrate": self.hashrate,
            "strategy_name": self.strategy_name,
            "payload": json.loads(self.payload_json)
        }

def init_db():
    Base.metadata.create_all(bind=engine)

def insert_log(db, log_data: dict):
    # Extract known fields, put rest in payload_json
    known_keys = {"level", "message", "agent_id", "timestamp", "forks", "hashrate", "strategy_name"}
    payload = {k: v for k, v in log_data.items() if k not in known_keys}
    
    # Parse timestamp if string
    ts = log_data.get("timestamp")
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts)
        except ValueError:
            ts = datetime.now()
    elif not ts:
        ts = datetime.now()

    db_log = LogModel(
        timestamp=ts,
        level=log_data.get("level", "INFO"),
        message=log_data.get("message", ""),
        agent_id=log_data.get("agent_id", "unknown"),
        hashrate=log_data.get("hashrate", "0 H/s"),
        strategy_name=log_data.get("strategy_name", "Unknown"),
        payload_json=json.dumps(payload)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_recent_logs(db, limit=50):
    return db.query(LogModel).order_by(LogModel.id.desc()).limit(limit).all()[::-1]

def increment_forks(db, log_id: int):
    log = db.query(LogModel).filter(LogModel.id == log_id).first()
    if log:
        log.forks += 1
        db.commit()
        db.refresh(log)
        return log.forks
    return None

def get_leaderboard(db, limit=5):
    # Order by forks descending
    return db.query(LogModel).order_by(LogModel.forks.desc()).limit(limit).all()

def get_logs_by_agent(db, agent_id: str, limit=100):
    return db.query(LogModel).filter(LogModel.agent_id == agent_id).order_by(LogModel.id.desc()).limit(limit).all()
