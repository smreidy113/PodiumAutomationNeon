from flask import Flask, render_template, jsonify, request
import pandas as pd

app = Flask(__name__)

# Pre-load the plant data. This works when there are a small number of entries.  TODO: add an abstraction layer for accessing data so 
# we can swap this code easily for an accessor to a database.
df = pd.read_json("database/plants.jsonl", lines=True)

# Define Categories and sub-categories.
types_subcats = df['type'].dropna().unique().tolist()
care_level_subcats = df['care_level'].dropna().unique().tolist()
category_hierarchy = {'Type': 'type', 'Care Level': 'care_level'}
subcategories = {'type': types_subcats, 'care_level': care_level_subcats}

# Add a filter, including the type of filter. Right now 'multi' and 'range' are supported. If you want to add another one, 
filter_columns = [('sunlight', 'multi'), ('propagation', 'multi'), ('hardiness', 'range')]

# Columns that can be displayed to the front-end, to limit the amount of data sent.
columns_to_send = ['common_name', 'type', 'care_level', 'indoor', 'scientific_name']

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# Generate a set of ranges for filters which are numerical.
def generate_even_ranges(min_val, max_val, segments):
    total_values = max_val - min_val + 1
    base_size = total_values // segments
    remainder = total_values % segments

    ranges = []
    start = min_val

    for i in range(segments):
        # Distribute remainder across the first `remainder` ranges
        size = base_size + (1 if i < remainder else 0)
        end = start + size - 1
        ranges.append((start, end))
        start = end + 1

    return ranges

# Based on the format of the data, provide a strategy for how to define and display the options.
# TODO: Add these as lambdas to the `filter_columns` constant so the info is all in one place.
def get_flattened_options_by_column_and_mode(df, k, mode):
    if mode == 'multi':
        return sorted({
            val.lower()
            for sublist in df[k].dropna()
            for val in sublist
        })
    # 'range' assumes that there will be a 'min' and 'max' value in this column.
    if mode == 'range':
        mins = [int(x) for x in df[k].dropna().apply(lambda h: h.get('min')).tolist()]
        maxs = [int(x) for x in df[k].dropna().apply(lambda h: h.get('max')).tolist()]

        #ToDO: make the hardcoded '5' a config.
        return generate_even_ranges(min(mins), max(maxs), 5)

# Generate initial list of filters. TODO: consolidate this redundant code with 
@app.route("/dbapi/filters/<string:category_value>/<string:subcategory_value>/")
def filters(category_value, subcategory_value):
    subcategory_elements = df[df[category_value] == subcategory_value]
    filter_configs = {}
    for filter in filter_columns:
        filter_configs[filter[0]] = {"type": filter[1], "options": get_flattened_options_by_column_and_mode(subcategory_elements,filter[0], filter[1])}
    return jsonify(filter_configs)

@app.route("/content/<string:category_value>/")
def category_page(category_value):
    return render_template("category.html")

@app.route("/api/<string:category_value>/")
def api_category(category_value):
    return jsonify(subcategories[category_value])


@app.route("/content/<string:category_value>/<string:subcategory_value>/")
def subcategory_page(category_value, subcategory_value):
    return render_template("subcategory.html")

def transform_selected_values(selected_values):
    ret = [tuple(map(int, selected_range_str.split(','))) for selected_range_str in selected_values]
    return ret


@app.route("/api/<string:category_value>/<string:subcategory_value>/filter-results")
def display_by_subcategory_and_filter(category_value, subcategory_value):
    app.logger.debug("Filtering based on request " + str(request) + ".")
    subcategory_elements = df[df[category_value] == subcategory_value]
    updated_options = {}

    # Pre-load options as-is to preserve options. We may eliminate some down the road if some filters eliminate enough entries.
    for filter in filter_columns:
        updated_options[filter[0]] = get_flattened_options_by_column_and_mode(subcategory_elements, filter[0], filter[1])

    for column in filter_columns:
        selected_values = request.args.getlist(column[0])
        
        if selected_values:
            app.logger.debug("Filtering " + str(column[0]) + " based on " + str(selected_values) + ".")

            # Apply filter based on filter type. TODO: Add these as a lambda to the `filter_columns` constant.
            if column[1] == 'multi': 
                subcategory_elements = subcategory_elements[
                    subcategory_elements[column[0]].apply(
                        lambda cell: any(val.lower() in [c.lower() for c in (cell or [])] for val in selected_values)
                    )
                ]
            elif column[1] == 'range':
                subcategory_elements = subcategory_elements[
                    subcategory_elements[column[0]].apply(
                        lambda cell: any(
                            cell and
                            cell.get('min') and cell.get('max') and
                            int(cell['min']) <= x[0] and int(cell['max']) >= x[1] for x in transform_selected_values(selected_values))
                    )]
        else:
            app.logger.debug("No filter on " + str(column[0]) + ".")
        
    # We don't want to remove other options from filters the user has selected. That will force them to refresh the page in order to remove filters.
    for column in filter_columns:
        selected_values = request.args.getlist(column[0])
        if not selected_values:
            updated_options[column[0]] = get_flattened_options_by_column_and_mode(subcategory_elements, column[0], column[1])
    
    return jsonify({
        "results": subcategory_elements[columns_to_send].to_dict(orient='records'),
        "available_filters": updated_options
    })

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