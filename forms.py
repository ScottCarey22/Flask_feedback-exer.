from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired, Email, Length


class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])


class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email Address", validators=[InputRequired(), Email()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])


class FeedbackForm(FlaskForm):
    """Add feedback form."""

    title = StringField(
        "Title",
        validators=[InputRequired(), Length(max=100)],
    )
    content = StringField(
        "Content",
        validators=[InputRequired()],
    )


class DeleteForm(FlaskForm):
    """Delete form -- this form is intentionally blank."""
