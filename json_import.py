"""json_import.py

Read recipes from an uploaded JSON file and turn them into the app's recipe format.

Accepted file shapes:
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

MAX_FILE_BYTES = 1024 * 1024   # 1 MB is plenty for a few hundred recipes
MAX_RECIPES = 200


class JsonImportError(Exception):
    """Raised when a file can't be read or contains no usable recipes."""


def read_json_file(file_storage) -> object:
    """Load the JSON from a Flask/Werkzeug uploaded file."""
    filename = file_storage.filename or "file"
    if not filename.lower().endswith(".json"):
        raise JsonImportError(f"'{filename}' isn't a .json file.")

    raw = file_storage.read(MAX_FILE_BYTES + 1)
    if len(raw) > MAX_FILE_BYTES:
        raise JsonImportError(f"'{filename}' is bigger than 1 MB.")

    try:
        return json.loads(raw.decode("utf-8-sig"))   # -sig copes with a BOM from Windows editors
    except UnicodeDecodeError as error:
        raise JsonImportError(f"'{filename}' isn't a UTF-8 text file.") from error
    except json.JSONDecodeError as error:
        raise JsonImportError(
            f"'{filename}' isn't valid JSON (line {error.lineno}, column {error.colno}: {error.msg})."
        ) from error


def recipe_items(data) -> list:
    """Find the list of recipe dicts in whichever shape the file uses."""
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
    """Turn one recipe from the file into the app's format, or raise JsonImportError."""
    schema_org = "recipeIngredient" in item or "recipeInstructions" in item

    name = first_text(item.get("name"))
    if not name:
        raise JsonImportError("A recipe in the file has no name, so it was skipped.")

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


def recipes_from_json(file_storage, genre: str) -> tuple:
    """Read an uploaded file. Returns (recipes, problems) — problems are messages to show."""
    items = recipe_items(read_json_file(file_storage))
    if not items:
        raise JsonImportError(
            f"No recipes found in '{file_storage.filename}'. "
            'Use {"recipes": [...]}, a list of recipes, or a single recipe.'
        )

    recipes, problems = [], []
    if len(items) > MAX_RECIPES:
        problems.append(f"Only the first {MAX_RECIPES} recipes in the file were read.")
        items = items[:MAX_RECIPES]

    for item in items:
        try:
            recipes.append(clean_recipe(item, genre))
        except JsonImportError as error:
            problems.append(str(error))
    return recipes, problems