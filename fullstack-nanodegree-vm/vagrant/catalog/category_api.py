from crud_api import Crud_API
from flask import render_template, flash, redirect, url_for, abort, jsonify
from database_setup import Category, Item
import datetime
import xmlify
import string

class Category_API(Crud_API):
    """Implements CRUD API calls for categories."""

# TODO: duplicate code
    def getCategories(self):
        return self.db_session.query(Category).order_by(Category.name).all()

    def getItems(self, category_id):
        return self.db_session.query(Item).filter_by(category_id=category_id).order_by(Item.name).all()

    def showAll(self, request, format=None):
        try:
            categories = self.getCategories()
            if format == 'JSON':
                return jsonify(Categories=[c.serialize for c in categories])
            elif format == 'XML':
                return string.replace(xmlify.dumps([c.serialize for c in categories], 'categories'), 'categories-item', 'category')
            elif not format:
                return render_template('category_all.html', categories=categories, category=None, items=None, item=None)
            else:
                abort(501)
        except:
            abort(404)


    def show(self, category_id, request, format=None):
        try:
            category = self.db_session.query(Category).filter_by(id=category_id).one()
            if format == 'JSON':
                return jsonify(Category=category.serialize)
            elif format == 'XML':
                return xmlify.dumps(category.serialize, 'category')
            elif format == None:
                return render_template('category.html', category=category, categories=self.getCategories(), items=self.getItems(category.id))
            else:
                abort(501)
        except:
            abort(404)


    def new(self, login_session, request):

        if 'username' not in login_session:
            return redirect('/login')

        if request.method == 'POST':
            category = Category(
                name=request.form['name'],
                user_id=login_session['user_id'])
            self.db_session.add(category)
            self.db_session.commit()
            self.db_session.refresh(category)
            flash('New category %s successfully created.' % category.name)
            return redirect(url_for('newItem', category_id=category.id))
        else:
            return render_template('user/category_new.html', user_id=login_session['user_id'], categories=self.getCategories())


    def edit(self, category_id, login_session, request):
        try:
            category = self.db_session.query(Category).filter_by(id=category_id).one()
        except:
            abort(404)

        if 'username' not in login_session:
            return redirect('/login')

        if category.user_id != login_session['user_id']:
            flash('You are only authorized to edit categories you created.')
            return redirect(url_for('showItems', category_id=category_id))

        if request.method == 'POST':
            category.name = request.form['name']
            self.db_session.commit()
            flash('Category %s successfully updated.' % category.name)
            return redirect(url_for('showCategories'))
        else:
            return render_template('user/category_edit.html', category=category, categories=self.getCategories(), items=self.getItems(category.id))


    def delete(self, category_id, login_session, request):
        try:
            category = self.db_session.query(Category).filter_by(id=category_id).one()
        except:
            abort(404)


        if 'username' not in login_session:
            return redirect('/login')

        if category.user_id != login_session['user_id']:
            flash('You are only authorized to delete categories you created.')
            return redirect(url_for('showItems', category_id=categuser_iduser_idory_id))

        if request.method == 'POST':
            name = category.name;
            items = self.db_session.query(Item).filter_by(category_id=category_id).all()
            for item in items:
                self.db_session.delete(item)
            self.db_session.delete(category)
            self.db_session.commit()
            flash('Category %s successfully deleted.' % name)
            return redirect(url_for('showCategories'))
        else:
            return render_template('user/category_delete.html', category=category, categories=self.getCategories(), items=self.getItems(category.id))
