# Menu Planner

A Flask web app and JSON API that plans your meals, builds your shopping list and keeps a calendar of what you cooked.

**Live site:** [Menu Planner](https://kahopythonbookshelf.pythonanywhere.com/)

---

## Try it out

You can explore the live site with the test account:


| Field    | Value               |
| ---------- | --------------------- |
| Email    | `test@example.com`  |
| Password | `test-password-123` |

> The test account is shared, so please don't store anything personal in it.
> You can also create your own account from the **Register** page.

---

## Features

### Browse recipes

- **All recipes**: every recipe, grouped by category (**Main dishes**, **Desserts**, **Bread**) and then by cuisine (Italian, Japanese, ...), sorted A–Z.
- Each recipe opens to show its ingredients, step-by-step instructions, its weight (how many meals it makes) and a link to the full original recipe if available.
- **Search**: find a recipe by name, across all categories or within one.
- **Get inspired**: a curated list of recipe websites, grouped by category.

### Get menu ideas

- **Get ideas** builds a random menu: main dishes adding up to 5 meals, one dessert and a bread suggestion.
- The same menu stays on screen until you press **Shuffle**, so refreshing the page doesn't lose it.
- Turn the suggested menu straight into a shopping list.

### Plan your week

- Add any recipe to **My week** with **+ My week**, or remove it again with one click.
- The navigation shows how many recipes are in your week.
- Clear the whole week to start again.

### Shopping list

- Builds a shopping list from all the recipes in My week.
- Matching ingredients are combined (same name and unit), and descriptive words like *finely chopped*, *fresh* or *to taste* are stripped out.
- Items are sorted into supermarket sections: Vegetables, Fruits, Meats & Fish, Spices, Pantry Goods (Dry), Pantry Goods (Liquid), Fridge & Freezer, and Uncategorized.
- **Edit the list**: add your own extra items, remove things you already have, or reset back to the original list.

### Calendar (log in required)

- **Save your week to a date**: pick a day and save the recipes in My week to it. Saving again to the same day replaces that day's recipes.
- **Month calendar**: see every day of the month with the recipes saved for it, and move between months. The current week opens automatically.
- **Cook it again**: copy a previous day's recipes back into My week. Handy when a menu was everyone's favourite. Any recipes that have since been deleted are skipped, and you'll be told how many.
- **Remove** a saved day from the calendar.
- **Recently saved**: quick links to your 8 most recently saved days.
- Saved recipes keep their name, cuisine and link, so the calendar still shows them even if the recipe is later renamed or deleted.

### Accounts

- Register with your name, email and password (minimum 8 characters), and log in with an optional **Keep me logged in**.
- Passwords are stored as hashes, never in plain text.
- Every user only sees their own calendar.

### Manage recipes

- **Add a recipe** with a form: category, name, cuisine, weight, link, ingredients (quantity, measurement, name) and instructions (one step per line).
- **Delete a recipe**: search for it first, then confirm before it's removed.

### Weekly email

- A GitHub Actions workflow emails a random weekly menu and shopping list every Friday at 10am, with a link back to the site to regenerate the menu.

---

## How it works

### Recipe weight

Each recipe has a `weight`, which is the number of meals it provides.
For example, a recipe with a `weight` of `2` covers two meals.
When building a random menu, main dishes are picked until their weights add up to at least 5 meals.

### Recipe data

Recipes are stored as JSON files in the `recipes/` folder, one file per category:


| File                   | Category                           |
| ------------------------ | ------------------------------------ |
| `main_recipes.json`    | Main dishes                        |
| `dessert_recipes.json` | Desserts                           |
| `bread_recipes.json`   | Bread                              |
| `inspiration.json`     | Recipe websites for *Get inspired* |

Each recipe looks like this:

```json
{
  "genre": "main",
  "name": "Chicken Katsu",
  "cuisine": "Japanese",
  "weight": 2,
  "link": "https://example.com/chicken-katsu",
  "ingredients": [
    { "quantity": "2", "measurement": "", "name": "chicken breasts" },
    { "quantity": "100", "measurement": "g", "name": "panko breadcrumbs" }
  ],
  "instructions": [
    "Coat the chicken in flour, egg and panko.",
    "Fry until golden and cooked through."
  ]
}
```

The files are read on every request, so newly added recipes show up straight away.

### User data

Accounts and saved calendar days are stored in a SQLite database (`menu_planner.db`), which is created automatically the first time the app runs.


| Table            | What it stores                                                              |
| ------------------ | ----------------------------------------------------------------------------- |
| `user`           | Name, email, password hash, date joined                                     |
| `confirmed_week` | One saved day per user (a user can only have one entry per date)            |
| `week_recipe`    | The recipes saved for that day, in order, with their name, cuisine and link |

My week, the current menu ideas and shopping-list edits are kept in the Flask session, so you can plan a week without logging in. Logging in is only needed to save to the calendar.

### Shopping list processing

1. Collect the ingredients from every recipe in the menu.
2. Clean up each ingredient name by removing stop words (`config.py` → `STOP_WORDS`).
3. Combine ingredients with the same name and unit.
4. Sort each ingredient into a section using the lists in `categories.py` (`config.py` → `CATEGORIES`). Singular and plural forms are matched, and meat stocks go into the aisle section rather than Meats & Fish.
5. Apply the user's edits: hide removed items and add extra items.

---

## Tech stack


| Area             | Tools                                                                 |
| ------------------ | ----------------------------------------------------------------------- |
| Backend          | Python, Flask (with Blueprints)                                       |
| Database         | SQLite, Flask-SQLAlchemy                                              |
| Accounts         | Flask-Login, Werkzeug password hashing                                |
| Forms & security | Flask-WTF, WTForms, CSRF protection on all forms                      |
| Config           | python-dotenv (`data.env`)                                            |
| Frontend         | Jinja templates, Bootstrap, custom CSS, vanilla JavaScript (calendar) |
| Data             | JSON recipe files                                                     |
| Automation       | GitHub Actions (weekly email)                                         |
| Hosting          | PythonAnywhere                                                        |

### Security

- CSRF protection on every form.
- Passwords hashed with Werkzeug.
- Login redirects (`?next=`) only follow links back to this site.
- Users can only view, reuse or delete their own saved days.
- Actions that change data (add, remove, save, delete, log out) use `POST`.

---

## Project structure

```
menu-planner/
├── main.py             # App setup, recipe, menu, My week and shopping list routes
├── auth.py             # Blueprint: register, log in, log out
├── history.py          # Blueprint: save to a date, calendar, reuse and delete days
├── models.py           # Database models: User, ConfirmedWeek, WeekRecipe
├── build_menu.py       # Random menu and bread suggestion
├── shopping_list.py    # Collect, combine and categorise ingredients
├── save_recipe.py      # Save a new recipe to its JSON file
├── config.py           # Ingredient categories and stop words
├── categories.py       # Ingredient lists for each supermarket section
├── recipes/            # Recipe JSON files
├── templates/          # Jinja templates (_macros.html holds the shared recipe row)
├── static/             # CSS and JavaScript
├── requirements.txt
└── data.env            # Secret key (not committed)
```

---

## Pages and routes

### Web pages


| Route                           | Method    | Description                                     | Login |
| --------------------------------- | ----------- | ------------------------------------------------- | ------- |
| `/`                             | GET       | Home page                                       |       |
| `/recipes`                      | GET       | Random menu ideas (`?shuffle=1` for a new menu) |       |
| `/all-recipes`                  | GET       | Every recipe, by category and cuisine           |       |
| `/search`                       | GET, POST | Search recipes by name                          |       |
| `/get-inspired`                 | GET       | Recipe websites by category                     |       |
| `/adding`                       | GET, POST | Add a new recipe                                |       |
| `/successful`                   | GET       | Confirmation after adding a recipe              |       |
| `/delete`                       | GET, POST | Find and delete a recipe                        |       |
| `/shopping_list`                | GET       | Shopping list for the current menu ideas        |       |
| `/my-week`                      | GET       | Recipes chosen for the week                     |       |
| `/plan/add`                     | POST      | Add a recipe to My week                         |       |
| `/plan/remove`                  | POST      | Remove a recipe from My week                    |       |
| `/plan/clear`                   | POST      | Clear My week                                   |       |
| `/my-week/shopping-list`        | GET       | Editable shopping list for My week              |       |
| `/my-week/shopping-list/add`    | POST      | Add an extra item                               |       |
| `/my-week/shopping-list/remove` | POST      | Remove an item                                  |       |
| `/my-week/shopping-list/reset`  | POST      | Undo all shopping-list edits                    |       |
| `/register`                     | GET, POST | Create an account                               |       |
| `/login`                        | GET, POST | Log in                                          |       |
| `/logout`                       | POST      | Log out                                         | ✓    |
| `/plan/confirm`                 | POST      | Save My week to a chosen date                   | ✓    |
| `/calendar`                     | GET       | Month calendar (`?year=&month=`)                | ✓    |
| `/calendar/<id>/reuse`          | POST      | Copy a saved day back into My week              | ✓    |
| `/calendar/<id>/delete`         | POST      | Remove a saved day                              | ✓    |

### JSON API


| Route     | Method | Description                                 |
| ----------- | -------- | --------------------------------------------- |
| `/sample` | GET    | Sample response to check the API is running |
| `/menu`   | GET    | A randomly built menu as JSON               |

---

## How to run locally

### 1. Clone the repository

```sh
git clone https://github.com/LegradiK/menu-planner-2.git
cd menu-planner
```

### 2. Set up a virtual environment

Create and activate a virtual environment, then install the required packages from `requirements.txt`:

```sh
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Add your secret key

Create a file called `data.env` next to `main.py`:

```
FLASK_KEY=<a long random string>
```

You can generate one with:

```sh
python -c "import secrets; print(secrets.token_hex(32))"
```

The app won't start without it.

### 4. Start the app

```sh
python main.py
```

The app runs at `http://127.0.0.1:5000`, and the SQLite database is created on the first run.

### 5. Make requests

Once the app is running, you can call the API:

```sh
curl http://127.0.0.1:5000/sample
```

Response:

```json
{
  "message": "Hello Flask API world!",
  "status": "success"
}
```

Get a random menu:

```sh
curl http://127.0.0.1:5000/menu
```

---

## Deployment

The app is deployed on [PythonAnywhere](https://www.pythonanywhere.com/) by cloning the GitHub repository and serving it as a Flask web app.
