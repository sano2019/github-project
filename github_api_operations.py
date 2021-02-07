import requests
import os
from collections import Counter

TOKEN = os.getenv('GITHUB_TOKEN')
HEADERS = {
    "Authorization": f"token {TOKEN}",
    "accept": "application/vnd.github.v3+json",
}

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
    response = requests.get(repository_endpoint, params=params, headers=HEADERS)
    repositories = response.json()
    return repositories


"""
A function to retrieve all users
"""


def fetch_users(username):
    users_endpoint = "https://api.github.com/search/users"
    params = {
        "q": username
    }
    response = requests.get(users_endpoint, params=params, headers=HEADERS)
    users = response.json()['items']
    if users:
        return users


"""
A function to retrieve a single user
"""


def fetch_user(username):
    user_endpoint = "https://api.github.com/users"
    response = requests.get(f"{user_endpoint}/{username}", headers=HEADERS)
    user = response.json()
    return user


"""
A function to check the languages used within the repository
"""


def fetch_repo_languages(owner, repo):
    repo_language_endpoint = "http://api.github.com/repos"
    response = requests.get(f"{repo_language_endpoint}/{owner}/{repo}/languages", headers=HEADERS)
    repo_languages = response.json()
    return repo_languages


"""
A function to count languages in repositories.
"""


def fetch_user_languages(username, repositories):
    languages = {}
    for repo in repositories:
        repo_language = fetch_repo_languages(username['login'], repo['name'])
        if len(languages) == 0:
            languages = Counter(repo_language)
        else:
            languages += Counter(repo_language)
    return languages
