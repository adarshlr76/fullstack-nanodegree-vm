from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine,asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')


def showCatalogs():
	categories = session.query(Category).order_by(asc(Category.name))
	return render_template('catalog.html',categories=categories)


@app.route('/catalog/<string:category>/items')

def showItems(category) :
	#return "show tems go here"
	c = session.query(Category).filter_by(name = category).one()
	items = session.query(Item).filter_by(category_id = c.id).all()
	categories = session.query(Category).order_by(asc(Category.name))
	return render_template('catalog.html',categories=categories,items=items)

@app.route('/catalog/items/<int:item_id>')

def showItemDesc(item_id) :
	item = session.query(Item).filter_by(id=item_id).one()
	return render_template('item_desc.html',item=item)



if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)