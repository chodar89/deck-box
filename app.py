import os
from flask import Flask, render_template, redirect, request, url_for, session, flash, g, abort
from flask_pymongo import PyMongo, pymongo
from bson.objectid import ObjectId
from bson.json_util import dumps
from dotenv import load_dotenv
from flask_paginate import Pagination, get_page_parameter
import bcrypt

load_dotenv()

app = Flask(__name__)

app.config['MONGO_DBNAME'] = os.environ.get('MONGO_DBNAME')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI')

mongo = PyMongo(app)

""" Launched username before render templates """
@app.context_processor
def user_context():
    if 'username' in session:
        user_name = session['username']
        user = mongo.db.users.find_one({"username": user_name})
        user_email = user['email']
        sign_out = 'Sign Out'
        user_avatar = user['avatar']
        return dict(user_name = user_name.upper(), user_email = user_email, sign_out = sign_out, user_avatar=user_avatar)
    else:
        return dict(user_name = None)
            
""" Render index page and checkes if user is in the session """
@app.route('/')
@app.route('/index')
def index():
    if 'username' in session:
        return redirect(url_for('decks'))
    else:
        return render_template('index.html', sign_in = 'Sign In')
        
""" CARDS """

""" Render addcard page and take values from collection and pass them to html form """
@app.route('/add_card')
def add_card():
    if 'username' in session:
        colors = mongo.db.colors.find()
        rarity = mongo.db.rarity.find()
        expansion = mongo.db.expansion_set.find()
        card_types = mongo.db.card_types.find()
        rating = mongo.db.rating.find()
        return render_template('addcard.html', **locals())
    else: 
        return redirect(url_for('register'))
        
""" Shows collection of all user cards plus pagination"""
@app.route('/my_cards')
def my_cards():
    if 'username' in session:
        search = False
        q = request.args.get('q')
        if q:
            search = True
        page = request.args.get(get_page_parameter(), type=int, default=1)
        user_name = session['username']
        user = mongo.db.users.find_one({"username": user_name})
        user_id = user.get('_id')
        per_page = 5 
        # try to find cards and count if user dont have any gives 0
        try:
            user_cards = mongo.db.cards.find({'user_id': user_id})
            count_user_cards = user_cards.count()
        except:
            count_user_cards = 0
        card_output = []
        try:
            cards = mongo.db.cards.find({'user_id': user_id}).skip((page - 1) * per_page).limit(per_page)
            for i in cards:
                card_output.append(i)
        except: 
            flash('you do not have any cards in your collection yet', 'no_cards')
        pagination = Pagination(page = page,per_page = per_page ,total = user_cards.count(), 
        search = search, record_name='card_output')
        return render_template('mycards.html', card_output = card_output, pagination = pagination, 
        count_user_cards = count_user_cards)
    else: 
        return redirect(url_for('register'))

""" Edit_card route with function that takes card id and its values """
@app.route('/edit_card/<card_id>')
def edit_card(card_id):
    if 'username' in session:
        card = mongo.db.cards.find_one({"_id": ObjectId(card_id)})
        colors = mongo.db.colors.find()
        rarity = mongo.db.rarity.find()
        expansion = mongo.db.expansion_set.find()
        card_types = mongo.db.card_types.find()
        rating = mongo.db.rating.find()
        card_color_id = card.get('color')
        return render_template('editcard.html', **locals())
    else: 
        return redirect(url_for('register'))

