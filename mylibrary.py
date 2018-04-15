#!/usr/bin/env python
# this python file was inspired by the fsnd lessons
# and from several users on git.

# this section imports modules to be used by the program
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from library_database_setup import Base, MyLibrary, MyBook, User
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

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "My Library Application"

engine = create_engine('sqlite:///mylibrary.db', echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST', 'GET'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data
    try:
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

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is'
                                 'already connected.'), 200)
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
    output += (' " style = "width: 200px;'
               'height: 200px;border-radius: 150px;'
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# create user
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).first()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception as e:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs
@app.route('/libraries/<int:mylibrary_id>/books/JSON')
def libraryBooksJSON(mylibrary_id):
    library = session.query(MyLibrary).filter_by(id=mylibrary_id).one_or_none()
    if genre is None:
        return "No such element."
    books = session.query(MyBook).filter_by(
        mylibrary_id=mylibrary_id).all()
    return jsonify(MyBooks=[i.serialize for i in books])


@app.route('/libraries/<int:mylibrary_id>/book/<int:book_id>/JSON')
def myBooksJSON(mylibrary_id, book_id):
    book = session.query(MyBook).filter_by(id=book_id).one_or_none()
    if Book_Item is None:
        return "No such element."
    return jsonify(MyBook=book.serialize)


@app.route('/libraries/JSON')
def librariesJSON():
    libraries = session.query(MyLibrary).all()
    return jsonify(libraries=[l.serialize for l in libraries])


# Show all libraries in the database
@app.route('/')
@app.route('/libraries/')
def allLibraries():
    libraries = session.query(MyLibrary).all()
    if 'username' not in login_session:
        return render_template('publiclibrarypage.html', libraries=libraries)
    else:
        return render_template('mainlibrarypage.html', libraries=libraries)


# add a library to the database
@app.route('/libraries/new/', methods=['GET', 'POST'])
def addnewLibrary():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newLibrary = MyLibrary(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newLibrary)
        session.commit()
        flash("Your new library has been created succesfully!")
        return redirect(url_for('allLibraries'))
    else:
        return render_template('newLibrary.html')


