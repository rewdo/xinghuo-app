# 星火 APP — MVP 产品需求与架构设计

> 版本: v0.1（MVP 骨架）
> 前端: Uniapp（微信小程序优先，后续打包APP）
> 后端: Python Flask + MySQL
> 域名: xinghuo.tongshengwangluo.com
> 设计原则: 先跑通全链路，再优化细节

---

## 一、MVP 功能范围

### 必须做（核心闭环，缺一不可）

```
用户注册登录 → 浏览任务 → 接受任务 → 执行任务 → 完成确认 → 获得收益 → 提现
                                                                        └→ 评价系统
```

| 模块 | 功能 | 说明 |
|------|------|------|
| **用户系统** | 微信授权一键登录 | 无需注册填表，降低门槛 |
| | 用户基本信息 | 头像、昵称、手机号、体能标签 |
| **任务系统** | 附近任务列表 | LBS 定位，按距离排序 |
| | 任务详情 | 描述、酬金、距离、B端信息 |
| | 接受/放弃任务 | 简单的状态切换 |
| | 任务完成确认 | B端扫码/输入验证码确认 |
| **结算系统** | 收益钱包 | 可查看总收益、待结算、已到账 |
| | 提现功能 | 微信零钱提现 |
| | 交易记录 | 每条任务的收益记录 |
| **B端管理台** | 发布任务 | 填写任务信息+酬金+位置 |
| | 确认完成 | 扫码或手动确认 |
| | 账户充值 | 先充值后发布 |
| **评价系统** | 五星评价 | 互评（B端评C端） |
| | 评价展示 | 用户主页展示历史评价 |

### 暂时不做（MVP之后迭代）

| 功能 | 理由 |
|------|------|
| 训练计划匹配算法 | MVP先手动浏览，后续AI匹配 |
| 游戏化等级/成就系统 | 第二批迭代，先跑通商业模式 |
| 权益/碳积分结算 | 只做现金结算，其他后面加 |
| 组队任务/团队模式 | 用户量起来后再做 |
| 英雄榜/排行榜 | 第二批迭代 |

---

## 二、数据库核心表设计

