from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Regexp, Length, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
    remember_me = BooleanField("Remember Me")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=4, max=25)]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            # source: https://stackoverflow.com/a/21456918
            # Min 8 characters, at least 1 letter, 1 number and 1 special character
            # lookahead for at least 1 of each A-Za-z, number and @$!%#?&
            # the rest can be anything letters, numbers, unicode, whitespace etc.
            Regexp(
                r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&]).{8,}$",
                message=(
                    "The password must be a minimum eight characters, "
                    "have at least one letter, one number and one "
                    'special character from "@$!%#?&"'
                ),
            ),
            EqualTo("confirm_password", message="Passwords must match"),
        ],
    )
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class FeedbackForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    contents = TextAreaField("Contents")
    submit = SubmitField("Send")