""" Function that takes values from form in editcard.html and update them in database """
@app.route('/update_card/<card_id>', methods = ["POST"])
def update_card(card_id):
    colors_id = []
    cards = mongo.db.cards
    colors_form = request.form.getlist('color')
    for colors in colors_form:
        color = mongo.db.colors.find_one({'color': colors})
        color_id = color.get('_id')
        colors_id.append(color_id)
    rarity_form = mongo.db.rarity.find_one({'rarity': request.form.get('rarity')})
    rarity_id = rarity_form.get('_id')
    expansion_form = mongo.db.expansion_set.find_one({'set': request.form.get('set')})
    expansion_id = expansion_form.get('_id')
    type_form = mongo.db.card_types.find_one({'type': request.form.get('type')})
    type_id = type_form.get('_id')
    user = mongo.db.users.find_one({"username": session['username']})
    user_id = user.get('_id')
    cards.update( {"_id": ObjectId(card_id)} ,
        {
        'card_name': request.form.get('card_name'),
        'color': colors_id,
        'rarity': rarity_id,
        'type': type_id,
        'set': expansion_id,
        'mana_cost': request.form.get('mana_cost'),
        'strength': request.form.get('strength'),
        'toughness': request.form.get('toughness'),
        'ruling': request.form.get('ruling'),
        'flavor_text': request.form.get('flavor_text'),
        'artist': request.form.get('artist'),
        'rating': request.form.get('rating'),
        'card_url': request.form.get('card_url'),
        'user_id': user_id
    })
    return redirect(url_for('my_cards'))


""" Function that removes document, card that user picked """
@app.route('/remove_card/<card_id>')
def remove_card(card_id):
    user_name = session['username']
    user = mongo.db.users.find_one({"username": user_name})
    user_id = user.get('_id')
    remove_from_deck = mongo.db.decks.update({'user_id': user_id},
    {'$pull': {'cards':card_id}},
    multi=True);
    mongo.db.cards.remove({'_id': ObjectId(card_id)})
    return redirect(url_for('my_cards'))


""" Take data from form and send it to database """
@app.route('/insert_card', methods = ['POST'])
def insert_card():
    colors_id = []
    cards = mongo.db.cards
    colors_form = request.form.getlist('color')
    for colors in colors_form:
        color = mongo.db.colors.find_one({'color': colors})
        color_id = color.get('_id')
        colors_id.append(color_id)
    rarity_form = mongo.db.rarity.find_one({'rarity': request.form.get('rarity')})
    rarity_id = rarity_form.get('_id')
    expansion_form = mongo.db.expansion_set.find_one({'set': request.form.get('set')})
    expansion_id = expansion_form.get('_id')
    type_form = mongo.db.card_types.find_one({'type': request.form.get('type')})
    type_id = type_form.get('_id')
    user = mongo.db.users.find_one({"username": session['username']})
    user_id = user.get('_id')
    cards.insert_one(   {
        'card_name': request.form.get('card_name'),
        'color': colors_id,
        'rarity': rarity_id,
        'type': type_id,
        'set': expansion_id,
        'mana_cost': request.form.get('mana_cost'),
        'strength': request.form.get('strength'),
        'toughness': request.form.get('toughness'),
        'ruling': request.form.get('ruling'),
        'flavor_text': request.form.get('flavor_text'),
        'artist': request.form.get('artist'),
        'rating': request.form.get('rating'),
        'card_url': request.form.get('card_url'),
        'user_id': user_id
    })
    flash('Card '+ request.form.get('card_name') + ' added to your collection', 'add_card')
    return redirect(url_for('add_card'))


""" DECKS """

""" This is the home page after login, dispays all users decks """
@app.route('/decks')
def decks():
    if 'username' in session:
        user_name = session['username']
        user = mongo.db.users.find_one({"username": user_name})
        user_id = user.get('_id')
        decks = mongo.db.decks.find({'user_id': user_id})
        return render_template('decks.html', decks = decks)
    else: 
        return redirect(url_for('register'))