# delete library from db, only can be done by creator
@app.route('/libraries/<int:mylibrary_id>/delete/', methods=['GET', 'POST'])
def deleteLibrary(mylibrary_id):
    libraryToDelete = session.query(MyLibrary).filter_by(id=mylibrary_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if libraryToDelete.user_id != login_session['user_id']:
        return ("<script function myFuncition() {alert"
                "('You are not authorized to delete this Library."
                " Please only attempt to edit/delete your own Libraries.')"
                ";</script><body onload='myFunction()''>")
    if request.method == 'POST':
        session.delete(libraryToDelete)
        session.commit()
        flash("The library has been deleted succesfully!")
        return redirect(url_for('allLibraries'))
    else:
        return render_template('deletelibrary.html', item=libraryToDelete)


# this section allows you to change the name of YOUR library
@app.route('/libraries/<int:mylibrary_id>/edit/', methods=['GET', 'POST'])
def editLibrary(mylibrary_id):
    editLibrary = session.query(MyLibrary).filter_by(id=mylibrary_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editLibrary.user_id != login_session['user_id']:
        return ("<script function myFuncition() {alert"
                "('You are not authorized to edit this Library."
                " Please only attempt to edit/delete your own Libraries.')"
                ";</script><body onload='myFunction()''>")
    if request.method == 'POST':
        if request.form['name']:
            editLibrary.name = request.form['name']
            flash('Library name succesfully changed to %s' % editLibrary.name)
            return redirect(url_for('allLibraries'))
    else:
        return render_template('editlibrary.html', mylibrary=editLibrary)


# displays current library chosen from main screen
@app.route('/libraries/<int:mylibrary_id>/')
@app.route('/libraries/<int:mylibrary_id>/books/')
def currentLibrary(mylibrary_id):
    libraries = session.query(MyLibrary).all()
    mylibrary = (session.query(MyLibrary).filter_by(id=mylibrary_id)
                 .one_or_none())
    if mylibrary is None:
        return 'No books in library'
    creator = getUserInfo(mylibrary.user_id)
    items = session.query(MyBook).filter_by(mylibrary_id=mylibrary_id).all()
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicbooks.html',
                               mylibrary=mylibrary, items=items,
                               creator=creator, libraries=libraries)
    else:
        return render_template('library.html',
                               mylibrary=mylibrary, items=items,
                               creator=creator, libraries=libraries)


# add a new book to your personal library
@app.route('/libraries/<int:mylibrary_id>/new/', methods=['GET', 'POST'])
def newLibraryBook(mylibrary_id):
    if 'username' not in login_session:
        return redirect('/login')
    library = session.query(MyLibrary).filter_by(id=mylibrary_id).one()
    if login_session['user_id'] != library.user_id:
        return ("<script function myFuncition() {alert"
                "('You cannot add books to this Library."
                " Create/Access your own library in order to add books.')"
                ";</script><body onload='myFunction()''>")
    if request.method == 'POST':
        newBook = MyBook(title=request.form['title'],
                         author=request.form['author'],
                         description=request.form['description'],
                         catalog=request.form['catalog'],
                         mylibrary_id=mylibrary_id,
                         user_id=library.user_id)
        session.add(newBook)
        session.commit()
        flash("Your new library book has been added succesfully!")
        return redirect(url_for('currentLibrary', mylibrary_id=mylibrary_id))
    else:
        return render_template('newbook.html', mylibrary_id=mylibrary_id)


# did you make a mistake? edit your book info here
@app.route('/libraries/<int:mylibrary_id>/<int:book_id>/edit/',
           methods=['GET', 'POST'])
def editLibraryBook(mylibrary_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    editBook = session.query(MyBook).filter_by(id=book_id).one()
    library = session.query(MyLibrary).filter_by(id=mylibrary_id).one()
    if login_session['user_id'] != library.user_id:
        return ("<script function myFuncition() {alert"
                "('You cannot edit books in this Library."
                " Create/Access your own library in order to edit books.')"
                ";</script><body onload='myFunction()''>")
    if request.method == 'POST':
        if request.form['title']:
            editBook.title = request.form['title']
        if request.form['author']:
            editBook.author = request.form['author']
        if request.form['description']:
            editBook.description = request.form['description']
        if request.form['catalog']:
            editBook.catalog = request.form['catalog']
        session.add(editBook)
        session.commit()
        flash("your library book has been edited succesfully!")
        return redirect(url_for('currentLibrary', mylibrary_id=mylibrary_id))
    else:
        return render_template('editlibrarybook.html',
                               mylibrary_id=mylibrary_id, book_id=book_id,
                               item=editBook)


# lose a book or give it away? delete that book here
@app.route('/libraries/<int:mylibrary_id>/<int:book_id>/delete/',
           methods=['GET', 'POST'])
def deleteLibraryBook(mylibrary_id, book_id):
    if 'username' not in login_session:
        return redirect('/login')
    bookToDelete = session.query(MyBook).filter_by(id=book_id).one_or_none()
    if bookToDelete is None:
        return ("<script>function myFunction() {alert('No such element');"
                "window.history.back();"
                "window.history.back();}</script>"
                "<body onload='myFunction()''>")
    library = session.query(MyLibrary).filter_by(id=mylibrary_id).one()
    if login_session['user_id'] != library.user_id:
        return ("<script function myFuncition() {alert"
                "('You cannot delete books from this Library."
                " Create/Access your own library in order to delete books.')"
                ";</script><body onload='myFunction()''>")
    if request.method == 'POST':
        session.delete(bookToDelete)
        session.commit()
        flash("your library book has been deleted succesfully!")
        return redirect(url_for('currentLibrary', mylibrary_id=mylibrary_id))
    else:
        return render_template('deletelibrarybook.html', item=bookToDelete)


if __name__ == '__main__':
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
