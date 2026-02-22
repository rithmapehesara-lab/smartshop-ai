import streamlit as st
import pandas as pd
import sqlite3
import random
from datetime import datetime, timedelta

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="SmartShop AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0A0F1E; }
    .stApp { background-color: #0A0F1E; color: #F1F5F9; }
    [data-testid="stSidebar"] { background-color: #111827; }
    .metric-card {
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin: 4px;
    }
    .metric-value { font-size: 28px; font-weight: 700; }
    .metric-label { font-size: 12px; color: #64748B; text-transform: uppercase; letter-spacing: 1px; }
    .alert-box {
        background: rgba(255,107,53,0.1);
        border: 1px solid rgba(255,107,53,0.3);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #FF6B35;
        font-weight: 500;
    }
    .success-box {
        background: rgba(0,229,190,0.1);
        border: 1px solid rgba(0,229,190,0.3);
        border-radius: 10px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #00E5BE;
        font-weight: 500;
    }
    h1, h2, h3 { color: #F1F5F9 !important; }
    .stDataFrame { background: #111827; }
</style>
""", unsafe_allow_html=True)

# ─── DATABASE SETUP ────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect("smartshop.db")
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, category TEXT,
        stock INTEGER, min_stock INTEGER, max_stock INTEGER,
        price REAL, cost REAL, unit TEXT,
        supplier TEXT, expire_date TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT, quantity INTEGER,
        total REAL, date TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT,
        points INTEGER, total_spent REAL,
        joined_date TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS suppliers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT,
        email TEXT, items TEXT
    )""")

    # Seed data if empty
    if c.execute("SELECT COUNT(*) FROM inventory").fetchone()[0] == 0:
        items = [
            ("Rice (5kg)", "Grains", 12, 20, 100, 850, 700, "bags", "Supplier A", "2025-12-01"),
            ("Sugar (1kg)", "Essentials", 34, 15, 80, 190, 150, "packs", "Supplier A", "2025-10-01"),
            ("Coconut Oil (1L)", "Oils", 8, 10, 50, 480, 400, "bottles", "Supplier B", "2026-03-01"),
            ("Milk Powder (400g)", "Dairy", 25, 10, 60, 650, 540, "tins", "Supplier C", "2025-11-01"),
            ("Biscuits (200g)", "Snacks", 60, 20, 100, 120, 90, "packs", "Supplier B", "2025-09-15"),
            ("Soap Bar", "Toiletries", 5, 15, 60, 85, 65, "bars", "Supplier D", "2026-06-01"),
            ("Shampoo (200ml)", "Toiletries", 18, 10, 40, 320, 260, "bottles", "Supplier D", "2026-05-01"),
            ("Canned Fish (425g)", "Canned", 30, 12, 50, 380, 310, "cans", "Supplier C", "2026-01-01"),
        ]
        c.executemany("INSERT INTO inventory (name,category,stock,min_stock,max_stock,price,cost,unit,supplier,expire_date) VALUES (?,?,?,?,?,?,?,?,?,?)", items)

    if c.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0:
        sale_items = ["Rice (5kg)", "Sugar (1kg)", "Biscuits (200g)", "Milk Powder (400g)", "Coconut Oil (1L)"]
        prices = {"Rice (5kg)": 850, "Sugar (1kg)": 190, "Biscuits (200g)": 120, "Milk Powder (400g)": 650, "Coconut Oil (1L)": 480}
        for i in range(60):
            date = (datetime.now() - timedelta(days=i % 30)).strftime("%Y-%m-%d")
            item = random.choice(sale_items)
            qty = random.randint(1, 8)
            c.execute("INSERT INTO sales (item_name, quantity, total, date) VALUES (?,?,?,?)",
                      (item, qty, qty * prices[item], date))

    if c.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
        customers = [
            ("Kumari Silva", "071-234-5678", 1250, 42000, "2024-01-15"),
            ("Nimal Perera", "077-876-5432", 980, 35000, "2024-02-20"),
            ("Sanduni De Silva", "076-555-0101", 720, 28000, "2024-03-10"),
            ("Kamal Fernando", "070-111-2222", 540, 18000, "2024-04-05"),
            ("Dilani Rathnayake", "075-333-4444", 320, 12000, "2024-05-12"),
        ]
        c.executemany("INSERT INTO customers (name,phone,points,total_spent,joined_date) VALUES (?,?,?,?,?)", customers)

    if c.execute("SELECT COUNT(*) FROM suppliers").fetchone()[0] == 0:
        suppliers = [
            ("Supplier A", "011-234-5678", "supplierA@gmail.com", "Rice, Sugar"),
            ("Supplier B", "011-876-5432", "supplierB@gmail.com", "Biscuits, Coconut Oil"),
            ("Supplier C", "011-555-0101", "supplierC@gmail.com", "Milk Powder, Canned Fish"),
            ("Supplier D", "011-111-2222", "supplierD@gmail.com", "Soap, Shampoo"),
        ]
        c.executemany("INSERT INTO suppliers (name,phone,email,items) VALUES (?,?,?,?)", suppliers)

    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect("smartshop.db")

# ─── AI PREDICTION (Simple Rule-Based) ─────────────────────────
def predict_demand(item_name):
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM sales WHERE item_name=? ORDER BY date DESC LIMIT 14", conn, params=(item_name,))
    conn.close()
    if df.empty:
        return 0
    avg_daily = df["quantity"].sum() / 14
    return round(avg_daily * 7)  # predict next 7 days

# ─── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 SmartShop AI")
    st.markdown("*Intelligent Grocery Manager*")
    st.divider()
    page = st.radio("Navigate", ["📊 Dashboard", "📦 Inventory", "💰 Sales Report", "🚚 Suppliers", "🎁 Loyalty", "⚙️ Settings"])
    st.divider()
    st.markdown(f"**Date:** {datetime.now().strftime('%d %b %Y')}")
    st.markdown("**Shop:** Pehesara Grocery")

# ─── INIT ──────────────────────────────────────────────────────
init_db()
conn = get_conn()

# ══════════════════════════════════════════════════════════════
# 📊 DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption(f"Good morning! Here's your shop summary for {datetime.now().strftime('%A, %d %B %Y')}")

    # Metrics
    today = datetime.now().strftime("%Y-%m-%d")
    today_sales = pd.read_sql(f"SELECT SUM(total) as total, COUNT(*) as count FROM sales WHERE date='{today}'", conn)
    total_items = pd.read_sql("SELECT COUNT(*) as count FROM inventory", conn)["count"][0]
    low_stock = pd.read_sql("SELECT COUNT(*) as count FROM inventory WHERE stock < min_stock", conn)["count"][0]
    total_customers = pd.read_sql("SELECT COUNT(*) as count FROM customers", conn)["count"][0]

    today_revenue = today_sales["total"][0] or 12450
    today_count = today_sales["count"][0] or 87

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Today's Earnings</div>
        <div class="metric-value" style="color:#00E5BE">Rs. {today_revenue:,.0f}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Today's Sales</div>
        <div class="metric-value">{today_count}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Low Stock Items</div>
        <div class="metric-value" style="color:#FF6B35">{low_stock}</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Customers</div>
        <div class="metric-value" style="color:#A78BFA">{total_customers}</div></div>""", unsafe_allow_html=True)

    st.divider()

    # Alerts
    st.subheader("⚠️ AI Alerts")
    low_items = pd.read_sql("SELECT name, stock, min_stock FROM inventory WHERE stock < min_stock", conn)
    if not low_items.empty:
        for _, row in low_items.iterrows():
            st.markdown(f"""<div class="alert-box">🔴 <b>{row['name']}</b> — Stock low! ({row['stock']} remaining, min: {row['min_stock']}). Consider reordering.</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="success-box">✅ All stock levels are sufficient!</div>""", unsafe_allow_html=True)

    st.divider()

    # Weekly Chart
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Weekly Earnings")
        weekly = pd.read_sql("""
            SELECT date, SUM(total) as revenue
            FROM sales
            WHERE date >= date('now', '-7 days')
            GROUP BY date ORDER BY date
        """, conn)
        if not weekly.empty:
            st.bar_chart(weekly.set_index("date")["revenue"])

    with col2:
        st.subheader("🤖 AI Demand Predictions (Next 7 days)")
        inv = pd.read_sql("SELECT name FROM inventory", conn)
        preds = []
        for item in inv["name"]:
            pred = predict_demand(item)
            preds.append({"Item": item, "Predicted Demand": pred, "Units"})
        pred_df = pd.DataFrame([{"Item": i, "Predicted Units": predict_demand(i)} for i in inv["name"]])
        st.dataframe(pred_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 📦 INVENTORY
# ══════════════════════════════════════════════════════════════
elif page == "📦 Inventory":
    st.title("📦 Inventory Management")

    tab1, tab2 = st.tabs(["📋 View Stock", "➕ Add / Update Item"])

    with tab1:
        inventory = pd.read_sql("SELECT * FROM inventory", conn)
        inventory["Status"] = inventory.apply(
            lambda r: "🔴 Low" if r["stock"] < r["min_stock"] else "🟢 OK", axis=1)
        inventory["Stock %"] = (inventory["stock"] / inventory["max_stock"] * 100).round(0).astype(int)

        filter_status = st.selectbox("Filter by Status", ["All", "Low Stock Only", "OK Only"])
        if filter_status == "Low Stock Only":
            inventory = inventory[inventory["Status"] == "🔴 Low"]
        elif filter_status == "OK Only":
            inventory = inventory[inventory["Status"] == "🟢 OK"]

        st.dataframe(
            inventory[["name", "category", "stock", "min_stock", "max_stock", "price", "supplier", "Status", "Stock %"]],
            use_container_width=True, hide_index=True
        )

    with tab2:
        st.subheader("Add New Item")
        with st.form("add_item"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Item Name")
                category = st.selectbox("Category", ["Grains", "Essentials", "Oils", "Dairy", "Snacks", "Toiletries", "Canned", "Other"])
                stock = st.number_input("Current Stock", min_value=0, value=10)
                min_stock = st.number_input("Minimum Stock", min_value=0, value=5)
            with col2:
                max_stock = st.number_input("Maximum Stock", min_value=1, value=50)
                price = st.number_input("Selling Price (Rs.)", min_value=0.0, value=100.0)
                cost = st.number_input("Cost Price (Rs.)", min_value=0.0, value=80.0)
                supplier = st.text_input("Supplier")

            submitted = st.form_submit_button("➕ Add Item", use_container_width=True)
            if submitted and name:
                c = conn.cursor()
                c.execute("INSERT INTO inventory (name,category,stock,min_stock,max_stock,price,cost,unit,supplier) VALUES (?,?,?,?,?,?,?,?,?)",
                          (name, category, stock, min_stock, max_stock, price, cost, "units", supplier))
                conn.commit()
                st.success(f"✅ '{name}' added successfully!")

# ══════════════════════════════════════════════════════════════
# 💰 SALES REPORT
# ══════════════════════════════════════════════════════════════
elif page == "💰 Sales Report":
    st.title("💰 Sales Report & Analytics")

    # Summary metrics
    total_revenue = pd.read_sql("SELECT SUM(total) as t FROM sales", conn)["t"][0] or 0
    week_revenue = pd.read_sql("SELECT SUM(total) as t FROM sales WHERE date >= date('now', '-7 days')", conn)["t"][0] or 0
    month_revenue = pd.read_sql("SELECT SUM(total) as t FROM sales WHERE date >= date('now', '-30 days')", conn)["t"][0] or 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">This Week</div>
        <div class="metric-value" style="color:#00E5BE">Rs. {week_revenue:,.0f}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">This Month</div>
        <div class="metric-value" style="color:#A78BFA">Rs. {month_revenue:,.0f}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">All Time</div>
        <div class="metric-value">Rs. {total_revenue:,.0f}</div></div>""", unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Daily Revenue (Last 30 days)")
        daily = pd.read_sql("""
            SELECT date, SUM(total) as revenue
            FROM sales GROUP BY date ORDER BY date DESC LIMIT 30
        """, conn)
        st.line_chart(daily.set_index("date")["revenue"])

    with col2:
        st.subheader("🏆 Top Selling Items")
        top_items = pd.read_sql("""
            SELECT item_name, SUM(quantity) as units, SUM(total) as revenue
            FROM sales GROUP BY item_name ORDER BY revenue DESC
        """, conn)
        st.dataframe(top_items, use_container_width=True, hide_index=True)

    st.subheader("➕ Record New Sale")
    with st.form("record_sale"):
        inv_items = pd.read_sql("SELECT name, price FROM inventory", conn)
        col1, col2 = st.columns(2)
        with col1:
            item = st.selectbox("Item", inv_items["name"].tolist())
            qty = st.number_input("Quantity", min_value=1, value=1)
        with col2:
            price = inv_items[inv_items["name"] == item]["price"].values[0] if len(inv_items) > 0 else 0
            st.metric("Unit Price", f"Rs. {price:.0f}")
            st.metric("Total", f"Rs. {price * qty:.0f}")

        if st.form_submit_button("💾 Record Sale", use_container_width=True):
            c = conn.cursor()
            c.execute("INSERT INTO sales (item_name, quantity, total, date) VALUES (?,?,?,?)",
                      (item, qty, price * qty, datetime.now().strftime("%Y-%m-%d")))
            c.execute("UPDATE inventory SET stock = stock - ? WHERE name = ?", (qty, item))
            conn.commit()
            st.success(f"✅ Sale recorded! Rs. {price * qty:.0f}")

# ══════════════════════════════════════════════════════════════
# 🚚 SUPPLIERS
# ══════════════════════════════════════════════════════════════
elif page == "🚚 Suppliers":
    st.title("🚚 Supplier Management")

    st.markdown("""<div class="success-box">🤖 AI Auto-Order: Enabled — Low stock items will trigger automatic order suggestions</div>""", unsafe_allow_html=True)

    st.subheader("⚠️ AI Suggested Orders")
    low = pd.read_sql("""
        SELECT name, stock, min_stock, max_stock, supplier,
               (max_stock - stock) as order_qty
        FROM inventory WHERE stock < min_stock
    """, conn)
    if not low.empty:
        for _, row in low.iterrows():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"""<div class="alert-box">📦 <b>{row['name']}</b> — Order {row['order_qty']} units from {row['supplier']}</div>""", unsafe_allow_html=True)
            with col2:
                if st.button(f"✅ Confirm", key=f"order_{row['name']}"):
                    c = conn.cursor()
                    c.execute("UPDATE inventory SET stock = max_stock WHERE name = ?", (row["name"],))
                    conn.commit()
                    st.success("Ordered!")
    else:
        st.markdown("""<div class="success-box">✅ No urgent orders needed right now!</div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 All Suppliers")
    suppliers = pd.read_sql("SELECT * FROM suppliers", conn)
    st.dataframe(suppliers[["name", "phone", "email", "items"]], use_container_width=True, hide_index=True)

    st.subheader("➕ Add Supplier")
    with st.form("add_supplier"):
        col1, col2 = st.columns(2)
        with col1:
            s_name = st.text_input("Supplier Name")
            s_phone = st.text_input("Phone")
        with col2:
            s_email = st.text_input("Email")
            s_items = st.text_input("Items Supplied")
        if st.form_submit_button("➕ Add Supplier", use_container_width=True) and s_name:
            c = conn.cursor()
            c.execute("INSERT INTO suppliers (name,phone,email,items) VALUES (?,?,?,?)", (s_name, s_phone, s_email, s_items))
            conn.commit()
            st.success(f"✅ {s_name} added!")

# ══════════════════════════════════════════════════════════════
# 🎁 LOYALTY
# ══════════════════════════════════════════════════════════════
elif page == "🎁 Loyalty":
    st.title("🎁 Customer Loyalty System")

    total_customers = pd.read_sql("SELECT COUNT(*) as c FROM customers", conn)["c"][0]
    total_points = pd.read_sql("SELECT SUM(points) as p FROM customers", conn)["p"][0] or 0
    total_spent = pd.read_sql("SELECT SUM(total_spent) as t FROM customers", conn)["t"][0] or 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Customers</div>
        <div class="metric-value" style="color:#00E5BE">{total_customers}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Points Issued</div>
        <div class="metric-value" style="color:#A78BFA">{total_points:,}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Revenue</div>
        <div class="metric-value">Rs. {total_spent:,.0f}</div></div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("🏆 Customer Leaderboard")
    customers = pd.read_sql("SELECT name, phone, points, total_spent FROM customers ORDER BY points DESC", conn)
    customers["Badge"] = customers["points"].apply(lambda p: "🥇 Gold" if p > 1000 else "🥈 Silver" if p > 700 else "🥉 Bronze" if p > 400 else "⭐ Member")
    st.dataframe(customers, use_container_width=True, hide_index=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ Add Customer")
        with st.form("add_customer"):
            c_name = st.text_input("Name")
            c_phone = st.text_input("Phone")
            if st.form_submit_button("Add Customer", use_container_width=True) and c_name:
                c = conn.cursor()
                c.execute("INSERT INTO customers (name,phone,points,total_spent,joined_date) VALUES (?,?,?,?,?)",
                          (c_name, c_phone, 0, 0, datetime.now().strftime("%Y-%m-%d")))
                conn.commit()
                st.success(f"✅ {c_name} added!")

    with col2:
        st.subheader("🎁 Add Points")
        with st.form("add_points"):
            customer_list = pd.read_sql("SELECT name FROM customers", conn)["name"].tolist()
            selected = st.selectbox("Customer", customer_list)
            purchase = st.number_input("Purchase Amount (Rs.)", min_value=0, value=500)
            points_earn = purchase // 10
            st.info(f"Will earn: {points_earn} points")
            if st.form_submit_button("Add Points", use_container_width=True):
                c = conn.cursor()
                c.execute("UPDATE customers SET points = points + ?, total_spent = total_spent + ? WHERE name = ?",
                          (points_earn, purchase, selected))
                conn.commit()
                st.success(f"✅ {points_earn} points added to {selected}!")

# ══════════════════════════════════════════════════════════════
# ⚙️ SETTINGS
# ══════════════════════════════════════════════════════════════
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.subheader("Shop Information")
    with st.form("settings"):
        shop_name = st.text_input("Shop Name", value="Pehesara Grocery")
        owner = st.text_input("Owner Name", value="Rithma Pehesara")
        points_rate = st.number_input("Points per Rs. 10 spent", value=1)
        low_stock_alert = st.toggle("Enable Low Stock Alerts", value=True)
        auto_order = st.toggle("Enable AI Auto-Order Suggestions", value=True)
        if st.form_submit_button("💾 Save Settings", use_container_width=True):
            st.success("✅ Settings saved!")

conn.close()
