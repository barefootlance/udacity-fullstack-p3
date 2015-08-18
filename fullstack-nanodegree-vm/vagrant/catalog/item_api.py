from crud_api import Crud_API
from flask import render_template, flash, redirect, url_for, abort
from database_setup import Category, Item

class Item_API(Crud_API):
    """Implements CRUD API calls for items."""

    def showAll(self, category_id, request):
        try:
            category = self.db_session.query(Category).filter_by(id=category_id).one()
            items = self.db_session.query(Item).filter_by(category_id=category_id).all()
            return render_template('item_all.html', category=category, items=items)
        except:
            abort(404)


    def show(self, category_id, item_id, request):
        try:
            item = self.db_session.query(Item).filter_by(category_id=category_id, id=item_id).one()
            return render_template('item.html', item=item)
        except:
            abort(404)


    def new(self, category_id, login_session, request):
        # make sure the category exists
        try:
            category = self.db_session.query(Category).filter_by(id=category_id).one()
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
            flash('New item %s successfully created.' % item.name)
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('user/item_new.html')


    def edit(self, category_id, item_id, login_session, request):
        try:
            item = self.db_session.query(Item).filter_by(category_id=category_id, id=item_id).one()
        except:
            abort(404)

        if 'username' not in login_session:
            return redirect('/login')

        if item.user_id != login_session['user_id']:
            flash('You are only authorized to edit items you created.')
            return redirect(url_for('showItem', category_id=category_id, item_id=item_id))

        if request.method == 'POST':
            item.name = request.form['name']
            item.description = request.form['description']
            item.image_url = request.form['image_url']
            self.db_session.commit()
            flash('Item %s successfully updated.' % item.name)
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('user/item_edit.html', user_id=1, item=item) # TODO user_id


    def delete(self, category_id, item_id, login_session, request):
        try:
            item = self.db_session.query(Item).filter_by(category_id=category_id, id=item_id).one()
        except:
            abort(404)

        if 'username' not in login_session:
            return redirect('/login')

        if item.user_id != login_session['user_id']:
            flash('You are only authorized to delete items you created.')
            return redirect(url_for('showItem', category_id=category_id, item_id=item_id))

        if request.method == 'POST':
            name = item.name;
            self.db_session.delete(item)
            self.db_session.commit()
            flash('Item %s successfully deleted.' % name)
            return redirect(url_for('showItems', category_id=category_id))
        else:
            return render_template('user/item_delete.html', user_id=user_id, item=item)
