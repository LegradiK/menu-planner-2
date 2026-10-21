"""Confirm a week's recipes and look back at past weeks on a calendar."""
import calendar
from datetime import date, timedelta

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from build_menu import load_recipes
from models import ConfirmedWeek, WeekRecipe, db, monday_of

history_bp = Blueprint("history", __name__)


def week_choices(today: date | None = None) -> list:
    """Weeks offered in the confirm form: last week, this week, next week."""
    this_monday = monday_of(today or date.today())
    labels = ["Last week", "This week", "Next week"]
    return [
        (this_monday + timedelta(weeks=offset), label)
        for offset, label in zip((-1, 0, 1), labels)
    ]


def recipes_by_name() -> dict:
    """All recipes, looked up by lower-case name."""
    return {r["name"].lower(): r for r in load_recipes("all")}


@history_bp.route("/plan/confirm", methods=["POST"])
@login_required
def confirm_week():
    """Save the recipes currently in My week to the chosen week."""
    plan = session.get("plan", [])
    if not plan:
        flash("Pick some recipes first.", "warning")
        return redirect(url_for("my_week"))

    try:
        week_start = monday_of(date.fromisoformat(request.form["week_start"]))
    except (KeyError, ValueError):
        abort(400)

    week = ConfirmedWeek.query.filter_by(
        user_id=current_user.id, week_start=week_start).first()
    if week is None:
        week = ConfirmedWeek(user_id=current_user.id, week_start=week_start)
        db.session.add(week)
    week.recipes.clear()  # confirming again replaces that week's recipes

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

    flash(f"Saved {len(plan)} recipes to the week of {week_start:%d %B}.", "success")
    return redirect(url_for("history.calendar_view",
                            year=week_start.year, month=week_start.month))


@history_bp.route("/calendar")
@login_required
def calendar_view():
    """Month view: every week of the month, with the recipes confirmed for it."""
    today = date.today()
    year = request.args.get("year", today.year, type=int)
    month = request.args.get("month", today.month, type=int)
    if not 1 <= month <= 12 or not 2000 <= year <= 2100:
        abort(404)

    weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)
    mondays = [days[0] for days in weeks]
    saved = {
        w.week_start: w for w in ConfirmedWeek.query.filter(
            ConfirmedWeek.user_id == current_user.id,
            ConfirmedWeek.week_start.in_(mondays),
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
        this_monday=monday_of(today),
        prev_month=prev_month,
        next_month=next_month,
        recent=current_user.weeks[:8],
    )


def own_week_or_404(week_id: int) -> ConfirmedWeek:
    """Fetch a confirmed week, but only if it belongs to the logged-in user."""
    week = db.session.get(ConfirmedWeek, week_id)
    if week is None or week.user_id != current_user.id:
        abort(404)
    return week


@history_bp.route("/calendar/<int:week_id>/reuse", methods=["POST"])
@login_required
def reuse_week(week_id):
    """Copy a past week's recipes back into My week."""
    week = own_week_or_404(week_id)
    lookup = recipes_by_name()
    plan = [r.name for r in week.recipes if r.name.lower() in lookup]
    missing = len(week.recipes) - len(plan)

    session["plan"] = plan
    session.pop("shopping_removed", None)
    session.pop("shopping_extra", None)

    message = f"Loaded the week of {week.week_start:%d %B} into My week."
    if missing:
        message += f" {missing} recipe(s) no longer exist and were skipped."
    flash(message, "success")
    return redirect(url_for("my_week"))


@history_bp.route("/calendar/<int:week_id>/delete", methods=["POST"])
@login_required
def delete_week(week_id):
    """Remove a confirmed week from the calendar."""
    week = own_week_or_404(week_id)
    week_start = week.week_start
    db.session.delete(week)
    db.session.commit()
    flash(f"Removed the week of {week_start:%d %B}.", "info")
    return redirect(url_for("history.calendar_view",
                            year=week_start.year, month=week_start.month))


@history_bp.app_context_processor
def inject_week_choices():
    """Lets my_week.html offer last / this / next week in the confirm form."""
    return {"week_choices": week_choices()}
