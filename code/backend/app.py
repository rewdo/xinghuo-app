"""
零星共成APP - Flask API 后端 v0.2
数据库密码通过环境变量读取，不硬编码
"""
from flask import Flask, jsonify, request, render_template_string, session, redirect
from werkzeug.security import check_password_hash
from flask_cors import CORS
import pymysql
import hashlib
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Flask session 密钥（从环境变量读取）
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# ===== 数据库连接（从环境变量读取，不留明文）=====
DB_PASSWORD = os.environ.get('XINGHUO_DB_PASSWORD', '')  # 生产环境由 .env 提供

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

# ===== 安全防护 =====
# 所有 SQL 查询均使用参数化查询 (%%s 占位符)，杜绝 SQL 注入
# 配置值输出时转义 HTML，杜绝 XSS
import html as html_module

def require_admin():
    """检查管理员登录状态，未登录返回 False"""
    return session.get('admin_logged_in') and session.get('admin_user')

def sanitize(val):
    """XSS 防护：转义 HTML 特殊字符"""
    if val is None:
        return ''
    return html_module.escape(str(val))

# ===== 管理员登录/登出 =====

@app.route('/api/v1/admin/login', methods=['POST'])
def admin_login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({"code": 1, "msg": "用户名和密码不能为空"})
    
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user and check_password_hash(user['password_hash'], password):
                session['admin_logged_in'] = True
                session['admin_user'] = username
                session.permanent = True
                # 更新最后登录时间
                cur.execute("UPDATE admin_users SET last_login=NOW() WHERE id=%s", (user['id'],))
                db.commit()
                return jsonify({"code": 0, "msg": "ok", "data": {"username": username}})
        return jsonify({"code": 1, "msg": "用户名或密码错误"})
    finally:
        db.close()

@app.route('/api/v1/admin/logout', methods=['POST'])
def admin_logout():
    session.clear()
    return jsonify({"code": 0, "msg": "已退出"})

@app.route('/api/v1/admin/check')
def admin_check():
    if require_admin():
        return jsonify({"code": 0, "data": {"username": session.get('admin_user')}})
    return jsonify({"code": 401, "msg": "未登录"})

# ===== 配置管理 API（需登录） =====

@app.route('/api/v1/admin/config')
def admin_config_list():
    if not require_admin():
        return jsonify({"code": 401, "msg": "请先登录"})
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM system_config ORDER BY config_key")
            rows = cur.fetchall()
        return jsonify({"code": 0, "data": rows})
    finally:
        db.close()

@app.route('/api/v1/admin/config/<key>', methods=['PUT'])
def admin_config_update(key):
    if not require_admin():
        return jsonify({"code": 401, "msg": "请先登录"})
    # 校验 key 格式（仅允许字母数字下划线，杜绝注入）
    import re
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
        return jsonify({"code": 1, "msg": "参数名格式错误"})
    data = request.json or {}
    value = data.get('value', '')
    # XSS 防护：转义 value（配置值不会包含 HTML）
    safe_value = sanitize(str(value)[:500])  # 限制长度
    db = get_db()
    try:
        with db.cursor() as cur:
            # 参数化查询防止 SQL 注入
            cur.execute("UPDATE system_config SET config_value=%s WHERE config_key=%s", (safe_value, key))
            db.commit()
            if cur.rowcount == 0:
                return jsonify({"code": 1, "msg": "配置项不存在"})
        return jsonify({"code": 0, "msg": "ok"})
    finally:
        db.close()

# ===== 后台管理页面（带登录校验） =====

LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>零星共成 后台登录</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.login-box { background: #fff; border-radius: 16px; padding: 40px; width: 360px; box-shadow: 0 20px 60px rgba(0,0,0,0.15); }
.logo { text-align: center; font-size: 28px; font-weight: bold; color: #333; margin-bottom: 8px; }
.subtitle { text-align: center; font-size: 14px; color: #999; margin-bottom: 30px; }
.input-group { margin-bottom: 20px; }
.input-group label { display: block; font-size: 14px; color: #666; margin-bottom: 6px; }
.input-group input { width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 15px; transition: border-color 0.2s; }
.input-group input:focus { outline: none; border-color: #667eea; }
.login-btn { width: 100%; padding: 12px; background: linear-gradient(135deg, #667eea, #764ba2); color: #fff; border: none; border-radius: 8px; font-size: 16px; cursor: pointer; transition: opacity 0.2s; }
.login-btn:hover { opacity: 0.9; }
.error { color: #f44336; font-size: 13px; text-align: center; margin-top: 12px; display: none; }
</style>
</head>
<body>
<div class="login-box">
  <div class="logo">&#9881; 零星共成后台</div>
  <div class="subtitle">管理系统</div>
  <div class="input-group">
    <label>用户名</label>
    <input type="text" id="username" placeholder="请输入用户名" autocomplete="username" />
  </div>
  <div class="input-group">
    <label>密码</label>
    <input type="password" id="password" placeholder="请输入密码" autocomplete="current-password" onkeydown="if(event.key==='Enter')login()" />
  </div>
  <button class="login-btn" onclick="login()">登 录</button>
  <div class="error" id="error"></div>
</div>
<script>
async function login() {
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value;
  if (!username || !password) {
    document.getElementById("error").textContent = "请输入用户名和密码";
    document.getElementById("error").style.display = "block";
    return;
  }
  const res = await fetch("/api/v1/admin/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username, password}),
    credentials: "same-origin"
  });
  const data = await res.json();
  if (data.code === 0) {
    window.location.href = "/admin";
  } else {
    document.getElementById("error").textContent = data.msg || "登录失败";
    document.getElementById("error").style.display = "block";
  }
}
</script>
</body>
</html>'''

ADMIN_HTML = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>零星共成 后台管理</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, sans-serif; background: #f5f5f5; padding: 20px; }
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
h1 { font-size: 24px; color: #333; }
.logout-btn { font-size: 14px; color: #999; cursor: pointer; padding: 8px 16px; border-radius: 8px; border: 1px solid #ddd; background: #fff; }
.logout-btn:hover { color: #f44336; border-color: #f44336; }
.card { background: #fff; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.card-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 16px; }
.row { display: flex; align-items: center; padding: 12px 0; border-bottom: 1px solid #f0f0f0; }
.row:last-child { border-bottom: none; }
.key { width: 160px; font-size: 14px; color: #666; }
.val { flex: 1; }
.val input { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; }
.val input:focus { outline: none; border-color: #ff6b35; }
.desc { font-size: 12px; color: #999; margin-top: 4px; }
.save-btn { background: #ff6b35; color: #fff; border: none; padding: 8px 24px; border-radius: 8px; font-size: 14px; cursor: pointer; }
.save-btn:hover { background: #e55a2b; }
.toast { position: fixed; top: 20px; right: 20px; background: #4caf50; color: #fff; padding: 12px 24px; border-radius: 8px; font-size: 14px; display: none; z-index: 999; }
</style>
</head>
<body>
<div class="header">
  <h1>&#9881; 零星共成 后台管理</h1>
  <button class="logout-btn" onclick="logout()">退出登录</button>
</div>
<div id="app"></div>
<div class="toast" id="toast">保存成功</div>
<script>
const API = "";
let configs = [];

async function checkLogin() {
  const res = await fetch(API + "/api/v1/admin/check", {credentials: "same-origin"});
  const data = await res.json();
  if (data.code === 401) {
    window.location.href = "/admin/login";
    return false;
  }
  return true;
}

async function loadConfig() {
  const res = await fetch(API + "/api/v1/admin/config", {credentials: "same-origin"});
  const data = await res.json();
  if (data.code === 0) {
    configs = data.data;
    render();
  } else if (data.code === 401) {
    window.location.href = "/admin/login";
  }
}

function render() {
  const groups = [
    { title: "★ 积分设置", keys: ["points_base","points_bonus_first","points_bonus_streak","points_bonus_review","points_bonus_plan"] },
    { title: "💰 佣金设置", keys: ["commission_rate","min_withdraw","max_daily_tasks"] },
    { title: "📱 应用设置", keys: ["app_name","app_version"] }
  ];
  let html = "";
  for (const g of groups) {
    html += `<div class="card"><div class="card-title">${g.title}</div>`;
    for (const key of g.keys) {
      const cfg = configs.find(c => c.config_key === key);
      if (!cfg) continue;
      html += `<div class="row"><div class="key">${key}</div><div class="val"><input id="input-${key}" value="${cfg.config_value}" /><div class="desc">${cfg.description || ""}</div></div></div>`;
    }
    html += `</div>`;
  }
  html += `<div style="text-align:center;padding:10px"><button class="save-btn" onclick="saveAll()">保存全部</button></div>`;
  document.getElementById("app").innerHTML = html;
}

async function saveAll() {
  for (const cfg of configs) {
    const input = document.getElementById("input-" + cfg.config_key);
    if (input && input.value !== cfg.config_value) {
      const res = await fetch(API + "/api/v1/admin/config/" + cfg.config_key, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ value: input.value }),
        credentials: "same-origin"
      });
      const data = await res.json();
      if (data.code === 0) {
        cfg.config_value = input.value;
      } else if (data.code === 401) {
        window.location.href = "/admin/login";
      }
    }
  }
  const toast = document.getElementById("toast");
  toast.style.display = "block";
  setTimeout(() => { toast.style.display = "none"; }, 2000);
}

async function logout() {
  await fetch(API + "/api/v1/admin/logout", {method: "POST", credentials: "same-origin"});
  window.location.href = "/admin/login";
}

checkLogin().then(ok => { if (ok) loadConfig(); });
</script>
</body>
</html>'''

@app.route('/admin/login')
def admin_login_page():
    # 如果已登录，直接跳转到管理页
    if require_admin():
        return redirect('/admin')
    return render_template_string(LOGIN_PAGE)

@app.route('/admin')
def admin_dashboard():
    if not require_admin():
        return redirect('/admin/login')
    return render_template_string(ADMIN_HTML)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
