"""
Replacement for RUSA ACP brevet time calculator
(see https://rusa.org/octime_acp.html)

"""

import flask
from flask import Flask, redirect, url_for, request, render_template
import os
import arrow  # Replacement for datetime, based on moment.js
import acp_times  # Brevet time calculations
#import config
from pymongo import MongoClient
from json import loads
import logging

###
# Globals
###
app = flask.Flask(__name__)
#CONFIG = config.configuration()
client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
database = client.tododb

###
# Pages
###


@app.route("/")
@app.route("/index")
def index():
    app.logger.debug("Main page entry")
    return flask.render_template('calc.html')


@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    return flask.render_template('404.html'), 404




###############
#
# AJAX request handlers
#   These return JSON, rather than rendering pages.
#
###############
@app.route("/_calc_times")
def _calc_times():
    """
    Calculates open/close times from miles, using rules
    described at https://rusa.org/octime_alg.html.
    Expects one URL-encoded argument, the number of miles.
    """
    app.logger.debug("Got a JSON request")
    km = request.args.get('km', 999, type=float)
    dist = request.args.get('dist', 200, type=int)
    start_time = request.args.get('start_time', type=str)
    app.logger.debug("km={}".format(km))
    app.logger.debug("request.args: {}".format(request.args))

    # now takes in distance, time and date inputted by user
    open_time = acp_times.open_time(km, dist, arrow.get(start_time)).format('YYYY-MM-DDTHH:mm')
    close_time = acp_times.close_time(km, dist, arrow.get(start_time)).format('YYYY-MM-DDTHH:mm')
    result = {"open": open_time, "close": close_time}
    return flask.jsonify(result=result)

@app.route('/insert/', methods=['POST'])
def insert():
    # delete contents of database
    # get data as a list
    data = loads(request.form.get("info"))
    # insert each dict into database
    database.tododb.drop()
    for item in data:
        database.tododb.insert_one(item);
        app.logger.debug(item)
    # redirect to initial page
    return flask.jsonify("Your data has been submitted!")

@app.route('/display/')
def display():
    app.logger.debug("DISPLAY CALLED")
    return render_template('display.html', items=list(database.tododb.find()))
#############

if app.debug:
    app.logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    print("Opening for global access on port 5000")
    app.run(port=5000, host="0.0.0.0")
