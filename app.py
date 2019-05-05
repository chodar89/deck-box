import os
from flask import Flask, render_template, redirect, request, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'cardBox'
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost')



@app.route('/')
def index():
     return render_template('index.html')

    

    
if __name__ == '__main__':
    app.run(host=os.getenv("IP", "0.0.0.0"),
            port=int(os.getenv("PORT", "5000")),
            debug=True)