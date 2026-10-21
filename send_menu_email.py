"""send_menu_email.py

Builds a random weekly menu and its shopping list, then emails both.
Run by the GitHub Actions workflow in .github/workflows/weekly-menu.yml.

Settings come from environment variables (GitHub secrets in the workflow):
    EMAIL_ADDRESS       Gmail address the email is sent from
    EMAIL_APP_PASSWORD  Gmail app password (not your normal password)
    EMAIL_TO            where to send it (comma-separated for several people);
                        defaults to EMAIL_ADDRESS
    SITE_URL            address of the deployed Menu Planner website (optional)

Preview without sending:
    python send_menu_email.py --dry-run
This writes menu_email_preview.html, which you can open in a browser.
"""
import argparse
import os
import smtplib
import sys
from datetime import date
from email.message import EmailMessage
from html import escape

from build_menu import build_main_menu, bread_suggestion
from shopping_list import collect_ingredients, update_shopping_list, categorize_ingredients

# Same colours as the website
GREEN = "#3f7d58"
GREEN_LIGHT = "#e6f1ea"
ORANGE = "#d9693a"
TEXT = "#2d2a26"
MUTED = "#6b665e"
BORDER = "#e4e7e3"


def make_shopping_list(menu):
    """Same steps as the website's /shopping_list route."""
    ingredients = collect_ingredients(menu)
    ingredient_list = update_shopping_list(ingredients)
    return categorize_ingredients(ingredient_list)


def item_text(item):
    """Format one shopping-list item or recipe ingredient as plain text."""
    if isinstance(item, str):
        return item
    parts = [str(item.get(key) or "").strip() for key in ("quantity", "measurement", "name")]
    return " ".join(part for part in parts if part)


def recipe_label(recipe):
    """Cuisine if the recipe has one, otherwise its genre."""
    return recipe.get("cuisine") or recipe.get("genre") or ""


def build_text(menu, bread, shopping, site_url):
    """Plain-text version, shown by email apps that don't display HTML."""
    lines = ["This week's menu", ""]
    for recipe in menu:
        label = recipe_label(recipe)
        lines.append(f"- {recipe['name']}" + (f" ({label})" if label else ""))
    if bread:
        lines.append(f"- Bread: {bread['name']}")

    lines += ["", "Shopping list"]
    for category, items in shopping.items():
        if not items:
            continue
        lines += ["", category]
        lines += [f"  [ ] {item_text(item)}" for item in items]

    if site_url:
        lines += ["", f"Not keen on this week's meals? Make a new menu: {site_url}"]
    return "\n".join(lines)


def build_html(menu, bread, shopping, site_url):
    """HTML version. Styles are inline because most email apps strip <style> blocks."""
    recipes = list(menu) + ([bread] if bread else [])

    recipe_rows = ""
    for recipe in recipes:
        name = escape(recipe["name"])
        link = recipe.get("link")
        if link:
            name = (f'<a href="{escape(link)}" '
                    f'style="color:{GREEN};text-decoration:none;">{name}</a>')
        label = escape("Bread" if recipe is bread else recipe_label(recipe))
        recipe_rows += f"""
        <tr>
          <td style="padding:12px 16px;border-top:1px solid {BORDER};font-weight:600;">{name}</td>
          <td style="padding:12px 16px;border-top:1px solid {BORDER};text-align:right;">
            <span style="background:{GREEN_LIGHT};color:{GREEN};font-size:12px;
                         padding:2px 10px;border-radius:999px;">{label}</span>
          </td>
        </tr>"""

    shopping_html = ""
    for category, items in shopping.items():
        if not items:
            continue
        rows = "".join(
            f'<li style="padding:4px 0;">&#9744;&nbsp; {escape(item_text(item))}</li>'
            for item in items
        )
        shopping_html += f"""
        <h3 style="color:{ORANGE};font-size:15px;margin:18px 0 6px;">{escape(category)}</h3>
        <ul style="list-style:none;margin:0;padding:0;">{rows}</ul>"""

    button = ""
    if site_url:
        button = f"""
        <p style="margin:28px 0 8px;color:{MUTED};">Not keen on this week's meals?</p>
        <a href="{escape(site_url)}" style="display:inline-block;background:{GREEN};color:#ffffff;
           padding:10px 22px;border-radius:999px;text-decoration:none;font-weight:600;">
          Make a new menu</a>"""

    return f"""<!DOCTYPE html>
<html>
<body style="margin:0;background:#f7f8f6;font-family:Arial,Helvetica,sans-serif;color:{TEXT};">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <h1 style="color:{GREEN};font-size:24px;margin:0 0 4px;">Menu Planner</h1>
    <p style="color:{MUTED};margin:0 0 20px;">Your menu for the week of {date.today():%d %B %Y}</p>

    <div style="background:#ffffff;border:1px solid {BORDER};border-radius:12px;overflow:hidden;">
      <h2 style="font-size:18px;margin:0;padding:16px;">This week's meals</h2>
      <table style="width:100%;border-collapse:collapse;">{recipe_rows}
      </table>
    </div>

    <div style="background:#ffffff;border:1px solid {BORDER};border-radius:12px;
                padding:16px;margin-top:16px;">
      <h2 style="font-size:18px;margin:0;">Shopping list</h2>{shopping_html}
    </div>

    <div style="text-align:center;">{button}</div>
  </div>
</body>
</html>"""


def send_email(subject, text, html):
    """Send the email through Gmail's SMTP server."""
    sender = os.environ["EMAIL_ADDRESS"]
    password = os.environ["EMAIL_APP_PASSWORD"]
    recipients = [a.strip() for a in os.getenv("EMAIL_TO", sender).split(",") if a.strip()]

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message.set_content(text)
    message.add_alternative(html, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.send_message(message)


def main():
    """Build the menu and shopping list, then send or preview the email."""
    parser = argparse.ArgumentParser(description="Email a random weekly menu and shopping list.")
    parser.add_argument("--dry-run", action="store_true",
                        help="write menu_email_preview.html instead of sending")
    args = parser.parse_args()

    site_url = os.getenv("SITE_URL", "").strip()
    if site_url:
        site_url = site_url.rstrip("/") + "/recipes"

    menu = build_main_menu()
    bread = bread_suggestion()
    shopping = make_shopping_list(menu)

    subject = f"Your weekly menu ({date.today():%d %b})"
    text = build_text(menu, bread, shopping, site_url)
    html = build_html(menu, bread, shopping, site_url)

    if args.dry_run:
        with open("menu_email_preview.html", "w", encoding="utf-8") as file:
            file.write(html)
        print(text)
        print("\nPreview written to menu_email_preview.html")
        return

    missing = [name for name in ("EMAIL_ADDRESS", "EMAIL_APP_PASSWORD") if not os.getenv(name)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}")

    send_email(subject, text, html)
    print(f"Sent: {subject}")


if __name__ == "__main__":
    main()

