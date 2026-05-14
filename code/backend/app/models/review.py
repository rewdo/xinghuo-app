from datetime import datetime
from app import db


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('task_orders.id'), unique=True, nullable=False)
    rating = db.Column(db.SmallInteger, nullable=False)   # 1-5星
    comment = db.Column(db.String(512))
    reviewer_type = db.Column(db.SmallInteger)             # 1B端评C端 2C端评B端
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'rating': self.rating,
            'comment': self.comment,
            'reviewer_type': self.reviewer_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
