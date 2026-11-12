"""json_import.py

Read recipes from pasted JSON text and turn them into the app's recipe format.

Accepted shapes:
    {"recipes": [ {...}, {...} ]}     <- same as main_recipes.json etc.
    [ {...}, {...} ]                  <- a plain list of recipes
    {...}                             <- one recipe on its own

Each recipe can be in this app's format, or a schema.org "Recipe" object
(the kind recipe websites publish), so a copied JSON-LD block works too.
The genre chosen on the form (main / dessert / bread) is applied to every recipe.
"""
import json

from import_recipe import (
    clean_text, default_weight, first_text,
    parse_ingredient, parse_instructions, parse_yield,
)

MAX_TEXT_LENGTH = 1024 * 1024   # 1 MB of text is plenty for a few hundred recipes
MAX_RECIPES = 200


class JsonImportError(Exception):
    """Raised when the text can't be read or contains no usable recipes."""


def read_json_text(text: str) -> object:
    """Parse the pasted JSON, with a helpful message if it's broken."""
    text = (text or "").strip()
    if not text:
        raise JsonImportError("Paste some recipe JSON first.")
    if len(text) > MAX_TEXT_LENGTH:
        raise JsonImportError("That's too much text to import in one go (over 1 MB).")
    try:
        return json.loads(text)
    except json.JSONDecodeError as error:
        raise JsonImportError(
            f"That isn't valid JSON (line {error.lineno}, column {error.colno}: {error.msg})."
        ) from error


def recipe_items(data) -> list:
    """Find the list of recipe dicts in whichever shape was pasted."""
    if isinstance(data, dict) and isinstance(data.get("recipes"), list):
        items = data["recipes"]
    elif isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        items = [data]
    else:
        items = []
    return [item for item in items if isinstance(item, dict)]


# ---------- Cleaning one recipe ----------

def _clean_ingredient(item) -> dict:
    """Ingredient as {"quantity", "measurement", "name"} or a line like '200 g flour'."""
    if isinstance(item, str):
        return parse_ingredient(item)
    if isinstance(item, dict):
        return {
            "quantity": clean_text(item.get("quantity", "")),
            "measurement": clean_text(item.get("measurement") or item.get("unit") or ""),
            "name": clean_text(item.get("name", "")),
        }
    return {"quantity": "", "measurement": "", "name": ""}


def _clean_weight(value, genre: str) -> int:
    """A whole number of at least 1; fall back to the genre's usual default."""
    try:
        weight = int(float(value))
    except (TypeError, ValueError):
        return default_weight(genre, 0)
    return weight if weight >= 1 else default_weight(genre, 0)


def clean_recipe(item: dict, genre: str) -> dict:
    """Turn one pasted recipe into the app's format, or raise JsonImportError."""
    schema_org = "recipeIngredient" in item or "recipeInstructions" in item

    name = first_text(item.get("name"))
    if not name:
        raise JsonImportError("A recipe has no name, so it was skipped.")

    if schema_org:
        raw_ingredients = item.get("recipeIngredient") or []
        instructions = parse_instructions(item.get("recipeInstructions"))
        cuisine = first_text(item.get("recipeCuisine"))
        weight = default_weight(genre, parse_yield(item.get("recipeYield")))
        link = clean_text(item.get("url", ""))
    else:
        raw_ingredients = item.get("ingredients") or []
        instructions = parse_instructions(item.get("instructions"))
        cuisine = first_text(item.get("cuisine"))
        weight = _clean_weight(item.get("weight"), genre)
        link = clean_text(item.get("link", ""))

    if not isinstance(raw_ingredients, list):
        raw_ingredients = [raw_ingredients]
    ingredients = [i for i in map(_clean_ingredient, raw_ingredients) if i["name"]]
    if not ingredients:
        raise JsonImportError(f"'{name}' has no ingredients, so it was skipped.")

    return {
        "genre": genre,
        "name": name,
        "ingredients": ingredients,
        "cuisine": cuisine or "Other",
        "weight": weight,
        "link": link,
        "instructions": instructions,
    }


def recipes_from_json(text: str, genre: str) -> tuple:
    """Read pasted JSON. Returns (recipes, problems) — problems are messages to show."""
    items = recipe_items(read_json_text(text))
    if not items:
        raise JsonImportError(
            "No recipes found in the pasted JSON. "
            'Use {"recipes": [...]}, a list of recipes, or a single recipe.'
        )

    recipes, problems = [], []
    if len(items) > MAX_RECIPES:
        problems.append(f"Only the first {MAX_RECIPES} recipes were read.")
        items = items[:MAX_RECIPES]

    for item in items:
        try:
            recipes.append(clean_recipe(item, genre))
        except JsonImportError as error:
            problems.append(str(error))
    return recipes, problems