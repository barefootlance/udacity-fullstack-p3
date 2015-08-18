from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base
from category_api import Category_API
from item_api import Item_API

app = Flask(__name__)

# Connect to Database and create database session
# good sqlalchemy tips: http://alextechrants.blogspot.com/2013/11/10-common-stumbling-blocks-for.html
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
db_session = DBSession()

category_api = Category_API(db_session)
item_api = Item_API(db_session)


def getCurrentUserId(): # TODO!
    return None

@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
@app.route('/category/', methods=['GET'])
def showCategories():
    return category_api.showAll(getCurrentUserId(), request)


@app.route('/category/<int:category_id>/', methods=['GET'])
def showCategory(category_id):
    return category_api.show(category_id, getCurrentUserId(), request)


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    return category_api.new(getCurrentUserId(), request)


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    return category_api.edit(category_id, getCurrentUserId(), request)


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    return category_api.delete(category_id, getCurrentUserId(), request)


@app.route('/category/<int:category_id>/item/', methods=['GET'])
def showItems(category_id):
    return item_api.showAll(category_id, getCurrentUserId(), request)


@app.route('/category/<int:category_id>/item/<int:item_id>/', methods=['GET'])
def showItem(category_id, item_id):
    return item_api.show(category_id, item_id, getCurrentUserId(), request)


@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    return item_api.new(category_id, getCurrentUserId(), request)


@app.route('/category/<int:category_id>/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    return item_api.edit(category_id, item_id, getCurrentUserId(), request)


@app.route('/category/<int:category_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    return item_api.delete(category_id, item_id, getCurrentUserId(), request)


if __name__ == '__main__':
    app.secret_key = 'ultra_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
