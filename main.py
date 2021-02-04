import requests
import os
import datetime
import matplotlib.pyplot as plt
from collections import Counter
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#
# login_manager = LoginManager()
# login_manager.init_app(app)
# db = SQLAlchemy(app)
#
# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))
Bootstrap(app)
TOKEN = os.getenv('GITHUB_TOKEN')


class SearchUserForm(FlaskForm):
    username = StringField(validators=[DataRequired()], render_kw={"placeholder": "Github Username"})
    submit = SubmitField("Search")


@app.route("/")
def home():
    return render_template("index.html")


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
    return render_template("search.html", form=form)


@app.route("/details/<username>")
def details(username):
    user_endpoint = "https://api.github.com/users"
    headers = {
        "Authorization": f"token {TOKEN}",
        "accept": "application/vnd.github.v3+json",
    }
    response = requests.get(f"{user_endpoint}/{username}", headers=headers)
    user = response.json()
    repositories = fetch_repositories(username)
    languages = {}
    # for repo in repositories[:5]:
    #     repo_language = check_repo_languages(username, repo['name'])
    #     if len(languages) == 0:
    #         languages = Counter(repo_language)
    #     else:
    #         languages += Counter(repo_language)
    #chart = create_chart(languages)
    print(user)
    return render_template('details.html', user=user, repos=repositories) #, languages=languages


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


def check_repo_languages(owner, repo):
    repo_language_endpoint = "http://api.github.com/repos"
    headers = {
        "Authorization": f"token {TOKEN}",
        "accept": "application/vnd.github.v3+json",
    }
    response = requests.get(f"{repo_language_endpoint}/{owner}/{repo}/languages", headers=headers)
    languages = response.json()
    return languages


def create_chart(languages):
    labels = []
    sizes = []

    for x, y in languages.items():
        labels.append(x)
        sizes.append(int(y))
    plt.pie(sizes, labels=labels)
    plt.axis('equal')
    return plt.show()


if __name__ == "__main__":
    app.run(debug=True)