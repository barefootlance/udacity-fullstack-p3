from crud_api import Crud_API
from flask import render_template, flash, redirect
from flask import url_for, abort, jsonify
from database_setup import Category, Item
import datetime
import xmlify
import string

class Category_API(Crud_API):
    """Implements CRUD API calls for categories."""

# TODO: duplicate code
    def getCategories(self):
        """Convenience method to get all categories.
        """
        return self.db_session \
                   .query(Category) \
                   .order_by(Category.name).all()

    def getItems(self, category_id):
        """Convenience method to get all items for the given category.
        """
        return self.db_session.query(Item) \
                   .filter_by(category_id=category_id) \
                   .order_by(Item.name).all()

    def getAllItems(self):
        """Convenience method to get all items regardless of category.
        """
        return self.db_session.query(Item) \
                   .order_by(Item.name).all()

    def showAll(self, request, format=None):
        """Returns all the categories in a given format.

        Args:
            request - http request
            format - The desired format of the returned data,
                     one of 'JSON', 'XML', or None. None returns
                     the html for a web page.
        """
        try:
            categories = self.getCategories()
            if format == 'JSON':
                return jsonify(
                        Categories=[c.serialize for c in categories])
            elif format == 'XML':
                return string.replace(
                        xmlify.dumps([c.serialize for c in categories],
                        'categories'), 'categories-item', 'category')
            elif not format:
                items = self.getAllItems()
                return render_template('category_all.html',
                        categories=categories, category=None,
                        items=items, item=None)
            else:
                abort(501)
        except:
            abort(404)


    def show(self, category_id, request, format=None):
        """Returns the category in a given format.

        Args:
            category_id - category of the items
            item_id - the item id
            request - http request
            format - The desired format of the returned data,
                     one of 'JSON', 'XML', or None. None returns
                     the html for a web page.
        """
        try:
            category = self.db_session.query(Category) \
                           .filter_by(id=category_id).one()
            if format == 'JSON':
                return jsonify(Category=category.serialize)
            elif format == 'XML':
                return xmlify.dumps(category.serialize, 'category')
            elif format == None:
                return render_template('category.html',
                            category=category,
                            categories=self.getCategories(),
                            items=self.getItems(category.id))
            else:
                abort(501)
        except:
            abort(404)


    def new(self, login_session, request):
        """ Add a new category to the database.

        Args:
            login_session - flask session
            request - http request

        HTTP Methods:
            GET - returns a web page for the user to enter the
                  category information.
            POST - adds the category to the database and returns a web
                   page for the category.
        """

        if 'username' not in login_session:
            return redirect('/login')

        if request.method == 'POST':
            category = Category(
                name=request.form['name'],
                user_id=login_session['user_id'])
            self.db_session.add(category)
            self.db_session.commit()
            self.db_session.refresh(category)
            flash('New category %s successfully created.'%category.name)
            return redirect(url_for('newItem', category_id=category.id))
        else:
            return render_template('user/category_new.html',
                                   categories=self.getCategories())


    def edit(self, category_id, login_session, request):
        """ Change data for the given category.

        Args:
            category_id - the category
            login_session - flask session
            request - http request

        HTTP Methods:
            GET - returns a web page for the user to enter the category
                  information.
            POST - updates the category data and returns a web page for
                  the category.
        """

        if 'username' not in login_session:
            return redirect('/login')

        try:
            category = self.db_session.query(Category) \
                           .filter_by(id=category_id).one()
        except:
            abort(404)

        if category.user_id != login_session['user_id']:
            flash('''You are only authorized to edit categories
                     you created.''')
            return redirect(url_for('showItems',
                    category_id=category_id))

        if request.method == 'POST':
            category.name = request.form['name']
            self.db_session.commit()
            flash('Category %s successfully updated.' % category.name)
            return redirect(url_for('showItems',
                    category_id=category_id))
        else:
            return render_template('user/category_edit.html',
                        category=category,
                        categories=self.getCategories(),
                        items=self.getItems(category.id))


    def delete(self, category_id, login_session, request):
        """ Delete the given category.

        Args:
            category_id - the category for the item
            login_session - flask session
            request - http request

        HTTP Methods:
            GET - returns a web page for the user to confirm the deletion.
            POST - deletes the item and returns a web page for the catalog.
        """

        if 'username' not in login_session:
            return redirect('/login')

        try:
            category = self.db_session.query(Category) \
                           .filter_by(id=category_id).one()
        except:
            abort(404)

        if category.user_id != login_session['user_id']:
            flash('''You are only authorized to delete
                     categories you created.''')
            return redirect(url_for('showItems',
                            category_id=categuser_iduser_idory_id))

        if request.method == 'POST':
            name = category.name;
            items = self.db_session.query(Item) \
                        .filter_by(category_id=category_id).all()
            for item in items:
                self.db_session.delete(item)
            self.db_session.delete(category)
            self.db_session.commit()
            flash('Category %s successfully deleted.' % name)
            return redirect(url_for('showCategories'))
        else:
            return render_template('user/category_delete.html',
                                    category=category,
                                    categories=self.getCategories(),
                                    items=self.getItems(category.id))
