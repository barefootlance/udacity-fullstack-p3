#!/usr/bin/env python
#
# restaurants.py -- implementation of a restaurant database
#
import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=restaurants")


def countRestaurants():
    """Returns the number of restaurants."""
    return sqlReadScalar("SELECT Count(*) FROM Restaurants;")


def deleteRestaurants():
    """Remove all the restaurants records from the database."""
    sqlCud("DELETE FROM Restaurants;")


def addRestaurant(name):
    """Adds a restaurant to the restaurant database.

    Args:
      name: the restaurant's name. (Must be unique.)
    """
    try:
        sqlCud("INSERT INTO Restaurants (Name) VALUES (%s);", (name,))
    except psycopg2.IntegrityError:
        # if it's a duplicate name we fail gracefully
        pass


def changeRestaurant(oldName, newName):
    """Change a restaurant's name in the database.

    Args:
      oldName: the restaurant's current name.
      newName: the restaurant's new name.
    """
    sqlCud("UPDATE Restaurants SET name = %s WHERE name = %s;", (newName, oldName,))


def deleteRestaurant(name):
    """Deletes a restaurant to the restaurant database.

    Args:
      name: the restaurant's name. (Must be unique.)
    """
    sqlCud("DELETE FROM Restaurants WHERE Name = %s;", (name,))

def getRestaurantNames():
    """
    Returns:
        A list of all restaurant names.
    """
    return [x[0] for x in sqlRead("SELECT Name FROM Restaurants ORDER BY Name")]

def getRestaurants():
    """
    Returns:
        A list of all restaurants.
    """
    return sqlRead("SELECT * FROM Restaurants ORDER BY Name")


def sqlCud(sql, data=()):
    """ Executes a sql command and commits the changes"""
    return sqlExecute(sql, data)

def sqlReadScalar(sql, data=()):
    """ Executes a sql query.

    Returns:
        A scalar value from the query.
    """
    return sqlExecute(sql, data, 'fetchone')[0]

def sqlRead(sql, data=()):
    """ Executes a sql query.

    Returns:
        A scalar value from the query.
    """
    return sqlExecute(sql, data, 'fetchall')

def sqlExecute(sql, data, resultMethodName=None):
    """ Generic sql execution.

    Returns:
        if resultMethod is provided, returns the result of that method.
        Examples would be 'fetchall' or 'fetchone'
    """
    conn = connect()
    c = conn.cursor()
    c.execute(sql, data)
    if resultMethodName == None:
        conn.commit()
        conn.close()
    else:
        result = getattr(c, resultMethodName)()
        conn.close()
        return result
