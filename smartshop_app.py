import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import requests as req
from supabase import create_client
from datetime import datetime, timedelta
import random

# ─── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="SmartShop AI",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0A0F1E; color: #F1F5F9; }
    [data-testid="stSidebar"] { display: none; }
    [data-testid="collapsedControl"] { display: none; }
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
    .main .block-container { padding-bottom: 90px !important; }

    /* Bottom Nav Bar */
    .bottom-nav {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        background: #111827;
        border-top: 1px solid #1E293B;
        border-radius: 20px 20px 0 0;
        display: flex;
        justify-content: space-around;
        align-items: center;
        padding: 10px 0 16px;
        z-index: 9999;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.4);
    }
    .nav-btn {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 3px;
        padding: 8px 16px;
        border-radius: 12px;
        cursor: pointer;
        text-decoration: none;
        font-size: 10px;
        color: #64748B;
        font-family: sans-serif;
        transition: all 0.2s;
    }
    .nav-btn.active {
        background: rgba(0,229,190,0.1);
        color: #00E5BE;
    }
    .nav-icon { font-size: 22px; }

    /* Radio buttons hidden - we use custom nav */
    div[data-testid="stRadio"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─── SUPABASE CONNECTION ────────────────────────────────────────
SUPABASE_URL = "https://ejktmvidjinjbhrypuok.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVqa3RtdmlkamluamJocnlwdW9rIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE3NTczMDIsImV4cCI6MjA4NzMzMzMwMn0.NyW3Co7htF_wNmA5jEpVTfWgXW2wPCI-7n5kKijCem8"

@st.cache_resource
def get_supabase():
    import httpx
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return client

try:
    supabase = get_supabase()
except Exception:
    st.cache_resource.clear()
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

import time
for _attempt in range(3):
    try:
        seed_data()
        break
    except Exception:
        if _attempt < 2:
            time.sleep(2)
        else:
            st.warning("⚠️ Database slow — refresh page!")

# ─── AI PREDICTION ──────────────────────────────────────────────
def predict_demand(item_name):
    data = supabase.table("sales").select("quantity").eq("item_name", item_name).execute()
    if not data.data:
        return 0
    total = sum([r["quantity"] for r in data.data])
    avg = total / max(len(data.data), 1)
    return round(avg * 7)

# ─── NAVIGATION ────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "📊 Dashboard"
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "currency" not in st.session_state:
    st.session_state.currency = "LKR"
if "currency_rate" not in st.session_state:
    st.session_state.currency_rate = 1.0

page = st.session_state.page

# Theme colors
_tc = {
    "dark":  {"bg":"#0A0F1E","card":"#111827","text":"#F1F5F9","sub":"#475569","border":"#1E293B"},
    "light": {"bg":"#F1F5F9","card":"#FFFFFF","text":"#0A0F1E","sub":"#64748B","border":"#E2E8F0"},
}
_t = _tc[st.session_state.theme]

st.markdown(f"""
<style>
.stApp {{ background-color: {_t["bg"]} !important; color: {_t["text"]} !important; }}
.metric-card {{ background: {_t["card"]}; border-color: {_t["border"]}; }}
div[data-testid="stMarkdownContainer"] p {{ color: {_t["text"]} !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="collapsedControl"], footer { display:none !important; }
.main .block-container { padding-top: 6px !important; }
div[data-testid="stHorizontalBlock"] button {
    background: rgba(17,24,39,0.9) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    color: #475569 !important;
    font-size: 11px !important;
    font-weight: 700 !important;
    border-radius: 20px !important;
    padding: 10px 2px !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stHorizontalBlock"] button:hover {
    background: rgba(0,229,190,0.1) !important;
    color: #00E5BE !important;
}
div[data-testid="stHorizontalBlock"] button p { font-size: 11px !important; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

# Currency helper
_SYMBOLS = {"LKR": "Rs.", "USD": "$", "EUR": "€", "GBP": "£", "INR": "₹"}
_RATES   = {"LKR": 1.0, "USD": 0.0031, "EUR": 0.0029, "GBP": 0.0025, "INR": 0.26}

def fmt_money(amount_lkr):
    cur = st.session_state.currency
    sym = _SYMBOLS.get(cur, "Rs.")
    rate = _RATES.get(cur, 1.0)
    converted = amount_lkr * rate
    return f"{sym} {converted:,.2f}" if cur != "LKR" else f"Rs. {converted:,.0f}"

# Header
st.markdown(f"""
<div style="padding:8px 0 4px;">
    <div style="font-size:21px;font-weight:800;color:#00E5BE;">🛒 SmartShop AI</div>
    <div style="font-size:11px;color:#475569;">{datetime.now().strftime('%A, %d %B %Y')} · Pehesara Grocery</div>
</div>
""", unsafe_allow_html=True)

# Nav bar - single unified pill
nav_labels = ["📊 Home", "📦 Stock", "💰 Sales", "🚚 Orders", "🎁 Loyal", "🤖 AI"]
nav_targets = ["📊 Dashboard", "📦 Inventory", "💰 Sales Report", "🚚 Suppliers", "🎁 Loyalty", "🤖 AI Chat"]
current_label = nav_labels[nav_targets.index(page)] if page in nav_targets else nav_labels[0]

st.markdown("""
<style>
/* Hide radio circle dots */
div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }

/* Radio container - glass pill bar */
div[data-testid="stRadio"] > div {
    background: rgba(10, 15, 28, 0.88) !important;
    backdrop-filter: blur(24px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(24px) saturate(180%) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 28px !important;
    padding: 6px 8px !important;
    gap: 2px !important;
    box-shadow: 0 4px 28px rgba(0,0,0,0.55) !important;
    margin-bottom: 16px !important;
    flex-wrap: nowrap !important;
}

/* Each radio option */
div[data-testid="stRadio"] > div > label {
    background: transparent !important;
    border-radius: 20px !important;
    padding: 8px 12px !important;
    cursor: pointer !important;
    transition: all 0.18s ease !important;
    flex: 1 !important;
    text-align: center !important;
    color: #475569 !important;
    font-size: 12px !important;
    font-weight: 700 !important;
}

/* Hover */
div[data-testid="stRadio"] > div > label:hover {
    background: rgba(0,229,190,0.1) !important;
    color: #00E5BE !important;
}

/* Active/selected */
div[data-testid="stRadio"] > div > label[data-selected="true"],
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: rgba(0,229,190,0.15) !important;
    color: #00E5BE !important;
    box-shadow: 0 0 14px rgba(0,229,190,0.22) !important;
}

div[data-testid="stRadio"] p {
    font-size: 12px !important;
    font-weight: 700 !important;
    color: inherit !important;
}
</style>
""", unsafe_allow_html=True)

selected_label = st.radio("nav", nav_labels, index=nav_labels.index(current_label),
    horizontal=True, label_visibility="collapsed", key="main_nav")

if nav_targets[nav_labels.index(selected_label)] != page:
    st.session_state.page = nav_targets[nav_labels.index(selected_label)]
    st.rerun()

page = st.session_state.page

# ══════════════════════════════════════════════════════════════
# 📊 DASHBOARD
# ══════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    # Auto refresh every 30 seconds
    st_autorefresh(interval=30000, key="dashboard_refresh")

    st.title("📊 Dashboard")
    _hour = datetime.now().hour
    _greeting = "🌅 Good Morning" if 5 <= _hour < 12 else "☀️ Good Afternoon" if 12 <= _hour < 17 else "🌆 Good Evening" if 17 <= _hour < 21 else "🌙 Good Night"
    st.caption(f"{_greeting}! Here's your shop summary for {datetime.now().strftime('%A, %d %B %Y')}")

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
        <div class="metric-value" style="color:#00E5BE">{fmt_money(today_revenue)}</div></div>""", unsafe_allow_html=True)
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

    # Expire date alerts
    today_date = datetime.now().date()
    soon = datetime.now().date() + timedelta(days=7)
    for item in all_inv:
        if item.get("expire_date"):
            try:
                exp = datetime.strptime(item["expire_date"], "%Y-%m-%d").date()
                if exp <= today_date:
                    st.markdown(f"""<div class="alert-box">☠️ <b>{item['name']}</b> — EXPIRED! ({item['expire_date']})</div>""", unsafe_allow_html=True)
                elif exp <= soon:
                    st.markdown(f"""<div class="alert-box">⏰ <b>{item['name']}</b> — Expiring soon! ({item['expire_date']})</div>""", unsafe_allow_html=True)
            except:
                pass

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

            # Sales comparison
            this_week = df[df["date"] >= datetime.now() - timedelta(days=7)]["total"].sum()
            last_week = df[(df["date"] >= datetime.now() - timedelta(days=14)) & (df["date"] < datetime.now() - timedelta(days=7))]["total"].sum()
            diff = this_week - last_week
            pct = ((diff / last_week) * 100) if last_week > 0 else 0
            arrow = "📈" if diff >= 0 else "📉"
            color = "#00E5BE" if diff >= 0 else "#FF6B35"
            st.markdown(f"""<div style="background:#111827;border-radius:10px;padding:12px;margin-top:8px;border:1px solid #1E293B;">
                <span style="color:#64748B;font-size:11px;">THIS WEEK VS LAST WEEK</span><br>
                <span style="color:{color};font-size:18px;font-weight:700;">{arrow} {'+' if diff>=0 else ''}Rs. {diff:,.0f} ({pct:+.1f}%)</span>
            </div>""", unsafe_allow_html=True)

    with col2:
        st.subheader("🤖 AI Demand Predictions (7 days)")
        inv_names = [i["name"] for i in all_inv]
        pred_df = pd.DataFrame([{"Item": n, "Predicted Units": predict_demand(n)} for n in inv_names])
        st.dataframe(pred_df, use_container_width=True, hide_index=True)

        # Weather + busy day prediction
        st.subheader("🌦️ Weather & Busy Day")

        import streamlit.components.v1 as components

        # Auto detect city from GPS via JS → query param
        if "weather_city" not in st.session_state:
            st.session_state.weather_city = "Negombo"

        # JS: get GPS → reverse geocode → set query param
        components.html("""
        <script>
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(function(pos) {
                var lat = pos.coords.latitude;
                var lon = pos.coords.longitude;
                fetch("https://nominatim.openstreetmap.org/reverse?lat=" + lat + "&lon=" + lon + "&format=json")
                .then(r => r.json())
                .then(data => {
                    var city = data.address.city || data.address.town || data.address.village || data.address.county || "";
                    if (city) {
                        var url = new URL(window.parent.location.href);
                        if (url.searchParams.get("city") !== city) {
                            url.searchParams.set("city", city);
                            window.parent.history.replaceState({}, "", url);
                            window.parent.location.reload();
                        }
                    }
                });
            }, function(err) {}, {timeout: 5000});
        }
        </script>
        """, height=0)

        # Read city from query params
        detected_city = st.query_params.get("city", None)
        if detected_city and detected_city != st.session_state.weather_city:
            st.session_state.weather_city = detected_city

        try:
            import requests as req
            city = st.session_state.weather_city
            weather_url = f"https://wttr.in/{city.replace(' ', '+')}?format=j1"
            w = req.get(weather_url, timeout=5).json()
            temp = w["current_condition"][0]["temp_C"]
            desc = w["current_condition"][0]["weatherDesc"][0]["value"]
            feels = w["current_condition"][0]["FeelsLikeC"]
            humidity = w["current_condition"][0]["humidity"]
            area = w["nearest_area"][0]["areaName"][0]["value"]
            country = w["nearest_area"][0]["country"][0]["value"]

            weather_icon = "☀️" if "Sunny" in desc or "Clear" in desc else "🌧️" if "Rain" in desc else "🌤️" if "Cloud" in desc else "⛅"
            busy = "🔴 Very Busy" if int(humidity) > 80 or "Rain" in desc else "🟡 Moderate" if int(temp) > 28 else "🟢 Normal"

            st.markdown(f"""<div style="background:#111827;border-radius:12px;padding:14px;border:1px solid #1E293B;">
                <div style="display:flex;align-items:center;gap:10px;">
                    <div style="font-size:32px">{weather_icon}</div>
                    <div>
                        <div style="color:#F1F5F9;font-size:16px;font-weight:700">{temp}°C — {desc}</div>
                        <div style="color:#64748B;font-size:11px">📍 {area}, {country} · Feels {feels}°C · 💧{humidity}%</div>
                    </div>
                </div>
                <div style="margin-top:10px;padding:8px;background:rgba(0,0,0,0.2);border-radius:8px;font-weight:700">
                    Shop Traffic Today: {busy}
                </div>
            </div>""", unsafe_allow_html=True)
        except:
            st.info("🌐 Weather loading... Allow location permission!")

    st.divider()

    # Profit Goal Tracker
    st.subheader("🎯 Monthly Profit Goal")
    if "profit_goal" not in st.session_state:
        st.session_state.profit_goal = 50000

    g1, g2 = st.columns([2,1])
    with g2:
        new_goal = st.number_input("Set Goal (Rs.)", min_value=1000, value=st.session_state.profit_goal, step=5000, key="goal_input")
        if st.button("💾 Save Goal", use_container_width=True):
            st.session_state.profit_goal = new_goal
            st.rerun()
    with g1:
        all_s = supabase.table("sales").select("total,date").execute().data
        month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        month_rev = sum(s["total"] for s in all_s if s["date"] >= month_start)
        inv_all = supabase.table("inventory").select("name,cost").execute().data
        cost_map = {i["name"]: i.get("cost",0) for i in inv_all}
        month_sales_full = supabase.table("sales").select("*").execute().data
        month_cost = sum(s.get("quantity",1)*cost_map.get(s["item_name"],0) for s in month_sales_full if s["date"] >= month_start)
        month_profit = month_rev - month_cost
        pct = min(int((month_profit / st.session_state.profit_goal) * 100), 100)
        bar_color = "#00E5BE" if pct >= 75 else "#F59E0B" if pct >= 40 else "#FF6B35"
        st.markdown(f"""
        <div style="background:#111827;border-radius:12px;padding:14px;border:1px solid #1E293B;">
            <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                <span style="color:#F1F5F9;font-weight:700">This Month: {fmt_money(month_profit)}</span>
                <span style="color:{bar_color};font-weight:700">{pct}%</span>
            </div>
            <div style="background:#1E293B;border-radius:8px;height:14px;">
                <div style="background:{bar_color};width:{pct}%;height:14px;border-radius:8px;transition:width 0.5s;"></div>
            </div>
            <div style="color:#64748B;font-size:11px;margin-top:6px;">Goal: {fmt_money(st.session_state.profit_goal)}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Daily Summary Email Button
    st.subheader("📱 Daily Summary Email")
    if st.button("📧 Send Today's Summary to Email", use_container_width=True):
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            gmail_user = st.secrets.get("gmail_user","")
            gmail_pass = st.secrets.get("gmail_pass","")
            recv_email = st.secrets.get("owner_email", gmail_user)
            if gmail_user and gmail_pass:
                subj = f"📊 SmartShop Daily Report — {datetime.now().strftime('%d %b %Y')}"
                body = f"""
<h2>🛒 Pehesara Grocery — Daily Summary</h2>
<p><b>Date:</b> {datetime.now().strftime('%A, %d %B %Y')}</p>
<hr>
<table>
<tr><td>💰 Today Revenue</td><td><b>{fmt_money(today_revenue)}</b></td></tr>
<tr><td>🛒 Sales Count</td><td><b>{today_count}</b></td></tr>
<tr><td>⚠️ Low Stock Items</td><td><b>{len(low_stock)}</b></td></tr>
<tr><td>🎯 Monthly Profit</td><td><b>{fmt_money(month_profit)} ({pct}% of goal)</b></td></tr>
</table>
<hr>
<p>Sent by SmartShop AI 🤖</p>
"""
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subj
                msg["From"] = gmail_user
                msg["To"] = recv_email
                msg.attach(MIMEText(body, "html"))
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as srv:
                    srv.login(gmail_user, gmail_pass)
                    srv.sendmail(gmail_user, recv_email, msg.as_string())
                st.success(f"✅ Daily summary sent to {recv_email}!")
            else:
                st.warning("⚠️ Gmail secrets set කරන්න!")
        except Exception as e:
            st.error(f"Email error: {e}")

    # Low stock browser notification
    import streamlit.components.v1 as _comp
    if low_stock:
        low_names = ", ".join([i["name"] for i in low_stock[:3]])
        _comp.html(f"""
        <script>
        if (Notification && Notification.permission !== "denied") {{
            Notification.requestPermission().then(function(p) {{
                if (p === "granted") {{
                    new Notification("⚠️ SmartShop AI — Low Stock!", {{
                        body: "Low stock: {low_names}",
                        icon: "https://cdn-icons-png.flaticon.com/512/891/891462.png"
                    }});
                }}
            }});
        }}
        </script>
        """, height=0)

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

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                filter_s = st.selectbox("Stock Filter", ["All", "Low Stock Only", "OK Only"])
            with col_f2:
                categories = ["All"] + sorted(df["category"].unique().tolist())
                filter_cat = st.selectbox("🏷️ Category", categories)

            if filter_s == "Low Stock Only":
                df = df[df["Status"] == "🔴 Low"]
            elif filter_s == "OK Only":
                df = df[df["Status"] == "🟢 OK"]
            if filter_cat != "All":
                df = df[df["category"] == filter_cat]

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

    st.divider()
    col_del, col_upd = st.columns(2)

    with col_del:
        st.subheader("🗑️ Delete Item")
        inv_del = supabase.table("inventory").select("id,name").execute().data
        if inv_del:
            del_names = [i["name"] for i in inv_del]
            del_item = st.selectbox("Item select කරන්න", del_names, key="del_select")
            if st.button("🗑️ Delete", type="primary", use_container_width=True):
                del_id = next((i["id"] for i in inv_del if i["name"] == del_item), None)
                if del_id:
                    supabase.table("inventory").delete().eq("id", del_id).execute()
                    st.success(f"✅ '{del_item}' deleted!")
                    st.rerun()

    with col_upd:
        st.subheader("✏️ Update Stock")
        inv_upd = supabase.table("inventory").select("*").execute().data
        if inv_upd:
            upd_names = [i["name"] for i in inv_upd]
            upd_item = st.selectbox("Item select කරන්න", upd_names, key="upd_select")
            selected = next((i for i in inv_upd if i["name"] == upd_item), None)
            if selected:
                new_stock = st.number_input("New Stock", min_value=0, value=selected["stock"], key="new_stock")
                new_price = st.number_input("New Price (Rs.)", min_value=0.0, value=float(selected["price"]), key="new_price")
                if st.button("✏️ Update", type="secondary", use_container_width=True):
                    supabase.table("inventory").update({"stock": new_stock, "price": new_price}).eq("id", selected["id"]).execute()
                    st.success(f"✅ '{upd_item}' updated!")
                    st.rerun()

# ══════════════════════════════════════════════════════════════
# 💰 SALES REPORT
# ══════════════════════════════════════════════════════════════
elif page == "💰 Sales Report":
    st.title("💰 Sales Report & Analytics")

    # ── QUICK SALE POS ──────────────────────────────────────────
    st.subheader("⚡ Quick Sale")
    st.caption("Item button click කළාම instant record!")

    # Barcode / search
    barcode_input = st.text_input("📷 Barcode scan හෝ item name search", placeholder="Scan barcode හෝ type කරන්න...", key="barcode_search")
    if barcode_input:
        matches = [i for i in inv_pos if barcode_input.lower() in i["name"].lower()]
        if matches:
            for item in matches:
                if st.button(f"➕ Add: {item['name']} — Rs.{item['price']}", key=f"bc_{item['id']}"):
                    if item["name"] in st.session_state.cart:
                        st.session_state.cart[item["name"]]["qty"] += 1
                    else:
                        st.session_state.cart[item["name"]] = {"qty": 1, "price": item["price"], "id": item["id"], "stock": item["stock"]}
                    st.rerun()
        else:
            st.warning("Item not found!")

    if "cart" not in st.session_state:
        st.session_state.cart = {}

    inv_pos = supabase.table("inventory").select("name,price,stock,id").execute().data

    # Item buttons grid
    cols_per_row = 3
    rows = [inv_pos[i:i+cols_per_row] for i in range(0, len(inv_pos), cols_per_row)]
    for row in rows:
        cols = st.columns(cols_per_row)
        for j, item in enumerate(row):
            with cols[j]:
                if st.button(f"**{item['name']}**\nRs.{item['price']}", key=f"pos_{item['id']}", use_container_width=True):
                    if item["name"] in st.session_state.cart:
                        st.session_state.cart[item["name"]]["qty"] += 1
                    else:
                        st.session_state.cart[item["name"]] = {"qty": 1, "price": item["price"], "id": item["id"], "stock": item["stock"]}
                    st.rerun()

    # Cart display
    if st.session_state.cart:
        st.markdown("---")
        st.markdown("**🛒 Cart:**")
        cart_total = 0
        for name, info in list(st.session_state.cart.items()):
            subtotal = info["qty"] * info["price"]
            cart_total += subtotal
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"📦 {name}")
            with col2:
                st.write(f"x{info['qty']}")
            with col3:
                st.write(f"Rs.{subtotal:,.0f}")
            with col4:
                if st.button("❌", key=f"remove_{name}"):
                    del st.session_state.cart[name]
                    st.rerun()

        st.markdown(f"### 💰 Total: Rs. {cart_total:,.0f}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm & Receipt", type="primary", use_container_width=True):
                from fpdf import FPDF
                import base64, io
                # Save sales
                for name, info in st.session_state.cart.items():
                    supabase.table("sales").insert({"item_name": name, "quantity": info["qty"], "total": info["qty"] * info["price"], "date": datetime.now().strftime("%Y-%m-%d")}).execute()
                    new_stock = info["stock"] - info["qty"]
                    supabase.table("inventory").update({"stock": new_stock}).eq("id", info["id"]).execute()

                # Generate PDF receipt
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Helvetica", "B", 16)
                pdf.cell(0, 10, "Pehesara Grocery", ln=True, align="C")
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 6, f"Date: {datetime.now().strftime('%d %b %Y %I:%M %p')}", ln=True, align="C")
                pdf.cell(0, 6, "--------------------------------", ln=True, align="C")
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(80, 8, "Item", border=0)
                pdf.cell(30, 8, "Qty", border=0)
                pdf.cell(0, 8, "Total", border=0, ln=True)
                pdf.set_font("Helvetica", "", 11)
                for name, info in st.session_state.cart.items():
                    pdf.cell(80, 7, name[:30], border=0)
                    pdf.cell(30, 7, str(info["qty"]), border=0)
                    pdf.cell(0, 7, f"Rs. {info['qty']*info['price']:,.0f}", border=0, ln=True)
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 6, "--------------------------------", ln=True, align="C")
                pdf.cell(0, 10, f"TOTAL: Rs. {cart_total:,.0f}", ln=True, align="C")
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(0, 8, "Thank you for shopping! Come again!", ln=True, align="C")

                pdf_bytes = pdf.output()
                b64 = base64.b64encode(bytes(pdf_bytes)).decode()
                st.markdown(f"""<a href="data:application/pdf;base64,{b64}" download="receipt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    style="display:block;text-align:center;padding:10px;background:rgba(0,229,190,0.15);
                    border:1px solid rgba(0,229,190,0.3);border-radius:12px;color:#00E5BE;
                    font-weight:700;text-decoration:none;margin-top:8px;">
                    🧾 Download Receipt (PDF)</a>""", unsafe_allow_html=True)

                st.session_state.cart = {}
                st.success(f"✅ Sale recorded! Rs. {cart_total:,.0f}")
                st.rerun()
        with col2:
            if st.button("🗑️ Clear Cart", use_container_width=True):
                st.session_state.cart = {}
                st.rerun()

    st.divider()

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

    # Monthly profit/loss
    st.divider()
    st.subheader("📊 Monthly Profit / Loss Report")
    if not df_sales.empty:
        inv_costs = {i["name"]: i.get("cost", 0) for i in supabase.table("inventory").select("name,cost").execute().data}
        df_sales["cost"] = df_sales.apply(lambda r: r["quantity"] * inv_costs.get(r["item_name"], 0) if "quantity" in df_sales.columns else 0, axis=1)
        df_sales["profit"] = df_sales["total"] - df_sales["cost"]
        df_sales["month"] = pd.to_datetime(df_sales["date"]).dt.strftime("%Y-%m")
        monthly = df_sales.groupby("month").agg({"total": "sum", "cost": "sum", "profit": "sum"}).reset_index()
        monthly.columns = ["Month", "Revenue (Rs.)", "Cost (Rs.)", "Profit (Rs.)"]
        st.dataframe(monthly, use_container_width=True, hide_index=True)

        # PDF download
        from fpdf import FPDF
        import base64
        pdf2 = FPDF()
        pdf2.add_page()
        pdf2.set_font("Helvetica", "B", 16)
        pdf2.cell(0, 10, "Pehesara Grocery - Monthly Report", ln=True, align="C")
        pdf2.set_font("Helvetica", "", 10)
        pdf2.cell(0, 6, f"Generated: {datetime.now().strftime('%d %b %Y')}", ln=True, align="C")
        pdf2.ln(4)
        pdf2.set_font("Helvetica", "B", 11)
        for col in ["Month", "Revenue (Rs.)", "Cost (Rs.)", "Profit (Rs.)"]:
            pdf2.cell(47, 8, col, border=1)
        pdf2.ln()
        pdf2.set_font("Helvetica", "", 10)
        for _, row in monthly.iterrows():
            pdf2.cell(47, 7, str(row["Month"]), border=1)
            pdf2.cell(47, 7, f"Rs. {row['Revenue (Rs.)']:,.0f}", border=1)
            pdf2.cell(47, 7, f"Rs. {row['Cost (Rs.)']:,.0f}", border=1)
            pdf2.cell(47, 7, f"Rs. {row['Profit (Rs.)']:,.0f}", border=1)
            pdf2.ln()
        pdf2_bytes = pdf2.output()
        b64_2 = base64.b64encode(bytes(pdf2_bytes)).decode()
        st.markdown(f"""<a href="data:application/pdf;base64,{b64_2}" download="monthly_report_{datetime.now().strftime('%Y%m')}.pdf"
            style="display:inline-block;padding:10px 20px;margin-top:8px;
            background:rgba(167,139,250,0.15);border:1px solid rgba(167,139,250,0.3);
            border-radius:12px;color:#A78BFA;font-weight:700;text-decoration:none;">
            📊 Download Monthly Report (PDF)</a>""", unsafe_allow_html=True)

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

    st.divider()
    col_del, col_upd = st.columns(2)
    with col_del:
        st.subheader("🗑️ Delete Sale")
        sales_del = supabase.table("sales").select("id,item_name,date,total").execute().data
        if sales_del:
            sale_options = [f"{s['item_name']} | {s['date']} | Rs.{s['total']}" for s in sales_del]
            del_sale = st.selectbox("Sale select කරන්න", sale_options, key="del_sale")
            if st.button("🗑️ Delete Sale", type="primary", use_container_width=True):
                del_idx = sale_options.index(del_sale)
                del_id = sales_del[del_idx]["id"]
                supabase.table("sales").delete().eq("id", del_id).execute()
                st.success("✅ Sale deleted!")
                st.rerun()
    with col_upd:
        st.subheader("✏️ Update Sale")
        if sales_del:
            upd_sale = st.selectbox("Sale select කරන්න", sale_options, key="upd_sale")
            upd_idx = sale_options.index(upd_sale)
            selected_sale = sales_del[upd_idx]
            new_qty = st.number_input("Quantity", min_value=1, value=selected_sale["quantity"] if "quantity" in selected_sale else 1, key="upd_qty")
            new_total = st.number_input("Total (Rs.)", min_value=0.0, value=float(selected_sale["total"]), key="upd_total")
            if st.button("✏️ Update Sale", use_container_width=True):
                supabase.table("sales").update({"quantity": new_qty, "total": new_total}).eq("id", selected_sale["id"]).execute()
                st.success("✅ Sale updated!")
                st.rerun()

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

            # Get supplier phone
            sup_info = supabase.table("suppliers").select("phone").eq("name", item["supplier"]).execute()
            sup_phone = sup_info.data[0]["phone"].replace("-", "").replace(" ", "") if sup_info.data else ""
            # Make sure phone starts with country code
            if sup_phone and not sup_phone.startswith("+"):
                sup_phone_intl = "94" + sup_phone.lstrip("0")
            else:
                sup_phone_intl = sup_phone.lstrip("+")

            wa_msg = f"Hello, I need to order {order_qty} units of {item['name']} urgently. Please confirm availability. - SmartShop AI"
            import urllib.parse
            wa_link = f"https://wa.me/{sup_phone_intl}?text={urllib.parse.quote(wa_msg)}"
            call_link = f"tel:{sup_phone}"

            st.markdown(f"""<div class="alert-box">
                📦 <b>{item['name']}</b> — Order <b>{order_qty} units</b> from <b>{item['supplier']}</b>
                {f"<br>📞 {item['supplier']} · {sup_info.data[0]['phone']}" if sup_info.data else ""}
            </div>""", unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                if sup_phone:
                    st.markdown(f"""<a href="{call_link}" style="
                        display:block;text-align:center;padding:10px;
                        background:rgba(0,229,190,0.12);border:1px solid rgba(0,229,190,0.3);
                        border-radius:12px;color:#00E5BE;font-weight:700;font-size:13px;
                        text-decoration:none;">📞 Call</a>""", unsafe_allow_html=True)
            with col2:
                if sup_phone:
                    st.markdown(f"""<a href="{wa_link}" target="_blank" style="
                        display:block;text-align:center;padding:10px;
                        background:rgba(37,211,102,0.12);border:1px solid rgba(37,211,102,0.3);
                        border-radius:12px;color:#25D366;font-weight:700;font-size:13px;
                        text-decoration:none;">💬 WhatsApp</a>""", unsafe_allow_html=True)
            with col3:
                if st.button("✅ Mark Ordered", key=f"order_{item['id']}"):
                    supabase.table("inventory").update({"stock": item["max_stock"]}).eq("id", item["id"]).execute()
                    st.success(f"✅ {item['name']} marked as ordered!")
                    st.rerun()

            st.markdown("<hr style='border-color:#1E293B;margin:12px 0'>", unsafe_allow_html=True)
    else:
        st.markdown("""<div class="success-box">✅ No urgent orders needed!</div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("📋 All Suppliers")
    sup_data = supabase.table("suppliers").select("*").execute().data
    if sup_data:
        st.dataframe(pd.DataFrame(sup_data)[["name", "phone", "email", "items"]], use_container_width=True, hide_index=True)

    st.divider()
    col_del, col_upd = st.columns(2)
    with col_del:
        st.subheader("🗑️ Delete Supplier")
        sup_del = supabase.table("suppliers").select("*").execute().data
        if sup_del:
            sup_names = [s["name"] for s in sup_del]
            del_sup = st.selectbox("Supplier select කරන්න", sup_names, key="del_sup")
            if st.button("🗑️ Delete Supplier", type="primary", use_container_width=True):
                del_id = next((s["id"] for s in sup_del if s["name"] == del_sup), None)
                if del_id:
                    supabase.table("suppliers").delete().eq("id", del_id).execute()
                    st.success(f"✅ '{del_sup}' deleted!")
                    st.rerun()
    with col_upd:
        st.subheader("✏️ Update Supplier")
        if sup_del:
            upd_sup = st.selectbox("Supplier select කරන්න", [s["name"] for s in sup_del], key="upd_sup")
            sel_sup = next((s for s in sup_del if s["name"] == upd_sup), None)
            if sel_sup:
                new_phone = st.text_input("Phone", value=sel_sup["phone"] or "", key="upd_sup_phone")
                new_email = st.text_input("Email", value=sel_sup["email"] or "", key="upd_sup_email")
                new_items = st.text_input("Items", value=sel_sup["items"] or "", key="upd_sup_items")
                if st.button("✏️ Update Supplier", use_container_width=True):
                    supabase.table("suppliers").update({"phone": new_phone, "email": new_email, "items": new_items}).eq("id", sel_sup["id"]).execute()
                    st.success(f"✅ '{upd_sup}' updated!")
                    st.rerun()

    st.divider()
    st.subheader("📅 Weekly Auto Order Schedule")
    st.caption("ස්වයංක්‍රීයව order කරන්න days set කරන්න")

    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    order_days = st.multiselect("Order Days", days, default=["Monday", "Thursday"], key="order_days")
    today_name = datetime.now().strftime("%A")

    if today_name in order_days:
        low_items = [i for i in supabase.table("inventory").select("*").execute().data if i["stock"] < i["min_stock"]]
        if low_items:
            st.markdown(f"""<div class="alert-box">📅 Today is <b>{today_name}</b> — Auto Order Day!<br>
            {len(low_items)} items need reordering.</div>""", unsafe_allow_html=True)
            if st.button("🚀 Auto Order All Low Items", type="primary", use_container_width=True):
                for item in low_items:
                    supabase.table("inventory").update({"stock": item["max_stock"]}).eq("id", item["id"]).execute()
                st.success(f"✅ {len(low_items)} items restocked!")
                st.rerun()
        else:
            st.markdown("""<div class="success-box">✅ All items sufficiently stocked!</div>""", unsafe_allow_html=True)
    else:
        st.info(f"📅 Next order day: **{next((d for d in days if days.index(d) > days.index(today_name)), days[0])}**")

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
    col_del, col_upd = st.columns(2)
    with col_del:
        st.subheader("🗑️ Delete Customer")
        cust_del = supabase.table("customers").select("*").execute().data
        if cust_del:
            cust_del_names = [c["name"] for c in cust_del]
            del_cust = st.selectbox("Customer select කරන්න", cust_del_names, key="del_cust")
            if st.button("🗑️ Delete Customer", type="primary", use_container_width=True):
                del_id = next((c["id"] for c in cust_del if c["name"] == del_cust), None)
                if del_id:
                    supabase.table("customers").delete().eq("id", del_id).execute()
                    st.success(f"✅ '{del_cust}' deleted!")
                    st.rerun()
    with col_upd:
        st.subheader("✏️ Update Customer")
        if cust_del:
            upd_cust = st.selectbox("Customer select කරන්න", [c["name"] for c in cust_del], key="upd_cust")
            sel_cust = next((c for c in cust_del if c["name"] == upd_cust), None)
            if sel_cust:
                new_phone = st.text_input("Phone", value=sel_cust["phone"] or "", key="upd_cust_phone")
                new_points = st.number_input("Points", min_value=0, value=sel_cust["points"], key="upd_cust_points")
                if st.button("✏️ Update Customer", use_container_width=True):
                    supabase.table("customers").update({"phone": new_phone, "points": new_points}).eq("id", sel_cust["id"]).execute()
                    st.success(f"✅ '{upd_cust}' updated!")
                    st.rerun()

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ Add Customer")
        with st.form("add_customer"):
            c_name = st.text_input("Name")
            c_phone = st.text_input("Phone")
            c_email = st.text_input("Email (auto notifications)")
            if st.form_submit_button("Add", use_container_width=True) and c_name:
                supabase.table("customers").insert({"name": c_name, "phone": c_phone, "email": c_email, "points": 0, "total_spent": 0, "joined_date": datetime.now().strftime("%Y-%m-%d")}).execute()
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
                    old_points = cust["points"]
                    new_points = old_points + points_earn

                    # Badge check
                    def get_badge(p):
                        return "🥇 Gold" if p > 1000 else "🥈 Silver" if p > 700 else "🥉 Bronze" if p > 400 else "⭐ Member"
                    old_badge = get_badge(old_points)
                    new_badge = get_badge(new_points)
                    badge_upgraded = old_badge != new_badge

                    supabase.table("customers").update({"points": new_points, "total_spent": cust["total_spent"] + purchase}).eq("id", cust["id"]).execute()

                    # Auto send email if customer has email
                    cust_email = cust.get("email", "")
                    if cust_email:
                        import smtplib
                        from email.mime.text import MIMEText
                        from email.mime.multipart import MIMEMultipart
                        try:
                            gmail_user = st.secrets["gmail_user"]
                            gmail_pass = st.secrets["gmail_pass"]

                            subject = f"🎉 You earned {points_earn} points! - Pehesara Grocery"
                            body = f"""
Hi {cust['name']}! 👋

Great news! You have earned <b>{points_earn} points</b> at Pehesara Grocery.

📊 Your Points Balance: <b>{new_points} pts</b>
🏆 Your Status: <b>{new_badge}</b>
💰 Purchase Amount: <b>Rs. {purchase:,}</b>

{"🎊 Congratulations! You've been upgraded to " + new_badge + " status!" if badge_upgraded else ""}

Keep shopping to earn more rewards!
Thank you for being a loyal customer! 🛒

— Pehesara Grocery Team
"""
                            msg = MIMEMultipart("alternative")
                            msg["Subject"] = subject
                            msg["From"] = gmail_user
                            msg["To"] = cust_email
                            msg.attach(MIMEText(body, "html"))

                            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                                server.login(gmail_user, gmail_pass)
                                server.sendmail(gmail_user, cust_email, msg.as_string())
                            st.success(f"✅ {points_earn} points added! 📧 Email sent to {cust_email}!")
                        except Exception as e:
                            st.success(f"✅ {points_earn} points added to {selected}!")
                            st.warning(f"⚠️ Email send failed: {str(e)}")
                    else:
                        st.success(f"✅ {points_earn} points added to {selected}! (No email on file)")
                    st.rerun()

    st.divider()
    st.subheader("📊 Customer Purchase History")
    if cust_data:
        hist_cust = st.selectbox("Customer select කරන්න", [c["name"] for c in cust_data], key="hist_cust")
        hist_sales = supabase.table("sales").select("*").execute().data
        if hist_sales:
            df_hist = pd.DataFrame(hist_sales)
            cust_hist = df_hist[df_hist["item_name"].notna()]

            # Get all sales tied to this customer by cross-referencing date + spending
            # Show all sales as history per item
            item_hist = df_hist.groupby("item_name").agg({"quantity": "sum", "total": "sum"}).reset_index()
            item_hist.columns = ["Item", "Total Qty Bought", "Total Spent (Rs.)"]
            st.dataframe(item_hist.sort_values("Total Spent (Rs.)", ascending=False), use_container_width=True, hide_index=True)

            sel_cust = next((c for c in cust_data if c["name"] == hist_cust), None)
            if sel_cust:
                st.markdown(f"""<div style="background:#111827;border-radius:12px;padding:14px;border:1px solid #1E293B;margin-top:8px;">
                    <b>{hist_cust}</b> — Total Spent: <span style="color:#00E5BE">Rs. {sel_cust['total_spent']:,.0f}</span> &nbsp;|&nbsp;
                    Points: <span style="color:#A78BFA">{sel_cust['points']}</span> &nbsp;|&nbsp;
                    Member since: {sel_cust.get('joined_date','N/A')}
                </div>""", unsafe_allow_html=True)

    st.divider()
    st.subheader("💳 Debt Tracker")
    st.caption("Customer credit / uduliya track කරන්න")

    debt_data = supabase.table("customers").select("id,name,debt").execute().data if "debt" in (supabase.table("customers").select("*").limit(1).execute().data[0] if supabase.table("customers").select("*").limit(1).execute().data else {}) else []

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.markdown("**📋 Customer Debts**")
        debt_items = supabase.table("customers").select("name,debt").execute().data
        if debt_items:
            for d in debt_items:
                debt_val = d.get("debt", 0) or 0
                if debt_val > 0:
                    st.markdown(f"""<div class="alert-box">💳 <b>{d['name']}</b> — Rs. {debt_val:,.0f} uduliya</div>""", unsafe_allow_html=True)
            total_debt = sum(d.get("debt",0) or 0 for d in debt_items)
            st.markdown(f"""<div class="metric-card"><div class="metric-label">Total Debt</div><div class="metric-value" style="color:#FF6B35">Rs. {total_debt:,.0f}</div></div>""", unsafe_allow_html=True)

    with col_d2:
        st.markdown("**➕ Add / Clear Debt**")
        debt_names = [c["name"] for c in (supabase.table("customers").select("*").execute().data or [])]
        if debt_names:
            sel_debt_cust = st.selectbox("Customer", debt_names, key="debt_cust")
            debt_action = st.radio("Action", ["➕ Add Debt", "✅ Clear Debt"], horizontal=True, key="debt_action")
            debt_amount = st.number_input("Amount (Rs.)", min_value=0, value=0, key="debt_amt")
            if st.button("💾 Save", use_container_width=True, key="debt_save"):
                cust_rec = next((c for c in supabase.table("customers").select("*").execute().data if c["name"] == sel_debt_cust), None)
                if cust_rec:
                    current_debt = cust_rec.get("debt", 0) or 0
                    new_debt = current_debt + debt_amount if "Add" in debt_action else max(0, current_debt - debt_amount)
                    supabase.table("customers").update({"debt": new_debt}).eq("id", cust_rec["id"]).execute()
                    st.success(f"✅ Updated! {sel_debt_cust} debt: Rs. {new_debt:,.0f}")
                    st.rerun()

    st.divider()
    st.subheader("📲 Send WhatsApp Message")
    st.caption("Customer ට directly WhatsApp message යවන්න")

    import urllib.parse

    if cust_data:
        msg_cust = st.selectbox("Customer select කරන්න", [c["name"] for c in cust_data], key="msg_cust_select")
        sel_msg_cust = next((c for c in cust_data if c["name"] == msg_cust), None)

        if sel_msg_cust:
            phone_raw = sel_msg_cust.get("phone", "")
            phone_clean = phone_raw.replace("-", "").replace(" ", "")
            if phone_clean and not phone_clean.startswith("+"):
                phone_intl = "94" + phone_clean.lstrip("0")
            else:
                phone_intl = phone_clean.lstrip("+")

            badge = "🥇 Gold" if sel_msg_cust["points"] > 1000 else "🥈 Silver" if sel_msg_cust["points"] > 700 else "🥉 Bronze" if sel_msg_cust["points"] > 400 else "⭐ Member"

            msg_type = st.selectbox("Message type", [
                "🎉 Points Earned",
                "🥇 Badge Upgrade",
                "🎂 Birthday Wishes",
                "🛒 Special Offer"
            ], key="msg_type_select")

            # Auto generate message
            if msg_type == "🎉 Points Earned":
                default_msg = f"Hi {sel_msg_cust['name']}! 🎉 You have earned points at Pehesara Grocery. Your total points: {sel_msg_cust['points']} pts. Keep shopping to earn more rewards! 🛒"
            elif msg_type == "🥇 Badge Upgrade":
                default_msg = f"Congratulations {sel_msg_cust['name']}! 🥇 You have reached {badge} status at Pehesara Grocery! Thank you for your loyalty. Special benefits await you! 🎁"
            elif msg_type == "🎂 Birthday Wishes":
                default_msg = f"Happy Birthday {sel_msg_cust['name']}! 🎂🎉 Wishing you a wonderful day! As a special gift, visit Pehesara Grocery today for a surprise discount! 🛒💝"
            else:
                default_msg = f"Hi {sel_msg_cust['name']}! 🛒 Special offer just for you at Pehesara Grocery! Visit us today and enjoy exclusive deals. Don't miss out! 🎁✨"

            custom_msg = st.text_area("Message edit කරන්න", value=default_msg, height=120, key="custom_msg")

            if phone_intl:
                wa_url = f"https://wa.me/{phone_intl}?text={urllib.parse.quote(custom_msg)}"
                st.markdown(f"""
                <a href="{wa_url}" target="_blank" style="
                    display:block;text-align:center;padding:14px;margin-top:8px;
                    background:rgba(37,211,102,0.15);border:1px solid rgba(37,211,102,0.35);
                    border-radius:14px;color:#25D366;font-weight:800;font-size:15px;
                    text-decoration:none;letter-spacing:0.3px;">
                    💬 Send WhatsApp to {sel_msg_cust['name']}
                </a>""", unsafe_allow_html=True)
            else:
                st.warning("⚠️ Phone number නෑ — Customer update කරලා phone add කරන්න!")

# ══════════════════════════════════════════════════════════════
# 🤖 AI CHAT
# ══════════════════════════════════════════════════════════════
elif page == "🤖 AI Chat":
    st.title("🤖 AI Assistant")
    st.caption("SmartShop ගැන ඕනෑම question ask කරන්න!")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Show chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Build shop context
    inv_ctx  = supabase.table("inventory").select("name,stock,min_stock,price").execute().data
    sale_ctx = supabase.table("sales").select("item_name,quantity,total,date").execute().data
    today_s  = sum(s["total"] for s in sale_ctx if s["date"] == datetime.now().strftime("%Y-%m-%d"))
    low_ctx  = [i["name"] for i in inv_ctx if i["stock"] < i["min_stock"]]

    system_prompt = f"""You are SmartShop AI — a friendly assistant for Pehesara Grocery shop.
Current data:
- Today's revenue: Rs. {today_s:,.0f}
- Low stock items: {low_ctx}
- Inventory: {[(i['name'], i['stock']) for i in inv_ctx]}
Answer in Sinhala or English based on how user asks. Be concise and helpful."""

    if prompt := st.chat_input("Message SmartShop AI..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    import json, urllib.request
                    messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history]
                    api_key = st.secrets.get("anthropic_key", "")
                    if not api_key:
                        reply = "⚠️ Anthropic API key set කරන්න! Streamlit Secrets > anthropic_key"
                    else:
                        payload = json.dumps({
                            "model": "claude-haiku-4-5-20251001",
                            "max_tokens": 500,
                            "system": system_prompt,
                            "messages": messages
                        }).encode()
                        req_obj = urllib.request.Request(
                            "https://api.anthropic.com/v1/messages",
                            data=payload,
                            headers={
                                "Content-Type": "application/json",
                                "x-api-key": api_key,
                                "anthropic-version": "2023-06-01"
                            }
                        )
                        with urllib.request.urlopen(req_obj) as res:
                            data = json.loads(res.read())
                        reply = data["content"][0]["text"]
                    st.write(reply)
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                except Exception as e:
                    err = f"Error: {e}"
                    st.error(err)
                    st.session_state.chat_history.append({"role": "assistant", "content": err})

    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
