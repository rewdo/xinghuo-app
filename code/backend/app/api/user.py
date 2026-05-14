import json
from datetime import datetime, timedelta

import requests
import jwt
from flask import Blueprint, request, jsonify, current_app

from app import db, redis_client
from app.models.user import User

user_bp = Blueprint('user', __name__)


def generate_token(user_id):
    """Generate JWT token for user."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + current_app.config['JWT_EXPIRATION_DELTA'],
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')


def login_required(f):
    """Decorator: verify JWT token and inject user_id."""
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'code': 401, 'msg': '未登录'}), 401
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            request.user_id = payload['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'msg': '登录已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'msg': '无效的登录凭证'}), 401
        return f(*args, **kwargs)
    return decorated


@user_bp.route('/wxlogin', methods=['POST'])
def wxlogin():
    """WeChat mini program login."""
    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify({'code': 400, 'msg': '缺少code参数'}), 400

    # Exchange code for session_key + openid via WeChat API
    wx_url = (
        f'https://api.weixin.qq.com/sns/jscode2session'
        f'?appid={current_app.config["WX_APPID"]}'
        f'&secret={current_app.config["WX_SECRET"]}'
        f'&js_code={code}&grant_type=authorization_code'
    )
    resp = requests.get(wx_url)
    wx_data = resp.json()

    if 'openid' not in wx_data:
        return jsonify({'code': 400, 'msg': '微信登录失败', 'detail': wx_data.get('errmsg')}), 400

    openid = wx_data['openid']

    # Find or create user
    user = User.query.filter_by(openid=openid).first()
    if not user:
        user = User(openid=openid)
        db.session.add(user)
        db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        'code': 0,
        'data': {
            'token': token,
            'user': user.to_dict(),
        }
    })


@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user profile."""
    user = User.query.get(request.user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404
    return jsonify({'code': 0, 'data': user.to_dict()})


@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update user profile."""
    user = User.query.get(request.user_id)
    if not user:
        return jsonify({'code': 404, 'msg': '用户不存在'}), 404

    data = request.get_json()
    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    if 'phone' in data:
        user.phone = data['phone']
    if 'gender' in data:
        user.gender = data['gender']
    if 'fitness_tags' in data:
        user.fitness_tags = ','.join(data['fitness_tags']) if isinstance(data['fitness_tags'], list) else data['fitness_tags']

    db.session.commit()
    return jsonify({'code': 0, 'data': user.to_dict()})
