"""Sign up, log in and log out."""
from urllib.parse import urlsplit

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import BooleanField, EmailField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError

from models import User, db

auth_bp = Blueprint("auth", __name__)


class RegisterForm(FlaskForm):
    """New account."""

    name = StringField("Your name", validators=[DataRequired(), Length(max=80)])
    email = EmailField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField(
        "Repeat password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create account")

    def validate_email(self, field):
        """Stop two accounts using the same email."""
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError("An account with this email already exists.")


class LoginForm(FlaskForm):
    """Log in with email and password."""

    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")


def safe_next_url(default: str) -> str:
    """Only follow ?next= if it points back to this site."""
    target = request.args.get("next", "")
    if target and not urlsplit(target).netloc and target.startswith("/"):
        return target
    return default


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Create an account and log straight in."""
    if current_user.is_authenticated:
        return redirect(url_for("history.calendar_view"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(name=form.name.data.strip(), email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash(f"Welcome, {user.name}! Your account is ready.", "success")
        return redirect(safe_next_url(url_for("my_week")))
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log in with email and password."""
    if current_user.is_authenticated:
        return redirect(url_for("history.calendar_view"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.name}.", "success")
            return redirect(safe_next_url(url_for("history.calendar_view")))
        flash("Email or password is incorrect.", "error")
    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Log out and go back to the home page."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))
