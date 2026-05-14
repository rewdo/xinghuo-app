from datetime import datetime
from app import db


class Merchant(db.Model):
    __tablename__ = 'merchants'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(128), nullable=False)
    contact_name = db.Column(db.String(32))
    contact_phone = db.Column(db.String(20))
    address = db.Column(db.String(256))
    lat = db.Column(db.Numeric(10, 7))
    lng = db.Column(db.Numeric(10, 7))
    business_license = db.Column(db.String(256))
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    password_hash = db.Column(db.String(256))  # 商户端密码
    status = db.Column(db.SmallInteger, default=0)  # 0待审核 1正常 2冻结
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship('Task', backref='merchant', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'contact_name': self.contact_name,
            'contact_phone': self.contact_phone,
            'address': self.address,
            'balance': float(self.balance),
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
