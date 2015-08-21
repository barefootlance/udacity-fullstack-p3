from flask import Flask, request, session as login_session, render_template, flash, redirect, url_for, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from category_api import Category_API
from item_api import Item_API
from google_session import Google_Session
from facebook_session import Facebook_Session
from amazon_session import Amazon_Session
from csrf import generate_csrf_token
import sys

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
    oauth2_session = Google_Session('secrets/google_secrets.json')
    result = oauth2_session.connect(request, login_session, db_session)
    return result


@app.route('/connect/facebook', methods=['POST'])
def facebookConnect():
    oauth2_session = Facebook_Session('secrets/facebook_secrets.json')
    result = oauth2_session.connect(request, login_session, db_session)
    return result


@app.route('/connect/amazon', methods=['GET'])
def amazonConnect():
    oauth2_session = Amazon_Session('secrets/amazon_secrets.json')
    result = oauth2_session.connect(request, login_session, db_session)
    #return result
    # TODO HACK: we're getting Amazon synchronously (which is how they
    # do it in their example). Would like it to behave like the other
    # logins (or maybe not - maybe they should act like this...consistency!)
    # Anyway, we hop straight back to the main page.
    return showCategories()


@app.route('/category/<int:category_id>/edit/', methods=['GET', 'POST'])
def editCategory(category_id):
    return category_api.edit(category_id, login_session, request)


@app.route('/category/<int:category_id>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_id):
    return category_api.delete(category_id, login_session, request)


@app.route('/login')
def showLogin():
    state = generate_csrf_token()
    login_session['state'] = state
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
        elif provider == 'amazon':
            oauth2_session = Amazon_Session('secrets/amazon_secrets.json')
            oauth2_session.disconnect(login_session)

        if oauth2_session:
            oauth2_session.clearCurrentUserInfo(login_session)

        del login_session['provider']

        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


@app.route('/category/<int:category_id>/JSON', methods=['GET'])
@app.route('/category/<int:category_id>/XML', methods=['GET'])
def categoryJSON(category_id):
    try:
        format = request.path.split('/')[-1]
        return category_api.show(category_id, request, format)
    except:
        abort(404)


@app.route('/category/JSON', methods=['GET'])
@app.route('/category/XML', methods=['GET'])
def categoriesJSON():
    try:
        format = request.path.split('/')[-1]
        return category_api.showAll(request, format)
    except:
        abort(404)


@app.route('/category/<int:category_id>/item/<int:item_id>/JSON', methods=['GET'])
@app.route('/category/<int:category_id>/item/<int:item_id>/XML', methods=['GET'])
def itemJSON(category_id, item_id):
    try:
        format = request.path.split('/')[-1]
        return item_api.show(category_id, item_id, request, format)
    except:
        abort(404)


@app.route('/category/<int:category_id>/item/JSON', methods=['GET'])
@app.route('/category/<int:category_id>/item/XML', methods=['GET'])
def itemsJSON(category_id):
    try:
        format = request.path.split('/')[-1]
        return item_api.showAll(category_id, request, format)
    except:
        abort(404)

### CSRF PROTECTION
# Drawn from http://flask.pocoo.org/snippets/3/
# NOTE: we implement CSRF protection two different
# ways. If we have access to the form then we include
# an invisible input in the form and use that to
# pass the nonce. However, if we don't have the form
# (as is the case with Oauth2 logins), we pass then
# value in the 'state' session value (as demonstrated
# in the oauth course sample).
@app.before_request
def csrf_protect():
    if request.method == "POST":
        token = login_session.pop('_csrf_token', None)
        print token
        print login_session.get('state')
        print request.form.get('_csrf_token')
        # not from this session
        if not token:
            abort(403)

        # Look for the form value first.
        # Doesn't match the value in the form (anything but oauth2 logins)
        if request.form.get('_csrf_token'):
            if token != request.form.get('_csrf_token'):
                abort(403)
        # Doesn't match the state value in the session (only oauth2 logins)
        elif login_session.get('state') != token:
            abort(403)

app.jinja_env.globals['csrf_token'] = generate_csrf_token
### END CSRF PROTECTION

if __name__ == '__main__':
    app.secret_key = 'ultra_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
