from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind(engine)

DBSession = sessionmaker(bind = engine)
session = DBSession()

myfirstRestaurant = Restaurant("Pizza Palace")
session.add(myfirstRestaurant)
session.commit()

cheesePizza = MenuItem(
                name="Cheese Pizza",
                description="Made with all natural ingredients and fresh mozzarella"),
                course="Entree",
                price="8.99",
                restaurant=myfirstRestaurant)

session.add(cheesePizza)
session.commit()
