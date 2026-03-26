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

# ─── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AIEM SynapticAIHub Analytics",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="metric-container"] { background:#1e1e2e; border-radius:10px; padding:16px; }
  .block-container { padding-top: 1.5rem; }
  h1 { color: #7c3aed; }
  h2 { color: #a78bfa; border-bottom: 1px solid #3f3f5a; padding-bottom: 6px; }
</style>
""", unsafe_allow_html=True)

# ─── DB connection ────────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    mongo_url = st.secrets.get("MONGODB_URI", os.environ.get("MONGO_URL", "mongodb://localhost:27017"))
    db_name   = os.environ.get("DB_NAME", "aiem_dashboard")
    client    = pymongo.MongoClient(mongo_url)
    return client[db_name]

db = get_db()

# ─── Helpers ─────────────────────────────────────────────────────────────────
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

# ─── Sidebar navigation ───────────────────────────────────────────────────────
col_logo1, col_logo2 = st.sidebar.columns(2)
import os as _os
if _os.path.exists("assets/logo_client.png"):
    col_logo1.image("assets/logo_client.png", use_container_width=True)
if _os.path.exists("assets/logo_synaptic.png"):
    col_logo2.image("assets/logo_synaptic.png", use_container_width=True)

st.sidebar.title("SynapticAIHub")
st.sidebar.caption("Tableau de bord analytique")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Tableau de bord", "📅 Périodes", "➕ Ajouter une période", "⚙️ Paramètres"],
)

settings  = get_settings()
periods   = get_periods()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: TABLEAU DE BORD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "📊 Tableau de bord":
    st.title("🧠 AIEM SynapticAIHub Analytics")

    if not periods:
        st.info("Aucune donnée. Allez à **➕ Ajouter une période** pour saisir votre première période, ou utilisez le bouton **Données de démonstration** ci-dessous.")
        if st.button("🌱 Données de démonstration"):
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
            st.success("Données de démonstration chargées ! Actualisation...")
            st.rerun()
        st.stop()

    # Sélecteur de période
    period_labels = [f"{p['period_start']} → {p['period_end']}" for p in periods]
    sel_label = st.selectbox("Sélectionner une période", period_labels)
    p = periods[period_labels.index(sel_label)]

    # ── KPI Row ──────────────────────────────────────────────────────────────
    st.markdown("### Indicateurs clés de performance")
    k1, k2, k3, k4, k5 = st.columns([2, 1.2, 1.5, 1.5, 2])
    k1.metric("Coût total",            f"${p.get('total_cost', 0):,.2f}")
    k2.metric("Clients",               f"{p.get('total_clients', 0):,}")
    k3.metric("Coût / Client",         f"${p.get('cost_per_client', 0):,.2f}")
    k4.metric("Heures économisées",    f"{p.get('estimated_hours_saved', 0):,.1f} h")
    k5.metric("Économies salariales",  f"${p.get('estimated_salary_savings', 0):,.2f}")

    st.divider()

    # ── Répartition des coûts ─────────────────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("## 💰 Répartition des coûts")
        cost_items = {
            "Voice AI":        p.get("voice_cost", 0),
            "Messages":        p.get("sms_cost", 0),
            "Email":           p.get("email_cost", 0) + p.get("email_notifications_cost", 0),
            "Flux de travail": p.get("workflow_cost", 0),
            "Vérifications":   p.get("verification_cost", 0),
            "Abonnement":      p.get("subscription_cost", 0),
        }
        # Graphique à barres horizontales trié par valeur
        sorted_items = dict(sorted(cost_items.items(), key=lambda x: x[1]))
        fig_cost = px.bar(
            x=list(sorted_items.values()),
            y=list(sorted_items.keys()),
            orientation="h",
            color=list(sorted_items.values()),
            color_continuous_scale="Purples",
        )
        fig_cost.update_traces(
            texttemplate="$%{x:,.2f}",
            textposition="outside",
        )
        fig_cost.update_layout(
            showlegend=False, coloraxis_showscale=False,
            margin=dict(t=20, b=20, r=100), yaxis_title="", xaxis_title="Coût ($)",
        )
        st.plotly_chart(fig_cost, use_container_width=True)

    with col_right:
        st.markdown("## 📨 Volume de communication")
        comm_items = {
            "Messages (SMS + Direct)":   p.get("sms_sent", 0) + p.get("messaging_direct", 0),
            "Emails (Envoyés + Notif.)": p.get("emails_sent", 0) + p.get("email_notifications", 0),
            "Appels IA":                 p.get("total_calls", 0),
            "Actions de flux":           p.get("workflow_actions", 0),
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
            margin=dict(t=20, b=20), yaxis_title="", xaxis_title="Nombre"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Voice AI & Rendez-vous ────────────────────────────────────────────────
    col_v, col_a = st.columns(2)

    with col_v:
        st.markdown("## 📞 Détail Voice AI")
        v1, v2, v3 = st.columns(3)
        v1.metric("Total appels",  f"{p.get('total_calls', 0):,}")
        v2.metric("Entrants",      f"{p.get('inbound_calls', 0):,}")
        v3.metric("Sortants",      f"{p.get('outbound_calls', 0):,}")
        minutes = p.get("total_call_minutes", 0)
        st.metric("Total minutes", f"{minutes:,.0f} min ({minutes/60:,.1f} h)")
        st.metric("Coût Voice",    f"${p.get('voice_cost', 0):,.2f}")

    with col_a:
        st.markdown("## 📅 Rendez-vous")
        appt_items = {
            "Téléphone (IA)": p.get("appointments_phone", 0),
            "Email":          p.get("appointments_email", 0),
            "SMS":            p.get("appointments_sms", 0),
        }
        total_appt = sum(appt_items.values())
        st.metric("Total rendez-vous", f"{total_appt:,}")
        fig_appt = px.pie(
            names=list(appt_items.keys()),
            values=list(appt_items.values()),
            color_discrete_sequence=["#7c3aed", "#a78bfa", "#c4b5fd"],
            hole=0.5,
        )
        fig_appt.update_layout(margin=dict(t=10, b=10), legend=dict(orientation="h"))
        st.plotly_chart(fig_appt, use_container_width=True)

    # ── Analyse ROI ───────────────────────────────────────────────────────────
    st.markdown("## 📈 Analyse ROI")
    r1, r2, r3, r4 = st.columns(4)
    total_cost     = p.get("total_cost", 0)
    salary_savings = p.get("estimated_salary_savings", 0)
    net_savings    = salary_savings - total_cost
    roi_pct        = (net_savings / total_cost * 100) if total_cost else 0

    r1.metric("Coût plateforme",   f"${total_cost:,.2f}")
    r2.metric("Salaire économisé", f"${salary_savings:,.2f}")
    r3.metric("Économies nettes",  f"${net_savings:,.2f}", delta=f"{net_savings:+,.2f}")
    r4.metric("ROI",               f"{roi_pct:.0f}%")

    # ── Comparaison de périodes ───────────────────────────────────────────────
    if len(periods) > 1:
        st.divider()
        st.markdown("## 🔄 Comparaison de périodes")
        df = pd.DataFrame(periods)
        df["label"] = df["period_start"] + " → " + df["period_end"]
        metrics_to_compare = ["total_cost", "total_actions", "estimated_hours_saved", "estimated_salary_savings"]
        selected_metric = st.selectbox("Comparer métrique", metrics_to_compare)
        fig_trend = px.bar(
            df, x="label", y=selected_metric,
            color_discrete_sequence=["#7c3aed"],
            text_auto=True,
        )
        fig_trend.update_layout(xaxis_title="Période", yaxis_title=selected_metric.replace("_", " ").title())
        st.plotly_chart(fig_trend, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PÉRIODES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "📅 Périodes":
    st.title("📅 Périodes")
    if not periods:
        st.info("Aucune période.")
    else:
        df = pd.DataFrame(periods)
        display_cols = [
            "period_start", "period_end", "total_clients",
            "total_cost", "total_actions", "estimated_hours_saved", "estimated_salary_savings",
        ]
        display_cols = [c for c in display_cols if c in df.columns]
        st.dataframe(
            df[display_cols].rename(columns={
                "period_start": "Début", "period_end": "Fin",
                "total_clients": "Clients", "total_cost": "Coût total ($)",
                "total_actions": "Actions", "estimated_hours_saved": "Heures économisées",
                "estimated_salary_savings": "Économies salariales ($)",
            }),
            use_container_width=True, hide_index=True,
        )
        st.divider()
        st.subheader("Supprimer une période")
        del_label = st.selectbox("Sélectionner une période à supprimer", [f"{p['period_start']} → {p['period_end']}" for p in periods])
        if st.button("🗑️ Supprimer", type="secondary"):
            idx   = [f"{p['period_start']} → {p['period_end']}" for p in periods].index(del_label)
            pid   = periods[idx]["id"]
            db.periods.delete_one({"id": pid})
            st.success("Période supprimée.")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: AJOUTER UNE PÉRIODE
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "➕ Ajouter une période":
    st.title("➕ Ajouter une nouvelle période")

    with st.form("add_period"):
        st.subheader("📆 Dates de la période")
        c1, c2 = st.columns(2)
        period_start = c1.date_input("Date de début")
        period_end   = c2.date_input("Date de fin")
        total_clients = st.number_input("Total clients", min_value=0, value=0)

        st.subheader("📱 Communication")
        col1, col2, col3 = st.columns(3)
        sms_sent         = col1.number_input("SMS Envoyés",         min_value=0, value=0)
        sms_cost         = col1.number_input("Coût SMS ($)",        min_value=0.0, value=0.0)
        emails_sent      = col2.number_input("Emails Envoyés",      min_value=0, value=0)
        email_cost       = col2.number_input("Coût Email ($)",      min_value=0.0, value=0.0)
        email_notif      = col3.number_input("Notifications Email", min_value=0, value=0)
        email_notif_cost = col3.number_input("Coût Notif. ($)",     min_value=0.0, value=0.0)

        st.subheader("📞 Voice AI")
        v1, v2, v3 = st.columns(3)
        total_calls    = v1.number_input("Total appels",      min_value=0, value=0)
        inbound_calls  = v2.number_input("Appels entrants",   min_value=0, value=0)
        outbound_calls = v3.number_input("Appels sortants",   min_value=0, value=0)
        call_minutes   = v1.number_input("Minutes d'appel",   min_value=0.0, value=0.0)
        voice_cost     = v2.number_input("Coût Voice ($)",    min_value=0.0, value=0.0)

        st.subheader("⚙️ Flux de travail & Messagerie")
        w1, w2 = st.columns(2)
        workflow_actions = w1.number_input("Actions de flux",      min_value=0, value=0)
        workflow_cost    = w1.number_input("Coût flux ($)",        min_value=0.0, value=0.0)
        messaging_direct = w2.number_input("Messages directs",     min_value=0, value=0)
        messaging_cost   = w2.number_input("Coût messagerie ($)",  min_value=0.0, value=0.0)

        st.subheader("📅 Rendez-vous")
        a1, a2, a3 = st.columns(3)
        appt_phone = a1.number_input("RDV téléphoniques", min_value=0, value=0)
        appt_email = a2.number_input("RDV par email",     min_value=0, value=0)
        appt_sms   = a3.number_input("RDV par SMS",       min_value=0, value=0)

        st.subheader("✅ Vérification & Abonnement")
        e1, e2, e3 = st.columns(3)
        email_verif  = e1.number_input("Vérifications email",   min_value=0, value=0)
        verif_cost   = e2.number_input("Coût vérification ($)", min_value=0.0, value=0.0)
        subscription = e3.number_input("Coût abonnement ($)",   min_value=0.0, value=settings.get("subscription_monthly", 297.0))

        submitted = st.form_submit_button("💾 Enregistrer la période", type="primary")

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
        st.success(f"✅ Période enregistrée ! Coût total : ${data['total_cost']:,.2f} | Heures économisées : {data['estimated_hours_saved']:.1f} h")
        st.balloons()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: PARAMÈTRES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "⚙️ Paramètres":
    st.title("⚙️ Paramètres")
    st.caption("Ces valeurs sont utilisées pour calculer les économies estimées.")

    with st.form("settings_form"):
        hourly_rate  = st.number_input("Taux horaire (CAD/h)", value=float(settings.get("hourly_rate", 20.0)), min_value=0.0, step=0.5)
        call_manual  = st.number_input("Durée moyenne d'un appel si fait manuellement (min)", value=float(settings.get("avg_call_duration_manual", 10.0)), min_value=0.0)
        email_manual = st.number_input("Temps moyen par email si fait manuellement (min)", value=float(settings.get("avg_email_time_manual", 3.0)), min_value=0.0)
        sms_manual   = st.number_input("Temps moyen par SMS si fait manuellement (min)", value=float(settings.get("avg_sms_time_manual", 1.0)), min_value=0.0)
        subscription = st.number_input("Abonnement mensuel ($)", value=float(settings.get("subscription_monthly", 297.0)), min_value=0.0)
        save = st.form_submit_button("💾 Enregistrer les paramètres", type="primary")

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
        st.success("Paramètres enregistrés !")
