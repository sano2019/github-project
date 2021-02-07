# Github Staff Finder App

##What the app does:
This app is aimed at IT recruiters within an organization. It allows them to search for people on Github and if they are registered save them to a database for later referral. They have the option to update information that might be missing on Github.

Searching for a user retrieves their general information as well as the last 5 updated respositories the person owns. Following this the languages used in the repositories are displayed as percentages of the code in the repositories which allows the recruiter to quickly get an estimation of what languages the person uses.

## Running Locally

Make sure you have Python installed


>1. git clone https://github.com/sano2019/github-project.git # or clone your own fork
>2. cd github-project
>3. pip install -r requirements.txt
>4. generate a personal access token: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
>5. save the access token as an environment variable named GITHUB_TOKEN
>6. generate a secret key for the app: https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY
>7. save the secret key as an environment variable named SECRET_KEY
>8. python main.py


Your app should now be running on [localhost:5000](http://localhost:5000/).


---
This app was created in PyCharm