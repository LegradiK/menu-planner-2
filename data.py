"""
This configuration file contains global settings for the application,
including categories of ingredients and common stop words that should
be ignored when processing ingredient names.
"""

# config.py
from categories import vegetables, fruits, meats_fish, spices, aisle_products, fridge_freezer

# Define category dictionary
CATEGORIES = {
    "Vegetables": [item.lower() for item in vegetables],
    "Fruits": [item.lower() for item in fruits],
    "Meats & Fish": [item.lower() for item in meats_fish],
    "Spices": [item.lower() for item in spices],
    "Pantry & Dry Goods": [item.lower() for item in aisle_products],
    "Fridge & Freezer": [item.lower() for item in fridge_freezer]
}

"""
CATEGORIES dictionary maps ingredient categories to lists of lowercase
ingredient names. This helps categorize ingredients for shopping lists and
recipe management.
"""

# Define common stop words
STOP_WORDS = {"see note", "coarsely", "grated","and", "very", "finely",
              "chopped", "sliced", "diced",
              "crushed", "peeled", "shredded", "fresh",
              "ground", "to taste", "optional",
              "well stirred", "juice only",
              "roughly chopped","cut into chunks", "bashed with a rolling pin",
              "fat ends", "torn into pieces",
              "if unavailable, use the grated zest of 1 lime",
              "if unavailable, use the zest of 1 lime","to serve",
              "boneless", "skinless"}

"""
STOP_WORDS is a set of common words and phrases that should be ignored
during ingredient processing. These words are usually descriptive and do
not affect the core ingredient name (e.g., "finely chopped", "fresh", etc.).
"""
