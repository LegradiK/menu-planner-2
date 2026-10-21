"""Database models: users and the weeks they have confirmed."""
# pylint: disable=too-few-public-methods
from datetime import date, datetime, timedelta, timezone

from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please log in to see your calendar."
login_manager.login_message_category = "info"


def utc_now():
    """Current time in UTC (timezone-aware)."""
    return datetime.now(timezone.utc)


def monday_of(day: date) -> date:
    """Return the Monday of the week that `day` falls in."""
    return day - timedelta(days=day.weekday())


class User(UserMixin, db.Model):
    """Someone who can log in and save weeks."""

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now)

    weeks = db.relationship(
        "ConfirmedWeek", back_populates="user",
        cascade="all, delete-orphan", order_by="ConfirmedWeek.week_start.desc()",
    )

    def set_password(self, password: str) -> None:
        """Store a hash of the password, never the password itself."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """True if the password matches the stored hash."""
        return check_password_hash(self.password_hash, password)


class ConfirmedWeek(db.Model):
    """One week (Monday to Sunday) that a user has confirmed."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    week_start = db.Column(db.Date, nullable=False)  # always a Monday
    confirmed_at = db.Column(db.DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    user = db.relationship("User", back_populates="weeks")
    recipes = db.relationship(
        "WeekRecipe", back_populates="week",
        cascade="all, delete-orphan", order_by="WeekRecipe.position",
    )

    __table_args__ = (db.UniqueConstraint("user_id", "week_start", name="one_entry_per_week"),)

    @property
    def week_end(self) -> date:
        """The Sunday that ends this week."""
        return self.week_start + timedelta(days=6)


class WeekRecipe(db.Model):
    """A recipe saved in a confirmed week.

    The name, cuisine and link are copied in, so the calendar still shows the
    recipe even if it is later renamed or deleted from the JSON files.
    """

    id = db.Column(db.Integer, primary_key=True)
    week_id = db.Column(db.Integer, db.ForeignKey("confirmed_week.id"), nullable=False)
    position = db.Column(db.Integer, default=0)
    name = db.Column(db.String(200), nullable=False)
    cuisine = db.Column(db.String(80), default="")
    link = db.Column(db.String(500), default="")

    week = db.relationship("ConfirmedWeek", back_populates="recipes")


@login_manager.user_loader
def load_user(user_id: str):
    """Tell Flask-Login how to find a user from the id in the session."""
    return db.session.get(User, int(user_id))
