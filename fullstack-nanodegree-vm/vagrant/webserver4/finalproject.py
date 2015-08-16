from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine, collate
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

#Fake Restaurants - TODO: remove when DB is in place
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}
restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]
#Fake Menu Items - TODO: remove when DB is in place
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree', 'id':'1'}

engine = create_engine('sqlite:///restaurantmenu.db')
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

@app.route('/', methods=['GET'])
@app.route('/restaurants', methods=['GET'])
def showRestaurants():
    """Show all the restuarants in the database."""
    '''
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id)
    return render_template('menu.html', restaurant=restaurant, items=items)
    '''
    restaurants = session.query(Restaurant).order_by(collate(Restaurant.name, 'NOCASE')).all()
    if len(restaurants) == 0:
        flash('There are no restaurants in the database.')
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurants/new', methods=['GET','POST'])
def newRestaurant():
    """Add a new restaurant to the database."""
    if request.method == 'POST':
        newRestaurant = Restaurant(name=request.form['name'])
        session.add(newRestaurant)
        session.commit()
        flash('{R} added as a new restaurant.'.format(R=newRestaurant.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('newrestaurant.html')


@app.route('/restaurants/<int:restaurant_id>/edit', methods=['GET','POST'])
def editRestaurant(restaurant_id):
    """Edit an existing restaurant.

    Args:
        restaurant_id: (integer) Id of the restaurant in the database.
    """
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        oldName = restaurant.name
        if request.form['name']:
            restaurant.name = request.form['name']
        session.add(restaurant)
        session.commit()
        flash('{old} changed to {new}.'.format(old=oldName, new=restaurant.name))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('editrestaurant.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/delete', methods=['GET','POST'])
def deleteRestaurant(restaurant_id):
    """Delete an existing restaurant.

    Args:
        restaurant_id: (integer) Id of the restaurant in the database.
    """
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if request.method == 'POST':
        oldName = restaurant.name
        session.delete(restaurant)
        session.commit()
        flash('{R} deleted.'.format(R=oldName))
        return redirect(url_for('showRestaurants'))
    else:
        return render_template('deleterestaurant.html', restaurant=restaurant)


@app.route('/restaurants/<int:restaurant_id>/', methods=['GET'])
@app.route('/restaurants/<int:restaurant_id>/menu', methods=['GET'])
def showMenu(restaurant_id):
    """Show all the menu items for a restaurant.

    Args:
        restaurant_id: (integer) Id of the restaurant in the database.
    """
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).order_by(collate(MenuItem.name, 'NOCASE')).all()
    if len(items) == 0:
        flash('There are no menu items for this restaurant.')
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurants/<int:restaurant_id>/menu/new', methods=['GET','POST'])
def newMenuItem(restaurant_id):
    """Add a new menu item for a restaurant.

    Args:
        restaurant_id: (integer) Id of the restaurant in the database.
    """
    if request.method == 'POST':
        newItem = MenuItem(
            name=request.form['name'],
            description=request.form['description'],
            price=request.form['price'],
            course=request.form['course'],
            restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        flash('New menu item {I} added.'.format(I=newItem.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    """Edit an existing menu item for a restaurant.

    Args:
        restaurant_id: (integer) Id of the restaurant in the database.
        menu_id: (integer) Id of the menu item in the database.
    """
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['course']:
            editedItem.course = request.form['course']
        if request.form['price']:
            editedItem.price = request.form['price']
        session.add(editedItem)
        session.commit()
        flash('Menu item {I} changed.'.format(I=editedItem.name))
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id=restaurant_id, item=editedItem)


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
    """Delete an existing menu item for a restaurant.

    Args:
        restaurant_id: (integer) Id of the restaurant in the database.
        menu_id: (integer) Id of the menu item in the database.
    """
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    if request.method == 'POST':
        oldName = editedItem.name
        session.delete(editedItem)
        session.commit()
        flash('Menu item {I} deleted.'.format(I=oldName))
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant_id=restaurant_id, item=editedItem)


@app.route('/restaurants/JSON')
def restaurantMenuJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[r.serialize for r in restaurants])


@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantsJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurants/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def restaurantMenuItemJSON(restaurant_id, menu_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(
        restaurant_id=restaurant_id, id=menu_id).one()
    return jsonify(MenuItem=item.serialize)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key' # TODO: need better key for production
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
