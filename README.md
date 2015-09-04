# udacity-fullstack-p3 - PostgreSQL

This is a fork of the p3 project that changes the database from Sqlite to PostgreSQL. This change is necessary to complete project 5, but I want to leave the original submission for p3 in place.

Udacity fullstack project #3: Catalog

This is an implementation of the specification for Tournament Results, the second project of the Udacity Full Stack Web Developer Nanodegree.

The basic program is a catalog. A catalog of what? A catalog of anything you like. The database comes pre-filled with a few categories. You can't delete those categories or the items in them, of course, because only the person who entered them can, but you can add your own. If you want to start from scratch you can delete catalog.db and create a new, empty database by running `python database_setup.py` to create an empty database.

Running down the points in the rubric:

* There are both JSON and XML endpoints for accessing both categories and items.
* READ - categories and items are both read from the database. They are displayed as clickable links on the left pane of the screen as well as visually in the content pane on the right.
* CREATE - a logged in user can create new categories and items. A user can create items in a category which they didn't create. An item has an image associated with it, but a category does not.
* UPDATE - a logged in user can edit categories and items they have created. When logged in, the ownership of a category or item is displayed at the bottom of the content page, along with creation and modification timestamps.
* DELETE - a logged in user can delete items they create. They can also delete categories they create. NOTE: deleting a category deletes all the items associated with it, regardless of whether the user created the items or not.
* CSRF - cross-site scripting is addressed for delete, as well as for create and update, all three of which are implemented using POST methods. Additionally the Oauth2 nonce processing in the Oauth training project is used here as well.

## Requirements
This project was tested on Python 2.7 using the following additional libararies:

Flask==0.9

SQLAlchemy==0.8.4

httplib2==0.9.1

oauth2client==1.4.12

requests==2.2.1

## Installation

* Clone the repo: `git clone https://github.com/barefootlance/udacity-fullstack-p3.git`.

### To run on the provided VM
* Install Vagrant
* Install Virtual Box.

### To run on your own Python installation
* Install the required libraries list in Requirements. This is most easily done with by running `pip install -r <path to>/fullstack-nanodegree-vm/vagrant/catalog/requirements.txt`.

* Install and configure PostgreSQL: `sudo apt-get -y install postgresql-9.3 postgresql-server-dev-9.3 postgresql-client-9.3`
* Create a new linux user named catalog with password 'catalog': `sudo useradd -p catalog catalog`
* Create a new postgresql user named catalog: `sudo --user=postgres createuser -DRS catalog`
* Give the postgresql user the password 'catalog': `sudo --user=postgres createuser -DRS catalog`
* Create a database called (surprise!) catalog: `sudo --user=postgres psql -c "CREATE DATABASE catalog"`
* Give the user permissions on the database: `sudo --user=postgres psql -c "GRANT ALL ON DATABASE catalog TO catalog"`

## Running the project

* `cd <path to>/fullstack-nanodegree-vm/vagrant/catalog`

To run on the virtual machine:
  * start up the virtual machine with the command `vagrant up`
  * ssh into the virtual machine with the command `vagrant ssh`
  * `cd /vagrant`

* Whether running on the VM or not, now run `python project.py` to start the web server.

By default the program is served on port 5000. You can change the port by editing project.py and changing the line `app.run(host='0.0.0.0', port=5000)` to the port you want. NOTE: if you run using the VM you will also need to make sure the port is exposed by VM by editing Vagrantfile and changing the line `config.vm.network "forwarded_port", guest: 5000, host: 5000`, where the guest port is the port in project.py and the host port is the port you want to use on your machine.

## Usage

To view the main page, open a web browser and enter `http://localhost:5000`. Note using `127.0.0.1:5000` will show the page as well, but not all Oauth2 providers will work from that address; this is because some providers allow only a single address for a redirect uri, so can't support both localhost and 127.0.0.1.

