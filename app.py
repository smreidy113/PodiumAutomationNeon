from flask import Flask, render_template, jsonify
import pandas as pd


#import requests  # Or internal function calls

app = Flask(__name__)

df = pd.read_json("database/plants.jsonl", lines=True)
types_subcats = df['type'].unique().tolist()
care_level_subcats = df['care_level'].unique().tolist()
category_hierarchy = {'Type': 'type', 'Care Level': 'care_level'}
subcategories = {'type': types_subcats, 'care_level': care_level_subcats}


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/<string:category_value>/")
def category_page(category_value):
    return render_template("category.html")

@app.route("/api/<string:category_value>/")
def api_category(category_value):
    return jsonify(subcategories[category_value])

@app.route("/<string:category_name>/<string:subcat>")
def api_subcategories(category, subcat):
    return {"content": "You selected the " + category + " and the " + subcat + " sub-category."}

@app.route("/api/getcategories")
def api_getcategories():
    return jsonify(category_hierarchy)

@app.route("/getsubcategories/<string:category_value>")
def api_getsubcategories(category_value):
    return jsonify(category_hierarchy[category_value])

@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":

    app.run(debug=True)