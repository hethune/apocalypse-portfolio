# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request, jsonify

from application.models import Property
from calc import calc_portfolio
from index import app, auto
from ..utils.helper import uuid_gen

portfolio_bp = Blueprint('portfolio', __name__)
logger = app.logger


@portfolio_bp.route('/recommend', methods=['GET'])
@auto.doc()
@uuid_gen
def get_recommend_portfolio():
  '''return recommend portfolio to user
  Method:
    GET
  Authentication:
    None
  Request Data:
    money 用户想投资的金额
    leverage 用户想使用的杠杆金额倍数
    mode 投资风格，1) High Appreciation 2) High Cash Return 3) Balanced Return
    limit 最大数量
    filter 二期定义
  Returns:
    {
      portfolio: [
        {
          "address1": "1325 S Ewing St",
          "appreciation": 0.00903009012924372,
          "bathrooms": 1.0,
          "bedrooms": 3.0,
          "built_year": 1962,
          "cbsacode": 26900,
          "city": "Indianapolis",
          "country": false,
          "id": 11490,
          "imgurl": "https://roofstock-cdn.azureedge.net/public/properties/1637245/photo/e24633ea-25e4-4789-b9b6-c66be7e22fd4_1-Screen_Shot_2017-09-01_at_11.11.10_AM-modified-20171911111618_640.jpg",
          "is_pool": false,
          "latitude": 39.74991,
          "list_price": 79033.0,
          "longitude": -86.10402,
          "lot_size": 6447,
          "monthly_rent": 650.0,
          "neighbor_regionid": null,
          "neighbor_score": 40.0,
          "property_type": "House",
          "score_v1_appreciation": 0.41438198535445,
          "score_v2_balance": 0.464290106531349,
          "score_v3_return": 0.514198227708248,
          "score_version": 0,
          "source": "roofstock",
          "source_id": 1637245,
          "square_feet": 912.0,
          "state": "IN",
          "status": "ForSale",
          "yearly_insurance_cost": 409.5,
          "yearly_property_taxes": 1400.0,
          "zip": "46203"
        }
      ]
    }
  '''
  money = request.args.get("money", default=500000, type=int)
  leverage = request.args.get("leverage", default=1, type=int)
  mode = request.args.get("mode", default=1, type=int)
  limit = request.args.get("limit", default=30, type=int)
  money = money * leverage

  # 查询数据库，取得所有符合要求的房源数据
  properties = Property.query.filter_by(status="ForSale").all()

  # 通过算法，找出合适的投资组合
  selected_ids = calc_portfolio(mode, money, limit, properties)

  # 组装结果数据，并返回
  result = {"portfolio": list(
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
    } for x in properties if x.id in selected_ids)}

  return jsonify(result)
