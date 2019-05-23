import os
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import bcrypt

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'deckBox'
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost')

mongo = PyMongo(app)


# launched username before render templates
@app.context_processor
def user_context():
    if 'username' in session:
         user_name=session['username']
         return dict(user_name=user_name)
    else:
        return dict(user_name=None)
# @app.before_request
# def check_username():
#     if 'username' in session:
#         # google it
#     else:
#         return redirect(url_for('register'))
        


# render index page and checkes if user is in the session
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        flash('Welcome back ' + session['username'], 'welcome')
        return redirect(url_for('decks'))
    else:
        return render_template('index.html', sign_in='Sign In')
        
        
"""         CARDS          """


# render addcard page and take values from collection and pass them to html form
@app.route('/add_card')
def add_card():
    if 'username' in session:
        colors=mongo.db.colors.find()
        rarity=mongo.db.rarity.find()
        expansion=mongo.db.expansion_set.find()
        card_types=mongo.db.card_types.find()
        rating=mongo.db.rating.find()
        sign_out='Sign Out'
        return render_template('addcard.html', **locals())
    else: 
        return redirect(url_for('register'))
        
# shows collection of all user cards
@app.route('/my_cards')
def my_cards():
    if 'username' in session:
        cards=mongo.db.cards.find()
        return render_template('mycards.html', cards=cards)
    else: 
        return redirect(url_for('register'))

# edit_card route with function that takes card id and its values
@app.route('/edit_card/<card_id>')
def edit_card(card_id):
    if 'username' in session:
        the_card = mongo.db.cards.find_one({"_id": ObjectId(card_id)})
        colors=mongo.db.colors.find()
        rarity=mongo.db.rarity.find()
        expansion=mongo.db.expansion_set.find()
        card_types=mongo.db.card_types.find()
        rating=mongo.db.rating.find()
        sign_out='Sign Out'
        card=the_card
        return render_template('editcard.html', **locals())
    else: 
        return redirect(url_for('register'))

# function that takes values from form in editcard.html and update them in database
@app.route('/update_card/<card_id>', methods=["POST"])
def update_card(card_id):
    card=mongo.db.cards
    card.update( {"_id": ObjectId(card_id)} ,
        {
        'card_name': request.form.get('card_name'),
        'color': request.form.getlist('color'),
        'rarity': request.form.get('rarity'),
        'type': request.form.get('type'),
        'set': request.form.get('set'),
        'strength': request.form.get('strength'),
        'toughness': request.form.get('toughness'),
        'ruling': request.form.get('ruling'),
        'flavor_text': request.form.get('flavor_text'),
        'artist': request.form.get('artist'),
        'rating': request.form.get('rating'),
        'card_url': request.form.get('card_url')
        })
    return redirect(url_for('decks'))
    
# function that removes document, card that user picked
@app.route('/remove_card/<card_id>')
def remove_card(card_id):
    mongo.db.cards.remove({'_id': ObjectId(card_id)})
    return redirect(url_for('my_cards'))

# function that change form data to dictionary and send it to MongoDB card collection
@app.route('/insert_card', methods=['POST'])
def insert_card():
    cards=mongo.db.cards
    cards.insert_one(   {
        'card_name': request.form.get('card_name'),
        'color': request.form.getlist('color'),
        'rarity': request.form.get('rarity'),
        'type': request.form.get('type'),
        'set': request.form.get('set'),
        'strength': request.form.get('strength'),
        'toughness': request.form.get('toughness'),
        'ruling': request.form.get('ruling'),
        'flavor_text': request.form.get('flavor_text'),
        'artist': request.form.get('artist'),
        'rating': request.form.get('rating'),
        'card_url': request.form.get('card_url')
    })
    return redirect(url_for('decks'))


"""         DECKS          """


# this is the home page after login, dispays all users decks
@app.route('/decks')
def decks():
    if 'username' in session:
        user_name=session['username']
        user_email=mongo.db.users.find()
        sign_out='Sign Out'
        decks=mongo.db.decks.find()
        return render_template('decks.html', **locals())
    else: 
        return redirect(url_for('register'))
        
#  page with form to create decks
@app.route('/deck_name')
def deck_name():
    if 'username' in session:
        colors=mongo.db.colors.find()
        return render_template('deckname.html', colors=colors, sign_out='Sign Out')
    else: 
        return redirect(url_for('register'))
        
# insert deck name to database
@app.route('/insert_deck', methods=['POST'])
def insert_deck():
    decks=mongo.db.decks
    deck = request.form.to_dict()
    decks.insert_one(deck)
    return redirect(url_for('decks'))

# redirect page where user can add cards to specific deck
@app.route('/deck_build/<deck_id>')
def deck_build(deck_id):
    if 'username' in session:
        deck=mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        sign_out='Sign Out'
        cards=mongo.db.cards.find()
        return render_template('deckbuild.html', **locals())
    else: 
        return redirect(url_for('register'))

@app.route('/add_card_to_deck/<deck_id>/<card_id>')
def add_card_to_deck(deck_id, card_id):
    if 'username' in session:
        # deck_cards=[]
        card=mongo.db.cards.find_one({'_id': ObjectId(card_id)})
        # append card id's to specific deck
        deck=mongo.db.decks.update({'_id': ObjectId(deck_id)},
        { '$push': {'cards':card_id}})
        # deck_cards.append
        sign_out='Sign Out'
        return redirect(url_for('decks'))
    else: 
        return redirect(url_for('register'))


@app.route('/deck_browse/<deck_id>')
def deck_browse(deck_id):
    if 'username' in session:
        cards_id=[]
        deck=mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        # import pdb;
        # pdb.set_trace()
        deck_cards=deck["cards"]
        for card in deck_cards:
            cardinformation = mongo.db.cards.find_one({'_id': ObjectId(card)})
            cards_id.append(cardinformation)
        sign_out='Sign Out'
        return render_template('deckbrowse.html', **locals())
    else: 
        return redirect(url_for('register'))
        
        
"""         REGISTRATION & LOGIN          """


# render register page and post registration form to mongo database
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'username' : request.form['username']})
        new_username = request.form['username']
        new_password = request.form['password']
        # first it checks if user name exists in database if not post form if yes flash allert
        if existing_user is None:
            if len(new_username) < 4:
               flash('Username to short', 'exists')
            elif len(new_password) < 6:
               flash('password to short', 'exists')
            else:
                hash_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert({'username':  request.form['username'], 'password' : hash_password})
                session['username'] =  request.form['username']
                flash('Thank you for creating an account', 'exists')
            return redirect(url_for('register'))
            
    
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
    return redirect(url_for('register'))

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