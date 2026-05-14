from datetime import datetime
from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    openid = db.Column(db.String(64), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(64))
    avatar_url = db.Column(db.String(256))
    phone = db.Column(db.String(20))
    gender = db.Column(db.SmallInteger, default=0)     # 0未知 1男 2女
    fitness_tags = db.Column(db.String(256))             # "跑步,爬楼,搬运"
    credit_score = db.Column(db.Integer, default=100)
    total_earnings = db.Column(db.Numeric(10, 2), default=0.00)
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    level = db.Column(db.Integer, default=1)
    status = db.Column(db.SmallInteger, default=1)       # 1正常 0冻结
    lat = db.Column(db.Numeric(10, 7), nullable=True)
    lng = db.Column(db.Numeric(10, 7), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = db.relationship('TaskOrder', backref='user', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'avatar_url': self.avatar_url,
            'phone': self.phone,
            'gender': self.gender,
            'fitness_tags': self.fitness_tags.split(',') if self.fitness_tags else [],
            'credit_score': self.credit_score,
            'total_earnings': float(self.total_earnings),
            'balance': float(self.balance),
            'level': self.level,
            'status': self.status,
        }
