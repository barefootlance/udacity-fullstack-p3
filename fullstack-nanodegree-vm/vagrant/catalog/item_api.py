from crud_api import Crud_API
from flask import render_template, flash, redirect, url_for
from database_setup import Category, Item

class Item_API(Crud_API):
    """Implements CRUD API calls for items."""

    def showAll(self, category_id, user_id, request):
        category = self.db_session.query(Category).filter_by(id=category_id).one()
        items = self.db_session.query(Item).filter_by(category_id=category_id).all()
        if user_id:
            return render_template('user/item_all.html', category=category, items=items, user_id=user_id)
        else:
            return render_template('public/item_all.html', category=category, items=items, user_id=1)


    def show(self, category_id, item_id, user_id, request):
        item = self.db_session.query(Item).filter_by(category_id=category_id, id=item_id).one()
        if user_id:
            return render_template('user/item.html', user_id=user_id, item_id=item_id)
        else:
            return render_template('public/item.html', item=item, user_id=1) # TODO user_id


    def new(self, category_id, user_id, request):
        '''
        if 'username' not in login_session:
            return redirect('/login')
            '''
        if request.method == 'POST':
            item = Item(
                name=request.form['name'],
                description=request.form['description'],
                image_url=request.form['image_url'],
                category_id=category_id,
                user_id=1) # TODO login_session['user_id'])
            self.db_session.add(item)
            self.db_session.commit()
            flash('New item %s successfully created.' % item.name)
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('user/item_new.html', user_id=1) # TODO user_id=user_id)


    def edit(self, category_id, item_id, user_id, request):
        item = self.db_session.query(Item).filter_by(category_id=category_id, id=item_id).one()
        '''
        if 'username' not in login_session:
            return redirect('/login')
        if restaurantToDelete.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
            '''
        if request.method == 'POST':
            item.name = request.form['name']
            item.description = request.form['description']
            item.image_url = request.form['image_url']
            self.db_session.commit()
            flash('Item %s successfully updated.' % item.name)
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('user/item_edit.html', user_id=1, item=item) # TODO user_id


    def delete(self, category_id, item_id, user_id, request):
        item = self.db_session.query(Item).filter_by(category_id=category_id, id=item_id).one()
        '''
        if 'username' not in login_session:
            return redirect('/login')
        if restaurantToDelete.user_id != login_session['user_id']:
            return "<script>function myFunction() {alert('You are not authorized to delete this restaurant. Please create your own restaurant in order to delete.');}</script><body onload='myFunction()''>"
            '''
        if request.method == 'POST':
            name = item.name;
            self.db_session.delete(item)
            self.db_session.commit()
            flash('Item %s successfully deleted.' % name)
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('user/item_delete.html', user_id=user_id, item=item)
