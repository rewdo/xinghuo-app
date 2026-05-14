from datetime import datetime

from flask import Blueprint, request, jsonify, current_app

from app import db
from app.models.merchant import Merchant
from app.models.task import Task
from app.models.order import TaskOrder
from app.models.transaction import Transaction

merchant_bp = Blueprint('merchant', __name__)


@merchant_bp.route('/register', methods=['POST'])
def register():
    """Merchant registration."""
    data = request.get_json()
    required = ['company_name', 'contact_name', 'contact_phone']
    for field in required:
        if field not in data:
            return jsonify({'code': 400, 'msg': f'缺少必填参数: {field}'}), 400

    merchant = Merchant(
        company_name=data['company_name'],
        contact_name=data['contact_name'],
        contact_phone=data['contact_phone'],
        address=data.get('address', ''),
        lat=data.get('lat'),
        lng=data.get('lng'),
        business_license=data.get('business_license', ''),
    )
    db.session.add(merchant)
    db.session.commit()

    return jsonify({'code': 0, 'data': merchant.to_dict()}), 201


@merchant_bp.route('/profile', methods=['GET'])
def profile():
    """Get merchant profile."""
    merchant_id = request.args.get('merchant_id', type=int)
    if not merchant_id:
        return jsonify({'code': 400, 'msg': '缺少 merchant_id'}), 400

    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return jsonify({'code': 404, 'msg': '商户不存在'}), 404

    return jsonify({'code': 0, 'data': merchant.to_dict()})


@merchant_bp.route('/tasks/<int:task_id>/confirm', methods=['POST'])
def confirm_complete(task_id):
    """Merchant confirms task completion, triggers payment settlement."""
    merchant_id = request.get_json().get('merchant_id')
    if not merchant_id:
        return jsonify({'code': 400, 'msg': '缺少 merchant_id'}), 400

    task = Task.query.get(task_id)
    if not task or task.merchant_id != merchant_id:
        return jsonify({'code': 404, 'msg': '任务不存在'}), 404

    # Find the "pending confirmation" order for this task
    order = TaskOrder.query.filter_by(
        task_id=task_id, status=2  # 待确认
    ).first()
    if not order:
        return jsonify({'code': 400, 'msg': '没有待确认的订单'}), 400

    # Calculate settlement
    order_amount = float(task.reward_amount)
    commission = round(order_amount * current_app.config['PLATFORM_COMMISSION_RATE'], 2)
    user_income = round(order_amount - commission, 2)

    # Update order status
    order.status = 3  # 已完成
    order.completed_at = datetime.utcnow()

    # Update user balance
    from app.models.user import User
    user = User.query.get(order.user_id)
    user.balance = float(user.balance) + user_income
    user.total_earnings = float(user.total_earnings) + user_income

    # Record transaction for user
    tx_user = Transaction(
        user_id=order.user_id,
        order_id=order.id,
        transaction_type=1,  # 任务收入
        amount=user_income,
        balance_before=float(user.balance) - user_income,
        balance_after=float(user.balance),
        status=1,
        remark=f'任务完成收入: {task.title}',
    )
    db.session.add(tx_user)

    # Record platform commission transaction
    tx_commission = Transaction(
        merchant_id=merchant_id,
        order_id=order.id,
        transaction_type=4,  # 平台佣金
        amount=commission,
        status=1,
        remark=f'平台佣金 {task.title}',
    )
    db.session.add(tx_commission)

    # Check if all orders for this task are done
    pending = TaskOrder.query.filter_by(task_id=task_id, status__in=[0, 1, 2]).count()
    if pending == 0:
        task.status = 2  # 全部完成

    db.session.commit()

    return jsonify({
        'code': 0,
        'data': {
            'order_id': order.id,
            'user_income': user_income,
            'commission': commission,
            'platform_commission_rate': current_app.config['PLATFORM_COMMISSION_RATE'],
        }
    })
