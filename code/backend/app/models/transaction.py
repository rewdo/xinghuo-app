from datetime import datetime
from app import db


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=True)
    order_id = db.Column(db.Integer, db.ForeignKey('task_orders.id'), nullable=True)
    transaction_type = db.Column(db.SmallInteger)   # 1任务收入 2提现 3充值 4平台佣金
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    balance_before = db.Column(db.Numeric(10, 2))
    balance_after = db.Column(db.Numeric(10, 2))
    status = db.Column(db.SmallInteger, default=0)  # 0处理中 1成功 2失败
    remark = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'merchant_id': self.merchant_id,
            'order_id': self.order_id,
            'type': self.transaction_type,
            'amount': float(self.amount),
            'balance_before': float(self.balance_before) if self.balance_before else None,
            'balance_after': float(self.balance_after) if self.balance_after else None,
            'status': self.status,
            'remark': self.remark,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
