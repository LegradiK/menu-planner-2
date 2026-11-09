"""import_recipe.py

Turn a recipe web page into a recipe dictionary in this app's JSON format.

Most recipe websites put a machine-readable copy of the recipe in the page
(schema.org "Recipe" data inside <script type="application/ld+json">).
This module reads that block, so no site-specific scraping is needed.
"""
import html
import json
import re
from fractions import Fraction
from html.parser import HTMLParser
from urllib.parse import urlparse

import requests

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/130.0 Safari/537.36"),
    "Accept-Language": "en-GB,en;q=0.9",
}
TIMEOUT = 15
MAX_URLS = 10


class RecipeImportError(Exception):
    """Raised when a page can't be fetched or has no recipe data."""


# ---------- Reading the page ----------

class _JsonLdParser(HTMLParser):
    """Collects the text of every <script type="application/ld+json"> tag."""

    def __init__(self):
        super().__init__()
        self.blocks = []
        self._inside = False

    def handle_starttag(self, tag, attrs):
        if tag == "script" and dict(attrs).get("type", "").lower().strip() == "application/ld+json":
            self._inside = True
            self.blocks.append("")

    def handle_endtag(self, tag):
        if tag == "script":
            self._inside = False

    def handle_data(self, data):
        if self._inside:
            self.blocks[-1] += data


def _walk(node):
    """Yield every dict inside nested JSON-LD (lists, @graph, etc.)."""
    if isinstance(node, list):
        for item in node:
            yield from _walk(item)
    elif isinstance(node, dict):
        yield node
        for value in node.values():
            if isinstance(value, (list, dict)):
                yield from _walk(value)


def _is_recipe(node: dict) -> bool:
    kind = node.get("@type", "")
    kinds = kind if isinstance(kind, list) else [kind]
    return "Recipe" in kinds


def find_recipe_data(page_html: str):
    """Return the schema.org Recipe dict from a page, or None."""
    parser = _JsonLdParser()
    parser.feed(page_html)
    for block in parser.blocks:
        try:
            data = json.loads(block.strip(), strict=False)
        except json.JSONDecodeError:
            continue
        for node in _walk(data):
            if _is_recipe(node):
                return node
    return None


