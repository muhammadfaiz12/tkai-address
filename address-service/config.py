import os
import requests
import json

from dotenv import load_dotenv, find_dotenv
from constant import LIST_HOST_ADD

load_dotenv(find_dotenv())
basedir = os.path.abspath(os.path.dirname(__file__))
quorum = {}

class Config(object):
    # ...
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, './eWallet.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

def init_quorum():
    quorum_list = os.getenv("QUORUM").split(",")

    if os.getenv("DEBUG") == "True":
        with open("./file/list.json", 'r') as f:
            val = json.load(f)
    else:
        r = requests.get(LIST_HOST_ADD)
        val = r.json()
    for d in val:
        if d["npm"] in quorum_list:
            quorum[d["npm"]] = d["ip"]