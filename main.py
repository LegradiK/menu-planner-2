"""main.py

Where it all comes together
"""
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from build_menu import build_main_menu, bread_suggestion
from save_recipe import save_recipe
from shopping_list import collect_ingredients, update_shopping_list, categorize_ingredients

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, "data.env"))

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("FLASK_KEY")

# sample data

sample_data = {
    "message": "Hello Flask API world!",
    "status": "success"
}

global_menu = []

RECIPE_FILES = {
    "main": "main_recipes.json",
    "dessert": "dessert_recipes.json",
    "bread": "bread_recipes.json",
}
 
CATEGORY_LABELS = {"main": "Main dishes", "dessert": "Desserts", "bread": "Bread"}
 



class SearchForm(FlaskForm):
    """
    FlaskForm for /search page, searches a particular recipe
    """
    genre = SelectField('Genre', choices=[('all', 'All'), ('main', 'Main'), ('dessert', 'Dessert'), ('bread', 'Bread')],
                        validators=[DataRequired()])
    recipe_name = StringField('Recipe Name', validators=[DataRequired()])
    submit = SubmitField('Search')

class DeleteForm(FlaskForm):
    """
    FlaskForm for /delete page, search and confirm delete a particular recipe
    """
    genre = SelectField('Genre', choices=[('main', 'Main'), ('dessert', 'Dessert')],
                        validators=[DataRequired()])
    recipe_name = StringField('Recipe Name', validators=[DataRequired()])
    submit = SubmitField('Search')
    delete = SubmitField('Confirm Delete')

@app.route('/')
def home():
    """
    Default route when visiting /
    Returns:
        Default site
    """
    return render_template('index.html')

@app.route('/sample', methods=['GET'])
def get_data():
    """
    Route when visiting /sample
    Returns:
        Sample response
    """
    return jsonify(sample_data)

@app.route('/menu', methods=['GET'])
def get_menu():
    """
    Route when visiting /menu
    Returns:
        json response of built menu
    """
    built_menu = build_main_menu()
    return jsonify(built_menu)

@app.route('/recipes', methods=['GET'])
def get_recipes():
    """
    Route when visiting /recipes
    Returns:
        HTML response of built menu
    """
    global global_menu    # pylint: disable=global-statement
    global_menu = build_main_menu()
    bread_suggestion_data = bread_suggestion()
    return render_template('recipes.html', menu=global_menu, bread=bread_suggestion_data)


@app.context_processor
def inject_year():
    """Make {{ current_year }} available in every template (used in the footer)."""
    return {"current_year": datetime.now().year}
 
 
@app.route("/all-recipes")
def all_recipes():
    """
    Route when visiting /all-recipes
    Returns:
        every recipe, grouped by category (main / dessert / bread)
        and then by cuisine (Italian, Japanese, ...)
    """
    catalogue = {}
 
    for key, filename in RECIPE_FILES.items():
        file_path = os.path.join(app.root_path, "recipes", filename)
        if not os.path.exists(file_path):
            continue
 
        # Read the file on every visit so newly added recipes show straight away
        with open(file_path, "r", encoding="utf-8") as file:
            recipes = json.load(file)["recipes"]
 
        groups = defaultdict(list)
        for recipe in recipes:
            cuisine = (recipe.get("cuisine") or "Other").strip().title()
            groups[cuisine].append(recipe)
 
        catalogue[CATEGORY_LABELS[key]] = {
            cuisine: sorted(items, key=lambda r: r["name"].lower())
            for cuisine, items in sorted(groups.items())
        }
 
    return render_template("all_recipes.html", catalogue=catalogue)


@app.route('/search', methods=["GET","POST"])
def search_recipe():
    """
    Route when visiting /search
    Returns:
        a search result
    """
    form = SearchForm()
    search_item = None

    if form.validate_on_submit():
        name = form.recipe_name.data
        genre = form.genre.data
        file_path = None

        if genre == "main":
            file_path = 'recipes/main_recipes.json'
        elif genre == "dessert":
            file_path = 'recipes/dessert_recipes.json'
        elif genre == "bread":
            file_path = 'recipes/bread_recipes.json'

        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            recipes = data["recipes"]

        for i in recipes:
            if name.lower() == i["name"].lower():
                search_item = i
                break

        return render_template('search.html', form=form, recipe=search_item)

    return render_template('search.html', form=form)

