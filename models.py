from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class Activity(Base):
    __tablename__ = 'activities'
    __table_args__ = (
        UniqueConstraint('url', name='uix_url'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    city = Column(String)
    venue = Column(String)
    address = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    age_range = Column(String)
    tags = Column(Text)  # 存储为JSON字符串
    url = Column(String)
    is_free = Column(Boolean)
    requires_registration = Column(Boolean)
    source = Column(String)
    last_updated = Column(String)

    def __init__(self, **kwargs):
        tags = kwargs.pop("tags", [])
        if isinstance(tags, list):
            kwargs["tags"] = json.dumps(tags)
        elif isinstance(tags, str):
            kwargs["tags"] = tags
        super().__init__(**kwargs)

    def to_dict(self):
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        return d

engine = create_engine('sqlite:///activities.db')
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine) 