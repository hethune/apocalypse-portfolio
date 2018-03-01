# -*- coding: utf-8 -*-
from index import app, db
from .utils.helper import uuid_gen, json_validate, requires_token, generate_token, verify_token, requires_auth, id_generator
from .utils.query import QueryHelper
from .utils.cache import RedisCache
from flask import request, jsonify, g
from flask.json import dumps
import json
from tasks import send_sms_mobilecode
import datetime
# from index import session, home_cache
import time
from application.main.mob import mob as mob_blueprint
from application.main.user import user_bp as user_blueprint

app.register_blueprint(mob_blueprint, url_prefix='/api/mob')
app.register_blueprint(user_blueprint, url_prefix='/api/user')
logger = app.logger
