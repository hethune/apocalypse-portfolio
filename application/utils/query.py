from ..models import User, Phone
from ..models import Picture
from index import app, db, bcrypt
from flask import jsonify
from sqlalchemy import and_
import hashlib
from urllib import quote_plus
import requests
import json
from sqlalchemy.exc import DataError, IntegrityError
import datetime
import sys
from qiniu import Auth
from flask.json import dumps

FIVE_MINUTES = 60*5

class QueryHelper(object):
  'You can use this class query the complex query via the SqlAlchemy query'
  @classmethod
  def to_json_with_filter(cls, rows_dict, columns):
    d = {'success':True}
    for k, v in rows_dict.items():
      # handle the dict and integer and float
      if type(v) == type({}) or type(v) == type(1) or type(v) == type(1.0) or type(v) == type('') or type(v) == type(u'') or type(v) == type(True) \
       or type(datetime.datetime.now()) == type(v):
        d[k] = v
      # handle the model object
      elif (type(v) != type([])) and (v is not None):
        d[k] = {_k:_v for _k, _v in v.__dict__.items() if _k in columns}
      # handle the list
      elif v is not None:
        l = []
        for item in v:
          # handle the model object
          if type(item) != type({}):
            l.append({_k:_v for _k, _v in item.__dict__.items() if _k in columns})
          # handle the dict  
          else:
            l.append({_k:_v for _k, _v in item.items() if _k in columns})
        d[k] = l
      # handle the None  
      else:
        d[k] = {}
    return jsonify(d), 200

  @classmethod
  def to_dict_with_filter(cls, rows_dict, columns):
    d = {'success':True}
    for k, v in rows_dict.items():
      # handle the dict and integer and float
      if type(v) == type({}) or type(v) == type(1) or type(v) == type(1.0) or type(v) == type('') or type(v) == type(u'') or type(v) == type(True) \
       or type(datetime.datetime.now()) == type(v):
        d[k] = v
      # handle the model object
      elif (type(v) != type([])) and (v is not None):
        d[k] = {_k:_v for _k, _v in v.__dict__.items() if _k in columns}
      # handle the list
      elif v is not None:
        l = []
        for item in v:
          # handle the model object
          if type(item) != type({}):
            l.append({_k:_v for _k, _v in item.__dict__.items() if _k in columns})
          # handle the dict  
          else:
            l.append({_k:_v for _k, _v in item.items() if _k in columns})
        d[k] = l
      # handle the None  
      else:
        d[k] = {}
    return d

  @classmethod
  def get_wechat_sessionkey_and_openid(cls, code):
    querystring = {
      'appid': app.config['WECHAT_APP_ID'],
      'secret': app.config['WECHAT_APP_SECRET'],
      'js_code': code,
      'grant_type': app.config['WECHAT_APP_GRANT_TYPE']
      }
    response = requests.request("GET", app.config['WECHAT_APP_CODE_URL'], params=querystring)
    return json.loads(response.text)

  @classmethod
  def get_user_with_openid(cls, openid):
    return User.query.filter_by(openid=openid).first()

  @classmethod
  def add_or_set_user(cls, openid, nick_name, gender, language, city, province, country, avatar_url, phone=None):
    user = cls.get_user_with_openid(openid=openid)
    if user:
      user.nick_name, user.gender = nick_name, gender
      user.language, user.city = language, city
      user.province, user.country = province, country
      user.avatar_url = avatar_url
    else:
      user = User(openid=openid, nick_name=nick_name, gender=gender,
        language=language, city=city, province=province, country=country, 
        avatar_url=avatar_url, phone=phone)
    try:
      db.session.merge(user)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return None
    return cls.get_user_with_openid(openid=openid)

  @classmethod
  def get_phone_with_phone_and_country(cls, phone, country):
    return Phone.query.filter_by(phone=phone, country=country).first()

  @classmethod
  def add_or_set_phone(cls, phone_nu, country, verification_code, verification_code_created_at, is_verified=False):
    phone = cls.get_phone_with_phone_and_country(phone=phone_nu, country=country)
    try:
      if not phone:
        phone = Phone(phone_nu, country, verification_code,
          verification_code_created_at, is_verified)
      else:
        phone.phone, phone.country = phone_nu, country
        phone.verification_code, phone.is_verified = verification_code, is_verified
        phone.verification_code_created_at = verification_code_created_at
      db.session.merge(phone)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return None
    return phone

  @classmethod
  def get_phone_with_phone_and_country(cls, phone, country):
    return Phone.query.filter(and_(Phone.phone==phone, Phone.country==country)).first()

  @classmethod
  def verify_sms_code(cls, phone, country, code, expiration=FIVE_MINUTES):
    phone = cls.get_phone_with_phone_and_country(phone, country)
    if phone and phone.verification_code == code \
        and phone.verification_code_created_at + datetime.timedelta(seconds=expiration) > datetime.datetime.utcnow():
      return True 
    return False

  @classmethod
  def get_user_with_id(cls, user_id):
    return User.query.filter_by(id=user_id).first()

  @classmethod
  def set_user_phone_with_id(cls, user_id, phone, country_code, is_verified=True):
    user = cls.get_user_with_id(user_id=user_id)
    try:
      user.phone = phone
      user.country_code = country_code
      db.session.merge(user)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return False
    return True

  @classmethod
  def set_phone_is_verified(cls, phone, country):
    phone = cls.get_phone_with_phone_and_country(phone=phone, country=country)
    try:
      phone.is_verified = True
      db.session.merge(phone)
      db.session.commit()
    except (DataError, IntegrityError), e:
      app.logger.error(sys._getframe().f_code.co_name + str(e))
      return False
    return True

  @classmethod
  def get_user_with_phone_and_country(cls, phone, country):
    user = User.query.filter_by(phone=phone, country=country).first()
    if user:
      return user
    else:
      return None

  @classmethod
  def get_wechat_access_token_for_app(cls, code):
    querystring = {
      'appid': app.config['WECHAT_APP_ID_FOR_APP'],
      'secret': app.config['WECHAT_SECRET_FOR_APP'],
      'code': code,
      'grant_type': app.config['WECHAT_GRANT_TYPE_FOR_APP']
      }
    response = requests.request("GET", app.config['WEHCAT_GET_ACCESS_TOKEN_URL'], params=querystring)
    return json.loads(response.text)

  @classmethod
  def get_wechat_user_info_for_app(cls, access_token, openid):
    querystring = {
      'access_token': access_token,
      'openid': openid
      }
    response = requests.request("GET", app.config['WEHCAT_GET_USERINFO_URL'], params=querystring)
    return json.loads(response.text)

  @classmethod
  def get_user_with_openid(cls, openid):
    return User.query.filter_by(openid=openid).first()

  @classmethod
  def to_response(cls, data):
    return app.response_class(
        response=(dumps(data), '\n'),
        status=200,
        mimetype='application/json'
    )