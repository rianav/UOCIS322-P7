from flask import Flask, jsonify, request
import flask
from flask_restful import Resource, Api, reqparse
from pymongo import MongoClient
import os
import logging
from passlib.apps import custom_app_context as pwd_context
from passlib.hash import sha256_crypt as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer \
                                  as Serializer, BadSignature, \
                                  SignatureExpired)

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
database = client.tododb
logindatabase = client.logindb

SECRET_KEY = 'test1234@#$'

def getData(which_format, num_entries, which_list):
    data = list(database.tododb.find())
    values = []

    # if num_entries is specified
    if num_entries == None:
        num_entries = len(data)
    if num_entries > len(data):
        num_entries = len(data) - 1
    if num_entries != -1:
    # get desired entries
        data = data[:num_entries]

    if which_list == "open":
        # only get km and open times - get rid of close times
        for entry in data:
            entry.pop("close", None)
            entry.pop("loc", None)
            entry.pop("_id", None)
            csv = "miles,km,open\n"
    elif which_list == "close":
        # only get km and close times - get rid of open times
        for entry in data:
            entry.pop("open", None)
            entry.pop("loc", None)
            entry.pop("_id", None)
            csv = "miles,km,close\n"
    else:
        # keep data as is
        for entry in data:
            entry.pop("_id", None)
            csv = "miles,km,loc,open,close\n"

    app.logger.debug(data)

    if which_format == "csv":
        i = 0
        for entry in data:
            # get values from dict
            values.append(list(entry.values())) # [0, 00:00, 01:00]
            # join values
            csv += ",".join(values[i]) + "\n" # 0,00:00,01:00\n
            app.logger.debug(csv)
            i += 1
        return csv
    else:
        # format is JSON
        app.logger.debug(jsonify(data))
        return jsonify(data)

# helper function to hash password
def hash_password(password):
    return pwd_context.encrypt(password)

# helper function to verify password
def verify_password(password, hashVal):
    return pwd_context.verify(password, hashVal)

# helper function to generate token
def generate_auth_token(user_id, expiration=600):
    s = Serializer(SECRET_KEY, expires_in=expiration)
    app.logger.debug("GENERATE TOKEN")
    app.logger.debug(s.dumps({'id': user_id}))
    return s.dumps({'id': user_id})

# helper function to verify token
def verify_auth_token(token):
    s = Serializer(SECRET_KEY)
    app.logger.debug(token)
    try:
        data = s.dumps(token)
    except SignatureExpired:
        return "Expired"    # valid token, but expired
    except BadSignature:
        return "Invalid"    # invalid token
    return "Success"

# add top entries argument
# TODO: add token arg
# if token: verify (verify_auth_token)
# if no token: error
# if verified token, continue
class listAll(Resource):
    def get(self, dtype):
        num_entries = request.args.get('top', type=int)
        token = request.args.get('token')
        token_status = verify_auth_token(token)
        if token_status == "Success":
            return getData(dtype, num_entries, "all")
        response = jsonify(token_status)
        response.status_code = 401
        return response

class listOpenOnly(Resource):
    def get(self, dtype):
        num_entries = request.args.get('top', type=int)
        token = request.args.get('token')
        token_status = verify_auth_token(token)
        if token_status == "Success":
            return getData(dtype, num_entries, "open")
        response = jsonify(token_status)
        response.status_code = 401
        return response

class listCloseOnly(Resource):
    def get(self, dtype):
        num_entries = request.args.get('top', type=int)
        token = request.args.get('token')
        token_status = verify_auth_token(token)
        if token_status == "Success":
            return getData(dtype, num_entries, "close")
        response = jsonify(token_status)
        response.status_code = 401
        return response

#index = 0
parser = reqparse.RequestParser()
parser.add_argument('user', type=str)
parser.add_argument('pass', type=str)
class register(Resource):
    def post(self):
        global index
        # get username and password
        args = parser.parse_args()
        username = args['user']
        password = args['pass']
    
        in_use = logindatabase.logindb.find_one({"username": username})
        
        if in_use != None:
           response = jsonify("This user already exists!")
           response.status_code = 400
           return response

        if username == "":
            response = jsonify("Please enter a username")
            response.status_code = 400
            return response
        if password == "":
            response = jsonify("Please enter a password")
            response.status_code = 400
            return response

        # hash password
        hashed_pw = hash_password(password)
        # assign id
        #index += 1
        index = logindatabase.logindb.count()
        app.logger.debug(index)

        # insert into database (id, username, password)
        user_info = {"id": index, "username": username, "password": hashed_pw}
        app.logger.debug("-----REGISTER DEBUGGING-----")
        app.logger.debug(index)
        app.logger.debug(user_info)
        logindatabase.logindb.insert_one(user_info);

        # return JSON object with newly added user
        response = flask.jsonify({"id": index, "username": username, "password": hashed_pw})
        response.status_code = 201
        app.logger.debug(response)
    
        return response

parser = reqparse.RequestParser()
parser.add_argument('user', type=str)
parser.add_argument('pass', type=str)
class token(Resource):
    def get(self):
        app.logger.debug("-----TOKEN RESOURCE-----")
        # get username and password
        # look up username in database
        args = parser.parse_args()
        username = args['user']
        password = args['pass']
        app.logger.debug(password)
        app.logger.debug(type(password))
        app.logger.debug(username)
        user = logindatabase.logindb.find_one({"username": username})
        app.logger.debug("-----DEBUGGING HERE-----")
        app.logger.debug(user)
        app.logger.debug(user['password'])
        app.logger.debug(type(user['password']))
        app.logger.debug(user['id'])

        # if no match, return error
        if user == None:
            response = jsonify("This username does not exist!")
            response.status_code = 401
            return response

        if not verify_password(password, user['password']):
            response = jsonify("Incorrect password!")
            response.status_code = 401
            return response

        # if valid, return a token
        token = generate_auth_token(user["id"])
        app.logger.debug("TOKEN: " + str(token))
        response = jsonify({"token": str(token), "username": user["username"], "id": user["id"]})
        app.logger.debug("RESPONSE: " + str(response))
        response.status_code = 201  
        return response

# add resources
api.add_resource(listAll, '/listAll', '/listAll/<string:dtype>')
api.add_resource(listOpenOnly, '/listOpenOnly', '/listOpenOnly/<string:dtype>')
api.add_resource(listCloseOnly, '/listCloseOnly', '/listCloseOnly/<string:dtype>')
api.add_resource(register, '/register')
api.add_resource(token, '/token')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