def fetch_page(url: str) -> str:
    """Download a page's HTML."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RecipeImportError(f"Couldn't open {url} ({error.__class__.__name__}).") from error
    return response.text


# ---------- Cleaning values ----------

def clean_text(value) -> str:
    """Strip HTML tags/entities and squash whitespace."""
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"\s+([.,;:!?])", r"\1", text).strip()


def first_text(value) -> str:
    """Values can be a string, a list, or a {"name": ...} dict."""
    if isinstance(value, list):
        value = value[0] if value else ""
    if isinstance(value, dict):
        value = value.get("name") or value.get("text") or ""
    return clean_text(value)


def parse_instructions(value) -> list:
    """recipeInstructions can be a string, list of strings, HowToStep or HowToSection."""
    steps = []
    if isinstance(value, str):
        # One long string: split on new lines, or on full stops if there are none
        text = html.unescape(value)
        parts = re.split(r"<br\s*/?>|</p>|</li>|\n", text)
        steps = [clean_text(p) for p in parts]
    elif isinstance(value, list):
        for item in value:
            steps.extend(parse_instructions(item))
    elif isinstance(value, dict):
        if value.get("itemListElement"):            # HowToSection
            steps.extend(parse_instructions(value["itemListElement"]))
        else:                                        # HowToStep
            steps.append(clean_text(value.get("text") or value.get("name")))
    return [s for s in steps if s]


def parse_yield(value) -> int:
    """'4 servings', ['4', '4 servings'], 12 -> the first whole number, or 0."""
    if isinstance(value, list):
        value = " ".join(str(v) for v in value)
    match = re.search(r"\d+", str(value or ""))
    return int(match.group()) if match else 0


# ---------- Ingredients: "1 ½ tbsp olive oil" -> quantity / measurement / name ----------

UNICODE_FRACTIONS = {
    "½": "1/2", "⅓": "1/3", "⅔": "2/3", "¼": "1/4", "¾": "3/4", "⅕": "1/5",
    "⅖": "2/5", "⅗": "3/5", "⅘": "4/5", "⅙": "1/6", "⅚": "5/6", "⅛": "1/8",
    "⅜": "3/8", "⅝": "5/8", "⅞": "7/8",
}

UNITS = {
    "g": "g", "gram": "g", "grams": "g", "gr": "g",
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "mg": "mg",
    "ml": "ml", "millilitre": "ml", "millilitres": "ml", "milliliter": "ml", "milliliters": "ml",
    "l": "l", "litre": "l", "litres": "l", "liter": "l", "liters": "l",
    "tsp": "tsp", "teaspoon": "tsp", "teaspoons": "tsp",
    "tbsp": "tbsp", "tbs": "tbsp", "tablespoon": "tbsp", "tablespoons": "tbsp",
    "cup": "cup", "cups": "cup",
    "oz": "oz", "ounce": "oz", "ounces": "oz",
    "lb": "lb", "lbs": "lb", "pound": "lb", "pounds": "lb",
    "pinch": "pinch", "pinches": "pinch",
    "clove": "clove", "cloves": "clove",
    "can": "can", "cans": "can", "tin": "tin", "tins": "tin",
    "slice": "slice", "slices": "slice",
    "piece": "piece", "pieces": "piece",
    "handful": "handful", "handfuls": "handful",
    "bunch": "bunch", "bunches": "bunch",
    "sprig": "sprig", "sprigs": "sprig",
    "stick": "stick", "sticks": "stick",
    "pack": "pack", "packs": "pack", "packet": "packet", "packets": "packet",
    "sheet": "sheet", "sheets": "sheet",
    "dash": "dash",
}

_NUMBER = r"\d+\s+\d+/\d+|\d+/\d+|\d+(?:\.\d+)?"
_INGREDIENT = re.compile(
    rf"^(?P<qty>{_NUMBER})"
    rf"(?:\s*(?:-|–|to)\s*(?:{_NUMBER}))?"          # ranges like 4-5: keep the first number
    r"\s*(?P<rest>.*)$"
)


def format_quantity(text: str) -> str:
    """'1 1/2' -> '1.5', '1/3' -> '0.33', '2' -> '2'."""
    total = sum(Fraction(part) for part in text.split())
    value = round(float(total), 2)
    return str(int(value)) if value.is_integer() else str(value)


def parse_ingredient(line: str) -> dict:
    """Split one ingredient line into the app's {quantity, measurement, name}."""
    text = clean_text(line)
    for symbol, fraction in UNICODE_FRACTIONS.items():
        text = re.sub(rf"(\d)\s*{symbol}", rf"\1 {fraction}", text)   # 1½ -> 1 1/2
        text = text.replace(symbol, fraction)

    match = _INGREDIENT.match(text)
    if not match:
        return {"quantity": "", "measurement": "", "name": text}

    quantity = format_quantity(match.group("qty"))
    rest = match.group("rest").strip()

    measurement = ""
    unit_match = re.match(r"([A-Za-z]+)\.?\b\s*(.*)$", rest)
    if unit_match and unit_match.group(1).lower() in UNITS:
        measurement = UNITS[unit_match.group(1).lower()]
        rest = unit_match.group(2)
        rest = re.sub(r"^of\s+", "", rest)

    return {"quantity": quantity, "measurement": measurement, "name": rest.strip(" ,")}


# ---------- Putting it together ----------

def default_weight(genre: str, servings: int) -> int:
    """Main = days the food lasts (guess 2); dessert/bread = servings or pieces."""
    if genre == "main":
        return 2
    return servings or 1


def recipe_from_url(url: str, genre: str = "main") -> dict:
    """Fetch a recipe page and return it in the app's recipe format."""
    data = find_recipe_data(fetch_page(url))
    if not data:
        raise RecipeImportError(
            f"No recipe data found on {url}. That site may not publish it, "
            "so please add this one by hand."
        )

    name = first_text(data.get("name"))
    if not name:
        raise RecipeImportError(f"The recipe on {url} has no name.")

    ingredients = [parse_ingredient(i) for i in data.get("recipeIngredient") or []
                   if clean_text(i)]

    return {
        "genre": genre,
        "name": name,
        "ingredients": ingredients,
        "cuisine": first_text(data.get("recipeCuisine")) or "Other",
        "weight": default_weight(genre, parse_yield(data.get("recipeYield"))),
        "link": url,
        "instructions": parse_instructions(data.get("recipeInstructions")),
    }


def split_urls(text: str) -> list:
    """One URL per line (or separated by spaces); keep http(s) ones, no duplicates."""
    urls = []
    for candidate in re.split(r"\s+", text or ""):
        parsed = urlparse(candidate.strip())
        if parsed.scheme in ("http", "https") and parsed.netloc and candidate not in urls:
            urls.append(candidate.strip())
    return urls