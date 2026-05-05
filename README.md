# 校园二手交易平台数据库系统

## 在线访问网址

**http://campus-trade.onrender.com**

（首次访问可能需要等待几秒加载）

---

## 一、项目概述

本项目是一个功能完整的校园二手交易平台数据库系统，使用 Python Flask + SQLite 实现，包含：

### 核心功能
- **用户系统**：注册、登录、个人主页
- **商品系统**：浏览、搜索、筛选、排序、发布商品
- **购物车**：添加商品、批量结算
- **订单系统**：购买商品、查看订单
- **评价系统**：对商品进行评分和评论

### 数据库功能
- **基本查询**：未售出商品、价格筛选、分类查询、卖家查询
- **连接查询**：已售商品+买家、订单详情、卖家销售状态
- **聚合统计**：商品总数、分类统计、平均价格、热门卖家
- **数据库视图**：已售商品视图、未售商品视图

---

## 二、从运行代码到获得网址的具体步骤

### 1. 本地运行

```bash
# 进入项目目录
cd campus-trade

# 安装依赖
pip install Flask

# 运行应用
python app.py

# 浏览器访问 http://localhost:5000
```

### 2. 部署到 Render（推荐 - 免费）

1. 访问 https://render.com 并注册账号（可用GitHub登录）
2. 点击 "New +" → "Web Service"
3. 连接到你的 GitHub 仓库
4. 设置配置：
   - **Name**: campus-trade
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
5. 点击 "Create Web Service"
6. 等待2-3分钟部署完成，获得 URL

### 3. 部署到 Railway

1. 访问 https://railway.app 并注册账号
2. 点击 "New Project" → "Deploy from GitHub"
3. 选择仓库，Railway 会自动检测 Python 项目
4. 部署完成后，复制提供的 URL

---

## 三、网页截图与功能说明

### 3.1 首页 (/)
- 系统概览统计（商品总数、用户总数、订单总数）
- 最新上架商品展示
- 热门商品展示
- 功能导航入口

### 3.2 用户认证 (/login, /register)
- 用户注册：设置用户名、密码、联系方式
- 用户登录：用户名+密码登录
- 测试账号：张三/123456，李四/123456

### 3.3 商品列表 (/items)
- 商品卡片展示（图片、价格、分类、卖家）
- 搜索商品名称或描述
- 按分类筛选
- 多种排序方式（最新、价格、热门）
- 发布新商品（需登录）
- 加入购物车（需登录）

### 3.4 商品详情 (/item/<id>)
- 商品完整信息展示
- 卖家信息
- 商品评价展示
- 发表评论（需登录）
- 立即购买
- 加入购物车

### 3.5 购物车 (/cart)
- 购物车商品列表
- 删除商品
- 批量结算购买
- 实时计算总价

### 3.6 订单列表 (/orders)
- 所有购买订单展示
- 订单状态追踪
- 并发与恢复说明

### 3.7 用户列表 (/users)
- 所有用户信息展示
- 用户统计信息
- 安全性说明

### 3.8 查询功能 (/queries)
包含所有作业要求的查询功能：

#### 聚合统计
- 商品总数
- 平均价格
- 商品最多的用户
- 各类商品数量（可视化柱状图）

#### 基本查询
- 未售出商品查询
- 价格大于30元的商品
- 按分类查询（生活用品、电子产品、学习资料等）
- 按卖家查询（u001、u002等）

#### 连接查询
- 已售商品及其买家姓名
- 订单详情（商品名+买家+日期）
- 卖家商品销售状态

#### 视图查询
- 已售商品视图
- 未售商品视图

---

## 四、数据库结构

### 4.1 用户表 (user)
| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | TEXT | 主键，如 u001 |
| username | TEXT | 用户名（唯一） |
| password | TEXT | 密码（MD5加密） |
| email | TEXT | 邮箱 |
| phone | TEXT | 电话 |
| created_at | TIMESTAMP | 注册时间 |

### 4.2 商品表 (item)
| 字段 | 类型 | 说明 |
|------|------|------|
| item_id | TEXT | 主键，如 i001 |
| item_name | TEXT | 商品名称 |
| price | REAL | 价格 |
| category | TEXT | 分类 |
| description | TEXT | 描述 |
| image | TEXT | 图片路径 |
| status | INTEGER | 0=未售出，1=已售出 |
| seller_id | TEXT | 卖家ID（外键） |
| view_count | INTEGER | 浏览量 |
| created_at | TIMESTAMP | 发布时间 |