@app.route('/delete', methods=['POST','GET'])
def delete():
    """
    Route when visiting /delete
    Returns:
        delete a certain recipe as requested
    """
    form = DeleteForm()
    recipe_to_delete = None
    # grab user inputs
    if request.method == 'POST':
        name = form.recipe_name.data
        genre = form.genre.data
    # check if the recipe is in main_recipes.json or dessert_recipes.json
        file_path = None
        if genre == "main":
            file_path = 'recipes/main_recipes.json'
        elif genre == "dessert":
            file_path = 'recipes/dessert_recipes.json'
        elif genre == "bread":
            file_path = 'recipes/bread_recipes.json'
        #check if file_path is correctly assigned
        if not file_path:
            return redirect(url_for('home'))

        # open the file according to the path with read mode
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            recipes = data["recipes"]
        # find a recipe user is looking for
        for i in recipes:
            if name.lower() == i["name"].lower():
                recipe_to_delete = i
                break
        # check if the recipe is in json file
        if not recipe_to_delete:
            flash(f"Recipe '{name}' not found!", "error")
            return redirect(url_for('delete'))
        # If the "Search" button was clicked
        if request.form.get('search') == 'search':
            return render_template('delete.html', form=form,
                                    recipe_to_delete=recipe_to_delete)

        name = recipe_to_delete['name']

        confirm_delete = request.form.get('delete')
        print("Confirm_delete_value:", confirm_delete)
        if confirm_delete == "yes":
            recipes.remove(recipe_to_delete)

            # Save the updated recipes list back to the file (write mode)
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump({"recipes": recipes}, file, indent=4)
            # message that the recipe has been deletec
            flash(message=
                  f"Recipe '{recipe_to_delete['name']}' has been successfully deleted.",
                  category="success")
            return redirect(url_for('home'))

        # this is the page when user searched for a certain recipe after opening /delete
        return render_template('delete.html', form=form,
                                   recipe_to_delete=recipe_to_delete)

    # this is the page when opening /delete
    return render_template('delete.html',form=form)

@app.route('/shopping_list', methods=['GET','POST'])
def make_list():
    """
    Generates a sorted shopping list based on recipes in global_menu.
    """
    # Collect ingredients, update shopping list and categorize ingredients
    ingredients = collect_ingredients(global_menu)
    ingredient_list = update_shopping_list(ingredients)
    categorized_ingredients = categorize_ingredients(ingredient_list)

    # Render the template with the categorized ingredients
    return render_template('shopping_list.html', categorized_ingredients=categorized_ingredients)
#     shopping_dict = {}  # Store ingredient quantities and measurements
#     ingredients = []
#     ingredient_list = []

#     for recipe in global_menu:
#         for ingredient in recipe.get("ingredients"):  # Directly access ingredients
#             raw_name = ingredient["name"].lower()
#             measurement = ingredient["measurement"]
#             quantity = ingredient["quantity"]
#             cleaned_name = clean_ingredient_name(raw_name)
#             # print(cleaned_name)
#             ingredients.append({
#                 'name': cleaned_name,
#                 'measurement' : measurement,
#                 'quantity' : quantity
#             })

# # Check if ingredient already exists
#     for ingredient in ingredients:
#         if ingredient['name'] in ingredient_list:
#             if shopping_dict['cleaned_name']['measurement'] == ingredient['measurement']:
#                 shopping_dict['cleaned_name']['measurement'] += ingredient['quantity']
#             else:
#                 shopping_dict = {
#                     'name':ingredient['name'],
#                     'quantity': ingredient['quantity'],
#                     'measurement': ingredient['measurement']
#                 }
#         else:
#             shopping_dict = {
#                     'name':ingredient['name'],
#                     'quantity': ingredient['quantity'],
#                     'measurement': ingredient['measurement']
#                 }
#         ingredient_list.append(shopping_dict)

