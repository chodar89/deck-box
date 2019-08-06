![Alt](/static/img/logoblack.png "Deck BOX")

# DECK BOX

This is my 3rd milestone project. Website is created for poeple that play and collect
Magic The Gathering cards. App allows users to hold their cards collection in the app and
manage collection and decks.<br/>
Database is NoSQL - MongoDB<br/>
**[DECK BOX](http://deck-box.herokuapp.com/)**<br/>
To check pre upload cards and pre-build deck.<br/>
Login: testuser<br/>
Password: testuser<br/>

## UX

Deck-Box, a place where users can create an account, upload MTG card collection build decks, 
and manage cards. The application allows for easy management 
and building of decks. No more taking all card out of box!

Mockup<br/>
(/static/img/mokup/)<br/>
Hosted mokup files<br/>
[Mockup1](https://i.ibb.co/NpDqHSb/mokup.jpg)<br/>
[Mockup2](https://i.ibb.co/dcFCVGn/mokup2.jpg)<br/>
[Mockup3](https://i.ibb.co/wKgz6xQ/mokup3.jpg)<br/>

## Features

- For fast check what app can do please - login: testuser password: testuser
- App is full responsive
- Slide navigation bar
- User can pick avatar
- User registration and login process
- Forms that allow user to upload cards and pick data that was already pre set 
- Browse collection. Assigned for each user
- Build decks from cards that user holds in his collection
- Delete and edit decks and cards
- Sort cards
- Charts with deck statistics
- Decks displays how many card we have and how many cards of each type is in the deck
- Card pagination where user can pick how many card are displayed per page. App saves settings
- Encrypoted password
- Usefull link in slide menu. To hosting service, shop and official wizard site

## Technologies Used

- HTML
- CSS
- Flask
- Python 3
- JavaScript
- Materialize
- Fontawesome
- jQuery
- dotenv
- PyMongo
- MongoDB
- Google Charts
- AWS Cloud9
- Photoshop

## Testing

### Run app on different devices.
- iPhone XS Max
    - Safari
    - Messanger
- Samsung S8
    - Chrome Mobile
    - Samsun Browser
- Huawei Mate 20 Pro
    - Chrome Mobile
- PC windows 10 x64 with 16:9 screens and ultrawide screens
    - Opera 62.0.3331.72
    - Firefox 67.0.4 (64-bit)

### Test app manual. 
- Checked home page all links plus tried to change endpoints manual for redirection check
- Registration page. Checked login system (upercase, lowercase should not be sensitive).<br/>
  Registration form. Cheked the same usernames and emails, if exists fired alert.<br/>
  Checked username and password length. 
- Adding new decks and new cards.
- Slide nav manu. Checked all links.
- Eddit card forms. 
- Delete cards from collection and decks.
- Adding new cards to decks

### Test with pytest-flask.
- Test views HTML codes with pytest-flask.

### App validate.
- CSS - https://jigsaw.w3.org/css-validator/
- Python - with pylint
- JavaScript - jshint.com

## Deployment
- App is currently hosted on [Heroku](http://deck-box.herokuapp.com/)

### Steps to deploy app on Heroku platform
- Create an account on [heroku](https://id.heroku.com/login) site
- After login create a new app from the dashboard:<br/>
    New > Create new app<br/>
or create app from CLI manual to this is [here](https://devcenter.heroku.com/articles/creating-apps)
- create requirements.txt and Profile file from CLI
```
$ pip3 freeze --local > requirements.txt
$ echo "web: python app.py" > Procfile
```
- now we can push our code
```
$ git push heroku master
```
- Last thing set up config vars. Go to Heroku Dashboard > Your App > Settings > Reveal Config Vars<br/>
- Config Vars that needs to provided:
1. debug
2. IP
3. key
4. MONGO_DBNAME
5. MONGO_URI
6. PORT

### Run app local
- ensure you are using Python 3
- create [virtual enviroment](https://docs.python.org/3/tutorial/venv.html)
- once you download app and run on your local development environment, you<br/>
will need to install packs from requirements.txt file 
```
$ pip3 install -r requirements.txt
```
- than you will need to change some config vars that are sensitive and are not enclosed here
```
app.config['MONGO_DBNAME']
app.config['MONGO_URI']
app.secret_key
debug
```
- Secret_key choosen by you. MONGO_URI and MONGO_DBNAME is provided by MongoDB.
- To run app with your own database. You will need to create an account with MongoDB and create your own 
- Cluster. Than create some collections that must be pre set:
  1. card_types
     * creature
     * artifact
     * land
     * enchantment
     * planeswalker
     * instant
     * sorcery
  2. colors
     * blue
     * white
     * red
     * black
     * green
     * colorless
  3. expansion_set
     * all expansions that you want include
  4. rarity
     * land
     * common
     * uncommon
     * rare
     * mythic rare
     * timeshifted
     * masterpiece
  5. cards
  6. decks
  7. rating
     * 1
     * 2
     * 3
     * 4
     * 5
  8. users

## Credits
- Most of the pictures were taken from Wizard website and imgbin.com
- Parallax picture with cards is from Adobe Stock
- Logo done by me in Photoshop