### 4.3 订单表 (orders)
| 字段 | 类型 | 说明 |
|------|------|------|
| order_id | TEXT | 主键 |
| item_id | TEXT | 商品ID（外键，唯一） |
| buyer_id | TEXT | 买家ID（外键） |
| total_price | REAL | 订单金额 |
| status | TEXT | 订单状态 |
| order_date | TIMESTAMP | 下单时间 |

### 4.4 购物车表 (cart)
| 字段 | 类型 | 说明 |
|------|------|------|
| cart_id | INTEGER | 主键（自增） |
| user_id | TEXT | 用户ID（外键） |
| item_id | TEXT | 商品ID（外键） |
| added_at | TIMESTAMP | 添加时间 |
| **约束** | | UNIQUE(user_id, item_id) |

### 4.5 评价表 (reviews)
| 字段 | 类型 | 说明 |
|------|------|------|
| review_id | TEXT | 主键 |
| item_id | TEXT | 商品ID（外键） |
| user_id | TEXT | 用户ID（外键） |
| rating | INTEGER | 评分（1-5） |
| comment | TEXT | 评论内容 |
| created_at | TIMESTAMP | 评论时间 |

---

## 五、数据操作

### 5.1 插入新商品
- 功能路径：商品列表页面 → 点击"发布商品"按钮
- 填写商品名称、价格、分类、描述
- 成功后自动刷新页面显示新商品

### 5.2 修改商品价格
- 功能路径：商品详情页 → 联系卖家修改
- 或直接在数据库执行 UPDATE 语句

### 5.3 删除未售出商品
- 功能路径：商品详情页 → 卖家自行删除
- 已售出商品不能删除（数据库约束保护）

### 5.4 购买商品
- 功能路径：商品详情页 → 点击"立即购买"
- 或：购物车 → 批量结算
- 购买后自动创建订单，商品状态变为"已售"

---

## 六、视图定义

### 6.1 已售商品视图 (sold_items_view)
```sql
CREATE VIEW sold_items_view AS
SELECT i.*, o.buyer_id, o.order_date
FROM item i
JOIN orders o ON i.item_id = o.item_id
WHERE i.status = 1
```

### 6.2 未售商品视图 (unsold_items_view)
```sql
CREATE VIEW unsold_items_view AS
SELECT * FROM item WHERE status = 0
```

---

## 七、业务逻辑实现

### 购买商品操作（事务保证）
```sql
BEGIN TRANSACTION;

-- 1. 检查商品状态
SELECT status FROM item WHERE item_id = ?;

-- 2. 创建订单
INSERT INTO orders (order_id, item_id, buyer_id, total_price, status)
VALUES (?, ?, ?, ?, 'completed');

-- 3. 更新商品状态
UPDATE item SET status = 1 WHERE item_id = ?;

-- 4. 从购物车移除
DELETE FROM cart WHERE user_id = ? AND item_id = ?;

COMMIT;
```

### 约束保证
- orders.item_id 有 UNIQUE 约束，防止重复购买
- 使用事务确保原子性
- 已售商品(status=1)不能再次购买
- 购物车同一用户同一商品唯一

---

## 八、安全性说明

### 8.1 如何防止普通用户删除数据

1. **应用层验证**
   - 只有登录用户才能执行删除操作
   - 使用 `@login_required` 装饰器保护API

2. **权限控制**
   - 只有商品所有者才能删除自己发布的商品
   - 后端检查 `seller_id == session['user_id']`

3. **前端隐藏**
   - 普通用户界面不显示删除按钮
   - 只有卖家能看到删除选项

4. **API验证**
   ```python
   @login_required
   def api_delete_item(item_id):
       # 检查是否是商品所有者
       cursor.execute('SELECT seller_id FROM item WHERE item_id = ?', (item_id,))
       item = cursor.fetchone()
       if item['seller_id'] != session['user_id']:
           return jsonify({'error': '无权限'})
   ```

### 8.2 如何限制用户只能查询数据

1. **只读API设计**
   - 提供独立的查询接口（GET请求）
   - 增删改操作需要额外验证

2. **数据库权限控制**
   ```sql
   -- 创建只读用户
   CREATE USER 'readonly'@'localhost' IDENTIFIED BY 'password';
   GRANT SELECT ON campus_trade.* TO 'readonly'@'localhost';
   ```

3. **会话验证**
   - 普通用户只能浏览
   - 管理员可以增删改

4. **操作日志审计**
   ```python
   # 记录所有写操作
   def log_operation(user_id, action, table, record_id):
       # 写入审计日志表
   ```

---