```sql
-- =============================================
-- 用户表（users）
-- =============================================
CREATE TABLE users (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  openid          VARCHAR(64) NOT NULL UNIQUE,     -- 微信openid
  nickname        VARCHAR(64),
  avatar_url      VARCHAR(256),
  phone           VARCHAR(20),
  gender          TINYINT DEFAULT 0,               -- 0未知 1男 2女
  fitness_tags    VARCHAR(256),                    -- "跑步,爬楼,搬运" 逗号分隔
  credit_score    INT DEFAULT 100,                 -- 信用分
  total_earnings  DECIMAL(10,2) DEFAULT 0.00,      -- 累计收益
  balance         DECIMAL(10,2) DEFAULT 0.00,      -- 当前余额
  level           INT DEFAULT 1,                   -- 等级
  status          TINYINT DEFAULT 1,               -- 1正常 0冻结
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_openid (openid),
  INDEX idx_location (lat, lng)                    -- 后续用GIS扩展
);

-- =============================================
-- B端商户表（merchants）
-- =============================================
CREATE TABLE merchants (
  id                INT PRIMARY KEY AUTO_INCREMENT,
  company_name      VARCHAR(128) NOT NULL,
  contact_name      VARCHAR(32),
  contact_phone     VARCHAR(20),
  address           VARCHAR(256),
  lat               DECIMAL(10,7),
  lng               DECIMAL(10,7),
  business_license  VARCHAR(256),                  -- 营业执照图片URL
  balance           DECIMAL(10,2) DEFAULT 0.00,    -- 账户余额
  status            TINYINT DEFAULT 0,             -- 0待审核 1正常 2冻结
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- =============================================
-- 任务表（tasks）
-- =============================================
CREATE TABLE tasks (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  merchant_id     INT NOT NULL,                    -- B端ID
  title           VARCHAR(128) NOT NULL,           -- 任务标题
  description     TEXT,                            -- 任务描述
  task_type       TINYINT NOT NULL,                -- 1配送 2搬运 3巡检 4其他
  reward_type     TINYINT DEFAULT 1,               -- 1现金 2权益 3积分
  reward_amount   DECIMAL(10,2) DEFAULT 0.00,      -- 酬金（现金时为金额）
  quantity        INT DEFAULT 1,                   -- 需要人数
  accepted_count  INT DEFAULT 0,                   -- 已接单人数
  status          TINYINT DEFAULT 0,               -- 0待接受 1进行中 2已完成 3已取消
  address         VARCHAR(256),
  lat             DECIMAL(10,7),
  lng             DECIMAL(10,7),
  difficulty      TINYINT DEFAULT 1,               -- 1轻松 2适中 3挑战
  estimated_min   INT DEFAULT 15,                  -- 预计耗时(分钟)
  expired_at      DATETIME,                        -- 过期时间
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_status (status),
  INDEX idx_location (lat, lng),
  INDEX idx_merchant (merchant_id),
  INDEX idx_type (task_type)
);

-- =============================================
-- 任务接单表（task_orders）
-- =============================================
CREATE TABLE task_orders (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  task_id         INT NOT NULL,
  user_id         INT NOT NULL,
  status          TINYINT DEFAULT 0,               -- 0已接单 1执行中 2待确认 3已完成 4取消
  accepted_at     DATETIME,                        -- 接单时间
  completed_at    DATETIME,                        -- 完成时间
  merchant_note   VARCHAR(256),                    -- B端备注
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_task_user (task_id, user_id),
  INDEX idx_user (user_id),
  INDEX idx_status (status)
);

-- =============================================
-- 评价表（reviews）
-- =============================================
CREATE TABLE reviews (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  order_id        INT NOT NULL UNIQUE,
  rating          TINYINT NOT NULL,                -- 1-5星
  comment         VARCHAR(512),
  reviewer_type   TINYINT,                         -- 1B端评C端 2C端评B端
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- 交易记录表（transactions）
-- =============================================
CREATE TABLE transactions (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  user_id         INT,
  merchant_id     INT,
  order_id        INT,
  type            TINYINT,                         -- 1任务收入 2提现 3充值 4平台佣金
  amount          DECIMAL(10,2) NOT NULL,
  balance_before  DECIMAL(10,2),
  balance_after   DECIMAL(10,2),
  status          TINYINT DEFAULT 0,               -- 0处理中 1成功 2失败
  remark          VARCHAR(256),
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_merchant (merchant_id)
);
```

---

## 三、API 接口设计（核心）

### C端接口

```
POST  /api/v1/user/wxlogin          -- 微信登录（接收code，返回token）
GET   /api/v1/user/profile           -- 获取用户信息
PUT   /api/v1/user/profile           -- 更新用户信息（体能标签等）

GET   /api/v1/tasks/nearby          -- 附近任务列表（lat,lng,radius）
GET   /api/v1/tasks/:id              -- 任务详情
POST  /api/v1/tasks/:id/accept       -- 接单
POST  /api/v1/tasks/:id/cancel       -- 取消接单
POST  /api/v1/tasks/:id/complete     -- 用户端点"已完成"

GET   /api/v1/orders                 -- 我的任务列表（进行中/已完成）
GET   /api/v1/orders/:id             -- 订单详情

GET   /api/v1/wallet/balance         -- 钱包余额
GET   /api/v1/wallet/transactions    -- 交易记录
POST  /api/v1/wallet/withdraw        -- 提现到微信零钱

POST  /api/v1/reviews                -- 提交评价
```

### B端接口

