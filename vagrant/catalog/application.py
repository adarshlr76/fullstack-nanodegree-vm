from flask import Flask, render_template, request, redirect, jsonify,url_for,flash
from sqlalchemy import create_engine,asc,desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import datetime
import random, string


from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


CLIENT_ID = json.loads(
    open('client_secret.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


app = Flask(__name__)

#Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')

#shows all the items in the catalog
def showCatalogs():
	categories = session.query(Category).order_by(desc(Category.name))
	items = session.query(Item).order_by(desc(Item.date))
	if 'username' not in login_session:
		return render_template('public_catalog.html',categories=categories,items=items)
	else:
		return render_template('catalog.html',categories=categories,items=items)

 
#JSON endpoint 
@app.route('/catalog/JSON')
def catalogsJSON():
    categories = session.query(Category).all()
    category_dict = [c.serialize for c in categories]
    for index in range(len(category_dict)):
        items = session.query(Item).filter_by(category_id=category_dict[index]["id"])
        items_dict = [i.serialize for i in items]
        if items:
            category_dict[index]["Item"] = items_dict
    return jsonify(Category=category_dict)

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html',STATE=state)

@app.route('/catalog/<string:category_name>/items')

def showItems(category_name) :
	#return "show tems go here"
	c = session.query(Category).filter_by(name = category_name).one()
	items = session.query(Item).filter_by(category_id = c.id).all()
	categories = session.query(Category).order_by(desc(Category.name))
    	if 'username' not in login_session:
        	return render_template('public_item_catalog.html',categories=categories,items=items,category_id=c.id,category_name = category_name)
    	else:
        	return render_template('item_catalog.html',categories=categories,items=items,category_id=c.id,category_name = category_name)


@app.route('/catalog/items/<int:item_id>')

def showItemDesc(item_id) :
	item = session.query(Item).filter_by(id=item_id).one()
    	if 'username' not in login_session:
        	return render_template('public_item_desc.html',item=item)
    	else:
        	return render_template('item_desc.html',item=item)
	
@app.route('/item/new',methods=['GET','POST'])


def newItem():
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    categories = session.query(Category).order_by(asc(Category.name))

    if request.method == 'POST' :
        category = session.query(Category).filter_by(name = request.form['category']).one()
        newItem = Item(name = request.form['name'], description = request.form['description'], category_id = category.id, user_id = 1,date=datetime.datetime.now())
        session.add(newItem)
        session.commit()
        #flash("New Item Successfully Created")
        return redirect(url_for('showCatalogs'))
    else :
        return render_template('new_item.html',categories = categories)



#edit item
@app.route('/catalog/<int:category_id>/<string:item_name>/edit', methods=['GET','POST'])
def editItem(category_id, item_name):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))

	editedItem = session.query(Item).filter_by(name = item_name).one()
	category = session.query(Category).filter_by(id = category_id).one()

    	categories = session.query(Category).order_by(desc(Category.name))


	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']: 
			editItem.description = request.form['description']
		if request.form['category']:
			category = session.query(Category).filter_by(name=request.form['category']).one()
			editedItem.category = category

		session.add(editedItem)
        	session.commit()
	        #flash('Item Successfully edited')
        	#return redirect(url_for('showItems', category_name = category.name))
            	return redirect(url_for('showCatalogs'))
	else :
        	return render_template('edit_item.html', item=editedItem,category=category,categories=categories)

#Delete a item
@app.route('/catalog/<int:category_id>/<string:item_name>/delete', methods = ['GET','POST'])
def deleteItem(category_id,item_name):
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	category = session.query(Category).filter_by(id = category_id).one()
	itemToDelete = session.query(Item).filter_by(name = item_name).one()
	if request.method == 'POST':
		session.delete(itemToDelete)
		session.commit()
		flash('Item Successfully Deleted')
		return redirect(url_for('showItems', category = category.name))
	else :
		return render_template('delete_Item.html', item = itemToDelete)



#connect using the facebook account
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token


    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]


    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

#disconnect function for either facebook or google
@app.route('/disconnect')
def showDisconnect():
    if login_session['provider'] == 'google' :
        return redirect(url_for('gdisconnect'))
    elif login_session['provider'] == 'facebook' :
        return redirect(url_for('fbdisconnect'))
    #else :
    #return "provider not supported"

    #return redirect(url_for(showCatalogs))

#disconnect from facebook account
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['provider']
    flash("Successfully disconnected")
    return redirect(url_for('showCatalogs'))


#connect to google+ account
@app.route('/gconnect', methods=['POST'])

def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    userId = getUserID(login_session['email']) 
    if not userId :
      createUser(login_session)

    login_session['user_id'] = userId

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
    


# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
  try:
    user = session.query(User).filter_by(id=user_id).one()
    return user
  except:
    return None


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
      return None



 # DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        flash("Successfully disconnected")
        #response = make_response(json.dumps('Successfully disconnected.'), 200)
        #response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showCatalogs'))
    else:
        
        #flash("Failed to revoke token for given user")
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response




if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 8000)
