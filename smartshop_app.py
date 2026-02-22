import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime, timedelta
import random

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
</style>
""", unsafe_allow_html=True)

# ─── SUPABASE CONNECTION ────────────────────────────────────────
SUPABASE_URL = "https://ejktmvidjinjbhrypuok.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVqa3RtdmlkamluamJocnlwdW9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3NTczMDIsImV4cCI6MjA4NzMzMzMwMn0.NyW3Co7htF_wNmA5jEpVTfWgXW2wPCI-7n5kKijCem8"

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# ─── SEED DATA ─────────────────────────────────────────────────
def seed_data():
    inv = supabase.table("inventory").select("id").execute()
    if not inv.data:
        items = [
            {"name": "Rice (5kg)", "category": "Grains", "stock": 12, "min_stock": 20, "max_stock": 100, "price": 850, "cost": 700, "unit": "bags", "supplier": "Supplier A", "expire_date": "2025-12-01"},
            {"name": "Sugar (1kg)", "category": "Essentials", "stock": 34, "min_stock": 15, "max_stock": 80, "price": 190, "cost": 150, "unit": "packs", "supplier": "Supplier A", "expire_date": "2025-10-01"},
            {"name": "Coconut Oil (1L)", "category": "Oils", "stock": 8, "min_stock": 10, "max_stock": 50, "price": 480, "cost": 400, "unit": "bottles", "supplier": "Supplier B", "expire_date": "2026-03-01"},
            {"name": "Milk Powder (400g)", "category": "Dairy", "stock": 25, "min_stock": 10, "max_stock": 60, "price": 650, "cost": 540, "unit": "tins", "supplier": "Supplier C", "expire_date": "2025-11-01"},
            {"name": "Biscuits (200g)", "category": "Snacks", "stock": 60, "min_stock": 20, "max_stock": 100, "price": 120, "cost": 90, "unit": "packs", "supplier": "Supplier B", "expire_date": "2025-09-15"},
            {"name": "Soap Bar", "category": "Toiletries", "stock": 5, "min_stock": 15, "max_stock": 60, "price": 85, "cost": 65, "unit": "bars", "supplier": "Supplier D", "expire_date": "2026-06-01"},
        ]
        supabase.table("inventory").insert(items).execute()

    cust = supabase.table("customers").select("id").execute()
    if not cust.data:
        customers = [
            {"name": "Kumari Silva", "phone": "071-234-5678", "points": 1250, "total_spent": 42000, "joined_date": "2024-01-15"},
            {"name": "Nimal Perera", "phone": "077-876-5432", "points": 980, "total_spent": 35000, "joined_date": "2024-02-20"},
            {"name": "Sanduni De Silva", "phone": "076-555-0101", "points": 720, "total_spent": 28000, "joined_date": "2024-03-10"},
            {"name": "Kamal Fernando", "phone": "070-111-2222", "points": 540, "total_spent": 18000, "joined_date": "2024-04-05"},
        ]
        supabase.table("customers").insert(customers).execute()

    sup = supabase.table("suppliers").select("id").execute()
    if not sup.data:
        suppliers = [
            {"name": "Supplier A", "phone": "011-234-5678", "email": "supplierA@gmail.com", "items": "Rice, Sugar"},
            {"name": "Supplier B", "phone": "011-876-5432", "email": "supplierB@gmail.com", "items": "Biscuits, Coconut Oil"},
            {"name": "Supplier C", "phone": "011-555-0101", "email": "supplierC@gmail.com", "items": "Milk Powder"},
            {"name": "Supplier D", "phone": "011-111-2222", "email": "supplierD@gmail.com", "items": "Soap, Shampoo"},
        ]
        supabase.table("suppliers").insert(suppliers).execute()

    sales = supabase.table("sales").select("id").execute()
    if not sales.data:
        sale_items = [
            ("Rice (5kg)", 850), ("Sugar (1kg)", 190),
            ("Biscuits (200g)", 120), ("Milk Powder (400g)", 650), ("Coconut Oil (1L)", 480)
        ]
        records = []
        for i in range(30):
            date = (datetime.now() - timedelta(days=i % 14)).strftime("%Y-%m-%d")
            item, price = random.choice(sale_items)
            qty = random.randint(1, 6)
            records.append({"item_name": item, "quantity": qty, "total": qty * price, "date": date})
        supabase.table("sales").insert(records).execute()

seed_data()

# ─── AI PREDICTION ──────────────────────────────────────────────
def predict_demand(item_name):
    data = supabase.table("sales").select("quantity").eq("item_name", item_name).execute()
    if not data.data:
        return 0
    total = sum([r["quantity"] for r in data.data])
    avg = total / max(len(data.data), 1)
    return round(avg * 7)

# ─── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 SmartShop AI")
    st.markdown("*Intelligent Grocery Manager*")
    st.divider()
    page = st.radio("Navigate", ["📊 Dashboard", "📦 Inventory", "💰 Sales Report", "🚚 Suppliers", "🎁 Loyalty"])
    st.divider()
    st.markdown(f"**Date:** {datetime.now().strftime('%d %b %Y')}")
    st.markdown("**Shop:** Pehesara Grocery")

# ══════════════════════════════════════════════════════════════
# 📊 DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption(f"Good morning! Here's your shop summary for {datetime.now().strftime('%A, %d %B %Y')}")

    today = datetime.now().strftime("%Y-%m-%d")
    today_sales = supabase.table("sales").select("total").eq("date", today).execute()
    today_revenue = sum([r["total"] for r in today_sales.data]) if today_sales.data else 0
    today_count = len(today_sales.data)

    all_inv = supabase.table("inventory").select("*").execute().data
    low_stock = [i for i in all_inv if i["stock"] < i["min_stock"]]
    all_customers = supabase.table("customers").select("id").execute().data

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Today's Earnings</div>
        <div class="metric-value" style="color:#00E5BE">Rs. {today_revenue:,.0f}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Today's Sales</div>
        <div class="metric-value">{today_count}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Low Stock Items</div>
        <div class="metric-value" style="color:#FF6B35">{len(low_stock)}</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Customers</div>
        <div class="metric-value" style="color:#A78BFA">{len(all_customers)}</div></div>""", unsafe_allow_html=True)

    st.divider()

    st.subheader("⚠️ AI Alerts")
    if low_stock:
        for item in low_stock:
            st.markdown(f"""<div class="alert-box">🔴 <b>{item['name']}</b> — Stock low! ({item['stock']} remaining, min: {item['min_stock']}). Consider reordering.</div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="success-box">✅ All stock levels are sufficient!</div>""", unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 Weekly Earnings")
        all_sales = supabase.table("sales").select("date,total").execute().data
        if all_sales:
            df = pd.DataFrame(all_sales)
            df["date"] = pd.to_datetime(df["date"])
            weekly = df[df["date"] >= datetime.now() - timedelta(days=7)]
            if not weekly.empty:
                st.bar_chart(weekly.groupby("date")["total"].sum())

    with col2:
        st.subheader("🤖 AI Demand Predictions (7 days)")
        inv_names = [i["name"] for i in all_inv]
        pred_df = pd.DataFrame([{"Item": n, "Predicted Units": predict_demand(n)} for n in inv_names])
        st.dataframe(pred_df, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════
# 📦 INVENTORY
# ══════════════════════════════════════════════════════════════
elif page == "📦 Inventory":
    st.title("📦 Inventory Management")
    tab1, tab2 = st.tabs(["📋 View Stock", "➕ Add Item"])

    with tab1:
        inv_data = supabase.table("inventory").select("*").execute().data
        if inv_data:
            df = pd.DataFrame(inv_data)
            df["Status"] = df.apply(lambda r: "🔴 Low" if r["stock"] < r["min_stock"] else "🟢 OK", axis=1)
            df["Stock %"] = (df["stock"] / df["max_stock"] * 100).round(0).astype(int)
            filter_s = st.selectbox("Filter", ["All", "Low Stock Only", "OK Only"])
            if filter_s == "Low Stock Only":
                df = df[df["Status"] == "🔴 Low"]
            elif filter_s == "OK Only":
                df = df[df["Status"] == "🟢 OK"]
            st.dataframe(df[["name", "category", "stock", "min_stock", "max_stock", "price", "supplier", "Status", "Stock %"]], use_container_width=True, hide_index=True)

    with tab2:
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
            if st.form_submit_button("➕ Add Item", use_container_width=True) and name:
                supabase.table("inventory").insert({"name": name, "category": category, "stock": stock, "min_stock": min_stock, "max_stock": max_stock, "price": price, "cost": cost, "unit": "units", "supplier": supplier}).execute()
                st.success(f"✅ '{name}' added!")
                st.rerun()

# ══════════════════════════════════════════════════════════════
# 💰 SALES REPORT
# ══════════════════════════════════════════════════════════════
elif page == "💰 Sales Report":
    st.title("💰 Sales Report & Analytics")

    all_sales = supabase.table("sales").select("*").execute().data
    df_sales = pd.DataFrame(all_sales) if all_sales else pd.DataFrame()

    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    week_rev = df_sales[df_sales["date"] >= week_ago]["total"].sum() if not df_sales.empty else 0
    month_rev = df_sales[df_sales["date"] >= month_ago]["total"].sum() if not df_sales.empty else 0
    total_rev = df_sales["total"].sum() if not df_sales.empty else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">This Week</div>
        <div class="metric-value" style="color:#00E5BE">Rs. {week_rev:,.0f}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">This Month</div>
        <div class="metric-value" style="color:#A78BFA">Rs. {month_rev:,.0f}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">All Time</div>
        <div class="metric-value">Rs. {total_rev:,.0f}</div></div>""", unsafe_allow_html=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Daily Revenue")
        if not df_sales.empty:
            daily = df_sales.groupby("date")["total"].sum().sort_index()
            st.line_chart(daily)

    with col2:
        st.subheader("🏆 Top Selling Items")
        if not df_sales.empty:
            top = df_sales.groupby("item_name").agg({"quantity": "sum", "total": "sum"}).reset_index()
            top.columns = ["Item", "Units Sold", "Revenue (Rs.)"]
            st.dataframe(top.sort_values("Revenue (Rs.)", ascending=False), use_container_width=True, hide_index=True)

    st.subheader("➕ Record New Sale")
    inv_data = supabase.table("inventory").select("name,price,stock,id").execute().data
    if inv_data:
        with st.form("record_sale"):
            item_names = [i["name"] for i in inv_data]
            col1, col2 = st.columns(2)
            with col1:
                item = st.selectbox("Item", item_names)
                qty = st.number_input("Quantity", min_value=1, value=1)
            with col2:
                selected_item = next((i for i in inv_data if i["name"] == item), None)
                price = selected_item["price"] if selected_item else 0
                st.metric("Unit Price", f"Rs. {price:.0f}")
                st.metric("Total", f"Rs. {price * qty:.0f}")
            if st.form_submit_button("💾 Record Sale", use_container_width=True):
                supabase.table("sales").insert({"item_name": item, "quantity": qty, "total": price * qty, "date": datetime.now().strftime("%Y-%m-%d")}).execute()
                new_stock = (selected_item["stock"] - qty)
                supabase.table("inventory").update({"stock": new_stock}).eq("id", selected_item["id"]).execute()
                st.success(f"✅ Sale recorded! Rs. {price * qty:.0f}")
                st.rerun()

# ══════════════════════════════════════════════════════════════
# 🚚 SUPPLIERS
# ══════════════════════════════════════════════════════════════
elif page == "🚚 Suppliers":
    st.title("🚚 Supplier Management")
    st.markdown("""<div class="success-box">🤖 AI Auto-Order: Enabled</div>""", unsafe_allow_html=True)

    st.subheader("⚠️ AI Suggested Orders")
    inv_data = supabase.table("inventory").select("*").execute().data
    low = [i for i in inv_data if i["stock"] < i["min_stock"]]

    if low:
        for item in low:
            order_qty = item["max_stock"] - item["stock"]
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"""<div class="alert-box">📦 <b>{item['name']}</b> — Order {order_qty} units from {item['supplier']}</div>""", unsafe_allow_html=True)
            with col2:
                if st.button("✅ Order", key=f"order_{item['id']}"):
                    supabase.table("inventory").update({"stock": item["max_stock"]}).eq("id", item["id"]).execute()
                    st.success("Ordered!")
                    st.rerun()
    else:
        st.markdown("""<div class="success-box">✅ No urgent orders needed!</div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 All Suppliers")
    sup_data = supabase.table("suppliers").select("*").execute().data
    if sup_data:
        st.dataframe(pd.DataFrame(sup_data)[["name", "phone", "email", "items"]], use_container_width=True, hide_index=True)

    st.subheader("➕ Add Supplier")
    with st.form("add_supplier"):
        col1, col2 = st.columns(2)
        with col1:
            s_name = st.text_input("Name")
            s_phone = st.text_input("Phone")
        with col2:
            s_email = st.text_input("Email")
            s_items = st.text_input("Items Supplied")
        if st.form_submit_button("➕ Add", use_container_width=True) and s_name:
            supabase.table("suppliers").insert({"name": s_name, "phone": s_phone, "email": s_email, "items": s_items}).execute()
            st.success(f"✅ {s_name} added!")
            st.rerun()

# ══════════════════════════════════════════════════════════════
# 🎁 LOYALTY
# ══════════════════════════════════════════════════════════════
elif page == "🎁 Loyalty":
    st.title("🎁 Customer Loyalty System")

    cust_data = supabase.table("customers").select("*").execute().data
    df_cust = pd.DataFrame(cust_data) if cust_data else pd.DataFrame()

    total_points = df_cust["points"].sum() if not df_cust.empty else 0
    total_spent = df_cust["total_spent"].sum() if not df_cust.empty else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Customers</div>
        <div class="metric-value" style="color:#00E5BE">{len(cust_data)}</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Points Issued</div>
        <div class="metric-value" style="color:#A78BFA">{int(total_points):,}</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Revenue</div>
        <div class="metric-value">Rs. {total_spent:,.0f}</div></div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("🏆 Customer Leaderboard")
    if not df_cust.empty:
        df_cust["Badge"] = df_cust["points"].apply(lambda p: "🥇 Gold" if p > 1000 else "🥈 Silver" if p > 700 else "🥉 Bronze" if p > 400 else "⭐ Member")
        st.dataframe(df_cust[["name", "phone", "points", "total_spent", "Badge"]].sort_values("points", ascending=False), use_container_width=True, hide_index=True)

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ Add Customer")
        with st.form("add_customer"):
            c_name = st.text_input("Name")
            c_phone = st.text_input("Phone")
            if st.form_submit_button("Add", use_container_width=True) and c_name:
                supabase.table("customers").insert({"name": c_name, "phone": c_phone, "points": 0, "total_spent": 0, "joined_date": datetime.now().strftime("%Y-%m-%d")}).execute()
                st.success(f"✅ {c_name} added!")
                st.rerun()

    with col2:
        st.subheader("🎁 Add Points")
        with st.form("add_points"):
            c_names = [c["name"] for c in cust_data] if cust_data else []
            selected = st.selectbox("Customer", c_names) if c_names else None
            purchase = st.number_input("Purchase Amount (Rs.)", min_value=0, value=500)
            points_earn = purchase // 10
            st.info(f"Will earn: {points_earn} points")
            if st.form_submit_button("Add Points", use_container_width=True) and selected:
                cust = next((c for c in cust_data if c["name"] == selected), None)
                if cust:
                    supabase.table("customers").update({"points": cust["points"] + points_earn, "total_spent": cust["total_spent"] + purchase}).eq("id", cust["id"]).execute()
                    st.success(f"✅ {points_earn} points added to {selected}!")
                    st.rerun()
