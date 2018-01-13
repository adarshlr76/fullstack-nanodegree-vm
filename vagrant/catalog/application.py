from flask import Flask, render_template, request, redirect, jsonify,url_for,flash
from sqlalchemy import create_engine,asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from flask import session as login_session
import datetime

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
	items = session.query(Item).order_by(Item.date)
	return render_template('catalog.html',categories=categories,items=items)


@app.route('/catalog/<string:category>/items')

def showItems(category) :
	#return "show tems go here"
	c = session.query(Category).filter_by(name = category).one()
	items = session.query(Item).filter_by(category_id = c.id).all()
	categories = session.query(Category).order_by(asc(Category.name))
	return render_template('catalog.html',categories=categories,items=items,category_id=c.id)

@app.route('/catalog/items/<int:item_id>')

def showItemDesc(item_id) :
	item = session.query(Item).filter_by(id=item_id).one()
	return render_template('item_desc.html',item=item)

@app.route('/catalog/<int:category_id>/item/new/',methods=['GET','POST'])
def newItem(category_id):
	category = session.query(Category).filter_by(id = category_id).one()


	if request.method == 'POST' :
		newItem = Item(name = request.form['name'], description = request.form['description'], category_id = category_id, user_id = 1,date=datetime.datetime.now())
		session.add(newItem)
		session.commit()
		flash("New Item Successfully Created")
		return redirect(url_for('showItems', category = category.name))
	else :
		return render_template('new_item.html', category_id = category_id)

	"""
	if request.method == 'POST':
		newItem = Item(name = request.form['name'], description = request.form['description'], category_id = category_id, user_id=login_session['user_id'])
		session.add(newItem)
      	session.commit()
      	flash("New Item Successfully Created")
      	return redirect(url_for('showItems', category_id = category_id))
    	

    if request.method == 'GET':"""
    	




if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)