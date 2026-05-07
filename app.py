"""
校园二手交易平台 - 完整版
包含用户认证、购物车、订单管理等完整功能
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from functools import wraps
import sqlite3
from datetime import datetime
import uuid
import hashlib

app = Flask(__name__)
app.secret_key = 'campus_trade_secret_key_2024'
DATABASE = 'campus_trade.db'


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 商品表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item (
            item_id TEXT PRIMARY KEY,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT,
            description TEXT,
            image TEXT,
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1)),
            seller_id TEXT NOT NULL,
            view_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (seller_id) REFERENCES user(user_id)
        )
    ''')

    # 订单表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL UNIQUE,
            buyer_id TEXT NOT NULL,
            total_price REAL,
            status TEXT DEFAULT 'pending',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES item(item_id),
            FOREIGN KEY (buyer_id) REFERENCES user(user_id)
        )
    ''')

    # 购物车表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(user_id),
            FOREIGN KEY (item_id) REFERENCES item(item_id),
            UNIQUE(user_id, item_id)
        )
    ''')

    # 商品评价表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id TEXT PRIMARY KEY,
            item_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES item(item_id),
            FOREIGN KEY (user_id) REFERENCES user(user_id)
        )
    ''')

    # 插入初始用户数据（密码都是123456的MD5）
    password_hash = hashlib.md5('123456'.encode()).hexdigest()
    users = [
        ('u001', '张三', password_hash, 'zhangsan@example.com', '13800138001'),
        ('u002', '李四', password_hash, 'lisi@example.com', '13800138002'),
        ('u003', '王五', password_hash, 'wangwu@example.com', '13800138003'),
        ('u004', '赵六', password_hash, 'zhaoliu@example.com', '13800138004'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO user VALUES (?, ?, ?, ?, ?, datetime('now'))
    ''', users)

    # 插入初始商品数据
    items = [
        ('i001', '二手自行车', 150.00, '交通工具', '八成新，无损坏，适合校园代步', 'bike.jpg', 0, 'u001'),
        ('i002', '高等数学教材', 35.00, '学习资料', '有笔记但不影响使用，考研必备', 'book.jpg', 0, 'u001'),
        ('i003', 'LED台灯', 45.00, '生活用品', '护眼台灯，三档调光', 'lamp.jpg', 0, 'u002'),
        ('i004', '降噪耳机', 80.00, '电子产品', '无线蓝牙降噪耳机，续航持久', 'headphone.jpg', 1, 'u002'),
        ('i005', '双肩背包', 60.00, '生活用品', '防水面料，多功能收纳', 'bag.jpg', 0, 'u003'),
        ('i006', '笔记本电脑', 2000.00, '电子产品', 'ThinkPad T系列，性能稳定', 'laptop.jpg', 0, 'u003'),
        ('i007', 'Nike运动鞋', 120.00, '生活用品', '尺码42，球鞋爱好者勿拍', 'shoes.jpg', 1, 'u004'),
        ('i008', '机械键盘', 55.00, '电子产品', '青轴机械键盘，背光效果', 'keyboard.jpg', 0, 'u004'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO item VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0, datetime('now'))
    ''', items)

    # 插入初始订单数据
    orders = [
        ('o001', 'i004', 'u003', 80.00, 'completed'),
        ('o002', 'i007', 'u001', 120.00, 'completed'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO orders VALUES (?, ?, ?, ?, ?, datetime('now'))
    ''', orders)

    # 创建视图
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS sold_items_view AS
        SELECT i.*, o.buyer_id, o.order_date
        FROM item i
        JOIN orders o ON i.item_id = o.item_id
        WHERE i.status = 1
    ''')

    cursor.execute('''
        CREATE VIEW IF NOT EXISTS unsold_items_view AS
        SELECT * FROM item WHERE status = 0
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成！")


# ========== 登录装饰器 ==========
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录！', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """获取当前登录用户"""
    if 'user_id' in session:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE user_id = ?', (session['user_id'],))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    return None


# ========== 页面路由 ==========

@app.route('/')
def index():
    """首页"""
    conn = get_db()
    cursor = conn.cursor()

    # 获取最新商品
    cursor.execute('''
        SELECT i.*, u.username as seller_name
        FROM item i
        LEFT JOIN user u ON i.seller_id = u.user_id
        ORDER BY i.created_at DESC
        LIMIT 8
    ''')
    latest_items = [dict(row) for row in cursor.fetchall()]

    # 获取热门商品
    cursor.execute('''
        SELECT i.*, u.username as seller_name
        FROM item i
        LEFT JOIN user u ON i.seller_id = u.user_id
        WHERE i.status = 0
        ORDER BY i.view_count DESC
        LIMIT 4
    ''')
    hot_items = [dict(row) for row in cursor.fetchall()]

    # 统计数据
    cursor.execute('SELECT COUNT(*) as count FROM item')
    total_items = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM user')
    total_users = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM orders')
    total_orders = cursor.fetchone()['count']

    cursor.execute('SELECT COUNT(*) as count FROM item WHERE status = 0')
    unsold_count = cursor.fetchone()['count']

    conn.close()

    return render_template('index.html',
                           latest_items=latest_items,
                           hot_items=hot_items,
                           total_items=total_items,
                           total_users=total_users,
                           total_orders=total_orders,
                           unsold_count=unsold_count)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        password_hash = hashlib.md5(password.encode()).hexdigest()

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user WHERE username = ? AND password = ?',
                      (username, password_hash))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            flash(f'欢迎回来，{user["username"]}！', 'success')
            return redirect(url_for('index'))
        else:
            flash('用户名或密码错误！', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """注册页面"""
    if request.method == 'POST':
        user_id = 'u' + str(uuid.uuid4())[:8]
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email', '')
        phone = request.form.get('phone', '')

        password_hash = hashlib.md5(password.encode()).hexdigest()

        conn = get_db()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO user (user_id, username, password, email, phone)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, username, password_hash, email, phone))
            conn.commit()
            flash('注册成功！请登录', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('用户名已存在！', 'danger')
        finally:
            conn.close()

    return render_template('register.html')


@app.route('/logout')
def logout():
    """退出登录"""
    session.clear()
    flash('已退出登录', 'info')
    return redirect(url_for('index'))


@app.route('/items')
def items():
    """商品列表"""
    category = request.args.get('category', '')
    sort = request.args.get('sort', 'latest')
    search = request.args.get('search', '')

    conn = get_db()
    cursor = conn.cursor()

    query = '''
        SELECT i.*, u.username as seller_name
        FROM item i
        LEFT JOIN user u ON i.seller_id = u.user_id
        WHERE 1=1
    '''
    params = []

    if category:
        query += ' AND i.category = ?'
        params.append(category)

    if search:
        query += ' AND (i.item_name LIKE ? OR i.description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    if sort == 'price_low':
        query += ' ORDER BY i.price ASC'
    elif sort == 'price_high':
        query += ' ORDER BY i.price DESC'
    elif sort == 'popular':
        query += ' ORDER BY i.view_count DESC'
    else:
        query += ' ORDER BY i.created_at DESC'

    cursor.execute(query, params)
    items_list = [dict(row) for row in cursor.fetchall()]

    # 获取所有分类
    cursor.execute('SELECT DISTINCT category FROM item')
    categories = [row['category'] for row in cursor.fetchall()]

    conn.close()

    return render_template('items.html',
                           items=items_list,
                           categories=categories,
                           current_category=category,
                           current_sort=sort,
                           search=search)


@app.route('/item/<item_id>')
def item_detail(item_id):
    """商品详情"""
    conn = get_db()
    cursor = conn.cursor()

    # 增加浏览量
    cursor.execute('UPDATE item SET view_count = view_count + 1 WHERE item_id = ?', (item_id,))

    cursor.execute('''
        SELECT i.*, u.username as seller_name, u.phone as seller_phone
        FROM item i
        LEFT JOIN user u ON i.seller_id = u.user_id
        WHERE i.item_id = ?
    ''', (item_id,))
    item = cursor.fetchone()

    # 获取评价
    cursor.execute('''
        SELECT r.*, u.username
        FROM reviews r
        LEFT JOIN user u ON r.user_id = u.user_id
        WHERE r.item_id = ?
        ORDER BY r.created_at DESC
    ''', (item_id,))
    reviews = [dict(row) for row in cursor.fetchall()]

    # 计算平均评分
    if reviews:
        avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
    else:
        avg_rating = 0

    conn.commit()
    conn.close()

    if not item:
        flash('商品不存在', 'danger')
        return redirect(url_for('items'))

    return render_template('product.html',
                           item=dict(item),
                           reviews=reviews,
                           avg_rating=round(avg_rating, 1))


@app.route('/users')
def users_page():
    """用户列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.*,
               (SELECT COUNT(*) FROM item WHERE seller_id = u.user_id) as item_count,
               (SELECT COUNT(*) FROM orders WHERE buyer_id = u.user_id) as order_count
        FROM user u
    ''')
    users_list = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template('users.html', users=users_list)


@app.route('/user/<user_id>')
def user_profile(user_id):
    """用户主页"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM user WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()

    if not user:
        flash('用户不存在', 'danger')
        return redirect(url_for('index'))

    # 该用户的商品
    cursor.execute('''
        SELECT * FROM item WHERE seller_id = ?
        ORDER BY created_at DESC
    ''', (user_id,))
    user_items = [dict(row) for row in cursor.fetchall()]

    # 该用户的订单
    cursor.execute('''
        SELECT o.*, i.item_name
        FROM orders o
        JOIN item i ON o.item_id = i.item_id
        WHERE o.buyer_id = ?
        ORDER BY o.order_date DESC
    ''', (user_id,))
    user_orders = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return render_template('profile.html',
                           user=dict(user),
                           items=user_items,
                           orders=user_orders)


@app.route('/orders')
@login_required
def orders_page():
    """订单列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.*, i.item_name, i.price, i.category, i.image,
               u.username as seller_name
        FROM orders o
        JOIN item i ON o.item_id = i.item_id
        JOIN user u ON i.seller_id = u.user_id
        WHERE o.buyer_id = ?
        ORDER BY o.order_date DESC
    ''', (session['user_id'],))
    orders_list = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return render_template('orders.html', orders=orders_list)


