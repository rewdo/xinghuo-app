from flask import Blueprint, request, jsonify

from app import db
from app.models.review import Review
from app.models.order import TaskOrder
from app.api.user import login_required

review_bp = Blueprint('review', __name__)


@review_bp.route('', methods=['POST'])
@login_required
def create_review():
    """Create a review for an order."""
    data = request.get_json()
    required = ['order_id', 'rating']
    for field in required:
        if field not in data:
            return jsonify({'code': 400, 'msg': f'缺少必填参数: {field}'}), 400

    rating = data['rating']
    if rating < 1 or rating > 5:
        return jsonify({'code': 400, 'msg': '评分必须是1-5星'}), 400

    # Check order exists and is completed
    order = TaskOrder.query.get(data['order_id'])
    if not order:
        return jsonify({'code': 404, 'msg': '订单不存在'}), 404
    if order.status != 3:
        return jsonify({'code': 400, 'msg': '只能评价已完成的任务'}), 400

    # Check if already reviewed
    existing = Review.query.filter_by(order_id=data['order_id']).first()
    if existing:
        return jsonify({'code': 400, 'msg': '已评价过此订单'}), 400

    review = Review(
        order_id=data['order_id'],
        rating=rating,
        comment=data.get('comment', ''),
        reviewer_type=data.get('reviewer_type', 2),
    )
    db.session.add(review)

    # Update user credit score
    from app.models.user import User
    if data.get('reviewer_type') == 1:  # Merchant reviewing user
        user = User.query.get(order.user_id)
        if user:
            # Simple credit score adjustment
            if rating >= 4:
                user.credit_score = min(100, user.credit_score + 1)
            elif rating <= 2:
                user.credit_score = max(60, user.credit_score - 5)

    db.session.commit()
    return jsonify({'code': 0, 'data': review.to_dict()}), 201


@review_bp.route('/order/<int:order_id>', methods=['GET'])
def get_order_review(order_id):
    """Get review for a specific order."""
    review = Review.query.filter_by(order_id=order_id).first()
    if not review:
        return jsonify({'code': 404, 'msg': '暂无评价'}), 404
    return jsonify({'code': 0, 'data': review.to_dict()})
