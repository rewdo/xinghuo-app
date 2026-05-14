import math
from datetime import datetime

from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import func

from app import db
from app.models.task import Task
from app.models.merchant import Merchant
from app.api.user import login_required

task_bp = Blueprint('task', __name__)


def haversine_distance(lat1, lng1, lat2, lng2):
    """Calculate distance in meters between two GPS coordinates."""
    R = 6371000  # Earth radius in meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lng2 - lng1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@task_bp.route('/nearby', methods=['GET'])
def nearby_tasks():
    """Get nearby available tasks based on location."""
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', type=int, default=current_app.config['DEFAULT_SEARCH_RADIUS'])
    task_type = request.args.get('task_type', type=int)
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=current_app.config['DEFAULT_PAGE_SIZE'])

    if not lat or not lng:
        return jsonify({'code': 400, 'msg': '缺少位置参数 lat/lng'}), 400

    # Query available tasks
    query = Task.query.filter(Task.status == 0, Task.accepted_count < Task.quantity)

    if task_type:
        query = query.filter(Task.task_type == task_type)

    tasks = query.order_by(Task.created_at.desc()).all()

    # Calculate distance and filter by radius
    result = []
    for task in tasks:
        if task.lat and task.lng:
            distance = haversine_distance(lat, lng, float(task.lat), float(task.lng))
            if distance > radius:
                continue
            task_dict = task.to_dict()
            task_dict['distance'] = round(distance)
            result.append(task_dict)

    # Paginate in-memory (simple approach, optimize later)
    total = len(result)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = result[start:end]

    return jsonify({
        'code': 0,
        'data': {
            'tasks': page_data,
            'total': total,
            'page': page,
            'per_page': per_page,
        }
    })


@task_bp.route('/<int:task_id>', methods=['GET'])
def task_detail(task_id):
    """Get task details."""
    task = Task.query.get(task_id)
    if not task:
        return jsonify({'code': 404, 'msg': '任务不存在'}), 404
    return jsonify({'code': 0, 'data': task.to_dict()})


@task_bp.route('/create', methods=['POST'])
def create_task():
    """Merchant creates a new task. (No auth for MVP - will add merchant auth)"""
    data = request.get_json()

    required = ['merchant_id', 'title', 'task_type', 'reward_amount']
    for field in required:
        if field not in data:
            return jsonify({'code': 400, 'msg': f'缺少必填参数: {field}'}), 400

    task = Task(
        merchant_id=data['merchant_id'],
        title=data['title'],
        description=data.get('description', ''),
        task_type=data['task_type'],
        reward_type=data.get('reward_type', 1),
        reward_amount=data['reward_amount'],
        quantity=data.get('quantity', 1),
        address=data.get('address', ''),
        lat=data.get('lat'),
        lng=data.get('lng'),
        difficulty=data.get('difficulty', 1),
        estimated_min=data.get('estimated_min', 15),
        expired_at=datetime.fromisoformat(data['expired_at']) if data.get('expired_at') else None,
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({'code': 0, 'data': task.to_dict()}), 201


@task_bp.route('/manage', methods=['GET'])
def manage_tasks():
    """Get merchant's tasks."""
    merchant_id = request.args.get('merchant_id', type=int)
    status = request.args.get('status', type=int)
    page = request.args.get('page', type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=20)

    if not merchant_id:
        return jsonify({'code': 400, 'msg': '缺少 merchant_id'}), 400

    query = Task.query.filter_by(merchant_id=merchant_id)
    if status is not None:
        query = query.filter_by(status=status)

    pagination = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'code': 0,
        'data': {
            'tasks': [t.to_dict() for t in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
        }
    })
