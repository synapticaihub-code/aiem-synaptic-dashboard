import streamlit as st
import pymongo
import os
import uuid
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
# On Streamlit Cloud secrets live in st.secrets, not os.environ
if "MONGODB_URI" in st.secrets:
    os.environ["MONGO_URL"] = st.secrets["MONGODB_URI"]

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ Page config Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
st.set_page_config(
    page_title="AIEM SynapticAIHub Analytics",
    page_icon="Ã°ÂÂ§Â ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ Custom CSS Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
st.markdown("""
<style>
  [data-testid="metric-container"] { background:#1e1e2e; border-radius:10px; padding:16px; }
  .block-container { padding-top: 1.5rem; }
  h1 { color: #7c3aed; }
  h2 { color: #a78bfa; border-bottom: 1px solid #3f3f5a; padding-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ DB connection Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
@st.cache_resource
def get_db():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name   = os.environ.get("DB_NAME", "aiem_dashboard")
    client    = pymongo.MongoClient(mongo_url)
    return client[db_name]

db = get_db()

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ Helpers Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
def get_settings():
    s = db.settings.find_one({"id": "global_settings"}, {"_id": 0})
    if not s:
        s = {
            "id": "global_settings",
            "hourly_rate": 20.0,
            "avg_call_duration_manual": 10.0,
            "avg_email_time_manual": 3.0,
            "avg_sms_time_manual": 1.0,
            "subscription_monthly": 297.0,
        }
        db.settings.insert_one(s.copy())
    return s

def calculate_totals(data: dict, settings: dict) -> dict:
    total_cost = sum(data.get(k, 0) for k in [
        "sms_cost", "email_cost", "email_notifications_cost",
        "voice_cost", "workflow_cost", "messaging_cost",
        "verification_cost", "subscription_cost",
    ])
    total_actions = sum(data.get(k, 0) for k in [
        "sms_sent", "emails_sent", "email_notifications",
        "total_calls", "workflow_actions", "messaging_direct",
    ])
    total_clients   = max(data.get("total_clients", 1), 1)
    cost_per_client = total_cost / total_clients
    hourly_rate     = settings.get("hourly_rate", 20.0)
    call_min   = data.get("total_call_minutes", 0)
    email_min  = (data.get("emails_sent", 0) + data.get("email_notifications", 0)) * settings.get("avg_email_time_manual", 3.0)
    sms_min    = data.get("sms_sent", 0) * settings.get("avg_sms_time_manual", 1.0)
    hours_saved = (call_min + email_min + sms_min) / 60
    salary_savings = hours_saved * hourly_rate
    data.update({
        "total_cost": round(total_cost, 2),
        "cost_per_client": round(cost_per_client, 2),
        "total_actions": total_actions,
        "estimated_hours_saved": round(hours_saved, 1),
        "estimated_salary_savings": round(salary_savings, 2),
    })
    return data

def get_periods():
    periods = list(db.periods.find({}, {"_id": 0}).sort("period_start", -1))
    return periods

def fmt(n, prefix="$", decimals=2):
    return f"{prefix}{n:,.{decimals}f}" if prefix == "$" else f"{n:,.{decimals}f}"

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂ Sidebar navigation Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
st.sidebar.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
st.sidebar.title("SynapticAIHub")
st.sidebar.caption("Analytics Dashboard")

page = st.sidebar.radio(
    "Navigation",
    ["Ã°ÂÂÂ Dashboard", "Ã°ÂÂÂ Periods", "Ã¢ÂÂ Add Period", "Ã¢ÂÂÃ¯Â¸Â Settings"],
)

settings  = get_settings()
periods   = get_periods()

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
# PAGE: DASHBOARD
# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
if page == "Ã°ÂÂÂ Dashboard":
    st.title("Ã°ÂÂ§Â  AIEM SynapticAIHub Analytics")

    if not periods:
        st.info("No data yet. Go to **Ã¢ÂÂ Add Period** to enter your first period, or use the **Seed Demo Data** button below.")
        if st.button("Ã°ÂÂÂ± Seed Demo Data"):
            demo = {
                "id": str(uuid.uuid4()),
                "period_start": "2026-02-22",
                "period_end":   "2026-03-23",
                "total_clients": 1610,
                "sms_sent": 3812, "sms_cost": 61.99,
                "emails_sent": 3283, "email_cost": 4.21,
                "email_notifications": 693, "email_notifications_cost": 4.62,
                "total_calls": 358, "inbound_calls": 263, "outbound_calls": 95,
                "total_call_minutes": 1954, "voice_cost": 253.96,
                "workflow_actions": 1614, "workflow_cost": 14.10,
                "messaging_direct": 3812, "messaging_cost": 61.99,
                "appointments_phone": 358, "appointments_email": 312, "appointments_sms": 310,
                "email_verifications": 190, "verification_cost": 2.90,
                "subscription_cost": 741.41,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            demo = calculate_totals(demo, settings)
            db.periods.insert_one(demo.copy())
            st.success("Demo data loaded! Refreshing...")
            st.rerun()
        st.stop()

    # Period selector
    period_labels = [f"{p['period_start']} Ã¢ÂÂ {p['period_end']}" for p in periods]
    sel_label = st.selectbox("Select period", period_labels)
    p = periods[period_labels.index(sel_label)]

    # Ã¢ÂÂÃ¢ÂÂ KPI Row Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    st.markdown("### Key Performance Indicators")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Total Cost", f"${p.get('total_cost', 0):,.2f} CAD")
    k2.metric("Clients",    f"{p.get('total_clients', 0):,}")
    k3.metric("Cost / Client", f"${p.get('cost_per_client', 0):,.2f}")
    k4.metric("Hours Saved", f"{p.get('estimated_hours_saved', 0):,.1f} h")
    k5.metric("Salary Savings", f"${p.get('estimated_salary_savings', 0):,.2f}")

    st.divider()

    # Ã¢ÂÂÃ¢ÂÂ Cost Breakdown Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("## Ã°ÂÂÂ° Cost Breakdown")
        cost_items = {
            "Voice AI":        p.get("voice_cost", 0),
            "SMS":             p.get("sms_cost", 0),
            "Email":           p.get("email_cost", 0) + p.get("email_notifications_cost", 0),
            "Workflows":       p.get("workflow_cost", 0),
            "Messaging":       p.get("messaging_cost", 0),
            "Verifications":   p.get("verification_cost", 0),
            "Subscription":    p.get("subscription_cost", 0),
        }
        fig_pie = px.pie(
            names=list(cost_items.keys()),
            values=list(cost_items.values()),
            color_discrete_sequence=px.colors.sequential.Purples_r,
            hole=0.4,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.markdown("## Ã°ÂÂÂ¨ Communication Volume")
        comm_items = {
            "SMS Sent":          p.get("sms_sent", 0),
            "Emails Sent":       p.get("emails_sent", 0),
            "Email Notif.":      p.get("email_notifications", 0),
            "AI Calls":          p.get("total_calls", 0),
            "Workflow Actions":  p.get("workflow_actions", 0),
            "Direct Messages":   p.get("messaging_direct", 0),
        }
        fig_bar = px.bar(
            x=list(comm_items.values()),
            y=list(comm_items.keys()),
            orientation="h",
            color=list(comm_items.values()),
            color_continuous_scale="purples",
            text_auto=True,
        )
        fig_bar.update_layout(
            showlegend=False, coloraxis_showscale=False,
            margin=dict(t=20, b=20), yaxis_title="", xaxis_title="Count"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Ã¢ÂÂÃ¢ÂÂ Voice AI & Appointments Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    col_v, col_a = st.columns(2)

    with col_v:
        st.markdown("## Ã°ÂÂÂ Voice AI Detail")
        v1, v2, v3 = st.columns(3)
        v1.metric("Total Calls",   f"{p.get('total_calls', 0):,}")
        v2.metric("Inbound",       f"{p.get('inbound_calls', 0):,}")
        v3.metric("Outbound",      f"{p.get('outbound_calls', 0):,}")
        minutes = p.get("total_call_minutes", 0)
        st.metric("Total Minutes", f"{minutes:,.0f} min ({minutes/60:,.1f} h)")
        st.metric("Voice Cost",    f"${p.get('voice_cost', 0):,.2f} CAD")

    with col_a:
        st.markdown("## Ã°ÂÂÂ Appointments")
        appt_items = {
            "Phone (AI)": p.get("appointments_phone", 0),
            "Email":      p.get("appointments_email", 0),
            "SMS":        p.get("appointments_sms", 0),
        }
        total_appt = sum(appt_items.values())
        st.metric("Total Appointments", f"{total_appt:,}")
        fig_appt = px.pie(
            names=list(appt_items.keys()),
            values=list(appt_items.values()),
            color_discrete_sequence=["#7c3aed", "#a78bfa", "#c4b5fd"],
            hole=0.5,
        )
        fig_appt.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig_appt, use_container_width=True)

    # Ã¢ÂÂÃ¢ÂÂ ROI Analysis Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    st.markdown("## Ã°ÂÂÂ ROI Analysis")
    r1, r2, r3, r4 = st.columns(4)
    total_cost     = p.get("total_cost", 0)
    salary_savings = p.get("estimated_salary_savings", 0)
    net_savings    = salary_savings - total_cost
    roi_pct        = (net_savings / total_cost * 100) if total_cost else 0

    r1.metric("Platform Cost",    f"${total_cost:,.2f}")
    r2.metric("Salary Saved",     f"${salary_savings:,.2f}")
    r3.metric("Net Savings",      f"${net_savings:,.2f}", delta=f"{net_savings:+,.2f}")
    r4.metric("ROI",              f"{roi_pct:.0f}%")

    # Ã¢ÂÂÃ¢ÂÂ Multi-period comparison Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
    if len(periods) > 1:
        st.divider()
        st.markdown("## Ã°ÂÂÂ Period Comparison")
        df = pd.DataFrame(periods)
        df["label"] = df["period_start"] + " Ã¢ÂÂ " + df["period_end"]
        metrics_to_compare = ["total_cost", "total_actions", "estimated_hours_saved", "estimated_salary_savings"]
        selected_metric = st.selectbox("Compare metric", metrics_to_compare)
        fig_trend = px.bar(
            df, x="label", y=selected_metric,
            color_discrete_sequence=["#7c3aed"],
            text_auto=True,
        )
        fig_trend.update_layout(xaxis_title="Period", yaxis_title=selected_metric.replace("_", " ").title())
        st.plotly_chart(fig_trend, use_container_width=True)

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
# PAGE: PERIODS LIST
# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
elif page == "Ã°ÂÂÂ Periods":
    st.title("Ã°ÂÂÂ Periods")
    if not periods:
        st.info("No periods yet.")
    else:
        df = pd.DataFrame(periods)
        display_cols = [
            "period_start", "period_end", "total_clients",
            "total_cost", "total_actions", "estimated_hours_saved", "estimated_salary_savings",
        ]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[display_cols].rename(columns={
                "period_start": "Start", "period_end": "End",
                "total_clients": "Clients", "total_cost": "Total Cost ($)",
                "total_actions": "Actions", "estimated_hours_saved": "Hours Saved",
                "estimated_salary_savings": "Salary Savings ($)",
            }),
            use_container_width=True, hide_index=True,
        )
        st.divider()
        st.subheader("Delete a period")
        del_label = st.selectbox("Select period to delete", [f"{p['period_start']} Ã¢ÂÂ {p['period_end']}" for p in periods])
        if st.button("Ã°ÂÂÂÃ¯Â¸Â Delete", type="secondary"):
            idx   = [f"{p['period_start']} Ã¢ÂÂ {p['period_end']}" for p in periods].index(del_label)
            pid   = periods[idx]["id"]
            db.periods.delete_one({"id": pid})
            st.success("Period deleted.")
            st.rerun()

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
# PAGE: ADD / EDIT PERIOD
# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
elif page == "Ã¢ÂÂ Add Period":
    st.title("Ã¢ÂÂ Add New Period")

    with st.form("add_period"):
        st.subheader("Ã°ÂÂÂ Period Dates")
        c1, c2 = st.columns(2)
        period_start = c1.date_input("Start date")
        period_end   = c2.date_input("End date")
        total_clients = st.number_input("Total clients", min_value=0, value=0)

        st.subheader("Ã°ÂÂÂ± Communication")
        col1, col2, col3 = st.columns(3)
        sms_sent         = col1.number_input("SMS Sent",            min_value=0, value=0)
        sms_cost         = col1.number_input("SMS Cost ($)",        min_value=0.0, value=0.0)
        emails_sent      = col2.number_input("Emails Sent",         min_value=0, value=0)
        email_cost       = col2.number_input("Email Cost ($)",      min_value=0.0, value=0.0)
        email_notif      = col3.number_input("Email Notifications", min_value=0, value=0)
        email_notif_cost = col3.number_input("Notif. Cost ($)",     min_value=0.0, value=0.0)

        st.subheader("Ã°ÂÂÂ Voice AI")
        v1, v2, v3 = st.columns(3)
        total_calls   = v1.number_input("Total Calls",     min_value=0, value=0)
        inbound_calls = v2.number_input("Inbound Calls",   min_value=0, value=0)
        outbound_calls= v3.number_input("Outbound Calls",  min_value=0, value=0)
        call_minutes  = v1.number_input("Call Minutes",    min_value=0.0, value=0.0)
        voice_cost    = v2.number_input("Voice Cost ($)",  min_value=0.0, value=0.0)

        st.subheader("Ã¢ÂÂÃ¯Â¸Â Workflows & Messaging")
        w1, w2 = st.columns(2)
        workflow_actions = w1.number_input("Workflow Actions", min_value=0, value=0)
        workflow_cost    = w1.number_input("Workflow Cost ($)",min_value=0.0, value=0.0)
        messaging_direct = w2.number_input("Direct Messages",  min_value=0, value=0)
        messaging_cost   = w2.number_input("Messaging Cost ($)",min_value=0.0, value=0.0)

        st.subheader("Ã°ÂÂÂ Appointments")
        a1, a2, a3 = st.columns(3)
        appt_phone = a1.number_input("Phone Appointments", min_value=0, value=0)
        appt_email = a2.number_input("Email Appointments", min_value=0, value=0)
        appt_sms   = a3.number_input("SMS Appointments",   min_value=0, value=0)

        st.subheader("Ã¢ÂÂ Verification & Subscription")
        e1, e2, e3 = st.columns(3)
        email_verif   = e1.number_input("Email Verifications", min_value=0, value=0)
        verif_cost    = e2.number_input("Verification Cost ($)", min_value=0.0, value=0.0)
        subscription  = e3.number_input("Subscription Cost ($)", min_value=0.0, value=settings.get("subscription_monthly", 297.0))

        submitted = st.form_submit_button("Ã°ÂÂÂ¾ Save Period", type="primary")

    if submitted:
        data = {
            "id": str(uuid.uuid4()),
            "period_start": str(period_start),
            "period_end":   str(period_end),
            "total_clients": total_clients,
            "sms_sent": sms_sent, "sms_cost": sms_cost,
            "emails_sent": emails_sent, "email_cost": email_cost,
            "email_notifications": email_notif, "email_notifications_cost": email_notif_cost,
            "total_calls": total_calls, "inbound_calls": inbound_calls, "outbound_calls": outbound_calls,
            "total_call_minutes": call_minutes, "voice_cost": voice_cost,
            "workflow_actions": workflow_actions, "workflow_cost": workflow_cost,
            "messaging_direct": messaging_direct, "messaging_cost": messaging_cost,
            "appointments_phone": appt_phone, "appointments_email": appt_email, "appointments_sms": appt_sms,
            "email_verifications": email_verif, "verification_cost": verif_cost,
            "subscription_cost": subscription,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        data = calculate_totals(data, settings)
        db.periods.insert_one(data.copy())
        st.success(f"Ã¢ÂÂ Period saved! Total cost: ${data['total_cost']:,.2f} CAD | Hours saved: {data['estimated_hours_saved']:.1f} h")
        st.balloons()

# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
# PAGE: SETTINGS
# Ã¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂÃ¢ÂÂ
elif page == "Ã¢ÂÂÃ¯Â¸Â Settings":
    st.title("Ã¢ÂÂÃ¯Â¸Â Settings")
    st.caption("These values are used to calculate estimated savings.")

    with st.form("settings_form"):
        hourly_rate    = st.number_input("Hourly rate (CAD/h)", value=float(settings.get("hourly_rate", 20.0)), min_value=0.0, step=0.5)
        call_manual    = st.number_input("Avg call duration if done manually (min)", value=float(settings.get("avg_call_duration_manual", 10.0)), min_value=0.0)
        email_manual   = st.number_input("Avg email time if done manually (min)", value=float(settings.get("avg_email_time_manual", 3.0)), min_value=0.0)
        sms_manual     = st.number_input("Avg SMS time if done manually (min)", value=float(settings.get("avg_sms_time_manual", 1.0)), min_value=0.0)
        subscription   = st.number_input("Monthly subscription ($)", value=float(settings.get("subscription_monthly", 297.0)), min_value=0.0)
        save = st.form_submit_button("Ã°ÂÂÂ¾ Save Settings", type="primary")

    if save:
        updated = {
            "id": "global_settings",
            "hourly_rate": hourly_rate,
            "avg_call_duration_manual": call_manual,
            "avg_email_time_manual": email_manual,
            "avg_sms_time_manual": sms_manual,
            "subscription_monthly": subscription,
        }
        db.settings.update_one({"id": "global_settings"}, {"$set": updated}, upsert=True)
        st.success("Settings saved!")
