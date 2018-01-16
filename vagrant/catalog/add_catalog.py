
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
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


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for Soccer
category1 = Category(user_id=1, name="Soccer")
session.add(category1)
session.commit()

category2 = Category(user_id=1, name="Basketball")
session.add(category2)
session.commit()

category3 = Category(user_id=1, name="Baseball")
session.add(category3)
session.commit()

category4 = Category(user_id=1, name="Frisbee")
session.add(category4)
session.commit()

category5 = Category(user_id=1, name="Snowboarding")
session.add(category5)
session.commit()

category6 = Category(user_id=1, name="Rock Climbing")
session.add(category6)
session.commit()

category7 = Category(user_id=1, name="Foosball")
session.add(category7)
session.commit()

category8 = Category(user_id=1, name="Skating")
session.add(category8)
session.commit()

category9 = Category(user_id=1, name="Hockey")
session.add(category9)
session.commit()

item1 = Item(user_id=1, name="Soccer Ball", description=" the ball used in the sport of association football", date=datetime.datetime.now(),category=category1)

session.add(item1)
session.commit()


item2 = Item(user_id=1, name="Goggles", description="for fine vision and long term well being", date=datetime.datetime.now(),category=category5)

session.add(item2)
session.commit()


item3 = Item(user_id=1, name="Snowboard", description=" for player to skie across the mountainous snow", date=datetime.datetime.now(),category=category5)

session.add(item3)
session.commit()

print ("added category and items of specified category!")