@app.route('/cart')
@login_required
def cart():
    """购物车"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, i.item_name, i.price, i.category, i.image, i.status, i.seller_id,
               u.username as seller_name
        FROM cart c
        JOIN item i ON c.item_id = i.item_id
        JOIN user u ON i.seller_id = u.user_id
        WHERE c.user_id = ?
    ''', (session['user_id'],))
    cart_items = [dict(row) for row in cursor.fetchall()]

    total = sum(item['price'] for item in cart_items if item['status'] == 0)

    conn.close()

    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/queries')
def queries_page():
    """查询功能页面"""
    return render_template('queries.html')


# ========== API接口 ==========

@app.route('/api/users')
def api_get_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user ORDER BY user_id')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)


@app.route('/api/items')
def api_get_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.*, u.username as seller_name
        FROM item i
        LEFT JOIN user u ON i.seller_id = u.user_id
        ORDER BY i.item_id
    ''')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/orders')
def api_get_orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.*, i.item_name, u.username as buyer_name
        FROM orders o
        JOIN item i ON o.item_id = i.item_id
        JOIN user u ON o.buyer_id = u.user_id
        ORDER BY o.order_id
    ''')
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(orders)


# ========== 数据操作API ==========

@app.route('/api/items', methods=['POST'])
@login_required
def api_add_item():
    data = request.json
    item_id = 'i' + str(uuid.uuid4())[:8]

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO item (item_id, item_name, price, category, description, image, status, seller_id)
            VALUES (?, ?, ?, ?, ?, ?, 0, ?)
        ''', (item_id, data['item_name'], float(data['price']), data['category'],
              data.get('description', ''), data.get('image', ''), session['user_id']))
        conn.commit()
        return jsonify({'success': True, 'item_id': item_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@app.route('/api/items/<item_id>', methods=['PUT'])
def api_update_item(item_id):
    data = request.json
    new_price = float(data['price'])

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE item SET price = ? WHERE item_id = ?', (new_price, item_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@app.route('/api/items/<item_id>', methods=['DELETE'])
@login_required
def api_delete_item(item_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT status, seller_id FROM item WHERE item_id = ?', (item_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'success': False, 'error': '商品不存在'})

        if result['status'] == 1:
            return jsonify({'success': False, 'error': '已售出商品不能删除'})

        cursor.execute('DELETE FROM item WHERE item_id = ?', (item_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


# ========== 购物车API ==========

@app.route('/api/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    item_id = request.json.get('item_id')

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO cart (user_id, item_id)
            VALUES (?, ?)
        ''', (session['user_id'], item_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@app.route('/api/cart/remove/<item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM cart WHERE user_id = ? AND item_id = ?',
                     (session['user_id'], item_id))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


# ========== 购买商品 ==========

@app.route('/api/buy', methods=['POST'])
@login_required
def buy_item():
    """购买商品 - 业务逻辑"""
    data = request.json
    item_id = data.get('item_id')
    buyer_id = session['user_id']

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('BEGIN TRANSACTION')

        cursor.execute('SELECT status, seller_id, price FROM item WHERE item_id = ?', (item_id,))
        item = cursor.fetchone()

        if not item:
            raise Exception('商品不存在')

        if item['status'] == 1:
            raise Exception('该商品已售出')

        if item['seller_id'] == buyer_id:
            raise Exception('不能购买自己发布的商品')

        order_id = 'o' + str(uuid.uuid4())[:8]

        cursor.execute('''
            INSERT INTO orders (order_id, item_id, buyer_id, total_price, status)
            VALUES (?, ?, ?, ?, 'completed')
        ''', (order_id, item_id, buyer_id, item['price']))

        cursor.execute('UPDATE item SET status = 1 WHERE item_id = ?', (item_id,))

        # 从购物车移除
        cursor.execute('DELETE FROM cart WHERE user_id = ? AND item_id = ?', (buyer_id, item_id))

        conn.commit()
        return jsonify({'success': True, 'order_id': order_id})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@app.route('/api/buy_cart', methods=['POST'])
@login_required
def buy_cart():
    """购买购物车中的所有商品"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute('BEGIN TRANSACTION')

        # 获取购物车中的未售出商品
        cursor.execute('''
            SELECT c.item_id, i.price
            FROM cart c
            JOIN item i ON c.item_id = i.item_id
            WHERE c.user_id = ? AND i.status = 0
        ''', (session['user_id'],))
        cart_items = cursor.fetchall()

        if not cart_items:
            raise Exception('购物车为空或商品已售出')

        order_ids = []
        for item in cart_items:
            order_id = 'o' + str(uuid.uuid4())[:8]
            cursor.execute('''
                INSERT INTO orders (order_id, item_id, buyer_id, total_price, status)
                VALUES (?, ?, ?, ?, 'completed')
            ''', (order_id, item['item_id'], session['user_id'], item['price']))
            cursor.execute('UPDATE item SET status = 1 WHERE item_id = ?', (item['item_id'],))
            order_ids.append(order_id)

        # 清空购物车
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))

        conn.commit()
        return jsonify({'success': True, 'order_ids': order_ids})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


