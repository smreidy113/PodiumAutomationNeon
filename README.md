# PodiumAutomationNeon

## About  
This is an app that allows a user to retrieve information about plants from a database. It serves as scaffolding for the website — the actual content is not yet fully populated.

The app uses Flask for back-end data processing and business logic, and JavaScript for the front-end, which is currently designed to display data.

## Website/Data Organization  
The website begins with a list of categories the user can click on. For now, there are two categories: Type and Level of Sunlight.

After selecting a category, subcategories are displayed. When a subcategory is selected, the user can view all plants in the database associated with that subcategory.

From there, users can apply filters to narrow down the results.

---

## Future State

The future roadmap can be thought of in three phases:

### Super-Short Term – Content Iteration  
This app has a solid foundation, so the following changes can be made without any restructuring:

1. **Add filters**: Simply add your filter to the `filter_columns` constant. If it's a new type of filter, you'll need to add a strategy to the `get_flattened_options_by_column_and_mode` and `display_by_subcategory_and_filter` methods.
2. **Add information to the front-end**: Add the desired columns to the `columns_to_send` list in the back-end `app.py`, and update the `renderContentModule` function in the `subcategory.html` file to display them.

### Medium Term – Refactoring  
Here are several improvements that will make future content iteration more sustainable:

1. **Centralize filter and front-end configuration**: Currently, adding filters or front-end display info requires updates in multiple places. While there are TODOs to consolidate this into a single constant declaration using lambdas, a better solution would be to define a `Filter` class that encapsulates this logic. Filters could then be instantiated more scalably.
2. **Abstract database access**: Right now, the database is a local file. While this works short-term, switching to an external database will eventually be necessary. We should start by abstracting database access into a single method that acts as a facade. This way, migrating backends later would only require modifying that method.
3. **Flexible hierarchy**: We currently support two fixed categories and subcategories, mapped directly to database fields. A more flexible structure would mirror the filter refactor: define a `Category` class with display names, categorization strategies (as lambdas), and other attributes to support more dynamic behavior.

### Longer-Term – Scaling and Architecture  
To support greater scale and more robust architecture, we’ll need the following:

1. **Unify filters and categories**: Filters and categories are conceptually similar — both apply a strategy to segment data. We could create an abstract base class with shared logic, then implement specific `Category` and `Filter` subclasses with different display metadata.
2. **Move the database offline**: Decouple the app from a local dataset by migrating to a dedicated data source.
3. **Precompute filters and categories**: As data volume and user activity grow, we’ll need to precompute filter/category mappings asynchronously. Heavy data lifting should be handled ahead of time, so the web app only interacts with a smaller, optimized dataset.
4. **Separate front-end/back-end pipelines**: Eventually, we’ll want separate pipelines for front-end and back-end development to support independent ownership and release cycles.

---

## How to Run Locally

1. Install Flask (if not already installed):  
   `python -m pip install flask`

2. Install pandas (if not already installed):  
   `python -m pip install pandas`

3. Run the app:  
   `python app.py`

4. Open your browser and navigate to:  
   `http://127.0.0.1:5000/`
