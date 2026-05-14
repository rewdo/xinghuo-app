from flask import Blueprint, request, jsonify

from app import db
from app.models.user import User
from app.models.transaction import Transaction
from app.api.user import login_required

wallet_bp = Blueprint('wallet', __name__)


@wallet_bp.route('/balance', methods=['GET'])
@login_required
def get_balance():
    """Get wallet balance."""
    user = User.query.get(request.user_id)
    return jsonify({
        'code': 0,
        'data': {
            'balance': float(user.balance),
            'total_earnings': float(user.total_earnings),
        }
    })


@wallet_bp.route('/transactions', methods=['GET'])
@login_required
def get_transactions():
    """Get transaction history."""
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=20)

    pagination = Transaction.query.filter_by(user_id=request.user_id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 0,
        'data': {
            'transactions': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }
    })


@wallet_bp.route('/withdraw', methods=['POST'])
@login_required
def withdraw():
    """Request withdrawal (placeholder - actual WeChat Pay transfer to be implemented)."""
    data = request.get_json()
    amount = data.get('amount', type=float)
    if not amount or amount <= 0:
        return jsonify({'code': 400, 'msg': '无效的提现金额'}), 400

    user = User.query.get(request.user_id)
    if float(user.balance) < amount:
        return jsonify({'code': 400, 'msg': '余额不足'}), 400

    # Placeholder: record withdrawal request
    # Actual WeChat Pay transfer integration will be added later
    user.balance = float(user.balance) - amount

    tx = Transaction(
        user_id=user.id,
        transaction_type=2,  # 提现
        amount=amount,
        balance_before=float(user.balance) + amount,
        balance_after=float(user.balance),
        status=0,  # 处理中
        remark='提现申请',
    )
    db.session.add(tx)
    db.session.commit()

    return jsonify({'code': 0, 'msg': '提现申请已提交，预计T+1到账'})
