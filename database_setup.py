from sqlalchemy import *
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_serializer import SerializerMixin
import datetime

# создание экземпляра declarative_base
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    about = Column(String, nullable=True)
    email = Column(String, index=True, unique=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    created_date = Column(DateTime, default=datetime.datetime.now)
    news = relationship("News", back_populates='author')

class News(Base):
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, autoincrement=True)
    header = Column(String, nullable=True)
    text = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    author = relationship("User")

# создает экземпляр create_engine в конце файла
engine = create_engine('sqlite:///news.db',echo=True)

Base.metadata.create_all(engine)