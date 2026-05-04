#!/usr/bin/env python3
"""
DemoPPT 订阅系统 v1.0
包含：套餐管理、订阅创建、续费、到期检查、权限控制
"""
import sqlite3
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List

# 数据库路径
BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "subscription.db"


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化订阅数据库"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 套餐表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plan_code VARCHAR(20) UNIQUE NOT NULL,  -- monthly/quarterly/yearly
            name VARCHAR(50) NOT NULL,
            description TEXT DEFAULT '',
            price INTEGER NOT NULL,  -- 价格（分）
            duration_days INTEGER NOT NULL,  -- 有效期（天）
            features TEXT DEFAULT '{}',  -- 功能列表JSON
            status INTEGER DEFAULT 1,  -- 1=上架, 0=下架
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 订阅表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            plan_code VARCHAR(20) NOT NULL,
            status VARCHAR(20) DEFAULT 'active',  -- active/expired/cancelled/pending
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL,
            auto_renew INTEGER DEFAULT 1,  -- 1=自动续费, 0=手动
            order_id VARCHAR(100) DEFAULT '',
            payment_method VARCHAR(20) DEFAULT 'wechat',  -- wechat/alipay/stripe
            total_paid INTEGER DEFAULT 0,  -- 已支付总额（分）
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 订单表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id VARCHAR(100) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            plan_code VARCHAR(20) NOT NULL,
            amount INTEGER NOT NULL,  -- 金额（分）
            status VARCHAR(20) DEFAULT 'pending',  -- pending/paid/cancelled/refunded
            payment_method VARCHAR(20) DEFAULT 'wechat',
            transaction_id VARCHAR(100) DEFAULT '',
            paid_time DATETIME,
            create_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 初始化默认套餐
    default_plans = [
        {
            "plan_code": "monthly",
            "name": "月卡",
            "description": "按月订阅，灵活方便",
            "price": 9900,  # ¥99
            "duration_days": 30,
            "features": '["PPT生成无限制", "20+模板任意用", "品牌定制", "导出高清PDF", "专属客服支持"]'
        },
        {
            "plan_code": "quarterly",
            "name": "季卡",
            "description": "季度订阅，更享优惠",
            "price": 24900,  # ¥249
            "duration_days": 90,
            "features": '["PPT生成无限制", "20+模板任意用", "品牌定制", "导出高清PDF", "专属客服支持", "优先生成队列"]'
        },
        {
            "plan_code": "yearly",
            "name": "年卡",
            "description": "年度订阅，最大优惠",
            "price": 79900,  # ¥799
            "duration_days": 365,
            "features": '["PPT生成无限制", "20+模板任意用", "品牌定制", "导出高清PDF", "专属客服支持", "优先生成队列", "专属模板定制", "API接口调用"]'
        }
    ]
    
    for plan in default_plans:
        cursor.execute("""
            INSERT OR IGNORE INTO plans (plan_code, name, description, price, duration_days, features)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (plan["plan_code"], plan["name"], plan["description"], 
              plan["price"], plan["duration_days"], plan["features"]))
    
    conn.commit()
    conn.close()


def generate_order_id() -> str:
    """生成订单号"""
    return f"DPT{datetime.now().strftime('%Y%m%d%H%M%S')}{secrets.token_hex(4).upper()}"


def get_all_plans() -> List[dict]:
    """获取所有上架套餐"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plans WHERE status = 1 ORDER BY price ASC")
    rows = cursor.fetchall()
    conn.close()
    
    plans = []
    for row in rows:
        p = dict(row)
        p["features"] = eval(p["features"]) if isinstance(p["features"], str) else p["features"]
        # 转换为元
        p["price_yuan"] = p["price"] / 100
        plans.append(p)
    
    return plans


