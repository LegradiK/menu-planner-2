"""This is to pull all the ingredients from suggested menus,
then sort the ingredients in an easier order/format for food shopping"""

# shopping_list.py
import re
from data import CATEGORIES, STOP_WORDS

def clean_ingredient_name(raw_name):
    """
    Removes unnecessary descriptive words, percentage values,
    text inside parentheses, and handles comma-separated ingredients.
    """
    # Remove percentage values (e.g., "85%", "93%", "85% to 93%")
    raw_name = re.sub(r'\b\d+%(\s*to\s*\d+%)?\b', '', raw_name).strip()

    # Remove unnecessary descriptive words from the ingredient name
    stop_words_pattern = r'\b(' + '|'.join(re.escape(word) for word in STOP_WORDS) + r')\b'
    cleaned_name = re.sub(stop_words_pattern, '', raw_name, flags=re.IGNORECASE).strip()

    # Remove anything inside parentheses (including brackets)
    cleaned_name = re.sub(r'\s*\(.*?\)\s*', ' ', cleaned_name).strip()

    # Clean after the first comma (if any)
    cleaned_name = re.split(r'\s*,\s*', cleaned_name, 1)[0]

    # Remove extra spaces
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()

    return cleaned_name

def collect_ingredients(global_menu):
    """
    Collects all ingredients from the global menu.
    """
    ingredients = []
    for recipe in global_menu:
        for ingredient in recipe.get("ingredients"):
            raw_name = ingredient["name"].lower()
            measurement = ingredient["measurement"]
            quantity = ingredient["quantity"]
            cleaned_name = clean_ingredient_name(raw_name)
            ingredients.append({
                'name': cleaned_name,
                'measurement': measurement,
                'quantity': quantity
            })
    return ingredients


def update_shopping_list(ingredients):
    """
    Updates the shopping list with ingredient quantities and measurements.
    """
    shopping_dict = {}
    ingredient_list = []

    for ingredient in ingredients:
        if ingredient['name'] in ingredient_list:
            if shopping_dict['cleaned_name']['measurement'] == ingredient['measurement']:
                shopping_dict['cleaned_name']['measurement'] += ingredient['quantity']
            else:
                shopping_dict = {
                    'name': ingredient['name'],
                    'quantity': ingredient['quantity'],
                    'measurement': ingredient['measurement']
                }
        else:
            shopping_dict = {
                'name': ingredient['name'],
                'quantity': ingredient['quantity'],
                'measurement': ingredient['measurement']
            }
        ingredient_list.append(shopping_dict)

    return ingredient_list


def singularize(word):
    """Converts plural words to singular (basic approach)."""
    if word.endswith("es"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def is_partial_match(ingredient_name, category_items):
    """
    Checks if any category item appears as a substring in the ingredient name.
    Also compares singular/plural forms.
    """
    words = ingredient_name.split()
    words = [singularize(word) for word in words]  # Convert words to singular form

    # Check for 'stock' in combination with meat names
    meat_keywords = ["beef", "pork", "chicken"]
    if any(meat in words for meat in meat_keywords) and "stock" in words:
        return "Aisle Product"  # Special case for stock-related meat items

    # Regular category matching logic
    for item in category_items:
        singular_item = singularize(item)  # Convert category item to singular form
        if any(singular_item in word for word in words):
            return category_items  # Return the matched category

    return None


def categorize_ingredients(ingredient_list):
    """Categorizes ingredients based on CATEGORIES."""
    categorized_ingredients = {category: [] for category in CATEGORIES}
    categorized_ingredients["Uncategorized"] = []  # For unknown ingredients

    for ingredient in ingredient_list:
        ingredient_name = ingredient["name"].lower()
        categorized = False

        # Check which category the ingredient belongs to (partial matching)
        for category, items in CATEGORIES.items():
            if is_partial_match(ingredient_name, items):
                categorized_ingredients[category].append(ingredient)
                categorized = True
                break  # Stop checking once a match is found

        # If no category matches, add to "Uncategorized"
        if not categorized:
            categorized_ingredients["Uncategorized"].append(ingredient)

    return categorized_ingredients
