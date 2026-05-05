# 校园二手交易平台数据库系统

## 在线访问网址

**http://campus-trade.onrender.com**

（首次访问可能需要等待几秒加载）

---

## 一、项目概述

本项目是一个校园二手交易平台数据库系统，使用 Python Flask + SQLite 实现，包含完整的 Web 界面和数据库操作功能。

### 功能特点
- 5个页面：首页、商品列表、用户列表、订单列表、查询功能
- 完整的CRUD操作：添加商品、修改价格、删除商品、购买商品
- 丰富的查询功能：基本查询、连接查询、聚合统计
- 数据库视图：已售商品视图、未售商品视图

---

## 二、从运行代码到获得网址的具体步骤

### 1. 本地运行

```bash
# 克隆或下载项目
cd campus-trade

# 安装依赖
pip install -r requirements.txt

# 运行应用
python app.py

# 访问 http://localhost:5000
```

### 2. 部署到 Render（推荐 - 免费）

1. 访问 https://render.com 并注册账号
2. 点击 "New +" → "Web Service"
3. 连接 GitHub 仓库或上传代码
4. 设置：
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. 点击 "Create Web Service"
6. 等待部署完成，获得 URL

### 3. 部署到 Railway

1. 访问 https://railway.app 并注册账号
2. 点击 "New Project" → "Deploy from GitHub"
3. 选择仓库，Railway 会自动检测 Python 项目
4. 部署完成后，复制提供的 URL

---

## 三、网页截图与说明

### 3.1 首页 (/)
显示系统概览，包括商品总数、用户总数、订单总数，以及功能入口卡片。

### 3.2 商品列表页面 (/items)
- 展示所有商品卡片
- 支持添加新商品
- 支持修改商品价格
- 支持删除未售出商品
- 支持购买未售出商品

### 3.3 用户列表页面 (/users)
- 展示所有用户信息
- 显示用户统计信息
- 包含安全性说明（第八部分）

### 3.4 订单列表页面 (/orders)
- 展示所有订单信息
- 包含并发与恢复说明（第九部分）

### 3.5 查询功能页面 (/queries)
包含所有要求的查询功能：

#### 基本查询
- 未售出商品查询
- 价格大于30元的商品
- 按分类查询（生活用品、电子产品、学习资料等）
- 按卖家查询（u001、u002等）

#### 连接查询
- 已售商品及其买家姓名
- 订单详情（商品名+买家+日期）
- 卖家商品销售状态

#### 聚合统计
- 商品总数
- 平均价格
- 商品最多的用户
- 各类商品数量

#### 视图查询
- 已售商品视图
- 未售商品视图

---

## 四、数据库结构

### 4.1 用户表 (user)
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | TEXT | 主键，如 u001 |
| username | TEXT | 用户名 |
| email | TEXT | 邮箱 |
| phone | TEXT | 电话 |

### 4.2 商品表 (item)
| 字段 | 类型 | 说明 |
|------|------|------|
| item_id | TEXT | 主键，如 i001 |
| item_name | TEXT | 商品名称 |
| price | REAL | 价格 |
| category | TEXT | 分类 |
| description | TEXT | 描述 |
| status | INTEGER | 0=未售出，1=已售出 |
| seller_id | TEXT | 外键关联用户 |

### 4.3 订单表 (orders)
| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | TEXT | 主键 |
| item_id | TEXT | 外键，唯一约束 |
| buyer_id | TEXT | 外键关联买家 |
| order_date | TIMESTAMP | 订单日期 |

---

## 五、数据操作结果

### 5.1 插入新商品
成功添加自定义商品，如"二手显示器"等。

### 5.2 修改商品价格
成功修改指定商品的价格。

### 5.3 删除未售出商品
成功删除未售出的商品，已售出商品不能删除。

### 5.4 购买商品
选择买家后，点击购买，订单创建成功，商品状态自动更新为"已售出"。

---

## 六、视图定义

### 6.1 已售商品视图 (sold_items_view)
```sql
CREATE VIEW sold_items_view AS
SELECT i.item_id, i.item_name, i.price, i.category, i.seller_id,
       o.buyer_id, o.order_date
FROM item i
JOIN orders o ON i.item_id = o.item_id
```

### 6.2 未售商品视图 (unsold_items_view)
```sql
CREATE VIEW unsold_items_view AS
SELECT item_id, item_name, price, category, description, seller_id, created_at
FROM item
WHERE status = 0
```

---

## 七、业务逻辑实现

### 购买商品操作
```sql
-- 1. 在 orders 表新增记录
INSERT INTO orders (order_id, item_id, buyer_id, order_date)
VALUES ('o003', 'i001', 'u004', datetime('now'));

-- 2. 修改商品状态
UPDATE item SET status = 1 WHERE item_id = 'i001';
```

### 约束保证
- orders.item_id 有 UNIQUE 约束，防止重复购买
- 使用事务保证数据一致性
- 已售商品(status=1)不能再次出现在购买流程中

---

## 八、安全性说明

### 8.1 如何防止普通用户删除数据
1. **权限控制**：SQLite 数据库可设置只读权限，普通用户只有 SELECT 权限
2. **应用层验证**：Web 应用只有管理员账户才能执行 DELETE 操作
3. **认证机制**：使用 Session/Cookie 验证用户身份，区分普通用户和管理员

### 8.2 如何限制用户只能查询数据
1. **数据库层**：创建只读用户，GRANT SELECT 权限
2. **应用层**：只提供只读 API 接口，禁用了 POST/PUT/DELETE 方法
3. **前端层**：隐藏操作按钮，普通用户界面无增删改入口

---

## 九、并发与恢复说明

### 9.1 两个用户同时购买同一商品会出现什么问题
1. **超卖问题**：两个订单都创建成功，导致同一商品被卖给多人
2. **数据不一致**：商品状态可能同时被多个事务修改
3. **约束违反**：可能违反 orders.item_id 的 UNIQUE 约束

### 9.2 如何解决（加锁/事务）
1. **数据库事务**：使用 BEGIN TRANSACTION 确保原子性
2. **唯一约束**：orders.item_id 设置 UNIQUE 约束，防止重复订单
3. **状态检查**：购买前检查商品状态是否为未售出
4. **乐观锁/悲观锁**：
   - 悲观锁：SELECT ... FOR UPDATE 锁定行
   - 乐观锁：检查版本号或时间戳

### 9.3 如果系统崩溃，如何恢复订单数据
1. **事务日志**：SQLite 使用 WAL 模式，支持自动恢复
2. **ACID 保证**：事务的原子性确保要么全部成功，要么全部回滚
3. **定期备份**：使用 cron 定期备份数据库文件
4. **云数据库**：部署到 PostgreSQL/MySQL 等企业级数据库
5. **幂等性设计**：使用唯一订单号，支持重复执行不重复创建

---

## 十、技术栈

- **后端**：Python 3 + Flask
- **数据库**：SQLite
- **前端**：HTML5 + CSS3 + JavaScript
- **部署**：Render / Railway

---

## 十一、项目结构

```
campus-trade/
├── app.py              # Flask 主应用
├── db_init.py           # 数据库初始化
├── requirements.txt     # Python 依赖
├── Procfile             # 部署配置
├── runtime.txt          # Python 版本
├── railway.json         # Railway 配置
├── templates/           # HTML 模板
│   ├── index.html
│   ├── items.html
│   ├── users.html
│   ├── orders.html
│   └── queries.html
└── campus_trade.db      # SQLite 数据库
```
