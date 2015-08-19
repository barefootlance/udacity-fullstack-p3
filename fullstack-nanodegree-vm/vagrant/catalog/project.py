from flask import Flask, request, session as login_session, render_template, flash, redirect, url_for, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from category_api import Category_API
from item_api import Item_API
from google_session import Google_Session
from facebook_session import Facebook_Session
import random, string, sys

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
    return category_api.showAll(request)


@app.route('/category/<int:category_id>/', methods=['GET'])
def showCategory(category_id):
    # TODO: do we want to do something different here?
    #return category_api.show(category_id, request)
    return showItems(category_id)


@app.route('/category/new/', methods=['GET', 'POST'])
def newCategory():
    return category_api.new(login_session, request)


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    return category_api.edit(category_id, login_session, request)


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    return category_api.delete(category_id, login_session, request)


@app.route('/category/<int:category_id>/item/', methods=['GET'])
def showItems(category_id):
    return item_api.showAll(category_id, request)


@app.route('/category/<int:category_id>/item/<int:item_id>/', methods=['GET'])
def showItem(category_id, item_id):
    return item_api.show(category_id, item_id, request)


@app.route('/category/<int:category_id>/item/new/', methods=['GET', 'POST'])
def newItem(category_id):
    return item_api.new(category_id, login_session, request)


@app.route('/category/<int:category_id>/item/<int:item_id>/edit/', methods=['GET', 'POST'])
def editItem(category_id, item_id):
    return item_api.edit(category_id, item_id, login_session, request)


@app.route('/category/<int:category_id>/item/<int:item_id>/delete/', methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    return item_api.delete(category_id, item_id, login_session, request)


@app.route('/connect/google', methods=['POST'])
def googleConnect():
    #if oauth2_session:
    #    oauth2_session.disconnect()
    oauth2_session = Google_Session('secrets/google_secrets.json')
    result = oauth2_session.connect(request, login_session, db_session)
    return result


@app.route('/connect/facebook', methods=['POST'])
def facebookConnect():
    #if oauth2_session:
    #    oauth2_session.disconnect()
    oauth2_session = Facebook_Session('secrets/facebook_secrets.json')
    result = oauth2_session.connect(request, login_session, db_session)
    return result


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    return category_api.edit(category_id, login_session, request)


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    return category_api.delete(category_id, login_session, request)

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        oauth2_session = None
        provider = login_session['provider']
        if provider == 'google':
            oauth2_session = Google_Session('secrets/google_secrets.json')
            oauth2_session.disconnect(login_session)
        elif provider == 'facebook':
            oauth2_session = Facebook_Session('secrets/facebook_secrets.json')
            oauth2_session.disconnect(login_session)

        if oauth2_session:
            oauth2_session.clearCurrentUserInfo(login_session)

        del login_session['provider']

        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


@app.route('/category/<int:category_id>/JSON')
@app.route('/category/<int:category_id>/XML')
def categoryJSON(category_id):
    try:
        format = request.path.split('/')[-1]
        return category_api.show(category_id, request, format)
    except:
        abort(404)


@app.route('/category/JSON')
@app.route('/category/XML')
def categoriesJSON():
    try:
        format = request.path.split('/')[-1]
        return category_api.showAll(request, format)
    except:
        abort(404)


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON')
@app.route('/category/<int:category_id>/item/<int:item_id>/XML')
def itemJSON(category_id, item_id):
    try:
        format = request.path.split('/')[-1]
        return item_api.show(category_id, item_id, request, format)
    except:
        abort(404)


@app.route('/category/<int:category_id>/item/JSON')
@app.route('/category/<int:category_id>/item/XML')
def itemsJSON(category_id):
    try:
        format = request.path.split('/')[-1]
        return item_api.showAll(category_id, request, format)
    except:
        abort(404)


if __name__ == '__main__':
    app.secret_key = 'ultra_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