def get_plan(plan_code: str) -> Optional[dict]:
    """获取指定套餐"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM plans WHERE plan_code = ? AND status = 1", (plan_code,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        p = dict(row)
        p["features"] = eval(p["features"]) if isinstance(p["features"], str) else p["features"]
        p["price_yuan"] = p["price"] / 100
        return p
    return None


def create_subscription(user_id: int, plan_code: str, payment_method: str = "wechat") -> dict:
    """创建订阅（生成订单）"""
    plan = get_plan(plan_code)
    if not plan:
        return {"success": False, "error": "套餐不存在"}
    
    order_id = generate_order_id()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 创建订单
    cursor.execute("""
        INSERT INTO orders (order_id, user_id, plan_code, amount, payment_method, status)
        VALUES (?, ?, ?, ?, ?, 'pending')
    """, (order_id, user_id, plan_code, plan["price"], payment_method))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "order_id": order_id,
        "amount": plan["price"],
        "amount_yuan": plan["price"] / 100,
        "plan_name": plan["name"],
        "message": "订单已创建"
    }


def pay_order(order_id: str, transaction_id: str = "") -> dict:
    """支付订单"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取订单信息
    cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
    order = cursor.fetchone()
    
    if not order:
        conn.close()
        return {"success": False, "error": "订单不存在"}
    
    if order["status"] == "paid":
        conn.close()
        return {"success": False, "error": "订单已支付"}
    
    # 更新订单状态
    cursor.execute("""
        UPDATE orders SET status = 'paid', transaction_id = ?, paid_time = CURRENT_TIMESTAMP
        WHERE order_id = ?
    """, (transaction_id, order_id))
    
    # 创建/更新订阅
    plan = get_plan(order["plan_code"])
    if plan:
        # 检查用户是否已有订阅
        cursor.execute("""
            SELECT id, end_time FROM subscriptions 
            WHERE user_id = ? AND status = 'active'
            ORDER BY end_time DESC LIMIT 1
        """, (order["user_id"],))
        existing = cursor.fetchone()
        
        if existing:
            # 累加时间
            end_time = datetime.fromisoformat(existing["end_time"])
            if datetime.now() > end_time:
                # 订阅已过期，从现在开始
                start_time = datetime.now()
                end_time = start_time + timedelta(days=plan["duration_days"])
            else:
                # 订阅未过期，累加
                start_time = end_time
                end_time = end_time + timedelta(days=plan["duration_days"])
        else:
            # 新建订阅
            start_time = datetime.now()
            end_time = start_time + timedelta(days=plan["duration_days"])
        
        cursor.execute("""
            INSERT INTO subscriptions (user_id, plan_code, status, start_time, end_time, order_id, total_paid)
            VALUES (?, ?, 'active', ?, ?, ?, ?)
        """, (order["user_id"], order["plan_code"], start_time, end_time, order_id, order["amount"]))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "支付成功",
        "order_id": order_id
    }


def get_user_subscription(user_id: int) -> Optional[dict]:
    """获取用户当前订阅"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.*, p.name as plan_name, p.features
        FROM subscriptions s
        JOIN plans p ON s.plan_code = p.plan_code
        WHERE s.user_id = ? AND s.status = 'active'
        ORDER BY s.end_time DESC LIMIT 1
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    sub = dict(row)
    sub["features"] = eval(sub["features"]) if isinstance(sub["features"], str) else sub["features"]
    
    # 检查是否过期
    end_time = datetime.fromisoformat(sub["end_time"])
    if datetime.now() > end_time:
        sub["is_expired"] = True
        sub["days_remaining"] = 0
    else:
        sub["is_expired"] = False
        sub["days_remaining"] = (end_time - datetime.now()).days
    
    return sub


def check_user_access(user_id: int) -> dict:
    """检查用户访问权限"""
    sub = get_user_subscription(user_id)
    
    if not sub or sub.get("is_expired"):
        return {
            "has_access": False,
            "reason": "未订阅或订阅已过期",
            "subscription": sub,
            "plans": get_all_plans()
        }
    
    return {
        "has_access": True,
        "subscription": sub,
        "features": sub.get("features", [])
    }


def cancel_subscription(user_id: int) -> dict:
    """取消订阅（关闭自动续费）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE subscriptions SET auto_renew = 0, update_time = CURRENT_TIMESTAMP
        WHERE user_id = ? AND status = 'active'
    """, (user_id,))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "已取消自动续费"}


def get_user_orders(user_id: int) -> List[dict]:
    """获取用户订单列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, p.name as plan_name
        FROM orders o
        JOIN plans p ON o.plan_code = p.plan_code
        WHERE o.user_id = ?
        ORDER BY o.create_time DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    orders = []
    for row in rows:
        o = dict(row)
        o["amount_yuan"] = o["amount"] / 100
        orders.append(o)
    
    return orders


# 初始化数据库
init_db()


if __name__ == "__main__":
    print("=== 订阅系统测试 ===")
    
    # 获取套餐列表
    plans = get_all_plans()
    print("\n可用套餐:")
    for p in plans:
        print(f"  {p['name']}: ¥{p['price_yuan']} ({p['duration_days']}天)")
    
    # 测试创建订单
    r = create_subscription(user_id=1, plan_code="monthly")
    print(f"\n创建订单: {r}")
    
    # 测试支付
    if r["success"]:
        r2 = pay_order(r["order_id"], "WX" + datetime.now().strftime("%Y%m%d%H%M%S"))
        print(f"支付订单: {r2}")
    
    # 测试权限检查
    access = check_user_access(user_id=1)
    print(f"\n权限检查: {access}")
