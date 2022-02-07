"""
"""

import os
from flask import (
    Flask, flash, render_template,
redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash


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


# Home Page
@app.route("/")
@app.route("/get_poems")
def get_poems():
    poems = mongo.db.poems.find()
    return render_template("poems.html", poems=poems)

# Sign Up Page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        #check if username exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("signup"))

        signup = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(signup)

        #  put new user into session
        session["user"] = request.form.get("username").lower()
        flash("You have successfully Signed Up!")
        return redirect(url_for("profile", username=session["user"]))
        return redirect(url_for("signup", username=session["user"]))


    return render_template("signup.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Hi, {}".format(
                            request.form.get("username")))
                        return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html") 


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # get the user's username form database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))



if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)