@app.route('/deck_browse/<deck_id>')
def deck_browse(deck_id):
    if 'username' in session:
        cards = []
        count_lands = 0
        count_creatures = 0
        count_artifacts = 0
        count_enchantments = 0
        count_planeswalkers = 0
        count_instants = 0
        count_sorceries = 0
        color_name = []
        rarity_land = 0
        rarity_common = 0
        rarity_uncommon = 0
        rarity_rare = 0
        rarity_mythic = 0
        rarity_timeshifted = 0
        rarity_masterpiece = 0
        # get all types from card_types collection
        types = mongo.db.card_types
        land_type = types.find_one({'type': 'land'})
        creature_type = types.find_one({'type': 'creature'})
        artifact_type = types.find_one({'type': 'artifact'})
        enchantment_type = types.find_one({'type': 'enchantment'})
        planeswalker_type = types.find_one({'type': 'planeswalker'})
        instant_type = types.find_one({'type': 'instant'})
        sorcery_type = types.find_one({'type': 'sorcery'})
        # get all rarities from card_rarity collection
        rarity = mongo.db.rarity
        land = rarity.find_one({'rarity': 'land'})
        common = rarity.find_one({'rarity': 'common'})
        uncommon = rarity.find_one({'rarity': 'uncommon'})
        rare = rarity.find_one({'rarity': 'rare'})
        mythic = rarity.find_one({'rarity': 'mythic rare'})
        timeshifted = rarity.find_one({'rarity': 'timeshifted'})
        masterpiece = rarity.find_one({'rarity': 'masterpiece'})
        # find deck by ObjectId
        deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        colors = mongo.db.colors
        # takes colors id and find color names in mongodb
        deck_color_id = deck.get('color')
        for color in deck_color_id:
            color_inf = colors.find_one({'_id': ObjectId(color)})
            color_name.append(color_inf.get('color'))
        # takes cards id from deck if empty throws None
        try:
            deck_cards = deck["cards"]
        except: 
            deck_cards = []
        # count cards in deck for later dispay
        count_cards = len(deck_cards)
        # find each card by id and check what type card it is and append it to array
        if deck_cards != None:
            # loop that check if card is in deck, if it is don't append add amount of that card
            for i in deck_cards:
                find_card = mongo.db.cards.find({'_id': ObjectId(i)})
                find_card_len = find_card.count()
                for each_card in find_card:
                    each_card["amount"] = find_card_len
                    if each_card not in cards:
                        cards.append(each_card)
            for card in deck_cards:
                card_information = mongo.db.cards.find_one({'_id': ObjectId(card)})
                card_type = card_information["type"]
                if card_type == land_type.get('_id'):
                    count_lands += 1
                elif card_type == creature_type.get('_id'):
                    count_creatures += 1
                elif card_type == artifact_type.get('_id'):
                    count_artifacts += 1
                elif card_type == enchantment_type.get('_id'):
                    count_enchantments += 1
                elif card_type == planeswalker_type.get('_id'):
                    count_planeswalkers += 1
                elif card_type == instant_type.get('_id'):
                    count_instants += 1
                elif card_type == sorcery_type.get('_id'):
                    count_sorceries += 1
            for card in deck_cards:
                card_information = mongo.db.cards.find_one({'_id': ObjectId(card)})
                card_rarity = card_information["rarity"]
                if card_rarity == land.get('_id'):
                    rarity_land += 1
                elif card_rarity == common.get('_id'):
                    rarity_common += 1
                elif card_rarity == uncommon.get('_id'):
                    rarity_uncommon += 1
                elif card_rarity == rare.get('_id'):
                    rarity_rare += 1
                elif card_rarity == mythic.get('_id'):
                    rarity_mythic += 1
                elif card_rarity == timeshifted.get('_id'):
                    rarity_timeshifted += 1
                elif card_rarity == masterpiece.get('_id'):
                    rarity_masterpiece += 1
        return render_template('deckbrowse.html', **locals())
    else: 
        return redirect(url_for('register'))
        
""" Page with form to create decks """
@app.route('/deck_name')
def deck_name():
    if 'username' in session:
        colors = mongo.db.colors.find()
        return render_template('deckname.html', colors = colors, sign_out = 'Sign Out')
    else: 
        return redirect(url_for('register'))
        
""" Insert deck name to database """
@app.route('/insert_deck', methods = ['POST'])
def insert_deck():
    colors_id = []
    colors_form = request.form.getlist('color')
    for colors in colors_form:
        color = mongo.db.colors.find_one({'color': colors})
        color_id = color.get('_id')
        colors_id.append(color_id)
    decks = mongo.db.decks
    user = mongo.db.users.find_one({"username": session['username']})
    user_id = user.get('_id')
    decks.insert_one(   {
        'deck_name': request.form.get('deck_name'),
        'color': colors_id,
        'user_id': user_id,
    })
    return redirect(url_for('decks'))
    
""" Delete deck """
@app.route('/remove_deck/<deck_id>')
def remove_deck(deck_id):
    mongo.db.decks.remove({'_id': ObjectId(deck_id)})
    return redirect(url_for('decks'))

