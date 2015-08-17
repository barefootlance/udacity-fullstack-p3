from crud_api import Crud_API
from flask import render_template

class Category_API(Crud_API):
    """Implements CRUD API calls for categories."""

    def showAll(self, user_id):
        if user_id:
            return render_template('user/category_all.html', user_id=user_id)
        else:
            return render_template('public/category_all.html')


    def show(self, category_id, user_id):
        if user_id:
            return render_template('user/category.html', user_id=user_id, category_id=category_id)
        else:
            return render_template('public/category.html', category_id=category_id)


    def new(self, user_id):
        return render_template('user/category_new.html', user_id=user_id)


    def edit(self, category_id, user_id):
        return render_template('user/category_edit.html', user_id=user_id, category_id=category_id)


    def delete(self, category_id, user_id):
        return render_template('user/category_delete.html', user_id=user_id, category_id=category_id)
