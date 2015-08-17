from flask import Flask
from category_api import Category_API
from item_api import Item_API

app = Flask(__name__)

category_api = Category_API()
item_api = Item_API()


def getCurrentUserId(): # TODO!
    return None

@app.route('/', methods=['GET'])
@app.route('/catalog/', methods=['GET'])
@app.route('/category/', methods=['GET'])
def showCategories():
    return category_api.showAll(getCurrentUserId())


@app.route('/category/<int:category_id>/', methods=['GET'])
def showCategory(category_id):
    return category_api.show(category_id, getCurrentUserId())


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    return category_api.new(getCurrentUserId())


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    return category_api.edit(category_id, getCurrentUserId())


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    return category_api.delete(category_id, getCurrentUserId())


@app.route('/category/<int:category_id>/item/', methods=['GET'])
def showItems(category_id):
    return item_api.showAll(category_id, getCurrentUserId())


@app.route('/category/<int:category_id>/item/<int:item_id>/', methods=['GET'])
def showItem(category_id, item_id):
    return item_api.show(category_id, item_id, getCurrentUserId())


@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    return item_api.new(category_id, getCurrentUserId())


@app.route('/category/<int:category_id>/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    return item_api.edit(category_id, item_id, getCurrentUserId())


@app.route('/category/<int:category_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id, item_id):
    return item_api.delete(category_id, item_id, getCurrentUserId())


if __name__ == '__main__':
    app.secret_key = 'ultra_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
