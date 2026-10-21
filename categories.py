"""
categories for sorting items in shopping list to sophisticate the shopping_list
"""

vegetables = [
    "carrot", "broccoli", "spinach", "lettuce", "potato",
    "cucumber", "bell pepper", "tomato", "onion", "courgette",
    "cauliflower", "green bean", "pea", "kale", "aubergine",
    "asparagus", "brussels sprout", "beetroot", "sweet potato",
    "artichoke", "radish", "squash", "leek", "cabbage", "mushroom",
    "fennel", "chard", "mustard green", "turnip", "okra",
    "celery", "pumpkin", "pak choi", "celeriac", "chilli pepper",
    "endive", "alfalfa sprout", "parsnip", "radicchio", "shallot",
    "watercress", "ginger", "taro", "daikon", "snow pea",
    "collard green", "yam", "chayote", "cucamelon", "water chestnut",
    "spring onion", "mangetout", "baby corn", "swede", "butternut squash",
    "romanesco", "tatsoi", "chinese cabbage", "nettle", "mooli",
    "kohlrabi", "jerusalem artichoke", "samphire", "salsify",
    "cress", "endive", "bok choy", "sea kale", "dandelion green",
    "bamboo shoot", "shitake mushroom", "portobello mushroom",
    "chestnut mushroom", "king oyster mushroom", "enoki mushroom",
    "coconut", "zaalouk", "button mushroom", "garlic", "red pepper"
]

fruits = [
    "apple", "banana", "orange", "strawberry", "grape",
    "pineapple", "mango", "pear", "watermelon", "blueberry",
    "kiwi", "peach", "plum", "cherry", "papaya", "lemon",
    "apricot", "nectarine", "raspberry", "blackberry", "melon",
    "fig", "dragon fruit", "lychee", "pomegranate", "coconut",
    "tangerine", "guava", "clementine", "passion fruit", "jackfruit",
    "persimmon", "mulberry", "soursop", "date", "starfruit",
    "acai berry", "carambola", "pomelo", "blood orange", "goji berry",
    "cherimoya", "rhubarb", "quince", "jabuticaba", "longan",
    "medlar", "loquat", "salak", "tamarind", "avocado",
    "lime", "lemon"
]

meats_fish = [
    "chicken breast", "chicken thigh", "chicken drumstick", "chicken wing",
    "beef steak", "ground beef", "beef rib", "beef shoulder", "beef brisket",
    "pork chop", "pork tenderloin", "bacon", "pork loin", "pork belly",
    "lamb chop", "lamb leg", "ground lamb", "lamb shank",
    "turkey breast", "turkey leg", "pork sausage", "chicken sausage",
    "beef sausage", "duck", "venison", "goat", "rabbit", "beef mince",
    "lamb shoulder", "pork fillet", "beef rump", "pork neck", "lamb rack",
    "boneless skinless chicken thigh", "pork rib", "beef mince", "pancetta",
    "beef", "chicken", "pork", "lamb",
    "salmon", "tuna", "cod", "trout", "halibut", "sardines", "mackerel",
    "tilapia", "bass", "herring", "pollock", "flounder", "snapper", "sole",
    "catfish", "mahi mahi", "anchovies", "rainbow trout", "yellowtail", "swordfish",
    "sea bass", "carp", "grouper", "perch", "red snapper", "wahoo", "kingfish",
    "whitefish", "bluefish", "fish fillet", "fish steak", "fish head"
]

spices = [
    "cumin", "coriander", "paprika", "turmeric", "ginger",
    "garlic powder", "onion powder", "chili powder", "cayenne pepper",
    "cinnamon", "clove", "nutmeg", "cardamom", "black pepper",
    "mustard seed", "fennel seed", "caraway seed", "fenugreek",
    "saffron", "bay leaf", "thyme", "rosemary", "oregano", "basil",
    "parsley", "tarragon", "marjoram", "sage", "allspice",
    "star anise", "sumac", "za'atar", "smoked paprika",
    "curry powder", "garam masala", "chinese five-spice", "ras el hanout",
    "harissa", "taco seasoning", "dried mint", "dried chili flake", "mace",
    "lemon zest", "lime zest", "annatto", "chili flake", "kala jeera",
    "turmeric root", "paprika", "szechuan peppercorn", "bay leaf",
    "smoked paprika", "oregano", "black pepper", "red pepper", "cilantro",
    "lemongrass", "white pepper"
]

pantry_liquids = [
    # sauces & condiments
    "soy sauce", "tomato sauce", "bbq sauce", "hot sauce", "ketchup",
    "worcestershire sauce", "fish sauce", "oyster sauce", "mayonnaise",
    "mustard", "pesto", "passata", "tomato paste", "tomato puree",
    # oils & vinegars
    "cooking oil", "olive oil", "extra virgin olive oil", "vegetable oil",
    "sunflower oil", "avocado oil", "neutral oil", "sesame oil", "rapeseed oil",
    "vinegar", "apple cider vinegar", "rice vinegar", "red wine vinegar",
    # sweet & spreads
    "honey", "maple syrup", "golden syrup", "molasses", "vanilla extract",
    "jam", "peanut butter", "marmite",
    # cooking liquids
    "coconut milk", "stock", "broth", "chicken stock", "beef stock",
    "vegetable stock", "dashi", "sake", "mirin", "rice wine", "wine", "cognac",
    # drinks
    "water", "juice", "soft drink", "energy drink", "squash", "sparkling water",
    "canned drink", "coconut water", "smoothie"
]

pantry_dry = [
    # grains, flour & baking
    "rice", "pasta", "noodle", "flour", "all-purpose flour", "bread",
    "breadcrumb", "bread crumb", "cereal", "oat", "sugar", "salt",
    "baking powder", "baking soda", "bicarbonate of soda", "yeast", "cocoa powder",
    # tins & pulses
    "lentil", "bean", "chickpea", "pulse", "canned tomato", "chopped tomato",
    "canned bean", "canned vegetable", "canned fruit", "tinned fish", "tuna",
    # cubes, roux & seasonings
    "stock cube", "stock pot", "curry roux", "togarashi",
    # snacks & hot drinks
    "biscuit", "cracker", "chip", "crisp", "chocolate", "sweet", "nut",
    "granola bar", "popcorn", "fruit snack", "coffee", "tea", "hot chocolate",
    "pickle"
]

fridge_freezer = [
    "milk", "butter", "cheese", "yogurt", "egg", "cream",
    "cottage cheese", "sour cream", "clotted cream", "cheese spread",
    "almond milk", "oat milk", "parmesan", "cheddar",
    "mozzarella", "feta", "ricotta", "greek yogurt", "unsalted butter", "salted butter",
    "frozen vegetable", "frozen fruit", "frozen chip", "frozen pizza",
    "frozen ready meal", "frozen fish", "frozen chicken nugget", "ice cream",
    "frozen dessert", "frozen bread", "ice lolly",
    "mascarpone", "greek yogurt", "gouda", "brie", "camembert", "blue cheese",
    "stilton", "manchego", "gruyère", "emmental", "chevre", "ricotta salata",
    "pecorino", "burrata", "colby", "munster", "havarti", "swiss cheese",
    "cheddar", "mild cheddar", "mature cheddar", "asiago", "fontina",
    "jarlsberg", "quark", "cottage cheese"
]