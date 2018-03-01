# -*- coding: utf-8 -*-

import random
import re
import string
import uuid
from datetime import datetime
from functools import wraps, partial

import flask
from flask import request, jsonify, g
from itsdangerous import SignatureExpired, BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from pytz import timezone

from index import app
from query import QueryHelper

TWO_HOURS = 60 * 60 * 2
ONE_DAY = TWO_HOURS * 12
ONE_WEEK = ONE_DAY * 7
logger = app.logger


def uuid_gen(f):
  @wraps(f)
  def decorated(*args, **kwargs):
    flask.g.uuid = str(uuid.uuid4()).split("-")[0]
    return f(*args, **kwargs)

  return decorated


def json_validate(f=None, filter=[]):
  if not f:
    return partial(json_validate, filter=filter)

  @wraps(f)
  def decorated(*args, **kwargs):
    incoming = request.get_json()
    if incoming is None:
      logger.error('Parameters not compatible')
      return jsonify(success=False,
                     message='Parameters not compatible'), 400
    for item in filter:
      if item not in incoming.keys():
        logger.error('Parameters not compatible')
        return jsonify(success=False,
                       message='Parameters not compatible'), 400
    return f(*args, **kwargs)

  return decorated


def requires_token(f=None):
  if not f:
    return partial(requires_auth)

  @wraps(f)
  def decorated(*args, **kwargs):
    incoming = request.get_json()
    token = incoming['token']
    if token == app.config['WECHAT_TOKEN']:
      return f(*args, **kwargs)

    logger.error('Token is required to access this resource token is {}'.format(token))
    return jsonify(message="Token is required to access this resource"), 401

  return decorated


def requires_auth(f=None):
  if not f:
    return partial(requires_auth)

  @wraps(f)
  def decorated(*args, **kwargs):
    third_session = request.headers.get('Authorization', None)
    session_user = verify_token(third_session)
    if session_user:
      g.current_user = session_user
      return f(*args, **kwargs)
    logger.error('Authorization is required to access this resource third_session is {}'.format(third_session))
    return jsonify(message="Authorization is required to access this resource"), 401

  return decorated


def requires_admin_auth(f=None):
  if not f:
    return partial(requires_auth)

  @wraps(f)
  def decorated(*args, **kwargs):
    third_session = request.headers.get('Authorization', None)
    session_user = verify_token(third_session)
    if session_user:
      g.current_user = session_user
      user = QueryHelper.get_user_with_id(g.current_user["id"])
      if user.admin:
        logger.error('Admin logged in {} {}'.format(user.id, user.wechat_nickname))
        return f(*args, **kwargs)
    logger.error('Unauthorized admin access. third_session is {}'.format(third_session))
    return jsonify(message="Authorization is required to access this resource"), 401

  return decorated


def optional_auth(f=None):
  if not f:
    return partial(requires_auth)

  @wraps(f)
  def decorated(*args, **kwargs):
    third_session = request.headers.get('Authorization', None)
    session_user = verify_token(third_session)
    if session_user:
      g.current_user = session_user
    return f(*args, **kwargs)

  return decorated


def internal_auth(f=None):
  if not f:
    return partial(requires_auth)

  @wraps(f)
  def decorated(*args, **kwargs):
    third_session = request.headers.get('Authorization', None)
    session_user = verify_token(third_session)
    if session_user:
      g.current_user = session_user
      user = QueryHelper.get_user_with_id(g.current_user["id"])
      if user.internal:
        logger.error('Internal User testing {}'.format(user.id))
        return f(*args, **kwargs)
    return jsonify(message="No access privileges"), 403

  return decorated


def generate_token(user, expiration=ONE_WEEK):
  s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
  token = s.dumps({
    'id': user.id,
    'phone': user.phone,
    'country': user.country,
    'wechat_nickname': user.wechat_nickname,
  }).decode('utf-8')
  return token


def verify_token(token):
  if not token:
    return None
  s = Serializer(app.config['SECRET_KEY'])
  try:
    data = s.loads(token)
  except (BadSignature, SignatureExpired):
    return None
  return data


def id_generator(size=6, chars=string.digits):
  return ''.join(random.choice(chars) for x in range(size))


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def convert_camel_to_snake(name):
  s1 = first_cap_re.sub(r'\1_\2', name)
  return all_cap_re.sub(r'\1_\2', s1).lower()


def convert_seconds_to_human_string(seconds):
  hh = seconds / 3600
  mm = seconds % 3600 / 60
  ss = seconds % 60
  return {
    "HH": hh,
    "MM": mm,
    "SS": ss
  }


def datetime_to_epoch(datetime_obj):
  if not datetime_obj:
    return None
  return (datetime_obj.replace(tzinfo=timezone('UTC')) - datetime(1970, 1, 1).replace(tzinfo=timezone('UTC'))).total_seconds()


def unify_price_trend_range(price_trend, current_datetime=datetime.utcnow(), history=60, future=12):
  from dateutil.relativedelta import relativedelta
  if price_trend is None:
    return None
  start_datetime = current_datetime - relativedelta(months=history)
  end_datetime = current_datetime + relativedelta(months=future - 1)
  filtered_list = []
  for x in price_trend:
    if (
        int(x.get("year")) > start_datetime.year or
        (int(x.get("year")) == start_datetime.year and int(x.get("month")) >= start_datetime.month)
    ) and (
        int(x.get("year")) < end_datetime.year or
        (int(x.get("year")) == end_datetime.year and int(x.get("month")) <= end_datetime.month)
    ):
      if int(x.get('year')) == current_datetime.year and int(x.get('month')) == current_datetime.month:
        x["current"] = True
      filtered_list.append(x)
  sorted_price_trend = sorted(filtered_list, key=lambda price: int(price.get("year")))
  return sorted_price_trend
