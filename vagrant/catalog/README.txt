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

