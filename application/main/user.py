from flask import request, jsonify, g
from flask import Blueprint
from index import app, db
from ..models import User
from sqlalchemy.exc import IntegrityError
from ..utils.query import QueryHelper
from ..utils.helper import uuid_gen, json_validate, requires_token, generate_token, verify_token, id_generator

user_bp = Blueprint('user', __name__)
logger = app.logger

@user_bp.route('/wechat/login', methods=['POST'])
@uuid_gen
@json_validate(filter=['token', 'code'])
@requires_token
def wechat_login():
  incoming = request.get_json()
  # get access token
  access_token = QueryHelper.get_wechat_access_token_for_app(code=incoming['code'])
  if not access_token.get('access_token', None):
    logger.error("Get wechat access_token failed {}".format(incoming["code"]))
    return jsonify(success=False, message='Get wechat access_token failed'), 403
  # get user info
  user_info = QueryHelper.get_wechat_user_info_for_app(access_token=access_token['access_token'],
    openid=access_token['openid'])
  user = QueryHelper.get_user_with_openid(openid=user_info['openid'])
  try:
    if not user:
      # ToDo: Fix and check session_key
      user = User(openid=user_info['openid'], nick_name=user_info['nickname'].encode('iso8859-1'), gender=user_info['sex'], language=None, city=None, country=user_info["country"],
      province=user_info['province'], avatar_url=user_info['headimgurl'], phone=None, type=1, password=None)
      db.session.add(user)
      db.session.commit()
      user = QueryHelper.get_user_with_openid(openid=user_info['openid'])
    else:
      user.nick_name = user_info['nickname'].encode('iso8859-1')
      user.avatar_url = user_info['headimgurl']
      db.session.merge(user)
      db.session.commit()
  except IntegrityError as e:
    logger.warning("Failed User Creation: phone openid {}, {}".format(user_info["openid"], e))
    return jsonify(success=False, message='login failed'), 403
  third_session = generate_token(user=user, session_key=None)
  # session[str(user.id)] = third_session
  return jsonify(nick_name=user.nick_name, avatar_url=user.avatar_url, user_id=user.id,
    third_session=third_session, success=True)