# ========== 评价API ==========

@app.route('/api/review', methods=['POST'])
@login_required
def add_review():
    data = request.json
    review_id = 'r' + str(uuid.uuid4())[:8]

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO reviews (review_id, item_id, user_id, rating, comment)
            VALUES (?, ?, ?, ?, ?)
        ''', (review_id, data['item_id'], session['user_id'],
              data['rating'], data.get('comment', '')))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


# ========== 查询API ==========

@app.route('/api/query/unsold')
def query_unsold():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE status = 0 ORDER BY item_id')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/query/price_above/<float:price>')
def query_price_above(price):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE price > ? ORDER BY price DESC', (price,))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/query/category/<category>')
def query_by_category(category):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE category = ? ORDER BY item_id', (category,))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/query/seller/<seller_id>')
def query_by_seller(seller_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.*, u.username as seller_name
        FROM item i
        LEFT JOIN user u ON i.seller_id = u.user_id
        WHERE i.seller_id = ?
        ORDER BY i.item_id
    ''', (seller_id,))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/query/sold_with_buyer')
def query_sold_with_buyer():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.item_id, i.item_name, i.price, u.username as buyer_name
        FROM item i
        JOIN orders o ON i.item_id = o.item_id
        JOIN user u ON o.buyer_id = u.user_id
        WHERE i.status = 1
    ''')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/query/order_details')
def query_order_details():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.order_id, i.item_name, u.username as buyer_name, o.order_date
        FROM orders o
        JOIN item i ON o.item_id = i.item_id
        JOIN user u ON o.buyer_id = u.user_id
        ORDER BY o.order_date DESC
    ''')
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(orders)


