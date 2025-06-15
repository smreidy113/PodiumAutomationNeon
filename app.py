from flask import Flask, render_template, jsonify, request
import pandas as pd


#import requests  # Or internal function calls

app = Flask(__name__)

df = pd.read_json("database/plants.jsonl", lines=True)
types_subcats = df['type'].dropna().unique().tolist()
care_level_subcats = df['care_level'].dropna().unique().tolist()
category_hierarchy = {'Type': 'type', 'Care Level': 'care_level'}
subcategories = {'type': types_subcats, 'care_level': care_level_subcats}
filter_columns = ['sunlight', 'propagation']

subcategory_elements = pd.DataFrame()

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

def flattened_list_by_key(df, k):
    return sorted({
        val.lower()
        for sublist in df[k].dropna()
        for val in sublist
    })

@app.route("/dbapi/filters/<string:category_value>/<string:subcategory_value>/")
def filters(category_value, subcategory_value):
    subcategory_elements = df[df[category_value] == subcategory_value]
    sunlight_values = flattened_list_by_key(subcategory_elements,'sunlight')
    propagation_values = flattened_list_by_key(subcategory_elements,'propagation')
    print(sunlight_values)
    return jsonify({
        "sunlight": {"type": "multi", "options": sunlight_values},
        "propagation": {"type": "multi", "options": propagation_values}
    })

@app.route("/content/<string:category_value>/")
def category_page(category_value):
    return render_template("category.html")

@app.route("/api/<string:category_value>/")
def api_category(category_value):
    return jsonify(subcategories[category_value])


@app.route("/content/<string:category_value>/<string:subcategory_value>/")
def subcategory_page(category_value, subcategory_value):
    return render_template("subcategory.html")

@app.route("/api/<string:category_value>/<string:subcategory_value>/filter-results")
def api_subcategory(category_value, subcategory_value):
    print(request)
    columns_to_send = ['common_name', 'type', 'care_level', 'indoor']
    subcategory_elements = df[df[category_value] == subcategory_value]
    for column in filter_columns:
        selected_values = request.args.getlist(column)
        if selected_values:
            subcategory_elements = subcategory_elements[
                subcategory_elements[column].apply(
                    lambda cell: any(val.lower() in [c.lower() for c in (cell or [])] for val in selected_values)
                )
            ]
    print(subcategory_elements)
    print("I GOT HERE")
    return jsonify(subcategory_elements[columns_to_send].to_dict(orient='records'))

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