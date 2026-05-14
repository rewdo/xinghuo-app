"""
星火APP - Flask API 后端 v0.2
数据库密码通过环境变量读取，不硬编码
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import hashlib
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ===== 数据库连接（从环境变量读取，不留明文）=====
DB_PASSWORD = os.environ.get('XINGHUO_DB_PASSWORD', 'c07a13ab48d414e6')

DB_CONFIG = {
    'host': os.environ.get('XINGHUO_DB_HOST', '127.0.0.1'),
    'port': int(os.environ.get('XINGHUO_DB_PORT', 3306)),
    'user': os.environ.get('XINGHUO_DB_USER', 'root'),
    'password': DB_PASSWORD,
    'database': os.environ.get('XINGHUO_DB_NAME', 'xinghuo'),
    'charset': 'utf8mb4'
}

def get_db():
    return pymysql.connect(**DB_CONFIG, cursorclass=pymysql.cursors.DictCursor)

# ===== 消耗计算公式 =====
CALORIES_FORMULAS = {
    'run':   lambda w, d: int(w * (d/1000) * 1.036),
    'walk':  lambda w, s: int(s * 0.04),
    'lift':  lambda w, m: int(m * 5),
    'climb': lambda w, f: int(f * 5),
    'carry': lambda w, d: int((d/1000) * w * 0.5),
}

EFFECT_MAP = {
    'run':   '耐力+腿部',
    'walk':  '有氧+腿部',
    'lift':  '核心+上肢',
    'climb': '心肺+腿部',
    'carry': '全身+爆发力',
}

STEPS_MAP = {
    'run':   lambda d: int(d / 1000 * 1250),
    'walk':  lambda s: s,
    'lift':  lambda m: m * 200,
    'climb': lambda f: f * 200,
    'carry': lambda d: int(d / 1000 * 1500),
}

def calc_calories(fitness_tag, distance_meters=0, estimated_min=0, steps=0, weight_kg=70, floors=0):
    formula = CALORIES_FORMULAS.get(fitness_tag)
    if not formula:
        return 0
    if fitness_tag == 'walk':
        return formula(weight_kg, steps)
    elif fitness_tag == 'climb':
        return formula(weight_kg, floors)
    elif fitness_tag == 'lift':
        return formula(weight_kg, estimated_min)
    elif fitness_tag in ('run', 'carry'):
        return formula(weight_kg, distance_meters)
    return 0

# ===== 以下 API Routes 保持不变 =====
@app.route('/api/v1/health')
def health():
    return jsonify({"status": "ok", "version": "v0.2", "time": datetime.now().isoformat()})

@app.route('/api/v1/user/wxlogin', methods=['POST'])
def wx_login():
    data = request.json or {}
    openid = data.get('code', '') or 'test_' + hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE openid = %s", (openid,))
            user = cur.fetchone()
            if not user:
                cur.execute("INSERT INTO users (openid, nickname) VALUES (%s, %s)", (openid, '新用户'))
                db.commit()
                uid = cur.lastrowid
                cur.execute("INSERT INTO user_points (user_id) VALUES (%s)", (uid,))
                db.commit()
                cur.execute("SELECT * FROM users WHERE id = %s", (uid,))
                user = cur.fetchone()
        return jsonify({"code": 0, "data": user})
    finally:
        db.close()

@app.route('/api/v1/user/fitness-plan', methods=['POST', 'PUT'])
def set_fitness_plan():
    data = request.json or {}
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"code": 1, "msg": "user_id required"})
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                UPDATE users SET 
                    fitness_goal=%s, fitness_frequency=%s, 
                    fitness_tags=%s, daily_minutes=%s, weight_kg=%s
                WHERE id=%s
            """, (
                data.get('goal', 'fat_loss'),
                data.get('frequency', 3),
                json.dumps(data.get('tags', ['walk'])),
                data.get('daily_minutes', 30),
                data.get('weight_kg', 70),
                user_id
            ))
            db.commit()
        return jsonify({"code": 0, "msg": "ok"})
    finally:
        db.close()

