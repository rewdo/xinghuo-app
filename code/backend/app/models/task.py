from datetime import datetime
from app import db


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    task_type = db.Column(db.SmallInteger, nullable=False)   # 1配送 2搬运 3巡检 4其他
    reward_type = db.Column(db.SmallInteger, default=1)      # 1现金 2权益 3积分
    reward_amount = db.Column(db.Numeric(10, 2), default=0.00)
    quantity = db.Column(db.Integer, default=1)
    accepted_count = db.Column(db.Integer, default=0)
    status = db.Column(db.SmallInteger, default=0)            # 0待接受 1进行中 2已完成 3已取消
    address = db.Column(db.String(256))
    lat = db.Column(db.Numeric(10, 7))
    lng = db.Column(db.Numeric(10, 7))
    difficulty = db.Column(db.SmallInteger, default=1)        # 1轻松 2适中 3挑战
    estimated_min = db.Column(db.Integer, default=15)
    expired_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = db.relationship('TaskOrder', backref='task', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'merchant_id': self.merchant_id,
            'merchant_name': self.merchant.company_name if self.merchant else '',
            'title': self.title,
            'description': self.description,
            'task_type': self.task_type,
            'reward_type': self.reward_type,
            'reward_amount': float(self.reward_amount),
            'quantity': self.quantity,
            'accepted_count': self.accepted_count,
            'status': self.status,
            'address': self.address,
            'lat': float(self.lat) if self.lat else None,
            'lng': float(self.lng) if self.lng else None,
            'difficulty': self.difficulty,
            'estimated_min': self.estimated_min,
            'expired_at': self.expired_at.isoformat() if self.expired_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
