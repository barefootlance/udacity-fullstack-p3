#!/usr/bin/env python
#
# Test cases for tournament.py

from restaurants import *

def testDeleteRestaurants():
    deleteRestaurants()
    print "1. Old matches can be deleted."


def testCount():
    deleteRestaurants()
    c = countRestaurants()
    if c == '0':
        raise TypeError(
            "countPlayers() should return numeric zero, not string '0'.")
    if c != 0:
        raise ValueError("After deleting, countPlayers should return zero.")
    print "2. After deleting, countPlayers() returns zero."


def testAddRestaurant():
    deleteRestaurants()
    name = "Four Seasons"
    addRestaurant(name)
    c = countRestaurants()
    if c != 1:
        raise ValueError(
            "After one restaurant is added, countRestaurants() should be 1.")

    addRestaurant(name)
    c = countRestaurants()
    if c != 1:
        raise ValueError(
            "After adding another restaurant with the same name, countRestaurants() should still be 1.")
    print "3. After adding a restaurant, countRestaurants() returns 1."


def testChangeRestaurant():
    deleteRestaurants()
    oldName = "Four Seasons"
    newName = "McDonald's"

    addRestaurant(oldName)
    if getRestaurantNames()[0] != oldName:
        raise ValueError(
            "The restaurant name is not correct.")

    c = countRestaurants()
    if c != 1:
        raise ValueError(
            "After one restaurant is added, countRestaurants() should be 1.")

    changeRestaurant(oldName, newName)
    if getRestaurantNames()[0] != newName:
        raise ValueError(
            "The restaurant name was not changed corectly.")

    print "4. The restaurant name can be changed."


def testDeleteRestaurant():
    deleteRestaurants()
    name = "Four Seasons"
    addRestaurant(name)
    c = countRestaurants()
    if c != 1:
        raise ValueError(
            "After one restaurant is added, countRestaurants() should be 1.")

    deleteRestaurant(name)
    c = countRestaurants()
    if c != 0:
        raise ValueError(
            "After deleting the restaurant, countRestaurants() should be 0.")
    print "5. The restaurant name can be deleted."


def testGetRestaurants():
    deleteRestaurants()
    names = ["Four Seasons", "McDonald's", "Tantris", "Red Robin"];
    for name in names:
        addRestaurant(name)
    c = countRestaurants()
    if c != len(names):
        raise ValueError(
            "Count of restaurants should be {expected}, but is {actual}.".format(expected=len(names), actual=c))

    restaurants = getRestaurants();
    print restaurants
    if len(restaurants) != len(names):
        raise ValueError(
            "List of restaurants should be {expected} long, but is {actual}.".format(expected=len(names), actual=len(restaurants)))
    print "6. The restaurants can be listed."


def testGetRestaurantNames():
    deleteRestaurants()
    names = ["Four Seasons", "McDonald's", "Tantris", "Red Robin"];
    for name in names:
        addRestaurant(name)
    c = countRestaurants()
    if c != len(names):
        raise ValueError(
            "Count of restaurants should be {expected}, but is {actual}.".format(expected=len(names), actual=c))

    restaurants = getRestaurantNames();
    if len(restaurants) != len(names):
        raise ValueError(
            "List of restaurants should be {expected} long, but is {actual}.".format(expected=len(names), actual=len(restaurants)))
    print "7. The restaurants names can be listed."

if __name__ == '__main__':
    testDeleteRestaurants()
    testCount()
    testAddRestaurant()
    testChangeRestaurant()
    testDeleteRestaurant()
    testGetRestaurants()
    testGetRestaurantNames()
    print "Success!  All tests pass!"