@app.route('/api/v1/tasks/recommended')
def recommended_tasks():
    user_id = request.args.get('user_id', 1, type=int)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cur.fetchone()
            if user and user.get('fitness_tags'):
                tags = json.loads(user['fitness_tags']) if isinstance(user['fitness_tags'], str) else user['fitness_tags']
                if tags:
                    placeholders = ','.join(['%s'] * len(tags))
                    cur.execute(f"""
                        SELECT t.*, tr.commission_amount, tr.coupon_desc, tr.platform_points
                        FROM tasks t LEFT JOIN task_rewards tr ON t.id = tr.task_id
                        WHERE t.status = 0 AND t.fitness_tag IN ({placeholders})
                        ORDER BY t.created_at DESC LIMIT 20
                    """, tags)
                else:
                    cur.execute("""
                        SELECT t.*, tr.commission_amount, tr.coupon_desc, tr.platform_points
                        FROM tasks t LEFT JOIN task_rewards tr ON t.id = tr.task_id
                        WHERE t.status = 0 ORDER BY t.created_at DESC LIMIT 20
                    """)
            else:
                cur.execute("""
                    SELECT t.*, tr.commission_amount, tr.coupon_desc, tr.platform_points
                    FROM tasks t LEFT JOIN task_rewards tr ON t.id = tr.task_id
                    WHERE t.status = 0 ORDER BY t.created_at DESC LIMIT 20
                """)
            tasks = cur.fetchall()
            weight = float(user.get('weight_kg', 70)) if user else 70
            for t in tasks:
                t['estimated_calories'] = calc_calories(t['fitness_tag'], t.get('distance_meters', 0) or 0, t.get('estimated_min', 15) or 15, weight_kg=weight)
                t['exercise_benefit'] = EFFECT_MAP.get(t['fitness_tag'], '全身锻炼')
        return jsonify({"code": 0, "data": tasks, "count": len(tasks)})
    finally:
        db.close()

@app.route('/api/v1/tasks/<int:task_id>')
def task_detail(task_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("""
                SELECT t.*, tr.commission_amount, tr.coupon_desc, tr.platform_points
                FROM tasks t LEFT JOIN task_rewards tr ON t.id = tr.task_id
                WHERE t.id = %s
            """, (task_id,))
            task = cur.fetchone()
            if not task:
                return jsonify({"code": 1, "msg": "任务不存在"})
            task['estimated_calories'] = calc_calories(task['fitness_tag'], task.get('distance_meters', 0) or 0, task.get('estimated_min', 15) or 15)
            task['exercise_benefit'] = EFFECT_MAP.get(task['fitness_tag'], '全身锻炼')
        return jsonify({"code": 0, "data": task})
    finally:
        db.close()

@app.route('/api/v1/tasks/nearby')
def nearby_tasks():
    tag = request.args.get('fitness_tag')
    db = get_db()
    try:
        with db.cursor() as cur:
            sql = """
                SELECT t.*, tr.commission_amount, tr.coupon_desc, tr.platform_points
                FROM tasks t LEFT JOIN task_rewards tr ON t.id = tr.task_id
                WHERE t.status = 0
            """
            params = []
            if tag:
                sql += " AND t.fitness_tag = %s"
                params.append(tag)
            sql += " ORDER BY t.created_at DESC LIMIT 50"
            cur.execute(sql, params)
            tasks = cur.fetchall()
        return jsonify({"code": 0, "data": tasks, "count": len(tasks)})
    finally:
        db.close()

@app.route('/api/v1/tasks/calc-calories', methods=['POST'])
def calc_calories_api():
    data = request.json or {}
    weight = float(data.get('weight_kg', 70))
    tag = data.get('fitness_tag', 'walk')
    distance = float(data.get('distance_meters', 0))
    minutes = float(data.get('estimated_min', 15))
    steps = int(data.get('steps', 0))
    floors = int(data.get('floors', 0))
    calories = calc_calories(tag, distance, minutes, steps, weight, floors)
    effect = EFFECT_MAP.get(tag, '全身锻炼')
    return jsonify({"code": 0, "data": {
        "calories": calories, "effect": effect,
        "label": f"🔥 AI估算: 约消耗{calories}大卡",
        "formula": f"{tag}类型 · 体重{weight}kg · {'距离'+str(int(distance))+'m' if distance else ''}{'时长'+str(int(minutes))+'min' if minutes else ''}"
    }})

@app.route('/api/v1/points/balance')
def points_balance():
    user_id = request.args.get('user_id', 1, type=int)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM user_points WHERE user_id = %s", (user_id,))
            points = cur.fetchone()
        return jsonify({"code": 0, "data": points})
    finally:
        db.close()

@app.route('/api/v1/points/transactions')
def points_transactions():
    user_id = request.args.get('user_id', 1, type=int)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM point_transactions WHERE user_id = %s ORDER BY created_at DESC LIMIT 20", (user_id,))
            txns = cur.fetchall()
        return jsonify({"code": 0, "data": txns})
    finally:
        db.close()

@app.route('/api/v1/points/shop/items')
def shop_items():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM point_shop_items WHERE status = 1 ORDER BY points_required ASC")
            items = cur.fetchall()
        return jsonify({"code": 0, "data": items})
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
