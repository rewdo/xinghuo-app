-- 星火 APP 数据库初始化脚本
-- 运行: mysql -u root -p < init_db.sql

CREATE DATABASE IF NOT EXISTS xinghuo DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE xinghuo;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  openid          VARCHAR(64) NOT NULL UNIQUE,
  nickname        VARCHAR(64),
  avatar_url      VARCHAR(256),
  phone           VARCHAR(20),
  gender          TINYINT DEFAULT 0 COMMENT '0未知 1男 2女',
  fitness_tags    VARCHAR(256) COMMENT '"跑步,爬楼,搬运"',
  credit_score    INT DEFAULT 100,
  total_earnings  DECIMAL(10,2) DEFAULT 0.00,
  balance         DECIMAL(10,2) DEFAULT 0.00,
  level           INT DEFAULT 1,
  status          TINYINT DEFAULT 1 COMMENT '1正常 0冻结',
  lat             DECIMAL(10,7),
  lng             DECIMAL(10,7),
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_openid (openid),
  INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 商户表
CREATE TABLE IF NOT EXISTS merchants (
  id                INT PRIMARY KEY AUTO_INCREMENT,
  company_name      VARCHAR(128) NOT NULL,
  contact_name      VARCHAR(32),
  contact_phone     VARCHAR(20),
  address           VARCHAR(256),
  lat               DECIMAL(10,7),
  lng               DECIMAL(10,7),
  business_license  VARCHAR(256),
  balance           DECIMAL(10,2) DEFAULT 0.00,
  password_hash     VARCHAR(256),
  status            TINYINT DEFAULT 0 COMMENT '0待审核 1正常 2冻结',
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 任务表
CREATE TABLE IF NOT EXISTS tasks (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  merchant_id     INT NOT NULL,
  title           VARCHAR(128) NOT NULL,
  description     TEXT,
  task_type       TINYINT NOT NULL COMMENT '1配送 2搬运 3巡检 4其他',
  reward_type     TINYINT DEFAULT 1 COMMENT '1现金 2权益 3积分',
  reward_amount   DECIMAL(10,2) DEFAULT 0.00,
  quantity        INT DEFAULT 1,
  accepted_count  INT DEFAULT 0,
  status          TINYINT DEFAULT 0 COMMENT '0待接受 1进行中 2已完成 3已取消',
  address         VARCHAR(256),
  lat             DECIMAL(10,7),
  lng             DECIMAL(10,7),
  difficulty      TINYINT DEFAULT 1 COMMENT '1轻松 2适中 3挑战',
  estimated_min   INT DEFAULT 15,
  expired_at      DATETIME,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_merchant (merchant_id),
  INDEX idx_status (status),
  INDEX idx_type (task_type),
  FOREIGN KEY (merchant_id) REFERENCES merchants(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 订单表
CREATE TABLE IF NOT EXISTS task_orders (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  task_id         INT NOT NULL,
  user_id         INT NOT NULL,
  status          TINYINT DEFAULT 0 COMMENT '0已接单 1执行中 2待确认 3已完成 4已取消',
  accepted_at     DATETIME,
  completed_at    DATETIME,
  merchant_note   VARCHAR(256),
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uk_task_user (task_id, user_id),
  INDEX idx_user (user_id),
  INDEX idx_status (status),
  FOREIGN KEY (task_id) REFERENCES tasks(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 评价表
CREATE TABLE IF NOT EXISTS reviews (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  order_id        INT NOT NULL UNIQUE,
  rating          TINYINT NOT NULL COMMENT '1-5星',
  comment         VARCHAR(512),
  reviewer_type   TINYINT COMMENT '1B端评C端 2C端评B端',
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (order_id) REFERENCES task_orders(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 交易记录表
CREATE TABLE IF NOT EXISTS transactions (
  id                INT PRIMARY KEY AUTO_INCREMENT,
  user_id           INT,
  merchant_id       INT,
  order_id          INT,
  transaction_type  TINYINT COMMENT '1任务收入 2提现 3充值 4平台佣金',
  amount            DECIMAL(10,2) NOT NULL,
  balance_before    DECIMAL(10,2),
  balance_after     DECIMAL(10,2),
  status            TINYINT DEFAULT 0 COMMENT '0处理中 1成功 2失败',
  remark            VARCHAR(256),
  created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_user (user_id),
  INDEX idx_merchant (merchant_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (merchant_id) REFERENCES merchants(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入测试数据
INSERT INTO merchants (id, company_name, contact_name, contact_phone, address, balance, status)
VALUES
(1, '兴隆超市（盼盼路店）', '王老板', '13800001111', '营口市站前区盼盼路88号', 500.00, 1),
(2, '鑫鑫水果店（东升路）', '李老板', '13800002222', '营口市站前区东升路22号', 300.00, 1),
(3, '顺丰便利店', '张老板', '13800003333', '营口市西市区新兴大街56号', 200.00, 1);

INSERT INTO tasks (merchant_id, title, description, task_type, reward_amount, quantity, address, lat, lng, difficulty, estimated_min)
VALUES
(1, '送5份盒饭到2栋', '从兴隆超市送5份盒饭到附近小区2栋3单元502', 1, 8.00, 1, '营口市站前区盼盼路88号→兴隆家园2栋3单元', 40.6850, 122.2650, 1, 20),
(1, '仓库货物整理', '把仓库30箱饮料搬到货架上，按日期排列', 2, 25.00, 2, '兴隆超市后院仓库', 40.6840, 122.2640, 2, 40),
(2, '送水果到东升小区', '2箱草莓+1箱车厘子，送到东升小区大门保安室', 1, 6.00, 1, '鑫鑫水果店→东升小区北门', 40.6780, 122.2700, 1, 15),
(2, '水果搬运上架', '新到一批西瓜和哈密瓜，搬到店内货架并摆整齐', 2, 20.00, 1, '鑫鑫水果店（东升路22号）', 40.6770, 122.2710, 2, 30),
(3, '楼道安全巡检', '检查A栋1-6层消防设施和照明，拍照上传', 3, 15.00, 1, '顺丰便利店旁边小区A栋', 40.6900, 122.2600, 1, 25),
(3, '送一箱水到7楼', '怡宝矿泉水一箱，送到A栋702室（无电梯）', 1, 10.00, 1, '顺丰便利店→A栋702', 40.6910, 122.2610, 3, 15);
