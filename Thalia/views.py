from urllib.parse import urljoin

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse

from .extensions import db
from .forms import FeedbackForm, LoginForm, RegistrationForm
from .models.portfolio import Portfolio
from .models.user import User

server_bp = Blueprint("main", __name__)


@server_bp.route("/", methods=["GET", "POST"])
def index():
    form = RegistrationForm()
    if form.validate_on_submit():
        if existing_username(form.username.data):
            error = "already registered"
            return render_template(
                "index.html", form=form, error=error, scroll="login_failed"
            )
        else:
            save_user(form.username.data, form.password.data)
            return redirect(url_for("main.login"))

    if form.is_submitted():
        return render_template("index.html", form=form, scroll="login_failed")

    return render_template("index.html", title="Home Page", form=form)


@server_bp.route("/about/")
def about():
    return render_template("about.html", title="About Page")


@server_bp.route("/us/")
def us():
    return render_template("us.html", title="About Us")


@server_bp.route("/contact/", methods=["GET", "POST"])
def contact():
    form = FeedbackForm()
    if form.validate_on_submit():
        # dump to feedback.csv
        with open("feedback.csv", "a") as file:
            file.write(
                "{},{},{}\n".format(
                    form.email.data, form.title.data, form.contents.data
                )
            )
    return render_template("contact.html", title="Contact Us", form=form)


@server_bp.route("/share/", methods=["POST"])
@login_required
def share_portfolio():
    portfolio_id = request.get_json().get("portfolio_id")
    portfolio = Portfolio.query.get(portfolio_id)
    if portfolio.owner != current_user.id:
        pass  # add redirect to 404
        return "404"
    else:
        uuid = portfolio.share()
        return uuid


@server_bp.route("/gallery/", methods=["GET"])
@login_required
def gallery():
    """
    We extract relevant values from the portfolio record into a separate array
    as we can not overwrite the strategy attribute of a Portfolio
    record with a strategy object, since it is not JSON serializable.
    An unelegant workaround, but it works.

    Also has post method for handling deletion and sharing
    """
    portfolios = []
    for p in Portfolio.query.filter_by(owner=current_user.id):
        portfolio = {"id": p.id, "name": p.name, "strat": p.get_strategy()}
        if p.uuid:
            portfolio["link"] = urljoin(
                request.host_url, url_for("/dashboard/") + p.uuid
            )
        else:
            portfolio["link"] = None
        portfolios.append(portfolio)

    return render_template("gallery.html", title="My Portfolios", portfolios=portfolios)


@server_bp.route("/login/", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        error = validate_credentials(user, form.password.data)
        if error:
            return render_template("login.html", form=form, error=error)

        login_user(user, remember=form.remember_me.data)
        next_page = find_next(backup="main.index")
        return redirect(next_page)

    return render_template("login.html", title="Sign In", form=form)


def find_next(backup):
    """
    find and validate the next argument when flask-login redirects
    from a protected page. Usually redirects back to the unathorized page.
    Use backup if next doesn't exist or fails to validate.

    e.g. try to access dashboard -> redirect to login -> redirected back to dashboard

    current validation only makes sure that next page is a relative path
    and doesn't have it's own netloc (netloc = www.example.com)
    """
    next_page = request.args.get("next")
    if not next_page or not url_parse(next_page).netloc != "":
        next_page = url_for(backup)
    return next_page


def validate_credentials(user, password):
    error = None
    if user is None:
        error = "Username not recognised"
    elif not user.check_password(password):
        error = "Incorrect password"
    return error


@server_bp.route("/logout/")
@login_required
def logout():
    logout_user()

    return redirect(url_for("main.index"))


@server_bp.route("/register/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        if existing_username(form.username.data):
            error = "already registered"
            return render_template("register.html", form=form, error=error)
        else:
            save_user(form.username.data, form.password.data)
            return redirect(url_for("main.login"))

    return render_template("register.html", title="Register", form=form)


def save_user(username, password):
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


def existing_username(username):
    return bool(User.query.filter_by(username=username).first())
