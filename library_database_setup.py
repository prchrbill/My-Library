import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class MyLibrary(Base):

    __tablename__ = 'mylibrary'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class MyBook(Base):

    __tablename__ = 'my_books'

    title = Column(String(120), nullable=False)
    id = Column(Integer, primary_key=True)
    author = Column(String(50))
    description = Column(String(1000))
    catalog = Column(String(20))
    mylibrary_id = Column(Integer, ForeignKey('mylibrary.id'))
    mylibrary = relationship(MyLibrary)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
            """Return object data in easily serializeable format"""
            return {
                'title': self.title,
                'description': self.description,
                'id': self.id,
                'catalog': self.catalog,
                'author': self.author,
            }


engine = create_engine('postgresql:////var/www/FlaskApps/mywebsite/mylibrary.db')
Base.metadata.create_all(engine)

print "added library items!"