@app.route('/api/query/seller_sold_status/<seller_id>')
def query_seller_sold_status(seller_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT i.item_id, i.item_name, i.status,
               CASE WHEN o.order_id IS NOT NULL THEN '已售' ELSE '未售' END as sale_status,
               o.buyer_id
        FROM item i
        LEFT JOIN orders o ON i.item_id = o.item_id
        WHERE i.seller_id = ?
        ORDER BY i.status, i.item_id
    ''', (seller_id,))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


# ========== 统计API ==========

@app.route('/api/stats/total_items')
def stats_total_items():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM item')
    result = cursor.fetchone()
    conn.close()
    return jsonify({'total': result['total']})


@app.route('/api/stats/category_count')
def stats_category_count():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM item
        GROUP BY category
        ORDER BY count DESC
    ''')
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(results)


@app.route('/api/stats/avg_price')
def stats_avg_price():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(price) as avg_price FROM item')
    result = cursor.fetchone()
    conn.close()
    return jsonify({'avg_price': round(result['avg_price'], 2) if result['avg_price'] else 0})


@app.route('/api/stats/top_seller')
def stats_top_seller():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.user_id, u.username, COUNT(i.item_id) as item_count
        FROM user u
        LEFT JOIN item i ON u.user_id = i.seller_id
        GROUP BY u.user_id, u.username
        ORDER BY item_count DESC
        LIMIT 1
    ''')
    result = cursor.fetchone()
    conn.close()
    return jsonify(dict(result) if result else {})


@app.route('/api/view/sold')
def view_sold():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sold_items_view')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/view/unsold')
def view_unsold():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM unsold_items_view')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


# ========== 错误处理 ==========

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404


# ========== 初始化路由（用于云端部署） ==========

@app.route('/init')
def init_route():
    """初始化数据库表和数据"""
    init_database()
    return '''
    <html>
    <head><title>初始化完成</title></head>
    <body>
        <h1>数据库初始化完成！</h1>
        <p>点击访问：<a href="/">首页</a></p>
    </body>
    </html>
    '''


# 确保应用启动时初始化数据库（云端部署需要）
with app.app_context():
    init_database()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
