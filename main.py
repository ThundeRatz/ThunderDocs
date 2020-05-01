# Python standard libraries
import json
import os
import sqlite3

# Third-party libraries
import flask

from oauthlib.oauth2 import WebApplicationClient
import requests

from local_settings import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, FLASK_SECRET_KEY

GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

# Flask app setup
app = flask.Flask(__name__)
app.secret_key = FLASK_SECRET_KEY


# OAuth 2 client setup
oauth_client = WebApplicationClient(GOOGLE_CLIENT_ID)


def is_logged_in():
    return True if AUTH_TOKEN_KEY in flask.session else False


@app.route("/")
def index():
    if is_logged_in():
        return "<p>Hello! You're logged in!</p>"
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route("/auth")
def nginx_auth():
    if is_logged_in():
        return 'Ok!', 202
    else:
        return 'User must be logged in!', 401


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = oauth_client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri= flask.request.base_url + "/login/callback",
        scope=["openid", "email", "profile"],
    )

    flask.session.permanent = True

    return flask.redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = flask.request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = oauth_client.prepare_token_request(
        token_endpoint,
        authorization_response=flask.request.url,
        redirect_url=flask.request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    oauth_client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = oauth_client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        flask.session[AUTH_TOKEN_KEY] = True
    else:
        return "User email not available or not verified by Google.", 400

    return flask.redirect(flask.url_for("index"))


if __name__ == "__main__":
    app.run(ssl_context="adhoc")
