# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request, jsonify

from application.models import Property
from index import app, auto
from ..utils.helper import uuid_gen, json_validate

from ..utils.query import QueryHelper
from datetime import datetime
from ..utils.helper import uuid_gen, json_validate, generate_token, verify_token, id_generator, convert_camel_to_snake, datetime_to_epoch

portfolio_bp = Blueprint('portfolio', __name__)
logger = app.logger


@portfolio_bp.route('/recommend', methods=['GET'])
@auto.doc()
@uuid_gen
@json_validate(filter=['money', "style", "leverage"])
def get_recommend_portfolio():
  '''return recommend portfolio to user
  Method:
    GET
  Authentication:
    None
  Request Data:
    money 用户想投资的金额
    leverage 用户想使用的杠杆金额倍数
    style 投资风格，1：按增长，2：按收益率，3：平衡
    filter 二期定义
  Returns:
    {
      portfolio: [
        {
          "id": news id,
          "value": epoch time
          ...
          }
        }
      ]
    }
  '''

  incoming = request.get_json()
  money = int(incoming['money'])
  leverage = int(incoming['leverage'])
  style = int(incoming['style'])
  money = money * leverage

  # 查询数据库，取得所有符合要求的房源数据
  # todo add filter
  properties = Property.query.all()

  # 通过算法，找出合适的投资组合
  rcmd_properties = {}

  # 组装结果数据，并返回
  result = {}
  result["portfolio"] = list({
                               "id": x.id,
                             } for x in rcmd_properties)

  return jsonify(result)


@portfolio_bp.route('/debug', methods=['GET'])
@auto.doc()
@uuid_gen
def for_debug():
  # 查询数据库，取得所有符合要求的房源数据
  properties = Property.query.filter_by(status="ForSale").all()

  # 通过算法，找出合适的投资组合
  rcmd_properties = {}

  # 组装结果数据，并返回
  result = {}
  result["portfolio"] = list(
    {
      "id": x.id,
      "source": x.source,
      "source_id": x.source_id,
      "latitude": x.latitude,
      "longitude": x.longitude,
      "square_feet": x.square_feet,
      "bedrooms": x.bedrooms,
      "bathrooms": x.bathrooms,
      "built_year": x.built_year,
      "property_type": x.property_type,
      "lot_size": x.lot_size,
      "is_pool": x.is_pool,
      "address1": x.address1,
      "zip": x.zip,
      "city": x.city,
      "country": x.is_pool,
      "cbsacode": x.cbsacode,
      "state": x.state,
      "list_price": x.list_price,
      "monthly_rent": x.monthly_rent,
      "yearly_insurance_cost": x.yearly_insurance_cost,
      "yearly_property_taxes": x.yearly_property_taxes,
      "appreciation": x.appreciation,
      "imgurl": x.imgurl,
      "neighbor_regionid": x.neighbor_regionid,
      "score_v1_appreciation": x.score_v1_appreciation,
      "score_v2_balance": x.score_v2_balance,
      "score_v3_return": x.score_v3_return,
      "score_version": x.score_version,
      "neighbor_score": x.neighbor_score,
      "status": x.status,
    } for x in properties)

  return jsonify(result)
