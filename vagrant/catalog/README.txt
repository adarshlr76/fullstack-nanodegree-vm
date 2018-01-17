Introduction
This project is created as part of full stack nanodegree program. This is a python based project. it is RESTful using python flask framework. for logging in into the system OAuth 2.0 is used. user can login to application if they have facebook or google+ ids. it is assumed that facebook or google+ login credentials are available or else the user will create one of them.
For database SQlite is used in this application.

Requirements:
1. clone the git hub repository
	git clone https://github.com/adarshlr76/item-catalog.git
2. install virtualbox and vagrant
3. use vagrant to start the new virtual machine using the below commands
	vagrant up 
	vagrant ssh
4. install and populate the database with the below commands
	python database_setup.py
	python add_catalog.py
5. The python flask application will be available in /vagrant/catalog
6. start the application using python application.py
7. access and test application using http://localhost:8000

Usage
The home page has the various categories in the database
it shows the latest items added along with the category for which they are added
on selecting the specific category in the home page all the items in the category along with the number of items in the category is displayed
selecting the specific item shows more detailed description
the user can login into the system using the facebook or google login
users who have logged in can add new items by using the additems button in the home page
there is also a provition to edit or delete the item in item description page
JSON endpoint is provided which displays all the items in the specified category

