import os
from flask import Flask, render_template, redirect, request, url_for, session
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'deckBox'
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost')

mongo = PyMongo(app)

@app.route('/')
def index():
    if 'username' in session:
        return 'Welcome back ' + session['username']
    return render_template('index.html')
    
@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login = users.find_one({'name': request.form['username']})
    
    if login:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), login['password']) == login['password']:
            session['username'] = request.form['username']
            return redirect( url_for('index'))
            
    return 'Invalid username or password'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})
        
        if existing_user is None: 
            hash_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name':  request.form['username'], 'password' : hash_password})
            session['username'] =  request.form['username']
            return redirect(url_for('index'))
            
        return 'Username already exists.'
        
    return render_template('register.html')

    

    
if __name__ == '__main__':
    app.secret_key = 'deckB0X'
    app.run(host=os.getenv("IP", "0.0.0.0"),
            port=int(os.getenv("PORT", "5000")),
            debug=True)