```
POST  /api/v1/merchant/login        -- 商户登录（账号密码/扫码）
POST  /api/v1/merchant/register     -- 商户注册（上传营业执照）

POST  /api/v1/tasks/create          -- 发布任务
PUT   /api/v1/tasks/:id              -- 修改任务
PUT   /api/v1/tasks/:id/close       -- 关闭任务（停止接单）
GET   /api/v1/tasks/manage          -- 我的任务列表（含进行中数据）

POST  /api/v1/tasks/:id/confirm     -- 确认完成（扫码/手动）

GET   /api/v1/merchant/wallet/balance      -- 商户余额
POST  /api/v1/merchant/wallet/recharge     -- 充值
GET   /api/v1/merchant/wallet/transactions -- 交易记录
```

---

## 四、技术架构

```
┌─────────────────────────────────────────┐
│           微信小程序（Uniapp）            │
│           iOS/Android (Uniapp打包)        │
└────────────────┬────────────────────────┘
                 │ HTTPS
                 ▼
┌─────────────────────────────────────────┐
│         Nginx（反向代理 + SSL）           │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     Flask REST API + Redis 缓存          │
│     - 用户认证（JWT Token）              │
│     - 任务管理 CRUD                     │
│     - 支付/提现（微信支付V3）            │
│     - LBS 距离计算                      │
└────────────────┬────────────────────────┘
                 │
          ┌──────┴──────┐
          ▼              ▼
┌─────────────────┐ ┌─────────────────┐
│   MySQL 8.0     │ │   Redis 7.x     │
│   核心数据库    │ │   会话/缓存/队列 │
└─────────────────┘ └─────────────────┘
```

### 关键设计决策

1. **为什么先做小程序不做APP？**
   - 微信生态内0安装成本，裂变分享方便
   - 微信支付直接对接，无需额外钱包
   - 用户认证简单（openid登录）
   - Uniapp 打包后直接转APP，不重写

2. **为什么用 Flask + Redis？**
   - 你熟悉 Python Flask，上手快
   - Redis 做任务队列（接单并发控制）
   - Redis 做 LBS 临近任务缓存（Geo模块）

3. **提现方案**
   - 企业付款到微信零钱（微信支付API）
   - 需开通「商家转账到零钱」功能
   - 单笔限额2000元，日限额10万（初始）

---

## 五、支付与分账设计

```
用户完成订单
    │
    ▼
B端确认完成
    │
    ├──→ 平台账户：扣除任务金额（进入平台账户）
    │
    ├──→ 平台佣金：任务金额 × 10%（平台收入）
    │
    └──→ 用户收益：任务金额 × 90%（进入用户钱包）
            │
            ▼
        用户发起提现
            │
            ▼
    企业付款到微信零钱
```

### 微信支付关键参数
- 商户号：需申请微信支付商户号（企业资质）
- 费率：微信支付0.6%（不可免）
- 分账：可以用微信支付分账功能自动分账
- 提现：企业付款到零钱接口，费率0.1%

---

## 六、MVP 开发顺序（6周）

```
第1-2周（搭建骨架）:
  ├── 项目初始化（Uniapp + Flask + MySQL）
  ├── 用户注册/登录（微信授权）
  ├── 附近任务列表页（LBS基础）
  └── 任务详情页

第3-4周（核心功能）:
  ├── 接单/完单流程
  ├── B端管理台（发布任务+确认完成）
  ├── 账户充值/结算
  └── 评价系统

第5-6周（收尾+支付）:
  ├── 微信支付对接
  ├── 提现功能
  ├── UI打磨
  ├── 小程序提审
  └── 上线
```

---

## 七、待办（需要你确认或提供的）

| # | 事项 | 备注 |
|---|------|------|
| 1 | 统一社会信用代码 | 软著材料需要 |
| 2 | 微信小程序AppID | 去微信公众平台注册后给我 |
| 3 | 微信支付商户号 | 申请后配置 |
| 4 | 服务器环境 | 用哪台服务器？现有还是新购？ |
| 5 | 地图服务商 | 高德还是腾讯地图？（LBS模块要用） |
