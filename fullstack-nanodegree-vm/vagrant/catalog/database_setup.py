"""
This is a utility file for creating the database and its Object
Relational Mapping (ORM). If you don't already have a database
you'll need to run this to create an empty one.

USAGE:
    python database_setup.py
"""
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime


Base = declarative_base()

def isoDateString(datetime):
    """Returns a date time string formatted correctly for
    international utc. Used for serializing our objects to ensure
    that we get a real, honest-to-goodness ISO formatted string
    including time zone that other apps can read in correctly.
    NOTE: YES, ALL OUR TIMESTAMPS ARE UTC. YOURS SHOULD BE TOO!
    """
    return datetime.isoformat() + "+00:00"

class User(Base):
    """
    Class representing a website user.

    FIELDS:
        name - the display name of the user
        email - the email, used as a unique identifier
        image_url - (optional) link to a picture of the user
        created_on - utc time of record creation
        updated_on - utc time of the most recent modification
    """
    # TODO: the email is a unique string which we get using Oauth2.
    # HOWEVER! Not all Oauth2 providers yield an email (Reddit, for
    # example, does not). Further other providers give more than
    # one email. AND EVEN FURTHER, some providers allow their users
    # to change their email addresses. The bottom line is that
    # the email is not a reliable unique identifier across providers.
    # The database needs to be changed to track a "provider_user_id",
    # which would be a string that varies from provider to provider.
    # AND, what do you do when a user logs in with different providers?
    # Because a google id and a facebook id would be different, AND
    # what about having multiple google accounts...? In short this
    # is too simple a solution for the real world and needs to be
    # revisited.
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    image_url = Column(String(250))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)


class Category(Base):
    """
    Class representing a category.

    FIELDS:
        name - the display name of the category
        created_on - utc time of record creation
        updated_on - utc time of the most recent modification
        user_id - (relation) the User who created this category
    """
    # TODO:
    # automatically delete the items just by setting the option
    # ON DELETE CASCADE in the database schema definition.
    # Look at the SQLAlchemy documentation at
    # http://docs.sqlalchemy.org/en/rel_0_9/orm/cascades.html
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'id'         : self.id,
           'name'       : self.name,
           'created_on' : isoDateString(self.created_on),
           'updated_on' : isoDateString(self.updated_on),
           'user_id'    : self.user_id,
       }


class Item(Base):
    """
    Class representing a category item.

    FIELDS:
        name - the display name of the item
        description - (optional) a brief description of the item
        image_url - (optional) link to a picture of the item
        created_on - utc time of record creation
        updated_on - utc time of the most recent modification
        category_id - (relation) the Category this item belongs to
        user_id - (relation) the User who created this item
    """
    __tablename__ = 'item'

    id = Column(Integer, primary_key = True)
    name =Column(String(80), nullable = False)
    description = Column(String(250))
    image_url = Column(String(250))
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    updated_on = Column(DateTime,
                        default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
            'id'            : self.id,
            'category_id'   : self.category_id,
            'name'          : self.name,
            'description'   : self.description,
            'image_url'     : self.image_url,
            'created_on'    : isoDateString(self.created_on),
            'updated_on'    : isoDateString(self.updated_on),
            'user_id'       : self.user_id,
       }


#engine = create_engine('sqlite:///catalog.db')
engine = create_engine("postgresql+psycopg2://catalog:catalog@/catalog")
Base.metadata.create_all(engine)
