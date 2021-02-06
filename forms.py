from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class UpdateSavedUser(FlaskForm):
    name = StringField()
    twitter_username = StringField()
    location = StringField()
    email = StringField()
    company = StringField()
    submit = SubmitField("Update")

class SearchUserForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={"placeholder": "Github Username"})
    submit = SubmitField("Search")


class RegisterUserForm(FlaskForm):
    email = StringField(validators=[DataRequired(),
                                    Email()])
    password = PasswordField(validators=[DataRequired(),
                                         Length(min=6, message="Password must be at least 6 characters"),
                                         EqualTo('confirm_password', message="Passwords must match")])
    confirm_password = PasswordField()
    submit = SubmitField("Register")


class LoginUserForm(FlaskForm):
    email = StringField(validators=[DataRequired(),
                                    Email()])
    password = PasswordField()
    submit = SubmitField("Log In")