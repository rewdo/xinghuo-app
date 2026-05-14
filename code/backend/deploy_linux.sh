#!/bin/bash
# 星火 APP 后端部署脚本（Linux）
# Ubuntu 22.04+ / CentOS 7+

set -e

echo "========================================="
echo "  星火 APP 后端部署向导"
echo "========================================="
echo ""

# 环境检测
echo "[1/5] 检测运行环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未安装 Python3，请先安装: apt install python3 python3-pip"
    exit 1
fi
echo "✅ $(python3 --version)"

# 创建虚拟环境
echo "[2/5] 创建虚拟环境..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 安装依赖
echo "[3/5] 安装 Python 依赖..."
pip install -r requirements.txt
echo "✅ 依赖安装完成"

# 配置检测
echo "[4/5] 检查配置文件..."
if [ ! -f ".env" ]; then
    echo "⚠️  .env 不存在，从 .env.example 复制"
    cp .env.example .env
    echo "⚠️  请编辑 .env 填写真实配置"
fi
echo "✅ 配置文件就绪"

# 数据库初始化
echo "[5/5] 初始化数据库..."
if [ -f "init_db.sql" ]; then
    echo "   请手动执行: mysql -u root -p < init_db.sql"
fi

# 启动
echo ""
echo "========================================="
echo "  部署完成!"
echo ""
echo "  开发模式启动:"
echo "    python app.py"
echo "    http://localhost:5000"
echo ""
echo "  生产模式启动:"
echo "    gunicorn -w 4 -b 0.0.0.0:5000 app:app"
echo ""
echo "  测试接口:"
echo "    curl http://localhost:5000/api/health"
echo "========================================="
