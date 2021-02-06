import requests
import os
import datetime
from collections import Counter
from flask import Flask, render_template, request, url_for, redirect, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

TOKEN = os.getenv('GITHUB_TOKEN')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

login_manager = LoginManager()
login_manager.init_app(app)
db = SQLAlchemy(app)
Bootstrap(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


# User class for registered users
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))


# Class for saved github profiles
class SavedProfiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String)
    html_url = db.Column(db.String, unique=True)
    avatar_url = db.Column(db.String)
    name = db.Column(db.String)
    hireable = db.Column(db.Boolean)
    twitter_username = db.Column(db.String)
    location = db.Column(db.String)
    email = db.Column(db.String)
    company = db.Column(db.String)

#db.create_all()


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


@app.route("/")
def home():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterUserForm()
    if form.validate_on_submit():
        new_user = User(
            email=request.form['email'],
            password=generate_password_hash(request.form['password'], method='pbkdf2:sha256', salt_length=8),
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html', form=form, logged_in=current_user.is_authenticated)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginUserForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Password incorrect, please try again.")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('search'))
    return render_template('login.html', form=form, logged_in=current_user.is_authenticated)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/search", methods=["GET", "POST"])
def search():
    form = SearchUserForm()
    if request.method == "POST":
        users_endpoint = "https://api.github.com/search/users"
        username = request.form.get('username')
        headers = {
            "Authorization": f"token {TOKEN}",
            "accept": "application/vnd.github.v3+json",
        }
        params = {
            "q": username
        }
        response = requests.get(users_endpoint, params=params, headers=headers)
        data = response.json()
        users = data['items']
        return render_template("search.html", users=users, form=form)
    return render_template("search.html", form=form, logged_in=current_user.is_authenticated)


@app.route("/details/<username>")
def details(username):
    user = fetch_user(username)
    repositories = fetch_repositories(username)
    languages = {}
    for repo in repositories[:5]:
        repo_language = check_repo_languages(username, repo['name'])
        if len(languages) == 0:
            languages = Counter(repo_language)
        else:
            languages += Counter(repo_language)
    #chart = create_chart(languages)
    total_language = sum(languages.values())
    return render_template('details.html', user=user, repos=repositories, languages=languages,
                           total=total_language, logged_in=current_user.is_authenticated)


@app.route("/saved_users", methods=["GET", "POST"])
@login_required
def saved_users():
    users = SavedProfiles.query.all()
    return render_template('saved_users.html', logged_in=current_user.is_authenticated, users=users)



@app.route("/save_user/<username>", methods=["GET"])
def save_user(username):
    user = fetch_user(username)
    new_user = SavedProfiles(
        login=user['login'],
        html_url=user['html_url'],
        avatar_url=user['avatar_url'],
        name=user['name'],
        hireable=user['hireable'],
        twitter_username=user['twitter_username'],
        location=user['location'],
        email=user['email'],
        company=user['company'],
    )
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('saved_users'))


@app.route("/update_saved_user/<user_id>", methods=["GET", "POST"])
@login_required
def update_saved_user(user_id):
    user = SavedProfiles.query.get(user_id)
    form = UpdateSavedUser(
        name=user.name,
        twitter_username=user.twitter_username,
        location=user.location,
        email=user.email,
        company=user.company,
    )
    if form.validate_on_submit():
        user.name = form.name.data
        user.twitter_username = form.twitter_username.data
        user.location = form.location.data
        user.email = form.email.data
        user.company = form.company.data
        db.session.commit()
        return redirect(url_for('saved_users'))
    return render_template('update_saved_user.html', form=form)


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    user = SavedProfiles.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('saved_users'))



"""
A function that will keep the current year in the footer up to date
"""
@app.context_processor
def current_year():
    now = datetime.datetime.now()
    return {'year': now.year}


"""
A function to retrieve the user's repositories
"""
def fetch_repositories(username):
    repository_endpoint = f"https://api.github.com/users/{username}/repos"
    params = {
        "username": username,
        "type": "owner",
        "sort": "updated",
        "per_page": "5",
    }
    headers = {
        "Authorization": f"token {TOKEN}",
        "accept": "application/vnd.github.v3+json",
    }
    response = requests.get(repository_endpoint, params=params, headers=headers)
    repositories = response.json()
    return repositories

def fetch_user(username):
    user_endpoint = "https://api.github.com/users"
    headers = {
        "Authorization": f"token {TOKEN}",
        "accept": "application/vnd.github.v3+json",
    }
    response = requests.get(f"{user_endpoint}/{username}", headers=headers)
    user = response.json()
    return user

def check_repo_languages(owner, repo):
    repo_language_endpoint = "http://api.github.com/repos"
    headers = {
        "Authorization": f"token {TOKEN}",
        "accept": "application/vnd.github.v3+json",
    }
    response = requests.get(f"{repo_language_endpoint}/{owner}/{repo}/languages", headers=headers)
    languages = response.json()
    return languages


if __name__ == "__main__":
    app.run(debug=True)