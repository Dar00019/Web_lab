from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, News

engine = create_engine('sqlite:///news.db',echo=True)
# Свяжем engine с метаданными класса Base
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# Экземпляр DBSession() отвечает за все обращения к базе данных
# и представляет «промежуточную зону» для всех объектов,
# загруженных в объект сессии базы данных.
session = DBSession()

user1 = User(name="user1", email="user1@mail.ru")
user2 = User(name="user2", email="user2@mail.ru")
news1 = News(text = "Новость1", author = user1)
news2 = News(text = "Новость2", author = user2)
news3 = News(text = "Новость3", author = user2)

session.add(user1)
session.add(user2)
session.add(news1)
session.add(news2)
session.add(news3)
session.commit()


