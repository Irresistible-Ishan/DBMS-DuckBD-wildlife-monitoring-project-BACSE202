import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random, time
from datetime import datetime

DB_FILE = "wildlife_conservation.duckdb"

st.set_page_config(
    page_title="WildGuard | Wildlife Conservation Platform",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
#  GLASSMORPHISM + DARK FOREST THEME
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Font ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Root Variables ──────────────────────────────────────── */
:root {
    --glass-bg:      rgba(255,255,255,0.06);
    --glass-border:  rgba(255,255,255,0.14);
    --glass-shadow:  0 8px 32px rgba(0,0,0,0.45);
    --accent-green:  #4ade80;
    --accent-teal:   #2dd4bf;
    --accent-amber:  #fbbf24;
    --accent-red:    #f87171;
    --text-primary:  #f0fdf4;
    --text-muted:    #86efac;
    --bg-deep:       #030f06;
}

/* ── Global App Background ───────────────────────────────── */
.stApp {
    background: linear-gradient(135deg, #030f06 0%, #061a0c 40%, #041810 100%);
    font-family: 'Inter', sans-serif;
    color: var(--text-primary);
}

/* ── Hide Streamlit chrome ───────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* ── SIDEBAR ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #031208 0%, #041a0d 100%) !important;
    border-right: 1px solid rgba(74,222,128,0.15);
}
[data-testid="stSidebar"] > div:first-child { padding: 1.2rem 1rem; }

/* Sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(74,222,128,0.10);
    border: 1px solid rgba(74,222,128,0.30);
    color: var(--accent-green) !important;
    border-radius: 10px;
    font-weight: 600;
    font-size: 0.82rem;
    transition: all 0.25s ease;
    width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(74,222,128,0.22);
    border-color: var(--accent-green);
    transform: translateY(-1px);
    box-shadow: 0 4px 20px rgba(74,222,128,0.25);
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div { color: #bbf7d0 !important; }

/* Primary button inside sidebar (Fire Trigger) */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: rgba(248,113,113,0.18);
    border-color: rgba(248,113,113,0.5);
    color: #fca5a5 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: rgba(248,113,113,0.35);
    box-shadow: 0 4px 20px rgba(248,113,113,0.3);
}

/* ── HERO TITLE ──────────────────────────────────────────── */
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(100deg, #4ade80 0%, #2dd4bf 50%, #a3e635 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}
.hero-sub {
    color: #86efac;
    font-size: 0.95rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
    line-height: 1.6;
}
.hero-badge {
    display: inline-block;
    background: rgba(74,222,128,0.12);
    border: 1px solid rgba(74,222,128,0.30);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    color: var(--accent-green);
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 8px;
}

/* ── KPI METRIC CARDS ────────────────────────────────────── */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(74,222,128,0.18);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    transition: transform 0.2s;
}
[data-testid="metric-container"]:hover { transform: translateY(-2px); }
[data-testid="metric-container"] label {
    color: #86efac !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f0fdf4 !important;
    font-size: 1.55rem !important;
    font-weight: 800 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

/* ── TABS ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    color: #86efac !important;
    font-weight: 600;
    font-size: 0.85rem;
    padding: 8px 16px;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(74,222,128,0.18) !important;
    color: var(--accent-green) !important;
    border: 1px solid rgba(74,222,128,0.30) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none; }
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ── SECTION LABEL / STEP BADGES ────────────────────────── */
.section-label {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.6rem;
    margin-top: 1rem;
}
.step-badge {
    background: rgba(74,222,128,0.15);
    border: 1px solid rgba(74,222,128,0.35);
    color: var(--accent-green);
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    white-space: nowrap;
}
.step-badge-fire {
    background: rgba(248,113,113,0.15);
    border: 1px solid rgba(248,113,113,0.40);
    color: #fca5a5;
    border-radius: 8px;
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f0fdf4;
}

/* ── INSTRUCTION BOXES ───────────────────────────────────── */
.how-to-box {
    background: rgba(45,212,191,0.07);
    border: 1px solid rgba(45,212,191,0.22);
    border-radius: 12px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 1rem;
    font-size: 0.83rem;
    color: #99f6e4;
    line-height: 1.7;
}
.how-to-box strong { color: #2dd4bf; }

/* ── DATAFRAMES ──────────────────────────────────────────── */
[data-testid="stDataFrame"] > div {
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.10);
    overflow: hidden;
}

/* ── FORM inputs ─────────────────────────────────────────── */
.stForm {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 1.2rem;
}
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(74,222,128,0.20) !important;
    border-radius: 10px !important;
    color: #f0fdf4 !important;
}
[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(90deg, #16a34a, #059669) !important;
    border: none !important;
    color: white !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.5rem !important;
    width: 100% !important;
    transition: all 0.25s !important;
}
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 24px rgba(22,163,74,0.40) !important;
}

/* ── ALERTS ──────────────────────────────────────────────── */
[data-testid="stAlert"] {
    border-radius: 14px !important;
    backdrop-filter: blur(12px) !important;
}

/* ── PLOTLY charts transparent bg ───────────────────────── */
.js-plotly-plot .plotly { border-radius: 14px; }

/* ── DIVIDER ─────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.08) !important; }

/* ── EXPANDER ────────────────────────────────────────────── */
details {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 12px !important;
    margin-bottom: 0.5rem;
}
details summary { color: #86efac !important; font-weight: 600; padding: 0.6rem 0.8rem; }

/* ── CODE BLOCK ──────────────────────────────────────────── */
code, pre { background: rgba(0,0,0,0.35) !important; border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────────────────────
ZONE_LABELS = {
    "ZONE-KAZ": " Kaziranga NP",
    "ZONE-COR": " Jim Corbett TR",
    "ZONE-SUN": " Sundarbans BR",
    "ZONE-RAN": " Ranthambore NP",
}
PLOT_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#86efac", family="Inter"),
    margin=dict(l=10, r=10, t=42, b=10),
    legend=dict(bgcolor="rgba(0,0,0,0.3)", bordercolor="rgba(255,255,255,0.1)", borderwidth=1),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.08)"),
)

def plo(fig):
    """Apply global plotly layout and return figure."""
    fig.update_layout(**PLOT_LAYOUT)
    return fig

def get_con():
    return duckdb.connect(DB_FILE)

def health_badge(val):
    colors = {
        "Healthy":           ("#16a34a", "#dcfce7"),
        "In Rehabilitation": ("#c2410c", "#ffedd5"),
        "Under Observation": ("#b45309", "#fef3c7"),
        "Critical Care":     ("#be123c", "#ffe4e6"),
    }
    bg, fg = colors.get(val, ("#374151", "#f9fafb"))
    return f"background-color:{bg}; color:{fg}; border-radius:6px; padding:2px 8px; font-size:0.78rem; font-weight:600;"


# ── LIVE SIMULATION ENGINE ────────────────────────────────────────────────────
def simulate_tick(force_fire=None, normalize=False):
    con = get_con()
    now = datetime.now()
    zones   = con.execute("SELECT zone_id, base_lat, base_lon FROM protected_zones").fetchall()
    animals = con.execute("SELECT animal_id, zone_id FROM animals").fetchall()
    zone_map = {z[0]: (z[1], z[2]) for z in zones}
    acts = ["Feeding", "Migrating", "Resting", "Patrolling Territory", "At Waterhole"]

    gps = []
    for aid, zid in animals:
        blat, blon = zone_map[zid]
        lat = round(blat + random.uniform(-0.025, 0.025), 5)
        lon = round(blon + random.uniform(-0.025, 0.025), 5)
        spd = round(random.uniform(1.0, 15.5), 1)
        hr  = random.randint(60, 100)
        act = random.choice(acts)
        if force_fire == zid:
            spd, hr, act = round(random.uniform(18, 28), 1), random.randint(125, 155), "Fleeing Hazard!"
        gps.append((now, aid, zid, lat, lon, spd, hr, act))
    con.executemany("INSERT INTO gps_telemetry VALUES (?,?,?,?,?,?,?,?);", gps)

    sensors = []
    for zid, _, _ in zones:
        sid = f"IOT-{zid.split('-')[1]}-01"
        if force_fire == zid:
            t, h, r, w, a, f = round(random.uniform(46.5,52),1), round(random.uniform(12,18),1), 0.0, round(random.uniform(40,55),1), random.randint(310,420), True
        elif normalize:
            t, h, r, w, a, f = round(random.uniform(27,31),1), round(random.uniform(65,80),1), round(random.uniform(2,8.5),1), round(random.uniform(82,95),1), random.randint(35,65), False
        else:
            t, h, r, w, a, f = round(random.uniform(27,34.5),1), round(random.uniform(55,82),1), round(random.choice([0,0,0.5,2.1]),1), round(random.uniform(74,94),1), random.randint(40,88), False
        sensors.append((now, sid, zid, t, h, r, w, a, f))
    con.executemany("INSERT INTO env_sensor_logs VALUES (?,?,?,?,?,?,?,?,?);", sensors)
    con.close()


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🐾 WildGuard")
    st.markdown("<span style='color:#4ade80;font-size:0.75rem;font-weight:600;'>POWERED BY DUCKDB COLUMNAR OLAP</span>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
    <div style='background:rgba(74,222,128,0.07);border:1px solid rgba(74,222,128,0.2);border-radius:12px;padding:0.75rem 1rem;font-size:0.78rem;color:#86efac;line-height:1.6;margin-bottom:1rem;'>
    <b style='color:#4ade80;'>How to use this panel</b><br>
    1. Click <b>Inject Tick</b> to push live GPS + sensor data into DuckDB.<br>
    2. Toggle <b>Auto-Stream</b> for continuous live telemetry.<br>
    3. Use <b>Fire Drill</b> to test emergency spatial correlation.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📡 Live Data Injection")
    if st.button("📡 Inject One GPS & IoT Tick", use_container_width=True):
        simulate_tick()
        st.success("✓ Batch written to DuckDB!")

    auto = st.toggle("🔄 Auto-Stream (Every 3 s)", value=False)

    st.markdown("---")
    st.markdown("#### 🚨 Emergency Fire Drill")
    st.markdown("""
    <div style='font-size:0.76rem;color:#fca5a5;margin-bottom:0.5rem;line-height:1.5;'>
    Spikes temp to ~50°C, drops humidity to 15%, triggers real-time spatial animal hazard detection.
    </div>
    """, unsafe_allow_html=True)

    fire_zone = st.selectbox(
        "Target Zone:",
        ["ZONE-KAZ", "ZONE-COR", "ZONE-SUN", "ZONE-RAN"],
        format_func=lambda x: ZONE_LABELS[x]
    )
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if st.button("🔥 Trigger Fire", type="primary", use_container_width=True):
            simulate_tick(force_fire=fire_zone)
            st.error(f"Fire injected in {fire_zone}!")
    with col_f2:
        if st.button("🌧️ Normalize", use_container_width=True):
            simulate_tick(normalize=True)
            st.info("Sensors cleared.")

    st.markdown("---")
    con_sb = get_con()
    n_gps = con_sb.execute("SELECT COUNT(*) FROM gps_telemetry").fetchone()[0]
    n_iot = con_sb.execute("SELECT COUNT(*) FROM env_sensor_logs").fetchone()[0]
    con_sb.close()
    st.markdown(f"""
    <div style='background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.10);border-radius:12px;padding:0.8rem 1rem;font-size:0.78rem;color:#86efac;line-height:1.9;'>
    <b style='color:#4ade80;'>📊 Live DB Stats</b><br>
    🛰️ GPS Rows: <b style='color:#f0fdf4;'>{n_gps:,}</b><br>
    🌡️ Sensor Rows: <b style='color:#f0fdf4;'>{n_iot:,}</b>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HERO HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="hero-title">🌲 WildGuard Conservation Platform</div>', unsafe_allow_html=True)
st.markdown("""
<div class="hero-sub">
  Centralized OLAP database monitoring <b>endangered species</b> via GPS &amp; RFID tags, 
  <b>protected sanctuaries</b> across India, <b>IoT environmental sensors</b>, 
  <b>veterinary rescue operations</b>, and <b>government conservation grants</b> in real-time.
</div>
<div>
  <span class="hero-badge">4 Sanctuaries</span>
  <span class="hero-badge">9 Tagged Animals</span>
  <span class="hero-badge">GPS + RFID</span>
  <span class="hero-badge">IoT Sensors</span>
  <span class="hero-badge">DuckDB ARG_MAX</span>
</div>
""", unsafe_allow_html=True)

con = get_con()

# ── FIRE ALERT BANNER ─────────────────────────────────────────────────────────
latest_env = con.execute("""
    SELECT e.zone_id, z.zone_name,
        ARG_MAX(e.station_id,             e.ts) AS station_id,
        ARG_MAX(e.temperature_c,          e.ts) AS latest_temp,
        ARG_MAX(e.humidity_pct,           e.ts) AS latest_humidity,
        ARG_MAX(e.aqi,                    e.ts) AS latest_aqi,
        ARG_MAX(e.water_availability_pct, e.ts) AS latest_water,
        ARG_MAX(e.rainfall_mm,            e.ts) AS latest_rain,
        ARG_MAX(e.fire_alert,             e.ts) AS is_fire_alert,
        MAX(e.ts)                               AS last_updated
    FROM env_sensor_logs e
    JOIN protected_zones z ON e.zone_id = z.zone_id
    GROUP BY e.zone_id, z.zone_name
    ORDER BY e.zone_id;
""").df()

fire_zones = latest_env[latest_env["is_fire_alert"] == True]
if not fire_zones.empty:
    for _, fr in fire_zones.iterrows():
        az = fr["zone_id"]
        trapped = con.execute("""
            SELECT a.animal_id, a.name, a.common_name, a.tag_id,
                   ARG_MAX(g.latitude,       g.ts) AS lat,
                   ARG_MAX(g.longitude,      g.ts) AS lon,
                   ARG_MAX(g.heart_rate_bpm, g.ts) AS hr_bpm,
                   ARG_MAX(g.activity_state, g.ts) AS activity
            FROM animals a JOIN gps_telemetry g ON a.animal_id = g.animal_id
            WHERE a.zone_id = ? GROUP BY a.animal_id, a.name, a.common_name, a.tag_id
        """, [az]).df()
        st.error(
            f"🚨 **CRITICAL FIRE ALERT — {fr['zone_name'].upper()}** | "
            f"Station `{fr['station_id']}`: **{fr['latest_temp']}°C** · Humidity **{fr['latest_humidity']}%** · "
            f"AQI **{fr['latest_aqi']}** | **{len(trapped)} animals** at risk — coordinates below. "
            f"Click **Normalize** in the sidebar to clear."
        )
        st.dataframe(trapped, use_container_width=True, hide_index=True)

# ── KPI ROW ───────────────────────────────────────────────────────────────────
st.markdown("")
k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Protected Zones",    con.execute("SELECT COUNT(*) FROM protected_zones").fetchone()[0])
k2.metric("Tracked Animals",    con.execute("SELECT COUNT(*) FROM animals").fetchone()[0])
k3.metric("GPS Telemetry",      f"{con.execute('SELECT COUNT(*) FROM gps_telemetry').fetchone()[0]:,}")
k4.metric("IoT Sensor Logs",    f"{con.execute('SELECT COUNT(*) FROM env_sensor_logs').fetchone()[0]:,}")
k5.metric("Grants (₹ Lakhs)",   f"₹{con.execute('SELECT SUM(grant_amount_lakhs) FROM conservation_projects').fetchone()[0]:,.0f}L")
k6.metric("Health Logs",        con.execute("SELECT COUNT(*) FROM health_rescue_logs").fetchone()[0])

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📍  GPS Tracking & Habitats",
    "🌡️  IoT Sensors & Fire Risk",
    "🏥  Health & Rescue CRUD",
    "📊  Projects & SQL Console",
])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 1 — LIVE GPS ANIMAL TRACKING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:
    st.markdown("""
    <div class="how-to-box">
    <b>📖 How this tab works:</b> DuckDB's <code>ARG_MAX(value, timestamp)</code> function fetches the 
    <b>latest GPS coordinate, heart rate, and activity state</b> for every animal in a single vectorized scan — 
    no slow self-joins needed. Use the zone filter to focus on a specific sanctuary, then pick any animal 
    below to trace its full movement trail and vitals over the last 30 pings.
    </div>
    """, unsafe_allow_html=True)

    zone_filter = st.selectbox(
        "🔍 Filter by Sanctuary:",
        ["All Sanctuaries", "ZONE-KAZ", "ZONE-COR", "ZONE-SUN", "ZONE-RAN"],
        format_func=lambda x: ZONE_LABELS.get(x, x) if x != "All Sanctuaries" else "🌍 All Sanctuaries"
    )

    gps_df = con.execute("""
        SELECT a.animal_id, a.name, a.common_name, a.species, a.tag_type, a.tag_id,
               a.zone_id, z.zone_name, a.sex, a.age,
               a.health_status, a.conservation_status,
               ARG_MAX(g.latitude,       g.ts) AS latitude,
               ARG_MAX(g.longitude,      g.ts) AS longitude,
               ARG_MAX(g.speed_kmh,      g.ts) AS speed_kmh,
               ARG_MAX(g.heart_rate_bpm, g.ts) AS heart_rate_bpm,
               ARG_MAX(g.activity_state, g.ts) AS activity_state,
               MAX(g.ts)                        AS last_ping
        FROM animals a
        JOIN gps_telemetry g   ON a.animal_id = g.animal_id
        JOIN protected_zones z ON a.zone_id   = z.zone_id
        GROUP BY ALL ORDER BY a.animal_id;
    """).df()

    if zone_filter != "All Sanctuaries":
        gps_df = gps_df[gps_df["zone_id"] == zone_filter]

    # Map + Table
    col_map, col_tbl = st.columns([1, 1.6])
    with col_map:
        st.markdown("""
        <div class="section-label">
            <span class="step-badge">STEP 1</span>
            <span class="section-title">Live Satellite Collar Map</span>
        </div>
        """, unsafe_allow_html=True)
        st.map(gps_df, latitude="latitude", longitude="longitude", size=70, color="#4ade80")

    with col_tbl:
        st.markdown("""
        <div class="section-label">
            <span class="step-badge">STEP 2</span>
            <span class="section-title">Latest Biometric Telemetry (DuckDB ARG_MAX)</span>
        </div>
        """, unsafe_allow_html=True)

        disp = gps_df[[
            "animal_id","name","common_name","tag_type",
            "zone_name","health_status","conservation_status",
            "activity_state","speed_kmh","heart_rate_bpm","last_ping"
        ]].copy()
        disp.columns = [
            "ID","Name","Species","Tag","Zone","Health",
            "IUCN","Activity","Speed km/h","HR bpm","Last Ping"
        ]
        styled = disp.style.map(health_badge, subset=["Health"])
        st.dataframe(styled, use_container_width=True, hide_index=True, height=320)

    st.markdown("---")

    # Movement trail
    st.markdown("""
    <div class="section-label">
        <span class="step-badge">STEP 3</span>
        <span class="section-title">Individual Animal Movement Trail & Vitals (Last 30 Pings)</span>
    </div>
    """, unsafe_allow_html=True)

    animal_opts = gps_df.apply(lambda r: f"{r['animal_id']} — {r['name']} ({r['common_name']})", axis=1).tolist()
    sel_label   = st.selectbox("Select animal to trace:", animal_opts)
    sel_id      = sel_label.split(" — ")[0]

    trail = con.execute("""
        SELECT ts, latitude, longitude, speed_kmh, heart_rate_bpm, activity_state
        FROM gps_telemetry WHERE animal_id = ?
        ORDER BY ts DESC LIMIT 30
    """, [sel_id]).df()

    c1, c2 = st.columns(2)
    with c1:
        fig = px.line(trail, x="ts", y=["heart_rate_bpm","speed_kmh"],
                      markers=True, title=f"Heart Rate & Speed — {sel_id}",
                      color_discrete_sequence=["#f87171","#60a5fa"])
        fig.update_traces(line_width=2.5)
        st.plotly_chart(plo(fig), use_container_width=True)
    with c2:
        fig2 = px.scatter(trail, x="longitude", y="latitude",
                          color="activity_state", size="speed_kmh",
                          hover_data=["ts","heart_rate_bpm"],
                          title=f"Spatial Trail — {sel_id}",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(plo(fig2), use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div class="section-label">
        <span class="step-badge">STEP 4</span>
        <span class="section-title">Zone-Wise Animal Census by IUCN Status</span>
    </div>
    """, unsafe_allow_html=True)

    census = con.execute("""
        SELECT z.zone_name, a.conservation_status, COUNT(*) AS count
        FROM animals a JOIN protected_zones z ON a.zone_id = z.zone_id
        GROUP BY z.zone_name, a.conservation_status ORDER BY z.zone_name;
    """).df()
    fig3 = px.bar(census, x="zone_name", y="count", color="conservation_status",
                  barmode="group", title="Animals per Sanctuary by IUCN Status",
                  color_discrete_map={"Endangered":"#f87171","Vulnerable":"#fbbf24","Least Concern":"#4ade80"})
    st.plotly_chart(plo(fig3), use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 2 — IOT SENSORS & HABITAT RISK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:
    st.markdown("""
    <div class="how-to-box">
    <b>📖 How this tab works:</b> Each protected sanctuary has one IoT weather station streaming 
    <b>temperature, humidity, rainfall, water availability, and Air Quality Index (AQI)</b> every 5 minutes. 
    The top table shows the <b>latest reading per zone</b> (via <code>ARG_MAX</code>). 
    Select a zone to drill into its historical time-series. Use the sidebar's <b>🔥 Trigger Fire</b> button 
    to inject a wildfire anomaly — watch temp spike above 45°C and the red fire threshold line breach.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section-label">
        <span class="step-badge">LIVE MATRIX</span>
        <span class="section-title">All Zones — Latest IoT Snapshot (DuckDB ARG_MAX)</span>
    </div>
    """, unsafe_allow_html=True)

    env_disp = latest_env.copy()
    env_disp["is_fire_alert"] = env_disp["is_fire_alert"].map({True: "🔥 ALERT", False: "✅ Normal"})
    env_disp.columns = ["Zone ID","Zone Name","Station","Temp °C","Humidity %","Rain mm","Water %","AQI","Fire Status","Last Updated"]
    st.dataframe(env_disp, use_container_width=True, hide_index=True)

    st.markdown("---")

    zone_sel = st.selectbox(
        "Select zone to explore historical telemetry:",
        ["ZONE-KAZ","ZONE-COR","ZONE-SUN","ZONE-RAN"],
        format_func=lambda x: ZONE_LABELS[x],
        key="env_sel"
    )

    hist = con.execute("""
        SELECT ts, temperature_c, humidity_pct, rainfall_mm, water_availability_pct, aqi, fire_alert
        FROM env_sensor_logs WHERE zone_id = ?
        ORDER BY ts DESC LIMIT 40
    """, [zone_sel]).df()

    g1, g2 = st.columns(2)
    with g1:
        st.markdown(f"""<div class="section-label"><span class="step-badge-fire">TEMP & HUMIDITY</span>
        <span class="section-title">{ZONE_LABELS[zone_sel]}</span></div>""", unsafe_allow_html=True)
        fig = px.line(hist, x="ts", y=["temperature_c","humidity_pct"], markers=True,
                      color_discrete_sequence=["#f97316","#38bdf8"])
        fig.add_hline(y=45, line_dash="dot", line_color="#f87171", line_width=2,
                      annotation_text="Fire Threshold 45°C", annotation_font_color="#f87171")
        st.plotly_chart(plo(fig), use_container_width=True)

    with g2:
        st.markdown(f"""<div class="section-label"><span class="step-badge">AQI & WATER</span>
        <span class="section-title">{ZONE_LABELS[zone_sel]}</span></div>""", unsafe_allow_html=True)
        fig2 = px.area(hist, x="ts", y=["aqi","water_availability_pct"], markers=True,
                       color_discrete_sequence=["#c084fc","#2dd4bf"])
        fig2.add_hline(y=200, line_dash="dot", line_color="#fbbf24", line_width=2,
                       annotation_text="Hazardous AQI 200", annotation_font_color="#fbbf24")
        st.plotly_chart(plo(fig2), use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        st.markdown("""<div class="section-label"><span class="step-badge">RAINFALL</span>
        <span class="section-title">Last 15 Readings (mm)</span></div>""", unsafe_allow_html=True)
        fig3 = px.bar(hist.head(15), x="ts", y="rainfall_mm",
                      color_discrete_sequence=["#3b82f6"])
        st.plotly_chart(plo(fig3), use_container_width=True)

    with g4:
        st.markdown("""<div class="section-label"><span class="step-badge">CROSS-ZONE</span>
        <span class="section-title">Environmental Comparison (Latest)</span></div>""", unsafe_allow_html=True)
        fig4 = px.bar(latest_env, x="zone_name", y=["latest_temp","latest_aqi","latest_water"],
                      barmode="group",
                      color_discrete_sequence=["#f97316","#c084fc","#2dd4bf"],
                      labels={"value":"Reading","variable":"Metric"})
        st.plotly_chart(plo(fig4), use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 3 — HEALTH, DISEASE & RESCUE CRUD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:
    st.markdown("""
    <div class="how-to-box">
    <b>📖 How this tab works:</b> Use the form on the left to <b>log a new field event</b> 
    (rescue operation, disease alert, breeding sighting, or health check). 
    Clicking <b>Save</b> performs an <b>ACID transaction</b> in DuckDB — 
    an <code>INSERT</code> into <code>health_rescue_logs</code> and an <code>UPDATE</code> on 
    <code>animals.health_status</code> atomically. The table on the right refreshes instantly.
    </div>
    """, unsafe_allow_html=True)

    col_form, col_logs = st.columns([1, 1.7])

    with col_form:
        st.markdown("""<div class="section-label"><span class="step-badge">LOG EVENT</span>
        <span class="section-title">New Field Report</span></div>""", unsafe_allow_html=True)

        with st.form("rescue_form", clear_on_submit=True):
            all_animals = con.execute("SELECT animal_id, name, common_name, zone_id FROM animals").fetchall()
            choices = [f"{a[0]} ({a[1]} - {a[2]}) [{a[3]}]" for a in all_animals]
            chosen = st.selectbox("🐾 Select Animal:", choices)

            evt = st.selectbox("Event Category:", [
                "Rescue & Rehabilitation",
                "Disease Outbreak Alert",
                "Breeding Activity",
                "Health Check & Tagging",
                "Feeding Behavior Observation",
            ])
            new_status = st.selectbox("Update Health Status:", [
                "Healthy","In Rehabilitation","Under Observation","Critical Care"
            ])
            vet = st.text_input("Veterinarian / Researcher:", "Dr. R. Subramanian (WII)")
            notes = st.text_area("Clinical Notes:", "Vitals stable; collar operational.")

            saved = st.form_submit_button("💾 Save Record to DuckDB", type="primary", use_container_width=True)
            if saved:
                aid = chosen.split(" ")[0]
                zid = chosen.split("[")[1].replace("]","")
                nid = con.execute("SELECT COALESCE(MAX(log_id),0)+1 FROM health_rescue_logs").fetchone()[0]
                con.execute("INSERT INTO health_rescue_logs VALUES (?,?,?,?,?,?,?,?);",
                            [nid, datetime.now(), aid, zid, evt, notes, vet, new_status])
                con.execute("UPDATE animals SET health_status=? WHERE animal_id=?;", [new_status, aid])
                st.success(f"✅ Record #{nid} saved → {aid} is now **{new_status}**")
                st.rerun()

        st.markdown("---")
        st.markdown("""<div class="section-label"><span class="step-badge">ANALYTICS</span>
        <span class="section-title">Events by Category</span></div>""", unsafe_allow_html=True)
        cat_df = con.execute("""
            SELECT event_category AS category, COUNT(*) AS count
            FROM health_rescue_logs GROUP BY event_category ORDER BY count DESC;
        """).df()
        fig_pie = px.pie(cat_df, values="count", names="category", hole=0.48,
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(plo(fig_pie), use_container_width=True)

    with col_logs:
        st.markdown("""<div class="section-label"><span class="step-badge">RECORDS</span>
        <span class="section-title">All Veterinary & Rescue Logs (Newest First)</span></div>""",
                    unsafe_allow_html=True)

        logs = con.execute("""
            SELECT h.log_id, h.log_time, h.animal_id, a.name AS animal_name,
                   a.common_name, h.zone_id, h.event_category,
                   h.rehab_status, h.vet_or_researcher, h.details
            FROM health_rescue_logs h JOIN animals a ON h.animal_id = a.animal_id
            ORDER BY h.log_time DESC;
        """).df()
        st.dataframe(logs, use_container_width=True, hide_index=True, height=380)

        st.markdown("---")
        st.markdown("""<div class="section-label"><span class="step-badge">TIMELINE</span>
        <span class="section-title">Event History Scatter Timeline</span></div>""",
                    unsafe_allow_html=True)

        tl = logs.copy()
        tl["log_time"] = pd.to_datetime(tl["log_time"])
        fig_tl = px.scatter(tl, x="log_time", y="animal_name", color="event_category",
                            symbol="event_category",
                            hover_data=["zone_id","vet_or_researcher","rehab_status"],
                            title="All Logged Events",
                            color_discrete_sequence=px.colors.qualitative.Bold)
        fig_tl.update_traces(marker_size=12)
        st.plotly_chart(plo(fig_tl), use_container_width=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TAB 4 — CONSERVATION PROJECTS & SQL CONSOLE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:
    st.markdown("""
    <div class="how-to-box">
    <b>📖 How this tab works:</b> Displays all government-funded conservation projects joined with 
    field survey reports — funding agency, grant size, biodiversity index, population estimates, and 
    researcher details. The <b>Live SQL Console</b> at the bottom lets you run <b>any DuckDB query</b> 
    directly during your viva. Pre-written example queries are ready to run with one click.
    </div>
    """, unsafe_allow_html=True)

    proj_df = con.execute("""
        SELECT p.project_id, p.project_title, p.funding_agency, p.grant_amount_lakhs,
               z.zone_name, p.target_species, p.start_date, p.status,
               s.lead_researcher, s.institution, s.survey_date,
               s.estimated_population, s.biodiversity_index, s.report_summary
        FROM conservation_projects p
        JOIN protected_zones z    ON p.zone_id    = z.zone_id
        LEFT JOIN field_surveys s ON p.project_id = s.project_id
        ORDER BY p.grant_amount_lakhs DESC;
    """).df()
    st.dataframe(proj_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="section-label"><span class="step-badge">FUNDING</span>
        <span class="section-title">Grant Allocation by Sanctuary (₹ Lakhs)</span></div>""",
                    unsafe_allow_html=True)
        fig = px.bar(proj_df, x="zone_name", y="grant_amount_lakhs",
                     color="funding_agency", text="grant_amount_lakhs",
                     color_discrete_sequence=px.colors.qualitative.Safe)
        fig.update_traces(texttemplate="₹%{text:.0f}L", textposition="outside")
        st.plotly_chart(plo(fig), use_container_width=True)

    with c2:
        st.markdown("""<div class="section-label"><span class="step-badge">BIODIVERSITY</span>
        <span class="section-title">Biodiversity Index by Zone</span></div>""",
                    unsafe_allow_html=True)
        fig2 = px.bar(proj_df, x="zone_name", y="biodiversity_index", color="target_species",
                      text="biodiversity_index",
                      hover_data=["estimated_population","lead_researcher"],
                      color_discrete_sequence=px.colors.qualitative.Pastel)
        fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(plo(fig2), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""<div class="section-label"><span class="step-badge">POPULATION</span>
        <span class="section-title">Estimated Wildlife Count by Zone</span></div>""",
                    unsafe_allow_html=True)
        fig3 = px.funnel(proj_df.sort_values("estimated_population", ascending=False),
                         x="estimated_population", y="zone_name",
                         color_discrete_sequence=["#4ade80"])
        st.plotly_chart(plo(fig3), use_container_width=True)

    with c4:
        st.markdown("""<div class="section-label"><span class="step-badge">SHARE</span>
        <span class="section-title">Funding Share by Agency</span></div>""",
                    unsafe_allow_html=True)
        fund_sum = con.execute("""
            SELECT funding_agency, SUM(grant_amount_lakhs) AS total
            FROM conservation_projects GROUP BY funding_agency ORDER BY total DESC;
        """).df()
        fig4 = px.pie(fund_sum, values="total", names="funding_agency", hole=0.45,
                      color_discrete_sequence=px.colors.qualitative.Bold)
        fig4.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(plo(fig4), use_container_width=True)

    # ── LIVE SQL CONSOLE ──────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div class="section-label">
        <span class="step-badge">LIVE CONSOLE</span>
        <span class="section-title">DuckDB OLAP SQL Query Inspector</span>
    </div>
    <div class="how-to-box" style="margin-top:0.5rem;">
    <b>How to use:</b> Edit or replace the query below and click <b>Execute</b>. 
    You can query any of the 7 tables: 
    <code>protected_zones</code> · <code>animals</code> · <code>gps_telemetry</code> · 
    <code>env_sensor_logs</code> · <code>health_rescue_logs</code> · 
    <code>conservation_projects</code> · <code>field_surveys</code>
    </div>
    """, unsafe_allow_html=True)

    default_sql = """-- DuckDB OLAP: Zone summary using ARG_MAX + multi-table joins
SELECT
    z.zone_name,
    z.state,
    COUNT(DISTINCT a.animal_id)                    AS tracked_animals,
    ROUND(AVG(e.temperature_c), 2)                 AS avg_temp_c,
    MAX(e.aqi)                                     AS peak_aqi,
    SUM(CASE WHEN e.fire_alert THEN 1 ELSE 0 END)  AS fire_incidents,
    MAX(p.grant_amount_lakhs)                      AS largest_grant_lakhs,
    MAX(s.biodiversity_index)                      AS biodiversity_index
FROM protected_zones z
LEFT JOIN animals               a ON z.zone_id    = a.zone_id
LEFT JOIN env_sensor_logs       e ON z.zone_id    = e.zone_id
LEFT JOIN conservation_projects p ON z.zone_id    = p.zone_id
LEFT JOIN field_surveys         s ON p.project_id = s.project_id
GROUP BY z.zone_name, z.state
ORDER BY tracked_animals DESC;"""

    sql_input = st.text_area("SQL Query:", value=default_sql, height=190)

    run_col, hint_col = st.columns([1,3])
    with run_col:
        run = st.button("▶️ Execute on DuckDB", type="primary", use_container_width=True)
    with hint_col:
        st.info("💡 Try: `SHOW TABLES;` or `DESCRIBE gps_telemetry;` or `SELECT * FROM animals;`")

    if run:
        try:
            res = con.execute(sql_input).df()
            st.success(f"✅ Query returned **{len(res)} rows** and **{len(res.columns)} columns**")
            st.dataframe(res, use_container_width=True, hide_index=True)
        except Exception as ex:
            st.error(f"❌ SQL Error: {ex}")

    # Pre-built example queries
    st.markdown("---")
    st.markdown("""<div class="section-label"><span class="step-badge">EXAMPLES</span>
    <span class="section-title">Ready-to-Run DuckDB Demo Queries for Viva</span></div>""",
                unsafe_allow_html=True)

    examples = {
        "1. Latest GPS ping per animal using ARG_MAX": """SELECT a.name, a.common_name, a.zone_id,
    ARG_MAX(g.latitude,       g.ts) AS lat,
    ARG_MAX(g.longitude,      g.ts) AS lon,
    ARG_MAX(g.heart_rate_bpm, g.ts) AS latest_hr,
    ARG_MAX(g.activity_state, g.ts) AS activity,
    MAX(g.ts)                        AS last_ping
FROM animals a JOIN gps_telemetry g ON a.animal_id = g.animal_id
GROUP BY ALL ORDER BY last_ping DESC;""",
        "2. Heart rate & speed by behaviour (aggregation)": """SELECT activity_state,
    COUNT(*)                       AS records,
    ROUND(AVG(heart_rate_bpm), 1)  AS avg_hr_bpm,
    ROUND(AVG(speed_kmh), 1)       AS avg_speed,
    MIN(heart_rate_bpm)            AS min_hr,
    MAX(heart_rate_bpm)            AS max_hr
FROM gps_telemetry
GROUP BY activity_state ORDER BY avg_hr_bpm DESC;""",
        "3. All fire alert events with zone info": """SELECT z.zone_name, e.station_id, e.ts,
    e.temperature_c, e.humidity_pct, e.aqi
FROM env_sensor_logs e
JOIN protected_zones z ON e.zone_id = z.zone_id
WHERE e.fire_alert = TRUE ORDER BY e.ts DESC;""",
        "4. Grant ROI — cost per individual tracked": """SELECT p.project_title, p.funding_agency,
    p.grant_amount_lakhs, s.estimated_population,
    ROUND(p.grant_amount_lakhs / s.estimated_population, 4) AS cost_per_individual_lakh,
    s.biodiversity_index
FROM conservation_projects p
JOIN field_surveys s ON p.project_id = s.project_id
ORDER BY s.biodiversity_index DESC;""",
    }

    for label, qsql in examples.items():
        with st.expander(f"📋 {label}"):
            st.code(qsql, language="sql")
            if st.button(f"▶️ Run this query", key=f"ex_{label}"):
                try:
                    r = con.execute(qsql).df()
                    st.dataframe(r, use_container_width=True, hide_index=True)
                except Exception as ex:
                    st.error(f"❌ {ex}")

con.close()

# ── AUTO-STREAM ───────────────────────────────────────────────────────────────
if auto:
    time.sleep(3)
    simulate_tick()
    st.rerun()
