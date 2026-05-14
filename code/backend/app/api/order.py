from datetime import datetime

from flask import Blueprint, request, jsonify, current_app

from app import db
from app.models.task import Task
from app.models.order import TaskOrder
from app.models.transaction import Transaction
from app.api.user import login_required

order_bp = Blueprint('order', __name__)


@order_bp.route('', methods=['GET'])
@login_required
def my_orders():
    """Get current user's orders."""
    status = request.args.get('status', type=int)
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=20)

    query = TaskOrder.query.filter_by(user_id=request.user_id)
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(TaskOrder.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'code': 0,
        'data': {
            'orders': [o.to_dict() for o in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }
    })


@order_bp.route('/<int:order_id>', methods=['GET'])
@login_required
def order_detail(order_id):
    """Get order detail."""
    order = TaskOrder.query.get(order_id)
    if not order or order.user_id != request.user_id:
        return jsonify({'code': 404, 'msg': '订单不存在'}), 404
    return jsonify({'code': 0, 'data': order.to_dict()})


@order_bp.route('/accept', methods=['POST'])
@login_required
def accept_task():
    """User accepts a task."""
    data = request.get_json()
    task_id = data.get('task_id')
    if not task_id:
        return jsonify({'code': 400, 'msg': '缺少task_id'}), 400

    task = Task.query.get(task_id)
    if not task:
        return jsonify({'code': 404, 'msg': '任务不存在'}), 404
    if task.status != 0:
        return jsonify({'code': 400, 'msg': '任务已停止接单'}), 400
    if task.accepted_count >= task.quantity:
        return jsonify({'code': 400, 'msg': '任务名额已满'}), 400

    # Check if user already accepted this task
    existing = TaskOrder.query.filter_by(task_id=task_id, user_id=request.user_id).first()
    if existing:
        return jsonify({'code': 400, 'msg': '你已经接了这个任务'}), 400

    # Create order and update task count (atomic)
    order = TaskOrder(
        task_id=task_id,
        user_id=request.user_id,
        status=1,  # 进行中
        accepted_at=datetime.utcnow(),
    )
    task.accepted_count += 1
    if task.accepted_count >= task.quantity:
        task.status = 1  # 已满员

    db.session.add(order)
    db.session.commit()

    return jsonify({'code': 0, 'data': order.to_dict()}), 201


@order_bp.route('/<int:order_id>/complete', methods=['POST'])
@login_required
def complete_order(order_id):
    """User marks order as completed (waiting for merchant confirmation)."""
    order = TaskOrder.query.get(order_id)
    if not order or order.user_id != request.user_id:
        return jsonify({'code': 404, 'msg': '订单不存在'}), 404
    if order.status != 1:
        return jsonify({'code': 400, 'msg': '订单状态不允许此操作'}), 400

    order.status = 2  # 待确认
    db.session.commit()

    return jsonify({'code': 0, 'data': order.to_dict()})


@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """User cancels an order."""
    order = TaskOrder.query.get(order_id)
    if not order or order.user_id != request.user_id:
        return jsonify({'code': 404, 'msg': '订单不存在'}), 404
    if order.status not in [0, 1]:
        return jsonify({'code': 400, 'msg': '无法取消已完成或已取消的订单'}), 400

    order.status = 4  # 已取消
    task = Task.query.get(order.task_id)
    if task:
        task.accepted_count = max(0, task.accepted_count - 1)
        if task.status == 1 and task.accepted_count < task.quantity:
            task.status = 0  # 重新开放

    db.session.commit()
    return jsonify({'code': 0, 'msg': '已取消'})
