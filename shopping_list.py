"""This is to pull all the ingredients from suggested menus,
then sort the ingredients in an easier order/format for food shopping"""

# shopping_list.py
import re
from data import CATEGORIES, STOP_WORDS

PANTRY_CATEGORY = "Pantry & Dry Goods"   # must match your label for aisle_products
PANTRY_WORDS = {"stock", "broth", "oil"}   

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


def singularize(word: str) -> str:
    """Turn a plural word into its singular form (simple rules)."""
    if len(word) <= 3 or word.endswith("ss"):
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith(("oes", "ches", "shes", "xes")):
        return word[:-2]
    if word.endswith("s"):
        return word[:-1]
    return word


def normalise(text: str) -> str:
    """Lower-case, strip punctuation and singularise every word."""
    words = re.findall(r"[a-zà-ÿ'&-]+", str(text).lower())
    return " ".join(singularize(w) for w in words)


def find_category(name: str) -> str:
    """Return the category whose longest matching phrase appears in the name."""
    padded = f" {normalise(name)} "
    if PANTRY_WORDS & set(padded.split()):
        return PANTRY_CATEGORY

    best, best_len = "Uncategorized", 0
    for category, items in CATEGORIES.items():
        for item in items:
            phrase = normalise(item)
            if phrase and f" {phrase} " in padded and len(phrase) > best_len:
                best, best_len = category, len(phrase)
    return best


def categorize_ingredients(ingredient_list: list) -> dict:
    """Group shopping-list items by supermarket aisle."""
    categorized = {category: [] for category in CATEGORIES}
    categorized["Uncategorized"] = []
    for ingredient in ingredient_list:
        categorized[find_category(ingredient["name"])].append(ingredient)
    return categorized
