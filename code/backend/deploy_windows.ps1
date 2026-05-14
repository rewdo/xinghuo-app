# 星火 APP 后端部署脚本
# 适用环境: Ubuntu 22.04+ / CentOS 7+ / Windows Server
# Python 3.8+

Write-Host "========================================="
Write-Host "  星火 APP 后端部署向导"
Write-Host "========================================="
Write-Host ""

# ==== 环境检测 ====
Write-Host "[1/5] 检测运行环境..."
$pythonVer = python --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 未安装 Python，请先安装 Python 3.8+"
    exit 1
}
Write-Host "✅ $pythonVer"

# ==== 安装依赖 ====
Write-Host "[2/5] 安装 Python 依赖..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 依赖安装失败"
    exit 1
}
Write-Host "✅ 依赖安装完成"

# ==== 配置检测 ====
Write-Host "[3/5] 检查配置文件..."
if (-not (Test-Path ".env")) {
    Write-Host "⚠️ .env 文件不存在，从 .env.example 复制"
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️ 请编辑 .env 填写真实配置"
}
Write-Host "✅ 配置文件就绪"

# ==== 数据库初始化 ====
Write-Host "[4/5] 数据库初始化..."
if (Test-Path "init_db.sql") {
    $envConfig = Get-Content ".env" | Where-Object { $_ -match "DB_" }
    Write-Host "   数据库配置如下："
    $envConfig | ForEach-Object { Write-Host "   $($_ -replace '=',' = ')" }
    Write-Host ""
    Write-Host "   请手动执行：mysql -u root -p < init_db.sql"
    Write-Host "   或登录 MySQL 后运行：source init_db.sql"
}
Write-Host "✅ 数据库脚本已就绪"

# ==== 启动服务 ====
Write-Host "[5/5] 启动服务..."
$flaskEnv = (Get-Content ".env" | Where-Object { $_ -match "^FLASK_ENV" }) -replace "FLASK_ENV=", ""
if ($flaskEnv -eq "development") {
    Write-Host "   开发模式：python app.py"
    Write-Host "   http://localhost:5000"
} else {
    Write-Host "   生产模式建议使用 gunicorn:"
    Write-Host "   gunicorn -w 4 -b 0.0.0.0:5000 app:app"
}
Write-Host ""

# ==== 完成 ====
Write-Host "========================================="
Write-Host "  部署完成!"
Write-Host "  测试接口: curl http://localhost:5000/api/health"
Write-Host "========================================="