## 九、并发与恢复说明

### 9.1 两个用户同时购买同一商品会出现什么问题

**问题场景：**
```
用户A: 点击购买商品X (t=0)
用户B: 点击购买商品X (t=0.001秒)

正常情况：只有1人能成功购买
并发问题：
  1. 读取库存时，两个请求都看到 status=0
  2. 两个请求都创建订单
  3. 商品被卖给两个人（超卖）
  4. 违反 orders.item_id UNIQUE 约束
```

**具体问题：**
- **超卖问题**：同一商品被卖给多个买家
- **数据不一致**：库存计数错误
- **约束违反**：可能抛出数据库异常

### 9.2 如何解决（加锁/事务）

**解决方案：**

1. **数据库事务**
   ```python
   try:
       cursor.execute('BEGIN TRANSACTION')
       # 检查+更新操作
       cursor.execute('COMMIT')
   except:
       cursor.execute('ROLLBACK')
   ```

2. **唯一约束**
   ```sql
   orders.item_id TEXT NOT NULL UNIQUE
   -- 阻止重复订单
   ```

3. **状态检查**
   ```python
   cursor.execute('SELECT status FROM item WHERE item_id = ?', (item_id,))
   item = cursor.fetchone()
   if item['status'] == 1:
       raise Exception('商品已售出')
   ```

4. **悲观锁（生产环境推荐）**
   ```sql
   SELECT * FROM item WHERE item_id = ? FOR UPDATE;
   ```

5. **乐观锁（高并发推荐）**
   ```sql
   UPDATE item SET status = 1, version = version + 1
   WHERE item_id = ? AND version = ?;
   ```

### 9.3 如果系统崩溃，如何恢复订单数据

1. **事务ACID保证**
   - Atomicity（原子性）：事务要么全成功，要么全失败
   - Consistency（一致性）：数据从一个一致状态到另一个
   - Isolation（隔离性）：并发事务互不干扰
   - Durability（持久性）：提交后数据永久保存

2. **SQLite WAL模式**
   ```python
   conn.execute('PRAGMA journal_mode=WAL')
   # 支持并发读写，自动崩溃恢复
   ```

3. **定期备份策略**
   ```bash
   # 每日凌晨3点备份
   0 3 * * * cp /path/to/campus_trade.db /backup/
   ```

4. **云数据库部署**
   - PostgreSQL：支持 Point-in-time Recovery
   - MySQL：支持 binlog 恢复
   - 云服务：RDS 自动备份

5. **幂等性设计**
   ```python
   # 使用唯一订单号，支持重复执行
   order_id = 'o' + hashlib.md5(item_id + buyer_id + timestamp).hexdigest()[:8]
   ```

---

## 十、技术栈

- **后端**：Python 3 + Flask
- **数据库**：SQLite（生产可用 PostgreSQL/MySQL）
- **前端**：HTML5 + CSS3 + Vanilla JavaScript
- **样式**：自定义CSS（参考参考项目设计）
- **部署**：Render / Railway / Heroku

---

## 十一、项目结构

```
campus-trade/
├── app.py              # Flask主应用（所有路由和API）
├── requirements.txt    # Python依赖
├── README.md           # 项目说明文档
├── Procfile           # 部署配置
├── runtime.txt        # Python版本
├── .gitignore         # Git忽略文件
├── static/
│   ├── css/
│   │   └── style.css  # 统一样式文件
│   ├── images/        # 商品图片
│   └── uploads/        # 用户上传
└── templates/
    ├── index.html     # 首页
    ├── login.html      # 登录页
    ├── register.html   # 注册页
    ├── items.html      # 商品列表
    ├── product.html    # 商品详情
    ├── cart.html       # 购物车
    ├── orders.html     # 订单列表
    ├── users.html      # 用户列表
    ├── profile.html    # 用户主页
    └── queries.html    # 查询功能
```

---

## 十二、测试账号

| 用户名 | 密码 | 说明 |
|--------|------|------|
| 张三 | 123456 | 默认用户 |
| 李四 | 123456 | 默认用户 |
| 王五 | 123456 | 默认用户 |
| 赵六 | 123456 | 默认用户 |

---

## 十三、常见问题

**Q: 首次访问加载慢？**
A: 免费版服务器有冷启动延迟，第二次访问会快很多。

**Q: 数据库在哪里？**
A: 本地运行时会生成 `campus_trade.db` 文件。

**Q: 如何重置数据？**
A: 删除 `campus_trade.db`，重新运行 `python app.py`。

---

**项目完成时间：2026年5月6日**
