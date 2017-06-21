from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from functools import wraps
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

engine = create_engine('sqlite:///category.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']

# Check for login decorator


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

# g+ login


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
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'
    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:150px;'
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/logout')
def logout():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            access_token = login_session.get('access_token')
            url = 'https://accounts.google.com/o/oauth2/revoke?token='
            url += access_token
            h = httplib2.Http()
            result = h.request(url, 'GET')[0]
            if result['status'] != '200':
                flash('Failed to revoke token for given user.')
                return
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        del login_session['access_token']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCatalog'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCatalog'))


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Show all categories and latest items


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    categories = session.query(Category).order_by(asc(Category.name))
    items = session.query(Item).order_by(Item.id.desc()).limit(8)
    return render_template('catalog.html', categories=categories, items=items)

# Show items of selected category


@app.route('/catalog/<string:category_name>/')
@app.route('/catalog/<string:category_name>/items/')
def showCatagory(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        cat_id=category.id).order_by(
        Item.id.desc())
    return render_template(
        'catalog.html', categories=categories, items=items, category=category)

# Show selected item


@app.route('/catalog/<string:category_name>/<string:item_title>/')
def showItem(category_name, item_title):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        cat_id=category.id).filter_by(
        title=item_title).one()
    return render_template('item.html', item=item, category=category)

# Add new item


@app.route('/item/new/', methods=['GET', 'POST'])
@login_required
def newItem():
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        newItem = Item(title=request.form['title'],
                       description=request.form['description'],
                       cat_id=category.id, user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('New %s Item Successfully Created' % (newItem.title))
        return redirect(url_for('showCatalog'))
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('newItem.html', categories=categories)

# Update selected item


@app.route('/catalog/<string:category_name>/<string:item_title>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_name, item_title):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        cat_id=category.id).filter_by(
        title=item_title).one()
    if login_session['user_id'] != item.user_id:
        flash('You are not authorized to edit %s item' % (item.title))
        return redirect(url_for('showCatalog'))

    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        item.title = request.form['title']
        item.description = request.form['description']
        item.cat_id = category.id
        session.add(item)
        session.commit()
        flash('%s Item Successfully Updated' % (item.title))
        return redirect(url_for('showCatalog'))
    categories = session.query(Category).order_by(asc(Category.name))

    return render_template('editItem.html', categories=categories, item=item)

# Delete selected item after confirmation


@app.route('/catalog/<string:category_name>/<string:item_title>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_name, item_title):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        cat_id=category.id).filter_by(
        title=item_title).one()
    if login_session['user_id'] != item.user_id:
        flash('You are not authorized to edit %s item' % (item.title))
        return redirect(url_for('showCatalog'))
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('%s Item Successfully Deleted' % (item.title))
        return redirect(url_for('showCatalog'))

    return render_template('deleteItem.html', item=item)


@app.route('/catalog.json')
def catalogJSON():
    categories = session.query(Category).all()
    list = []
    for category in categories:
        dict = category.serialize
        items = session.query(Item).filter_by(
            cat_id=category.id).order_by(
            Item.title.asc())
        itemList = []
        for item in items:
            itemList.append(item.serialize)
        if len(itemList) != 0:
            dict['item'] = itemList
        list.append(dict)
    return jsonify(categories=list)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
