"""This is to pull all the ingredients from suggested menus,
then sort the ingredients in an easier order/format for food shopping"""

# shopping_list.py
import re

from data import CATEGORIES, STOP_WORDS

# Must match the labels used in CATEGORIES (data.py)
LIQUIDS = "Pantry Goods - Liquid"
DRY = "Pantry Goods - Dry"


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
    cleaned_name = re.split(r'\s*,\s*', cleaned_name, maxsplit=1)[0]

    # Remove extra spaces
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip()

    return cleaned_name


def collect_ingredients(global_menu):
    """
    Collects all ingredients from the global menu.
    """
    ingredients = []
    for recipe in global_menu:
        for ingredient in recipe.get("ingredients", []):
            ingredients.append({
                'name': clean_ingredient_name(ingredient["name"].lower()),
                'measurement': ingredient.get("measurement", ""),
                'quantity': ingredient.get("quantity", "")
            })
    return ingredients


def to_number(quantity):
    """Return the quantity as a float, or None if it isn't a plain number."""
    try:
        return float(quantity)
    except (TypeError, ValueError):
        return None


def format_number(number):
    """Show 2.0 as '2' and 1.25 as '1.25'."""
    return f"{number:g}"


def update_shopping_list(ingredients):
    """
    Merges duplicate ingredients: the same name and unit are added together
    (e.g. 1 onion + 0.5 onion = 1.5 onion, 3 eggs + 1 egg = 4 eggs).
    """
    merged = {}
    for ingredient in ingredients:
        key = (normalise(ingredient['name']), str(ingredient['measurement']).strip().lower())
        quantity = to_number(ingredient['quantity'])

        if key not in merged:
            merged[key] = dict(ingredient)
        elif quantity is not None and to_number(merged[key]['quantity']) is not None:
            total = to_number(merged[key]['quantity']) + quantity
            merged[key]['quantity'] = format_number(total)
        elif not str(merged[key]['quantity']).strip():
            # "to taste" first, real amount later: keep the amount
            merged[key]['quantity'] = ingredient['quantity']

    return list(merged.values())


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
    words = set(padded.split())

    # Stock: cubes/pots are dry, everything else ("chicken stock") is liquid
    if words & {"stock", "broth"}:
        return DRY if words & {"cube", "pot"} else LIQUIDS

    best, best_len = "Uncategorized", 0
    for category, items in CATEGORIES.items():
        for item in items:
            phrase = normalise(item)
            if phrase and f" {phrase} " in padded and len(phrase) > best_len:
                best, best_len = category, len(phrase)

    # Any leftover oil ("oil, for frying") belongs with the liquids
    if best == "Uncategorized" and "oil" in words:
        return LIQUIDS
    return best


def categorize_ingredients(ingredient_list: list) -> dict:
    """Group shopping-list items by supermarket section."""
    categorized = {category: [] for category in CATEGORIES}
    categorized["Uncategorized"] = []
    for ingredient in ingredient_list:
        categorized[find_category(ingredient["name"])].append(ingredient)
    return categorized