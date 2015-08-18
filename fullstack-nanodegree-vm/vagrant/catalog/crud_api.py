from singleton import Singleton
from flask import render_template

class Crud_API(object):
    """Singleton class to allow for refactoring of API calls
    into more manageable files.
    """
    __metaclass__ = Singleton

    def __init__(self, db_session):
        self.db_session = db_session

    def showAll(self, *args, **kwargs):
        raise NotImplementedError( "Should have implemented this" )


    def show(self, *args, **kwargs):
        raise NotImplementedError( "Should have implemented this" )


    def new(self, *args, **kwargs):
        raise NotImplementedError( "Should have implemented this" )


    def edit(self, *args, **kwargs):
        raise NotImplementedError( "Should have implemented this" )


    def delete(self, *args, **kwargs):
        raise NotImplementedError( "Should have implemented this" )