* The site is a generic catalog of items.
* The left side is a menu listing different categories of items. Clicking on a category takes you to a page listing the items in a category. The right (content) pane showing rotating images for each of the categories. Clicking on an image takes you to the page for that category.
* For a category page, the items are displayed both in the menu and with an image in the content pane. Clicking on either takes you to a page for that item.
* An item page displays all the information for that item.
* At the top of each page is a link for logging in. Categories and items can be added, edited, and deleted by logged in users. However, a user can only edit or delete items they have created. Login in requires an account on one of the Oauth2 providers shown on the login page: Google, Facebook, Amazon, or Reddit.
* When logged in, the menu will contain links for editing categories and items based on the page you are on and whether or not you created the category or item. The person who created the category or item is listed at the bottom of the page (but only for logged in users).
* For categories and items, clicking on the name displays a Google search of the term in a separate tab.
* Clicking on images (except the rotating images on the main Catalog page) opens a page to see a full sized view of the image.

### Accessing JSON and XML endpoints

There are four endpoints for both JSON and XML. They provide access to a single category, a list of all categories, an item, and a list of all items for a particular category. NOTE: all timestamps are UTC.

Category:
  * /category/<int:category_id>/JSON
  * /category/<int:category_id>/XML

Category list:
  * /category/JSON
  * /category/XML

Item:
  * /category/<int:category_id>/item/<int:item_id>/JSON
  * /category/<int:category_id>/item/<int:item_id>/XML

Item list:
  * /category/<int:category_id>/item/JSON
  * /category/<int:category_id>/item/XML

## Conclusions and Reflections

Although this project is heavily based on existing code, it is large enough that refactoring of the code from previous projects was required. My experience with Python is pretty limited, so if it looks like someone is trying to impose C++ OOP sensibilities on Python, you're probably right.

The main project.py file runs the web server and acts as a router for the endpoints, but all the heavy lifting has been moved to other modules.

It was relatively obvious that I needed to pull the oauth handling code into different provider classes, but I have no idea if I used best practices in doing so. The structure that I added did make it easier to add new providers (Amazon and Reddit), but it feels like there should be more commonality, and I don't know if using a "virtual" base class is best Python practice, but it did give me a place to put shared oauth methods.

The code feels pretty good, at least for the quality needed for this project (in my mind anyway, your mileage may vary). There are some things I would want to address for production code.

User logins are vague to me. Using email as a unique identifier is lovely until you run across Reddit that doesn't provide emails. I opted to stick the username in the email column which works for this project because it's unique, but it obviously pollutes the email column which may or may not be okay depending on whether you are planning to spam your users or not. For this project I deem it okay...but probably wouldn't do it in the real world. The key thing is that you want a unique identifier for each user aside from our internal user id. However, unique identifiers vary from provider to provider. Emails seem like a good idea when you look at Google, but the Reddit doesn't have one, and it looks like GitHub has multiple emails for a single acccount, and I believe you can change your primary email for Facebook - and in the current implementation, changing your email means that you can't edit categories and items you've created. The unique identifier really needs to be addressed on a per provider basis rather than using emails. Further, there should be some facility for combining multiple oauth accounts for a single user. (Sorry for the wall of text.)

What the devil is going on with oauth disconnecting? When do I need to log out? When don't I?

I don't know ajax well enough to repicate the Google and Facebook login processing from the oauth processing. What I've implemented works, but I'd rather be more consistent. (Yes, there are a lot of oauth-related issues. Guess what technology I am least familiar with...)

There should be an administrator level of authorization in order to edit Users.

When creating or editing an item, putting in an image url should show you the image that you're about to add. The GUI is not modal, so it's pretty quick to go back and change something, but it seems like that would be a nice touch.

In HTML: tables vs. grids. Grids sound good, but they seem not ready for prime time. Tables are more reliable, but require more support code. I use both in this project, but it is not yet clear to me when to opt for one over the other.
