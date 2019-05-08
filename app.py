import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'deckBox'
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost')

mongo = PyMongo(app)

# render index page and checkes if user is in the session

@app.route('/')
def index():
    if 'username' in session:
        flash('Welcome back ' + session['username'], 'welcome')
        return render_template('index.html', sign_out='Sign Out')
    else:
        return render_template('index.html')
        
    
@app.route('/addcard')
def addcard():
    colors=mongo.db.colors.find()
    rarity=mongo.db.rarity.find()
    expansion=mongo.db.expansion_set.find()
    card_types=mongo.db.card_types.find()
    rating=mongo.db.rating.find()
    return render_template('addcard.html', **locals())
    

# render register page and post registration form to mongo database

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})
        
        # first it checks if user name exists in database if not post form if yes flash allert
        if existing_user is None: 
            hash_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name':  request.form['username'], 'password' : hash_password})
            session['username'] =  request.form['username']
            return redirect(url_for('index'))
            
    
        else: flash('Username already exists', 'exists')

    return render_template('register.html')
    

# login form, encode and checks data in form with database that exists if not flash allert
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login = users.find_one({'name': request.form['log_username']})
    
    if login:
        if bcrypt.hashpw(request.form['log_password'].encode('utf-8'), login['password']) == login['password']:
            session['username'] = request.form['log_username']
            return redirect(url_for('index'))
        
    flash("Incorrect password or username", 'error')
    return render_template('register.html')  

# simply logout session function
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = 'deckB0X'
    app.run(host=os.getenv("IP", "0.0.0.0"),
            port=int(os.getenv("PORT", "5000")),
            debug=True)