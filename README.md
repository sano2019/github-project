# Github Staff Finder App

## What the app does:
This app is aimed at IT recruiters within an organization.

The main feature is the ability to quickly retrieve the recently used programming languages from a potential candidate.

In addition, if the recruiter is registered and signed in, the application allows the recruiter to save the Github profiles of potentially interesting candidates to a database for future reference.

Searching for a user retrieves their general information as well as the last 5 updated respositories the person owns. Following this the languages used in the repositories are displayed as percentages of the code in the repositories which allows the recruiter to quickly get an estimation of what languages the person uses.

This can be useful in order to see if a candidate is likely to have the required languages for a particular vacancy, and gives a quick access to the repositories where the languages were used.

## Running Locally

Make sure you have Python3 installed


>1. git clone https://github.com/sano2019/github-project.git # or clone your own fork
>2. cd github-project
>3. pip install -r requirements.txt
>4. generate a personal access token: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
>5. save the access token as an environment variable named GITHUB_TOKEN
>6. generate a secret key for the app: https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY
>7. save the secret key as an environment variable named SECRET_KEY
>8. python main.py


Your app should now be running on [localhost:5000](http://localhost:5000/).

## Known issues:

When not logged in, pressing the back button from the details page of a user will result in an error. Probably remedied by implementing anonymous sessions.

## Future improvements:

* This app is currently scoped to be used by different recruiters sharing one database. In the future it might be necessary / wanted to have individual profile saves for the logged in user instead of shared.
* As this is a prototype, further development in this area should be discussed with the customer.
* Extract database code into a separate file for more separation of concerns
* Allow the user to update the languages on the saved profiles. Currently, the language information is only gathered at the point the profile is saved, and can't be updated.

---
This app was created in PyCharm using Flask