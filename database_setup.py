import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):

    __tablename__ = 'user'

    """ Table for user information.
    Columns:
        id: Distinct user id.
        name: Name of the user.
        email: E-Mail of the user.
        picture: Path to external profile picture.
    """

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):

    __tablename__ = 'category'

    """ Table for Category information.
    Columns:
        id: Distinct catalog id.
        name: name of category
        user_id: user id of user that created category
    """

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name
        }


class Item(Base):
    __tablename__ = 'item'

    """ Table for Item information.
    Columns:
        id: Distinct item id.
        title: title of item
        description: description of item
        cat_id: category id of item.
        user_id: user id of user that created item
    """

    title = Column(String(100), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(2000))
    cat_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):

        return {
            'title': self.title,
            'description': self.description,
            'id': self.id,
            'cat_id': self.cat_id
        }

engine = create_engine('sqlite:///category.db')


Base.metadata.create_all(engine)
