from crud_api import Crud_API
from flask import render_template, flash, redirect, url_for, abort, jsonify
from database_setup import Category, Item, User
from sqlalchemy import collate
import json
import datetime
import xmlify
import string

class Item_API(Crud_API):
    """Implements CRUD API calls for items."""

    def getItems(self, category_id):
        """Convenience method to get all items for the given category.
        """
        return self.db_session.query(Item) \
                   .filter_by(category_id=category_id) \
                   .order_by(collate(Item.name, 'NOCASE')) \
                   .all()

    def getCategories(self):
        """Convenience method to get all categories.
        """
        return self.db_session.query(Category) \
                   .order_by(collate(Category.name, 'NOCASE')) \
                   .all()

    def showAll(self, category_id, request, format=None):
        """Returns all the items from the a category in a given format.

        Args:
            category_id - category of the items
            request - http request
            format - The desired format of the returned data,
                     one of 'JSON', 'XML', or None. None returns
                     the html for a web page.
        """
        try:
            items = self.getItems(category_id)
            if format == 'JSON':
                return jsonify(Items=[i.serialize for i in items])
            elif format == 'XML':
                return string.replace(
                            xmlify.dumps([i.serialize for i in items],
                                         'items'),
                            'items-item',
                            'item')
            elif not format:
                category = self.db_session \
                               .query(Category) \
                               .filter_by(id=category_id) \
                               .one()
                categories = self.getCategories()
                user = self.db_session.query(User) \
                           .filter_by(id=category.user_id) \
                           .one()
                return render_template('item_all.html',
                                       category=category,
                                       categories=categories,
                                       items=items,
                                       item=None,
                                       user=user)
            else:
                abort(501)
        except:
            abort(404)


    def show(self, category_id, item_id, request, format=None):
        """Returns an item from the category in a given format.

        NOTE: the category_id should be the same as the
              Item.category_id. This relationship is loosely enforced,
              but if they're out of sync you probably have a database
              problem, so consider this a canary in your coal mine.

        Args:
            category_id - category of the items
            item_id - the item id
            request - http request
            format - The desired format of the returned data,
                     one of 'JSON', 'XML', or None. None returns
                     the html for a web page.
        """
        try:
            item = self.db_session.query(Item) \
                       .filter_by(category_id=category_id, id=item_id) \
                       .one()
            if format == 'JSON':
                return jsonify(Item=item.serialize)
            elif format == 'XML':
                return xmlify.dumps(item.serialize, 'item')
            elif not format:
                category = self.db_session.query(Category) \
                               .filter_by(id=category_id) \
                               .one()
                categories = self.getCategories()
                items = self.getItems(category_id)
                user = self.db_session.query(User) \
                           .filter_by(id=category.user_id) \
                           .one()
                return render_template('item.html',
                                       category=category,
                                       categories=categories,
                                       item=item,
                                       items=items,
                                       user=user)
            else:
                abort(501)
        except:
            abort(404)


    def new(self, category_id, login_session, request):
        """ Add a new item to the given category.

        Args:
            category_id - the category for the new item
            login_session - flask session
            request - http request

        HTTP Methods:
            GET - returns a web page for the user to enter the item
                  information.
            POST - adds the item to the database and returns a web page
                   for the item.
        """
        # make sure the category exists
        try:
            category = self.db_session.query(Category) \
                           .filter_by(id=category_id) \
                           .one()
        except:
            abort(404)

        if 'username' not in login_session:
            return redirect('/login')

        if request.method == 'POST':
            item = Item(
                name=request.form['name'],
                description=request.form['description'],
                image_url=request.form['image_url'],
                category_id=category_id,
                user_id=login_session['user_id'])
            self.db_session.add(item)
            self.db_session.commit()
            self.db_session.refresh(item)
            flash('New item %s successfully created.' % item.name)
            return redirect(url_for('showItem',
                                    category_id=category_id,
                                    item_id=item.id))
        else:
            return render_template('user/item_new.html',
                                   category=category,
                                   categories=self.getCategories(),
                                   items=self.getItems(category_id))


    def edit(self, category_id, item_id, login_session, request):
        """ Change data for the given item.

        Args:
            category_id - the category for the item
            item_id - the item
            login_session - flask session
            request - http request

        HTTP Methods:
            GET - returns a web page for the user to enter the item information.
            POST - updates the item data and returns a web page for the item.
        """
        try:
            category = self.db_session.query(Category) \
                           .filter_by(id=category_id) \
                           .one()
            item = self.db_session.query(Item) \
                       .filter_by(category_id=category_id, id=item_id) \
                       .one()
        except:
            abort(404)

        if 'username' not in login_session:
            return redirect('/login')

        if item.user_id != login_session['user_id']:
            flash('You are only authorized to edit items you created.')
            return redirect(url_for('showItem',
                                    category_id=category_id,
                                    item_id=item_id))

        if request.method == 'POST':
            item.name = request.form['name']
            item.description = request.form['description']
            item.image_url = request.form['image_url']
            self.db_session.commit()
            flash('Item %s successfully updated.' % item.name)
            return redirect(url_for('showItems',
                                    category_id=category_id))
        else:
            return render_template('user/item_edit.html',
                                   category=category,
                                   categories=self.getCategories(),
                                   item=item,
                                   items=self.getItems(category_id))


    def delete(self, category_id, item_id, login_session, request):
        """ Delete the given item.

        Args:
            category_id - the category for the item
            item_id - the item
            login_session - flask session
            request - http request

        HTTP Methods:
            GET - returns a web page for the user to confirm the
                  deletion.
            POST - deletes the item and returns a web page for the
                   category.
        """
        try:
            category = self.db_session.query(Category) \
                           .filter_by(id=category_id) \
                           .one()
            item = self.db_session.query(Item) \
                           .filter_by(category_id=category_id,
                                      id=item_id) \
                           .one()
        except:
            abort(404)

        if 'username' not in login_session:
            return redirect('/login')

        if item.user_id != login_session['user_id']:
            flash('''You are only authorized to delete
                     items you created.''')
            return redirect(url_for('showItem',
                                    category_id=category_id,
                                    item_id=item_id,
                                    items=self.getItems()))

        if request.method == 'POST':
            name = item.name;
            self.db_session.delete(item)
            self.db_session.commit()
            flash('Item %s successfully deleted.' % name)
            return redirect(url_for('showItems',
                                    category_id=category_id))
        else:
            return render_template('user/item_delete.html',
                                   category=category,
                                   categories=self.getCategories(),
                                   item=item,
                                   items=self.getItems(category_id))
