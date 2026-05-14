from datetime import datetime
from app import db


class TaskOrder(db.Model):
    __tablename__ = 'task_orders'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.SmallInteger, default=0)   # 0已接单 1执行中 2待确认 3已完成 4已取消
    accepted_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    merchant_note = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('task_id', 'user_id', name='uk_task_user'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'task_id': self.task_id,
            'task_title': self.task.title if self.task else '',
            'user_id': self.user_id,
            'user_nickname': self.user.nickname if self.user else '',
            'user_avatar': self.user.avatar_url if self.user else '',
            'status': self.status,
            'reward_amount': float(self.task.reward_amount) if self.task else 0,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
