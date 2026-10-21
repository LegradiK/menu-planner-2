"""build_menu.py

Load recipes from the JSON files in /recipes and build menus from them.
"""
import json
import random
from pathlib import Path

RECIPE_DIR = Path(__file__).parent / "recipes"

RECIPE_FILES = {
    "main": "main_recipes.json",
    "dessert": "dessert_recipes.json",
    "bread": "bread_recipes.json",
}


def load_recipes(genre: str) -> list:
    """Return recipes for one genre, or all genres if genre == 'all'."""
    genres = RECIPE_FILES.keys() if genre == "all" else [genre]
    recipes = []
    for g in genres:
        with (RECIPE_DIR / RECIPE_FILES[g]).open(encoding="utf-8") as file:
            recipes.extend(json.load(file)["recipes"])
    return recipes


def build_main_menu():
    """Build the menu by selecting random main recipes
    up to a total weight of 5, plus a random dessert."""
    main_menu = []
    total_weight = 0
    available_recipes = load_recipes("main")

    while total_weight < 5 and available_recipes:
        recipe = random.choice(available_recipes)
        main_menu.append(recipe)
        total_weight += recipe["weight"]
        available_recipes.remove(recipe)

    main_menu.append(random.choice(load_recipes("dessert")))
    return main_menu


def bread_suggestion():
    """Suggest a random bread recipe."""
    return random.choice(load_recipes("bread"))


if __name__ == "__main__":
    print(build_main_menu())
