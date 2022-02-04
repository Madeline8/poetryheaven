import os
from flask import Flask


# Import the env package in order to use my environment
# variables only when os can locate an existing
# file path for env.py file
if os.path.exists("env.py"):
    import env


# Create instance of Flask
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World"


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
        port=int(os.environ.get("PORT")),
        debug=True)

