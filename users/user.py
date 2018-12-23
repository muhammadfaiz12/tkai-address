import os
import requests
import math
import sys

from flask import Flask, request, jsonify, Blueprint
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from config import Config, quorum, init_quorum
from flask_migrate import Migrate
from constant import (
    BERHASIL, GAGAL_DATABASE,
    GAGAL_QUORUM, HOST_GAGAL,
    TIDAK_TERDEFINISI,
    USER_ID_TIDAK_ADA,
    SYARAT_TRANSFER_GAGAL
)
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
quorum_list = os.getenv("QUORUM").split(",")
host = os.getenv("HOST")
hostname = os.getenv("HOST_NAME")

bp = Blueprint('user', __name__, url_prefix='/user')

threshold_high  = len(quorum_list)
threshold_mid = math.floor(len(quorum_list)/2) + 1

# DB model for account
class Users(db.Model):
    user_id    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name    = db.Column(db.String)
    def __repr__(self):
        return '<Account {0} {1}>'.format(self.user_id, self.name)

def init_account():
    account = Account.query.filter_by(user_id=host).first()
    if not account:
        newAccount = Account(user_id=9999, address="Dummy Address")
        db.session.add(newAccount)
        db.session.commit()


db.create_all()
db.session.commit()

print("\nHOST:", host, "\n")

@app.route('/ping',  methods=["POST"])
def ping():
    pong = BERHASIL
    return jsonify({"pingReturn":pong})

@app.route('/user', methods=["GET"])
def getAllUser():
    try:
        accounts = Users.query.all()
        res = []
        for x in accounts:
            row = {"user_id":x.user_id, "name":x.name}
            res.append(row)
        if not accounts:
            return jsonify({"status": -2, "message":"User record none Failed"})

        return jsonify(res)
    except Exception as e:
        print(e)
        return jsonify({"status": -10})

@app.route('/user', methods=["POST"])
def addUser():
    try:
        data = request.json
        account = Users(name=data["name"])
        db.session.add(account)
        db.session.commit()
        if not account:
            return jsonify({"status": -2, "message":"User record creation Failed"})

        return jsonify({"status": 1, "user_id":account.user_id, "name": data["name"]})
    except Exception as e:
        print(e)
        return jsonify({"status": -10})

@app.route('/user', methods=["DELETE"])
def deleteUser():
    try:
        data = request.json
        account = Users.query.filter_by(user_id=data["user_id"]).first()
        if not account:
            return jsonify({"status": -2, "message":"User Not Found"})
        db.session.delete(account)
        db.session.commit()

        return jsonify({"status": 1})
    except Exception as e:
        return jsonify({"status": -1, "message":str(e)})

if __name__ == "__main__":
    app.register_blueprint(bp)
    app.run(host=str(sys.argv[1]), port=int(sys.argv[2]))