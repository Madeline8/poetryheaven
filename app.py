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
@app.route("/home")
def home():
    poems = list(mongo.db.poems.find())
    mobile_poems = [poems[0], poems[2], poems[5]]
    return render_template(
        "home.html", poems=poems, mobile_poems=mobile_poems)


@app.route("/poems")
def poems():
    poems=mongo.db.poems.find()
    return render_template(
        "poems.html", poems=poems)


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
    # get the user's username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    
    poems = list(mongo.db.poems.find({"created_by": session['user']}))
    

    if session["user"]:
        return render_template("profile.html", username=username, poems=poems)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove the user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_poem", methods=["GET", "POST"])
def add_poem():
    if request.method == "POST":
        poem = {
            "title": request.form.get("title"),
            "category": request.form.get("category"),
            "content": request.form.get("content"),
            "created_by": session["user"],
            "gender": request.form.get("gender"),
            "created_on": request.form.get("created_on"),
            "location": request.form.get("location")

        }
        mongo.db.poems.insert_one(poem)
        flash("New Poem Added!")
        # return redirect(url_for("profile"))
        return redirect(url_for("profile", username=session["user"]))

    categories = mongo.db.categories.find().sort("category_name", 1)
    gender_selection = mongo.db.gender_selection.find().sort("gender", 1)
    return render_template("add_poem.html", categories=categories, gender_selection=gender_selection)

# To see a specific poem separately
@app.route("/read_poem/<poems_id>")
# we are expecting a variable called 'poems_id' to be passed in whenever this
# URL is accessed
def read_poem(poems_id):
    """
    we define a variable called 'poem' which is an object from the MongoDB
    it uses the 'poems_id' value to find the right poem in the DB
    """
    poem = mongo.db.poems.find_one({"_id": ObjectId(poems_id)})
    """
    We render the 'read_poems.html' template and pass in the name of a
    variable that the template will have access to. It makes sense to call
    this variable 'poem'. This is the left-hand-side of the poem=poem
    The right-hand side of poem=poem is pointing to the variable we created above (poem = mongo.db.poems...)
    Now we have access to 'poem' in the template, and it will refer to the 
    'poem' variable we've created in this function.
    We need to make sure that in read_poem.html we use {{ poem }} whenever we 
    want to refer to our poem object.
    """
    return render_template(
        "read_poem.html",
        poem=poem)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)