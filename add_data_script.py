from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///category.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

user1 = User(name="Fatih", email="fatih@fatih.com", picture="testurl")
session.add(user1)
session.commit()
# Menu for UrbanBurger
category1 = Category(name="Soccer", user=user1)

session.add(category1)
session.commit()

item11 = Item(title="Ball", description="Ball", category=category1, user=user1)

session.add(item11)
session.commit()

item12 = Item(
    title="Shoes",
    description="Football shoes",
    category=category1,
    user=user1)

session.add(item12)
session.commit()


category2 = Category(name="Basketball", user=user1)

session.add(category2)
session.commit()

category3 = Category(name="Baseball", user=user1)

session.add(category3)
session.commit()

item31 = Item(title="Gear", description="Gear", category=category3, user=user1)
session.add(item31)
session.commit()

item32 = Item(
    title="Gloves",
    description="Gloves",
    category=category3,
    user=user1)
session.add(item32)
session.commit()

category4 = Category(name="Frisbee")

session.add(category4)
session.commit()

item41 = Item(
    title="Watch",
    description="Scorekeeping watch",
    category=category4,
    user=user1)
session.add(item41)
session.commit()

item42 = Item(
    title="Gloves",
    description="Gloves",
    category=category4,
    user=user1)
session.add(item42)
session.commit()

category5 = Category(name="Snowboarding", user=user1)

session.add(category5)
session.commit()

item51 = Item(
    title="Googles",
    description="Googles",
    category=category5,
    user=user1)

session.add(item51)
session.commit()

item52 = Item(
    title="Snowboard",
    description="Snowboards",
    category=category5,
    user=user1)

session.add(item52)
session.commit()

category6 = Category(name="Rock Climbing", user=user1)

session.add(category6)
session.commit()

category7 = Category(name="Foosball", user=user1)

session.add(category7)
session.commit()

category8 = Category(name="Skating", user=user1)

session.add(category8)
session.commit()

category9 = Category(name="Hockey", user=user1)

session.add(category9)
session.commit()

print "added items!"
