from flask import Flask, render_template, jsonify
import pandas as pd


#import requests  # Or internal function calls

app = Flask(__name__)

df = pd.read_json("database/plants.jsonl", lines=True)

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/category/<string:category>")
def api_categories(category):
    return {"content": "You selected the " + category + " category."}

@app.route("/category/<string:category>/subcat/<string:subcat>")
def api_subcategories(category, subcat):
    return {"content": "You selected the " + category + " and the " + subcat + " sub-category."}

@app.route("/getcategories")
def api_getcategories():
    return jsonify(['Herb', 'Begonia', 'Shrub'])


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":

    app.run(debug=True)