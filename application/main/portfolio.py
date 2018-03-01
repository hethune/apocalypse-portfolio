# -*- coding: utf-8 -*-

from flask import Blueprint
from flask import request, jsonify

from index import app, auto
from ..utils.helper import uuid_gen, json_validate

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
  print money, style

  # 通过算法，找出合适的投资组合
  rcmd_properties = {}

  # 组装结果数据，并返回
  result = {}
  result["portfolio"] = list({
                               "id": x.id,
                             } for x in rcmd_properties)

  return jsonify(result)
