from index import db, bcrypt
# from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
import datetime

class User(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  phone = db.Column(db.String(255))
  country = db.Column(db.String(255))
  wechat_nickname = db.Column(db.String(255))
  wechat_province = db.Column(db.String(255))
  wechat_city = db.Column(db.String(255))
  wechat_openid = db.Column(db.String(255), index = True)
  wechat_unionid = db.Column(db.String(255), index = True)
  wechat_gender = db.Column(db.Integer()) # 0 or null not specified 1 - Male 2 - Female
  wechat_country = db.Column(db.String(255))
  wechat_avatar_uri = db.Column(db.String(255))
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

  __table_args__ = (
    db.Index("idx_phone", "phone"),
    db.Index("idx_wechat_nickname", "wechat_nickname"),
    db.Index("idx_phone_country", "phone", "country"),
    db.UniqueConstraint("phone", "country", name='unique_phone_contry'),
  )

class Phone(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  phone = db.Column(db.String(255))
  country = db.Column(db.String(255))
  verification_code = db.Column(db.String(255))
  verification_code_created_at = db.Column(db.DateTime())
  is_verified = db.Column(db.Boolean(), index=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)
  __table_args__ = (
    db.Index("idx_phone", "phone"),
    db.Index("idx_phone_country", "phone", "country"),
    db.UniqueConstraint("phone", "country", name='unique_phone_contry'),
  )

  def __init__(self, phone, country):
    self.phone = phone
    self.country = country
    self.is_verified = False


class Picture(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  pic_url = db.Column(db.String(1024))
  is_active = db.Column(db.Boolean(), default=False, index=True)
  type = db.Column(db.Integer(), index=True)
  created_at = db.Column(db.DateTime(), default=datetime.datetime.now)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.now, onupdate=datetime.datetime.now)

  __table_args__ = (
    db.Index("idx_picture_type_is_active", "type", 'is_active'),
  )