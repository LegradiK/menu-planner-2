"""Save recipes to a day and look back at past days on a calendar."""
import calendar
import json
import os
from datetime import date, timedelta

from flask import (Blueprint, abort, current_app, flash, redirect, render_template,
                   request, session, url_for)
from flask_login import current_user, login_required

from models import ConfirmedWeek, WeekRecipe, db

history_bp = Blueprint("history", __name__)


RECIPE_FILES = ("main_recipes.json", "dessert_recipes.json", "bread_recipes.json")


def recipes_by_name() -> dict:
    """All recipes from the JSON files, looked up by lower-case name."""
    lookup = {}
    for filename in RECIPE_FILES:
        path = os.path.join(current_app.root_path, "recipes", filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as file:
                for recipe in json.load(file)["recipes"]:
                    lookup[recipe["name"].lower()] = recipe
    return lookup


@history_bp.route("/plan/confirm", methods=["POST"])
@login_required
def confirm_week():
    """Save the recipes currently in My week to the chosen day."""
    plan = session.get("plan", [])
    if not plan:
        flash("Pick some recipes first.", "warning")
        return redirect(url_for("my_week"))

    try:
        day = date.fromisoformat(request.form["day"])
    except (KeyError, ValueError):
        flash("Please choose a date.", "warning")
        return redirect(url_for("my_week"))

    week = ConfirmedWeek.query.filter_by(user_id=current_user.id, day=day).first()
    if week is None:
        week = ConfirmedWeek(user_id=current_user.id, day=day)
        db.session.add(week)
    week.recipes.clear()  # saving again replaces that day's recipes

    lookup = recipes_by_name()
    for position, name in enumerate(plan):
        recipe = lookup.get(name.lower(), {})
        week.recipes.append(WeekRecipe(
            position=position,
            name=recipe.get("name", name),
            cuisine=recipe.get("cuisine", ""),
            link=recipe.get("link", ""),
        ))
    db.session.commit()

    flash(f"Saved {len(plan)} recipes for {day:%a %d %B}.", "success")
    return redirect(url_for("history.calendar_view", year=day.year, month=day.month))


@history_bp.route("/calendar")
@login_required
def calendar_view():
    """Month view: every day of the month, with the recipes saved for it."""
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)
    if not 1 <= month <= 12 or not 2000 <= year <= 2100:
        abort(404)

    weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)
    saved = {
        entry.day: entry for entry in ConfirmedWeek.query.filter(
            ConfirmedWeek.user_id == current_user.id,
            ConfirmedWeek.day.between(weeks[0][0], weeks[-1][-1]),
        )
    }

    first_of_month = date(year, month, 1)
    prev_month = first_of_month - timedelta(days=1)
    next_month = first_of_month + timedelta(days=32)

    return render_template(
        "calendar.html",
        weeks=weeks,
        saved=saved,
        month_start=first_of_month,
        today=today,
        prev_month=prev_month,
        next_month=next_month,
        recent=current_user.weeks[:8],
    )


def own_week_or_404(week_id: int) -> ConfirmedWeek:
    """Fetch a saved day, but only if it belongs to the logged-in user."""
    week = db.session.get(ConfirmedWeek, week_id)
    if week is None or week.user_id != current_user.id:
        abort(404)
    return week


@history_bp.route("/calendar/<int:week_id>/reuse", methods=["POST"])
@login_required
def reuse_week(week_id):
    """Copy a saved day's recipes back into My week."""
    week = own_week_or_404(week_id)
    lookup = recipes_by_name()
    plan = [r.name for r in week.recipes if r.name.lower() in lookup]
    missing = len(week.recipes) - len(plan)

    session["plan"] = plan
    session.pop("shopping_removed", None)
    session.pop("shopping_extra", None)

    message = f"Loaded {week.day:%a %d %B} into My week."
    if missing:
        message += f" {missing} recipe(s) no longer exist and were skipped."
    flash(message, "success")
    return redirect(url_for("my_week"))


@history_bp.route("/calendar/<int:week_id>/delete", methods=["POST"])
@login_required
def delete_week(week_id):
    """Remove a saved day from the calendar."""
    week = own_week_or_404(week_id)
    day = week.day
    db.session.delete(week)
    db.session.commit()
    flash(f"Removed {day:%a %d %B}.", "info")
    return redirect(url_for("history.calendar_view", year=day.year, month=day.month))


@history_bp.app_context_processor
def inject_today():
    """Lets my_week.html default the date picker to today."""
    return {"today": date.today()}