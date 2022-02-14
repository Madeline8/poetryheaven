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
    """
    This is the function for home.
    """
    poems = list(mongo.db.poems.find())
    mobile_poems = [poems[0], poems[2], poems[5]]
    return render_template(
        "home.html", poems=poems, mobile_poems=mobile_poems)


@app.route("/poems")
def poems():
    poems=list(mongo.db.poems.find())
    return render_template(
        "poems.html", poems=poems)


# Filter poems by category 
@app.route("/poems/<category>")
def filter_poems(category):
    if category == "Death":
        poems = list(mongo.db.poems.find({"category": "Death"}))
    elif category == "Family":
        poems = list(mongo.db.poems.find({"category": "Family"}))
    elif category == "Friendship":
        poems = list(mongo.db.poems.find({"category": "Friendship"}))
    elif category == "Humour":
        poems = list(mongo.db.poems.find({"category": "Humour"}))
    elif category == "Life":
        poems = list(mongo.db.poems.find({"category": "Life"}))
    elif category == "Love":
        poems = list(mongo.db.poems.find({"category": "Love"}))
    elif category == "Nature":
        poems = list(mongo.db.poems.find({"category": "Nature"}))
    elif category == "Family":
        poems = list(mongo.db.poems.find({"category": "Family"}))
    else:
        poems = list(mongo.db.poems.find({"category": "Spiritual"}))
    return render_template ("poems.html", poems=poems, category=category)


# Search functionality on poems.html
@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    poems = list(mongo.db.poems.find({"$text": {"$search": query}}))
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
            "password": generate_password_hash(request.form.get("password")),
            "gender": request.form.get("gender").lower()
        }

        mongo.db.users.insert_one(signup)

        #  put new user into session
        session["user"] = request.form.get("username").lower()
        flash("You have successfully Signed Up!")
        return redirect(url_for("profile", username=session["user"]))


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
    # Profile is only accessible by registered users 
    if not session.get("user"):
        return render_template("404.html")

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
    # Add Poem is only accessible by registered users 
    if not session.get("user"):
        return render_template("404.html")

    # Add new poem to db 
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

    categories = mongo.db.categories.find().sort("category", 1)
    gender_selection = mongo.db.gender_selection.find().sort("gender", 1)
    
    return render_template("add_poem.html", 
                            categories=categories,             gender_selection=gender_selection)

# To see a specific poem separately
@app.route("/read_poem/<poems_id>")
# we are expecting a variable called 'poems_id' to be passed in whenever this
# URL is accessed
def read_poem(poems_id):
    poem = mongo.db.poems.find_one({"_id": ObjectId(poems_id)})
    return render_template(
        "read_poem.html",
        poem=poem)


@app.route("/update_poem/<poems_id>", methods=["GET", "POST"])
def update_poem(poems_id):
    # Update Poem is only accessible by registered users 
    if not session.get("user"):
        return render_template("404.html")

    if request.method == "POST":
        submit = {
            "title": request.form.get("title"),
            "category": request.form.get("category"),
            "content": request.form.get("content"),
            "created_by": session["user"],
            "gender": request.form.get("gender"),
            "created_on": request.form.get("created_on"),
            "location": request.form.get("location")

        }
        mongo.db.poems.update({"_id": ObjectId(poems_id)}, submit)
        flash("Poem Successfully Updated!")
        return redirect(url_for("profile", username=session["user"]))

    poem = mongo.db.poems.find_one({"_id": ObjectId(poems_id)})
    categories = mongo.db.categories.find().sort("category", 1)
    gender = mongo.db.gender_selection.find().sort("gender", 1)
    return render_template("update_poem.html", poem=poem, categories=categories, gender=gender)


@app.route("/delete_poem/<poems_id>")
def delete_poem(poems_id):
    """
    Deletes user's poem
    """
    mongo.db.poems.remove({"_id": ObjectId(poems_id)})
    flash("Poem Successfully Deleted")
    return redirect(url_for("profile", username=session["user"]))


@app.route("/categories")
def categories():
    # Categories field is only accessible by admin
    if not session.get("user") == "admin":
        return render_template("404.html")

    categories = list(mongo.db.categories.find().sort("category", 1))
    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":
        category = {
            "category": request.form.get("category")
        }
        mongo.db.categories.insert_one(category)
        flash("New Category Added")
        return redirect(url_for("categories"))

    return render_template("add_category.html")


@app.route("/update_category/<category_id>", methods=["GET", "POST"])
def update_category(category_id):
    if request.method == "POST":
        submit = {
            "category": request.form.get("category")
        }
        mongo.db.categories.update({"_id": ObjectId(category_id)}, submit)
        flash("Category Successfully Updated")
        return redirect(url_for("categories"))

    category = mongo.db.categories.find_one({"_id": ObjectId(category_id)})
    return render_template("update_category.html", category=category)


@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    mongo.db.categories.remove({"_id": ObjectId(category_id)})
    flash("Category Successfully Deleted")
    return redirect(url_for("categories"))

# Error Handlers 
@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)