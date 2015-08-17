from crud_api import Crud_API
from flask import render_template

class Item_API(Crud_API):
    """Implements CRUD API calls for items."""

    def showAll(self, category_id, user_id):
        if user_id:
            return render_template('user/item_all.html', category_id=category_id, user_id=user_id)
        else:
            return render_template('public/item_all.html', category_id=category_id)


    def show(self, category_id, item_id, user_id):
        if user_id:
            return render_template('user/item.html', user_id=user_id, item_id=item_id)
        else:
            return render_template('public/item.html', item_id=item_id)


    def new(self, category_id, user_id):
        return render_template('user/item_new.html', user_id=user_id)


    def edit(self, category_id, item_id, user_id):
        return render_template('user/item_edit.html', user_id=user_id, item_id=item_id)


    def delete(self, category_id, item_id, user_id):
        return render_template('user/item_delete.html', user_id=item_id, item_id=item_id)
