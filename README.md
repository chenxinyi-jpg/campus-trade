# 校园二手交易平台数据库系统

基于Flask + SQLite的校园二手交易平台，包含完整的数据库操作、查询功能和Web界面。

## 快速开始

### 本地运行
```bash
pip install -r requirements.txt
python app.py
```
访问 http://localhost:5000

### 部署
本项目可部署到Railway、Render等平台。

## 功能模块

### 数据库操作
- 用户管理
- 商品管理
- 订单管理

### 查询功能
- 基本查询（未售出商品、价格筛选、分类查询、用户商品）
- 连接查询（已售商品、订单详情、卖家商品）
- 聚合统计（商品总数、分类统计、平均价格、热门卖家）

### 业务逻辑
- 购买商品（创建订单+更新状态）

## 技术栈
- 后端：Python Flask
- 数据库：SQLite
- 前端：HTML/CSS/JavaScript