""" Redirect page where user can add cards to specific deck """
@app.route('/deck_build/<deck_id>')
def deck_build(deck_id):
    if 'username' in session:
        deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        user_name = session['username']
        user = mongo.db.users.find_one({"username": user_name})
        user_id = user.get('_id')
        cards = mongo.db.cards.find({'user_id': user_id})
        return render_template('deckbuild.html', deck = deck, cards = cards)
    else: 
        return redirect(url_for('register'))

""" Add card to deck """
@app.route('/add_card_to_deck/<deck_id>/<card_id>', methods = ['POST'])
def add_card_to_deck(deck_id, card_id):
    if 'username' in session:
        current_deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        deck_id = current_deck.get('_id')
        deck_name = current_deck.get('deck_name')
        card = mongo.db.cards.find_one({'_id': ObjectId(card_id)})
        card_name = card.get('card_name')
        cards_amount = request.form.get('one_four_cards')
        # loop takes card amount from form and push cards to deck
        for i in range(0, int(cards_amount)):
            deck = mongo.db.decks.update({'_id': ObjectId(deck_id)},
            {'$push': {'cards':card_id}})
        flash(' Card '+ card_name +' added to ' + deck_name + ' deck', 'card_append')
        return redirect(url_for('deck_build', deck_id = deck_id))
    else: 
        return redirect(url_for('register'))
        
""" Remove card from deck """
@app.route('/remove_card_from_deck/<deck_id>/<card_id>')
def remove_card_from_deck(deck_id, card_id):
        current_deck = mongo.db.decks.find_one({'_id': ObjectId(deck_id)})
        deck_id = current_deck.get('_id')
        deck_name = current_deck.get('deck_name')
        card = mongo.db.cards.find_one({'_id': ObjectId(card_id)})
        card_name = card.get('card_name')
        deck = mongo.db.decks.update({'_id': ObjectId(deck_id)},
            {'$pull': {'cards':card_id}})
        flash(' Card '+ card_name +' removed from ' + deck_name + ' deck', 'card_removed')
        return redirect(url_for('deck_browse', deck_id = deck_id, card_id = card_id))
        
""" REGISTRATION & LOGIN """

""" Render register page and post registration form to mongo database """
@app.route('/register', methods = ['POST', 'GET'])
def register():
    if 'username' in session:
        return redirect(url_for('decks'))
    else:
        if request.method == 'POST':
            users = mongo.db.users
            # import pdb;
            # pdb.set_trace()
            new_username = request.form['username']
            new_password = request.form['password']
            email = request.form.get('email')
            existing_user = users.find_one({'username' : new_username.lower()})
            existing_email = users.find_one({'email': email})
            # first it checks if username and emial exists in database if not post form if yes flash allert
            if existing_user is None and existing_email is None:
                if len(new_username) < 4:
                   flash('Username to short', 'exists')
                elif len(new_password) < 6:
                   flash('password to short', 'exists')
                else:
                    hash_password = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                    users.insert({'username':new_username.lower(), 'password' : hash_password, 'email': request.form['email'], 'avatar': request.form['avatar']})
                    session['username'] = request.form['username']
                    flash('Thank you for creating an account', 'exists')
                return redirect(url_for('register'))
            else: flash('Username or email already exists', 'exists')
        return render_template('register.html')


""" Login form, encode and checks data in form with database that exists if not flash allert """
@app.route('/login', methods = ['POST'])
def login():
    users = mongo.db.users
    log_username = request.form['log_username']
    login = users.find_one({'username': log_username.lower()})
    if login:
        if bcrypt.hashpw(request.form['log_password'].encode('utf-8'), login['password']) == login['password']:
            session['username'] = log_username.lower()
            flash('Welcome back ' + session['username'], 'welcome')
            return redirect(url_for('decks'))
    flash("Incorrect password or username", 'error')
    return redirect(url_for('register'))

""" Simply logout session function """
@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.secret_key = os.environ.get('key')
    app.run(host = os.environ.get("IP", "0.0.0.0"),
            port = int(os.environ.get("PORT", "5000")),
            debug = os.environ.get('debug'))