"""
校园二手交易平台 - Flask Web应用
包含所有页面、查询功能和业务逻辑
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import uuid

app = Flask(__name__)
DATABASE = 'campus_trade.db'


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ========== 页面路由 ==========

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')


@app.route('/items')
def items_page():
    """商品列表页面"""
    return render_template('items.html')


@app.route('/users')
def users_page():
    """用户列表页面"""
    return render_template('users.html')


@app.route('/orders')
def orders_page():
    """订单列表页面"""
    return render_template('orders.html')


@app.route('/queries')
def queries_page():
    """查询功能页面"""
    return render_template('queries.html')


# ========== API接口 ==========

@app.route('/api/users')
def get_users():
    """获取所有用户"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user ORDER BY user_id')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)


@app.route('/api/items')
def get_items():
    """获取所有商品"""
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
def get_orders():
    """获取所有订单"""
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


# ========== 数据操作 ==========

@app.route('/api/items', methods=['POST'])
def add_item():
    """添加新商品"""
    data = request.json
    item_id = 'i' + str(uuid.uuid4())[:8]

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO item (item_id, item_name, price, category, description, status, seller_id)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        ''', (item_id, data['item_name'], float(data['price']), data['category'],
              data.get('description', ''), data['seller_id']))

        # 更新视图
        cursor.execute('''
            INSERT OR REPLACE INTO unsold_items_view VALUES (?, ?, ?, ?, ?, ?, datetime("now"))
        ''', (item_id, data['item_name'], float(data['price']), data['category'],
              data.get('description', ''), data['seller_id']))

        conn.commit()
        return jsonify({'success': True, 'item_id': item_id})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


@app.route('/api/items/<item_id>', methods=['PUT'])
def update_item_price(item_id):
    """修改商品价格"""
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
def delete_item(item_id):
    """删除未售出商品"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        # 检查商品状态
        cursor.execute('SELECT status FROM item WHERE item_id = ?', (item_id,))
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


# ========== 购买商品业务逻辑 ==========

@app.route('/api/buy', methods=['POST'])
def buy_item():
    """
    购买商品 - 业务逻辑
    1. 在orders表新增记录
    2. 更新item表status为1
    3. 保证已售商品不能再次购买（事务+检查）
    """
    data = request.json
    item_id = data['item_id']
    buyer_id = data['buyer_id']

    conn = get_db()
    cursor = conn.cursor()

    try:
        # 开启事务
        cursor.execute('BEGIN TRANSACTION')

        # 检查商品是否存在且未售出
        cursor.execute('SELECT status, seller_id FROM item WHERE item_id = ?', (item_id,))
        item = cursor.fetchone()

        if not item:
            raise Exception('商品不存在')

        if item['status'] == 1:
            raise Exception('该商品已售出，无法重复购买')

        # 检查是否是自己的商品
        if item['seller_id'] == buyer_id:
            raise Exception('不能购买自己发布的商品')

        # 生成订单ID
        order_id = 'o' + str(uuid.uuid4())[:8]

        # 1. 在orders表新增记录
        cursor.execute('''
            INSERT INTO orders (order_id, item_id, buyer_id, order_date)
            VALUES (?, ?, ?, datetime('now'))
        ''', (order_id, item_id, buyer_id))

        # 2. 更新商品status为1
        cursor.execute('UPDATE item SET status = 1 WHERE item_id = ?', (item_id,))

        # 提交事务
        conn.commit()
        return jsonify({'success': True, 'order_id': order_id})

    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)})
    finally:
        conn.close()


# ========== 基本查询 ==========

@app.route('/api/query/unsold')
def query_unsold():
    """查询所有未售出商品"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE status = 0 ORDER BY item_id')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/query/price_above/<float:price>')
def query_price_above(price):
    """查询价格大于指定值的商品"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE price > ? ORDER BY price DESC', (price,))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/query/category/<category>')
def query_by_category(category):
    """查询指定分类的商品"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM item WHERE category = ? ORDER BY item_id', (category,))
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/query/seller/<seller_id>')
def query_by_seller(seller_id):
    """查询指定卖家发布的所有商品"""
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


# ========== 连接查询 ==========

@app.route('/api/query/sold_with_buyer')
def query_sold_with_buyer():
    """查询所有已售商品及其买家姓名"""
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
    """查询每个订单：商品名 + 买家名 + 日期"""
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
    """查询卖家商品是否被购买"""
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


# ========== 聚合与分组 ==========

@app.route('/api/stats/total_items')
def stats_total_items():
    """统计商品总数"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM item')
    result = cursor.fetchone()
    conn.close()
    return jsonify({'total': result['total']})


@app.route('/api/stats/category_count')
def stats_category_count():
    """统计每类商品数量"""
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
    """计算所有商品平均价格"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(price) as avg_price FROM item')
    result = cursor.fetchone()
    conn.close()
    return jsonify({'avg_price': round(result['avg_price'], 2) if result['avg_price'] else 0})


@app.route('/api/stats/top_seller')
def stats_top_seller():
    """查询发布商品数量最多的用户"""
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


# ========== 视图查询 ==========

@app.route('/api/view/sold')
def view_sold():
    """已售商品视图"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sold_items_view')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


@app.route('/api/view/unsold')
def view_unsold():
    """未售商品视图"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM unsold_items_view')
    items = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(items)


# ========== 错误页面 ==========

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404


if __name__ == '__main__':
    # 初始化数据库
    from db_init import init_database
    init_database()

    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000)
