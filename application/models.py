import datetime

from index import db


class User(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)
  phone = db.Column(db.String(255))
  country = db.Column(db.String(255))
  wechat_nickname = db.Column(db.String(255))
  wechat_province = db.Column(db.String(255))
  wechat_city = db.Column(db.String(255))
  wechat_openid = db.Column(db.String(255), index=True)
  wechat_unionid = db.Column(db.String(255), index=True)
  wechat_gender = db.Column(db.Integer())  # 0 or null not specified 1 - Male 2 - Female
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


class Property(db.Model):
  id = db.Column(db.Integer(), index=True, primary_key=True)

  source = db.Column(db.String(255))
  source_id = db.Column(db.Integer())
  latitude = db.Column(db.FLOAT())
  longitude = db.Column(db.FLOAT())
  square_feet = db.Column("squarefeet", db.FLOAT())
  bedrooms = db.Column(db.FLOAT())
  bathrooms = db.Column(db.FLOAT())
  built_year = db.Column("yearbuilt", db.Integer())
  property_type = db.Column("propertytype", db.String(255))
  lot_size = db.Column("lotsize", db.Integer())
  is_pool = db.Column("ispool", db.Boolean(), default=False)

  address1 = db.Column(db.String(255))
  zip = db.Column(db.String(255))
  city = db.Column(db.String(255))
  county = db.Column(db.String(255))
  cbsacode = db.Column(db.Integer())
  state = db.Column(db.String(10))

  list_price = db.Column("listprice", db.FLOAT())
  monthly_rent = db.Column("monthlyrent", db.FLOAT())
  yearly_insurance_cost = db.Column("yearlyinsurancecost", db.FLOAT())
  yearly_property_taxes = db.Column("yearlypropertytaxes", db.FLOAT())
  appreciation = db.Column("appreciation", db.FLOAT())

  neighbor_score = db.Column("neighborscore", db.FLOAT())

  status = db.Column(db.String(255))

  created_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow)
  updated_at = db.Column(db.DateTime(), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
