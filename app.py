import os
from flask import (
    Flask, flash, render_template,
redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


# Import the env package in order to use my environment
# variables only when os can locate an existing
# file path for env.py file
if os.path.exists("env.py"):
    import env


# Create instance of Flask
app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

#  Set up instance of PyMongo to make sure Flask 
# app is communicating with my Mongo Database
mongo = PyMongo(app)


@app.route("/")
@app.route("/get_poems")
def get_poems():
    poems = mongo.db.poems.find()
    return render_template("poems.html", poems=poems)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)

