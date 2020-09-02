from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Email, Length, Optional

class RegisterForm(FlaskForm):
    """Form for registering a user"""

    username = StringField("Username", validators = [InputRequired()])
    password = PasswordField("Password", validators = [InputRequired()])
    email = StringField("Email", validators = [InputRequired(), Length(0,30)])
    first_name = StringField("First Name", validators = [InputRequired(), Length(0,30)])
    last_name = StringField("Last Name", validators = [InputRequired(), Length(0,30)])


class LoginForm(FlaskForm):
    """Form for logging-in a user"""
    username = StringField("Username", validators = [InputRequired()])
    password = PasswordField("Password", validators = [InputRequired()])

class FeedbackForm(FlaskForm):
    """Form for providing feedback"""
    title = StringField("Title",validators = [InputRequired(),Length(0,100)])
    content = StringField("Feedback",validators = [InputRequired()])