#     categorized_ingredients = {category: [] for category in CATEGORIES.keys()}
#     categorized_ingredients["Uncategorized"] = []  # For unknown ingredients

#     def singularize(word):
#         """Convert plural words to singular (basic approach)."""
#         if word.endswith("es"):  # Handle plural ending in "es" (e.g., tomatoes -> tomato)
#             return word[:-2]
#         if word.endswith("s") and not word.endswith("ss"):
#             # Handle regular plural (e.g., apples -> apple)
#             return word[:-1]
#         return word

#     def is_partial_match(ingredient_name, category_items):
#         """
#         Check if any category item appears as a substring in the ingredient name.
#         Also compares singular/plural forms.
#         """
#         words = ingredient_name.split()
#         words = [singularize(word) for word in words]  # Convert words to singular form

#         # Check for 'stock' in combination with meat names
#         meat_keywords = ["beef", "pork", "chicken"]
#         if any(meat in words for meat in meat_keywords) and "stock" in words:
#             return "Aisle Product"  # Special case for stock-related meat items

#         # Regular category matching logic
#         for item in category_items:
#             singular_item = singularize(item)  # Convert category item to singular form
#             if any(singular_item in word for word in words):
#                 return category_items  # Return the matched category

#         return None  # If no match is found, return None

#     def categorize_ingredients(ingredient_list):
#         for ingredient in ingredient_list:
#             ingredient_name = ingredient["name"].lower()
#             categorized = False

#             # Check which category the ingredient belongs to (partial matching)
#             for category, items in CATEGORIES.items():
#                 if is_partial_match(ingredient_name, items):
#                     categorized_ingredients[category].append(ingredient)
#                     categorized = True
#                     break  # Stop checking once a match is found

#             # If no category matches, add to "Uncategorized"
#             if not categorized:
#                 categorized_ingredients["Uncategorized"].append(ingredient)

#     return render_template('shopping_list.html', categorized_ingredients=categorized_ingredients)


def process_webform(webform_text):
    """
    Processes a multi-line string of webform text.
    Args:
        webform_text (str): A string containing items separated by new lines.
    Returns:
        list: A list of cleaned, non-empty webform strings.
    """
    return [webform_text.strip() for webform_text in webform_text.splitlines()
            if webform_text.strip()]

@app.route('/adding', methods=['GET', 'POST'])
def add_recipes():
    """
    Route when visiting /adding
    Returns:
        Save input to existing recipes
    """
    if request.method == 'POST':
        list_ingredients = []

        index = 0
        while f'ingredients[{index}][quantity]' in request.form:
            # Extracting ingredient data
            ingredient_quantity = request.form.get(f'ingredients[{index}][quantity]')
            ingredient_measurement = request.form.get(f'ingredients[{index}][measurement]')
            ingredient_name = request.form.get(f'ingredients[{index}][name]')
            list_ingredients.append({'quantity': ingredient_quantity,
                                     'measurement': ingredient_measurement,
                                     'name': ingredient_name})
            index += 1
            # print(index, list_ingredients)
        # Create the recipe dictionary as per the required format
        recipe = {
        "genre": request.form['genre'],
        "name": request.form['name'],
        "ingredients": list_ingredients,
        "cuisine": request.form['cuisine'],
        "weight": int(request.form['weight']),
        "link": request.form['link'],
        "instructions": process_webform(request.form['instructions'])
    }
        save_recipe(recipe)
        session['new_recipe'] = recipe  # Store in session for retrieval
        return redirect(url_for('successful'))
    return render_template('adding.html')

@app.route('/successful', methods=['GET'])
def successful():
    """
    Route when visiting /successful
    Returns:
        HTML response when add_recipes() ran correctly
    """
    recipe = session.get('new_recipe')

    if not recipe:
        flash("No recipe found! Please try adding a recipe again.", "error")
        return redirect(url_for('add_recipes'))

    return render_template('successful.html', recipe=recipe)


if __name__ == '__main__':
    app.run(debug=True)
