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

bp = Blueprint('ewallet', __name__, url_prefix='/ewallet')

threshold_high  = len(quorum_list)
threshold_mid = math.floor(len(quorum_list)/2) + 1

# DB model for account
class Account(db.Model):
    address_id    = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_id       = db.Column(db.INTEGER)
    address    = db.Column(db.String)
    def __repr__(self):
        return '<Account {0} {1} {2}>'.format(self.user_id, self.user_id, self.address)

def init_account():
    account = Account.query.filter_by(user_id=host).first()
    if not account:
        newAccount = Account(user_id=9999, address="Dummy Address")
        db.session.add(newAccount)
        db.session.commit()


db.create_all()
db.session.commit()

print(quorum)
print("\nHOST:", host, "\n")

@app.route('/ping',  methods=["POST"])
def ping():
    pong = BERHASIL
    return jsonify({"pingReturn":pong})

@app.route('/edit-address', methods=["POST"])
def editAddress():
    try:
        data = request.json
        account = Account.query.filter_by(user_id=data["user_id"]).first()
        if not account:
            return jsonify({"status": -2, "message":"User Not Found"})
        account.address = data["address"]
        db.session.commit()

        return jsonify({"status": 1, "new-address": data["address"]})
    except Exception:
        return jsonify({"status": -1})

@app.route('/address', methods=["GET"])
def getAddress():
    try:
        accounts = Account.query.all()
        res = []
        for x in accounts:
            row = {"address_id":x.address_id, "user_id":x.user_id, "address":x.address}
            res.append(row)
        if not accounts:
            return jsonify({"status": -2, "message":"User record none Failed"})

        return jsonify(res)
    except Exception as e:
        print(e)
        return jsonify({"status": -10})

@app.route('/address', methods=["POST"])
def addAddress():
    try:
        data = request.json
        account = Account(user_id=data["user_id"], address=data["address"])
        db.session.add(account)
        db.session.commit()
        if not account:
            return jsonify({"status": -2, "message":"User record creation Failed"})
        account.address = data["address"]
        db.session.commit()

        return jsonify({"status": 1, "id":account.user_id, "address": data["address"]})
    except Exception as e:
        print(e)
        return jsonify({"status": -10})

@app.route('/address', methods=["DELETE"])
def deleteAddress():
    try:
        data = request.json
        account = Account.query.filter_by(user_id=data["user_id"]).first()
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