from crud_api import Crud_API
from flask import render_template, flash, redirect, url_for
from database_setup import Category, Item

class Category_API(Crud_API):
    """Implements CRUD API calls for categories."""

    def showAll(self, user_id, request):
        categories = self.db_session.query(Category).all()
        if user_id:
            return render_template('user/category_all.html', categories=categories, user_id=user_id)
        else:
            return render_template('public/category_all.html', categories=categories, user_id=1) # TODO


    def show(self, category_id, user_id, request):
        if user_id:
            return render_template('user/category.html', user_id=user_id, category_id=category_id)
        else:
            return render_template('public/category.html', category_id=category_id)


    def new(self, user_id, request):
        '''
        if 'username' not in login_session:
            return redirect('/login')
            '''
        if request.method == 'POST':
            category = Category(
                name=request.form['name'],
                user_id=1) # TODO login_session['user_id'])
            self.db_session.add(category)
            self.db_session.commit()
            flash('New category %s successfully created.' % category.name)
            return redirect(url_for('showCategories'))
        else:
            return render_template('user/category_new.html', user_id=1) # TODO user_id=user_id)


    def edit(self, category_id, user_id, request):
        category = self.db_session.query(Category).filter_by(id=category_id).one()
        '''
        if 'username' not in login_session:
            return redirect('/login')
        if restaurantToDelete.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
            '''
        if request.method == 'POST':
            category.name = request.form['name']
            self.db_session.commit()
            flash('Category %s successfully updated.' % category.name)
            return redirect(url_for('showCategories'))
        else:
            return render_template('user/category_edit.html', user_id=1, category=category) # TODO user_id


    def delete(self, category_id, user_id, request):
        category = self.db_session.query(Category).filter_by(id=category_id).one()
        '''
        if 'username' not in login_session:
            return redirect('/login')
        if restaurantToDelete.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
            '''
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
