from crud_api import Crud_API
from flask import render_template, flash, redirect, url_for, abort, jsonify
from database_setup import Category, Item

class Category_API(Crud_API):
    """Implements CRUD API calls for categories."""

    def showAll(self, request, format=None):
        try:
            categories = self.db_session.query(Category).all()
            if format == 'JSON':
                return jsonify(Categories=[c.serialize for c in categories])
            elif not format:
                return render_template('category_all.html', categories=categories)
            else:
                abort(501)
        except:
            abort(404)


    def show(self, category_id, request, format=None):
        try:
            category = self.db_session.query(Category).filter_by(id=category_id).one()
            if format == 'JSON':
                return jsonify(Category=category.serialize)
            elif format == None:
                return render_template('category.html', category=category)
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
            flash('New category %s successfully created.' % category.name)
            return redirect(url_for('showCategories'))
        else:
            return render_template('user/category_new.html', user_id=login_session['user_id'])


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
            return render_template('user/category_edit.html', user_id=1, category=category) # TODO user_id


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
            return render_template('user/category_delete.html', user_id=user_id, category=category)
