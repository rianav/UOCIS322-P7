from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, abort
from urllib.parse import urlparse, urljoin
import flask
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user, UserMixin,
                         confirm_login, fresh_login_required)
from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt as pwd_context
import json
import requests
import os
import config
import logging

app = Flask(__name__)

app.secret_key = "and the cats in the cradle and the silver spoon"

app.config.from_object(__name__)

login_manager = LoginManager()

login_manager.session_protection = "strong"

login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."

login_manager.refresh_view = "login"
login_manager.needs_refresh_message = (
    u"To protect your account, please reauthenticate to access this page."
)
login_manager.needs_refresh_message_category = "info"

# user class
class User(UserMixin):
    def __init__(self, id, username, token):
        self.id = id
        self.username = username
        self.token = token

@login_manager.user_loader
def load_user(user_id):
    return User(int(user_id), flask.session["username"], flask.session["token"])

login_manager.init_app(app)

# LOGIN FORM
class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
            message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
            message=u"Huh, little too short for a password."),
        validators.InputRequired(u"Forget something?")])
    remember = BooleanField('Remember me')

# REGISTRATION FORM
class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(min=2, max=25,
            message=u"Huh, little too short for a username."),
        validators.InputRequired(u"Forget something?")])
    password = PasswordField('Password', [
        validators.Length(min=2, max=25,
            message=u"Huh, little too short for a password."),
        validators.InputRequired(u"Forget something?"),
        validators.EqualTo("confirm", message="Passwords must match")
        ])
    confirm = PasswordField("Retype Password")
        
def is_safe_url(target):
    """
    :source: https://github.com/fengsp/flask-snippets/blob/master/security/redirect_back.py
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

# helper function to hash password
def hash_password(password):
    return pwd_context.using(salt="somestring").encrypt(password)

# MAIN PAGE - buttons to choose output
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# LIST DATA PAGE
@app.route('/listdata')
def listeverything():
    token = flask.session.get("token")
    if token == None:
        token = ""
    app.logger.debug("-----LIST DATA PAGE-----")
    app.logger.debug(token)

    whichformat = request.args.get("whichformat", type=str)
    whichlist = request.args.get("whichlist", type=str)
    num_entries = request.args.get("num_entries", type=int)

    app.logger.debug(num_entries)

    data = requests.get('http://' + os.environ['BACKEND_ADDR'] + ':' 
            + os.environ['BACKEND_PORT'] + whichlist + whichformat 
            + '?top=' + str(num_entries) + '&token=' + token)
    
    rslt = {'which_data': data.text}
    return jsonify(result=rslt)

# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():
    app.logger.debug("------------LOGIN PAGE------------")
    form = LoginForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form and "password" in request.form:
        # get username and password and hash
        username = request.form["username"]
        password = request.form["password"]
        remember = request.form.get("remember", "false") == "true"
        hashed_pw = hash_password(password)
        
        # send request to token with user and pass
        get_token = requests.get('http://' + os.environ['BACKEND_ADDR'] 
                + ':' + os.environ['BACKEND_PORT'] + '/token?user=' + username
                + '&pass=' + hashed_pw)
         
        # if token success, set token
        app.logger.debug(str(get_token))
        user_info = json.loads(get_token.text)
        if get_token.status_code == 201:
            curr_user = User(int(user_info["id"]), user_info["username"], user_info["token"])
            flask.session["id"] = int(user_info["id"])
            flask.session["username"] = user_info["username"]
            flask.session["token"] = user_info["token"]
            if login_user(curr_user, remember=remember):
                flash("Logged in!")
                flash("I'll remember you") if remember else None
                next = request.args.get("next")
                if not is_safe_url(next):
                    abort(400)
                return redirect(url_for('index'))
            else:
                flash("Sorry, but you could not log in.")
        else:   
            flash(get_token.text)
        # if no success, render login template
    return render_template("login.html", form=form)

# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit() and request.method == "POST" and "username" in request.form and "password" in request.form:
        # get username and password and hash
        username = request.form["username"]
        password = request.form["password"]
        hashed_pw = hash_password(password)

        # send request to api
        registered = requests.post('http://' + os.environ['BACKEND_ADDR']
                + ':' + os.environ['BACKEND_PORT'] + '/register?user=' + username
                + '&pass=' + hashed_pw)
        if registered.status_code == 400:
            flash("This user already exists!")
            return render_template("register.html", form=form)
        flash("Registered!")
        # if no success, return error message
    return render_template("register.html", form=form)

@app.route("/logout")
@login_required
def logout():
    flask.session.pop("id", None)
    flask.session.pop("username", None)
    flask.session.pop("token", None)
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

