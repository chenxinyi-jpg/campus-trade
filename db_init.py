"""
校园二手交易平台数据库系统
数据库初始化脚本 - 包含表结构、初始数据和视图
"""

import sqlite3
from datetime import datetime

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect('campus_trade.db')
    cursor = conn.cursor()

    # ========== 1. 创建表 ==========
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            user_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
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
            status INTEGER DEFAULT 0 CHECK(status IN (0, 1)),
            seller_id TEXT NOT NULL,
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
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (item_id) REFERENCES item(item_id),
            FOREIGN KEY (buyer_id) REFERENCES user(user_id)
        )
    ''')

    # ========== 2. 插入初始数据 ==========
    # 用户数据
    users = [
        ('u001', '张三', 'zhangsan@example.com', '13800138001'),
        ('u002', '李四', 'lisi@example.com', '13800138002'),
        ('u003', '王五', 'wangwu@example.com', '13800138003'),
        ('u004', '赵六', 'zhaoliu@example.com', '13800138004'),
    ]
    cursor.executemany('INSERT OR IGNORE INTO user VALUES (?, ?, ?, ?, datetime("now"))', users)

    # 商品数据
    items = [
        ('i001', '二手自行车', 150.00, '交通工具', '八成新，无损坏', 0, 'u001'),
        ('i002', '高等数学教材', 35.00, '学习资料', '有笔记但不影响使用', 0, 'u001'),
        ('i003', '台灯', 45.00, '生活用品', 'LED护眼台灯', 0, 'u002'),
        ('i004', '耳机', 80.00, '电子产品', '降噪耳机', 1, 'u002'),
        ('i005', '书包', 60.00, '生活用品', '双肩背包', 0, 'u003'),
        ('i006', '笔记本电脑', 2000.00, '电子产品', 'ThinkPad T系列', 0, 'u003'),
        ('i007', '运动鞋', 120.00, '生活用品', 'Nike球鞋', 1, 'u004'),
        ('i008', '键盘', 55.00, '电子产品', '机械键盘', 0, 'u004'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO item (item_id, item_name, price, category, description, status, seller_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime("now"))
    ''', items)

    # 订单数据（已售出的商品）
    orders = [
        ('o001', 'i004', 'u003'),
        ('o002', 'i007', 'u001'),
    ]
    cursor.executemany('''
        INSERT OR IGNORE INTO orders (order_id, item_id, buyer_id, order_date)
        VALUES (?, ?, ?, datetime("now"))
    ''', orders)

    # ========== 3. 创建视图 ==========
    # 已售商品视图
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS sold_items_view AS
        SELECT i.item_id, i.item_name, i.price, i.category, i.seller_id,
               o.buyer_id, o.order_date
        FROM item i
        JOIN orders o ON i.item_id = o.item_id
    ''')

    # 未售商品视图
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS unsold_items_view AS
        SELECT item_id, item_name, price, category, description, seller_id, created_at
        FROM item
        WHERE status = 0
    ''')

    conn.commit()
    conn.close()
    print("数据库初始化完成！")

def get_connection():
    """获取数据库连接"""
    return sqlite3.connect('campus_trade.db')

if __name__ == '__main__':
    init_database()
