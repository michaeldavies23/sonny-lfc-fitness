import streamlit as st
import streamlit.components.v1 as components
import json
import os
import base64
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Sonny's LFC Pro Tracker",
    page_icon="⚽",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- LFC THEME & FUT CARD CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Teko:wght@500;700&family=Inter:wght@400;700;900&display=swap');

    .stApp {
        background: radial-gradient(circle at top, #9b001a 0%, #4a000b 50%, #1a0004 100%);
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3 {
        color: #F6EB61 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* FUT Card Styling */
    .fut-card {
        background: linear-gradient(135deg, #c8102e 0%, #8a081c 55%, #111111 100%);
        border: 4px solid #F6EB61;
        border-radius: 24px 24px 40px 40px;
        width: 310px;
        margin: 0 auto 20px auto;
        padding: 20px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.7), inset 0 0 20px rgba(246, 235, 97, 0.25);
        color: #fff;
        font-family: 'Teko', sans-serif;
        position: relative;
        text-align: center;
    }
    .fut-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 2px solid rgba(246, 235, 97, 0.4);
        padding-bottom: 8px;
    }
    .fut-rating {
        font-size: 4.2rem;
        line-height: 0.85;
        color: #F6EB61;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.6);
    }
    .fut-pos {
        font-size: 2rem;
        color: #ffffff;
        letter-spacing: 2px;
    }
    .fut-badge {
        font-size: 3.5rem;
        line-height: 1;
        filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.5));
    }
    .fut-name {
        font-size: 2.8rem;
        font-weight: 700;
        letter-spacing: 3px;
        margin: 10px 0 4px 0;
        color: #ffffff;
        text-shadow: 2px 2px 5px #000;
        border-bottom: 2px solid #F6EB61;
    }
    .fut-tier {
        font-family: 'Inter', sans-serif;
        font-size: 0.8rem;
        font-weight: 900;
        color: #00B2A9;
        background: rgba(0,0,0,0.6);
        padding: 3px 10px;
        border-radius: 12px;
        display: inline-block;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .fut-stats {
        display: flex;
        justify-content: space-around;
        padding-top: 6px;
    }
    .stat-box {
        text-align: center;
    }
    .stat-val {
        font-size: 2.4rem;
        font-weight: 700;
        color: #F6EB61;
        line-height: 1;
    }
    .stat-label {
        font-size: 1.3rem;
        color: #ddd;
        letter-spacing: 1px;
    }

    /* Trophy & Milestone Cards */
    .trophy-card {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(246, 235, 97, 0.4);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 15px;
    }
    .trophy-unlocked {
        background: linear-gradient(90deg, rgba(200, 16, 46, 0.6), rgba(0, 178, 169, 0.3));
        border: 2px solid #F6EB61;
    }
    .trophy-icon {
        font-size: 2.2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- DATA PERSISTENCE ---
DATA_FILE = "sonny_lfc_save.json"

DEFAULT_DATA = {
    "pac_xp": 0,      # 100 XP per point above 70
    "sta_xp": 0,      # 100 XP per point above 70
    "men_xp": 0,      # 100 XP per point above 70
    "total_distance_m": 0,
    "total_sprints": 0,
    "total_runs": 0,
    "best_100m": None,
    "history": []
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_DATA.copy()
    return DEFAULT_DATA.copy()

def save_data(data):
    st.session_state.player_data = data
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

if "player_data" not in st.session_state:
    st.session_state.player_data = load_data()

data = st.session_state.player_data

# --- STAT CALCULATIONS ---
def calc_stat(xp):
    return min(99, 70 + int(xp // 100))

pac = calc_stat(data["pac_xp"])
sta = calc_stat(data["sta_xp"])
men = calc_stat(data["men_xp"])
ovr = int(round((pac + sta + men) / 3))

def get_card_tier(ovr_score):
    if ovr_score < 75:
        return "Kirkby Academy Prospect"
    elif ovr_score < 82:
        return "First Team Debutant"
    elif ovr_score < 88:
        return "Anfield Regular"
    elif ovr_score < 94:
        return "Kop Idol"
    else:
        return "99 Club Legend"

tier_name = get_card_tier(ovr)

# --- HEADER & FUT CARD ---
st.markdown(f"""
<div class="fut-card">
    <div class="fut-top">
        <div>
            <div class="fut-rating">{ovr}</div>
            <div class="fut-pos">ST • #9</div>
        </div>
        <div class="fut-badge">🦅</div>
    </div>
    <div class="fut-name">SONNY</div>
    <div class="fut-tier">{tier_name}</div>
    <div class="fut-stats">
        <div class="stat-box">
            <div class="stat-val">{pac}</div>
            <div class="stat-label">PAC</div>
        </div>
        <div class="stat-box">
            <div class="stat-val">{sta}</div>
            <div class="stat-label">STA</div>
        </div>
        <div class="stat-box">
            <div class="stat-val">{men}</div>
            <div class="stat-label">MEN</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# XP Progress Bars to next stat level
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"⚡ PAC XP ({data['pac_xp'] % 100}/100)")
    st.progress((data["pac_xp"] % 100) / 100)
with col2:
    st.caption(f"🫁 STA XP ({data['sta_xp'] % 100}/100)")
    st.progress((data["sta_xp"] % 100) / 100)
with col3:
    st.caption(f"🧠 MEN XP ({data['men_xp'] % 100}/100)")
    st.progress((data["men_xp"] % 100) / 100)

# --- NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["⏱️ Pitch Tracker", "🏆 Trophy Room", "💾 Save / Backup"])

# ==========================================
# TAB 1: REAL-TIME GPS & STOPWATCH TRACKER
# ==========================================
with tab1:
    st.subheader("Live Session Tracker")
    
    drill_type = st.selectbox(
        "Choose Your Training Drill:",
        [
            "⚡ Counter-Attack Sprint (Target: 101m / 1 Anfield Length)",
            "⚡ Penalty Box Dash (Target: 50m Quick Sprint)",
            "🏃‍♂️ High Press Shuttle / Custom Sprint",
            "🫁 Full Match Shift (1km Endurance Run)",
            "🫁 Extra Time Engine (2km+ Distance Run)"
        ]
    )

    st.caption("Use the live GPS & Stopwatch below during your run, then log the stats beneath to upgrade your card!")

    # Embedded Real-Time JS GPS + Stopwatch Component
    gps_stopwatch_html = """
    <div style="background:#111; border:2px solid #F6EB61; border-radius:16px; padding:16px; color:#fff; font-family:sans-serif; text-align:center;">
        <div style="display:flex; justify-content:space-around; margin-bottom:12px;">
            <div>
                <div style="font-size:0.8rem; color:#aaa; text-transform:uppercase;">Live Timer</div>
                <div id="time-display" style="font-size:2.4rem; font-weight:900; color:#F6EB61; font-family:monospace;">00:00.0</div>
            </div>
            <div>
                <div style="font-size:0.8rem; color:#aaa; text-transform:uppercase;">GPS Distance</div>
                <div id="dist-display" style="font-size:2.4rem; font-weight:900; color:#00B2A9; font-family:monospace;">0 m</div>
            </div>
        </div>

        <div style="background:#222; border-radius:8px; padding:8px; margin-bottom:12px;">
            <div style="font-size:0.85rem; color:#ddd;">🏟️ Anfield Pitch Progress (101m = 1 Pitch)</div>
            <div id="anfield-count" style="font-size:1.1rem; font-weight:bold; color:#F6EB61; margin-top:4px;">0.00 Anfield Pitches</div>
        </div>

        <div id="gps-status" style="font-size:0.8rem; color:#aaa; margin-bottom:12px;">
            📍 GPS Ready — Press Start when ready to run
        </div>

        <div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap;">
            <button id="start-btn" onclick="startTracking()" style="background:#00B2A9; color:#fff; border:none; padding:12px 20px; border-radius:10px; font-weight:bold; font-size:1rem; cursor:pointer;">▶ START</button>
            <button id="checkin-btn" onclick="manualCheckIn()" style="background:#C8102E; color:#fff; border:1px solid #F6EB61; padding:12px 16px; border-radius:10px; font-weight:bold; font-size:1rem; cursor:pointer;">📍 GPS CHECK-IN</button>
            <button id="stop-btn" onclick="stopTracking()" style="background:#e63946; color:#fff; border:none; padding:12px 20px; border-radius:10px; font-weight:bold; font-size:1rem; cursor:pointer;" disabled>⏹ STOP</button>
            <button onclick="resetTracking()" style="background:#444; color:#fff; border:none; padding:12px 16px; border-radius:10px; font-weight:bold; font-size:1rem; cursor:pointer;">↺ RESET</button>
        </div>
    </div>

    <script>
        let startTime = 0;
        let elapsedTime = 0;
        let timerInterval = null;
        let watchId = null;
        let lastPos = null;
        let totalDistance = 0;
        let running = false;

        function haversine(lat1, lon1, lat2, lon2) {
            const R = 6371000;
            const toRad = x => x * Math.PI / 180;
            const dLat = toRad(lat2 - lat1);
            const dLon = toRad(lon2 - lon1);
            const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
                      Math.sin(dLon/2) * Math.sin(dLon/2);
            return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        }

        function updateDisplay() {
            let totalSec = elapsedTime / 1000;
            let mins = Math.floor(totalSec / 60);
            let secs = (totalSec % 60).toFixed(1);
            document.getElementById('time-display').innerText = 
                String(mins).padStart(2, '0') + ':' + String(secs).padStart(4, '0');
            
            let roundedDist = Math.round(totalDistance);
            document.getElementById('dist-display').innerText = roundedDist + ' m';
            document.getElementById('anfield-count').innerText = (totalDistance / 101).toFixed(2) + ' Anfield Pitches';
        }

        function handlePosition(pos) {
            const lat = pos.coords.latitude;
            const lon = pos.coords.longitude;
            const acc = Math.round(pos.coords.accuracy);

            if (lastPos) {
                const d = haversine(lastPos.lat, lastPos.lon, lat, lon);
                // Filter tiny GPS jitter (< 2.5m)
                if (d >= 2.5) {
                    totalDistance += d;
                    lastPos = {lat, lon};
                    updateDisplay();
                }
            } else {
                lastPos = {lat, lon};
            }
            document.getElementById('gps-status').innerText = `📍 GPS Locked (±${acc}m accuracy)`;
        }

        function startTracking() {
            if (running) return;
            running = true;
            startTime = Date.now() - elapsedTime;
            timerInterval = setInterval(() => {
                elapsedTime = Date.now() - startTime;
                updateDisplay();
            }, 100);

            document.getElementById('start-btn').disabled = true;
            document.getElementById('stop-btn').disabled = false;

            if (navigator.geolocation) {
                document.getElementById('gps-status').innerText = "📡 Acquiring satellite lock...";
                watchId = navigator.geolocation.watchPosition(
                    handlePosition,
                    err => { document.getElementById('gps-status').innerText = "⚠️ GPS Error: " + err.message; },
                    { enableHighAccuracy: true, maximumAge: 0, timeout: 10000 }
                );
            } else {
                document.getElementById('gps-status').innerText = "⚠️ Geolocation not supported by browser";
            }
        }

        function manualCheckIn() {
            if (!navigator.geolocation) return;
            document.getElementById('gps-status').innerText = "📍 Checking in current point...";
            navigator.geolocation.getCurrentPosition(
                pos => {
                    const lat = pos.coords.latitude;
                    const lon = pos.coords.longitude;
                    if (lastPos) {
                        const d = haversine(lastPos.lat, lastPos.lon, lat, lon);
                        totalDistance += d;
                    }
                    lastPos = {lat, lon};
                    updateDisplay();
                    document.getElementById('gps-status').innerText = "✅ Check-in point recorded!";
                },
                err => { document.getElementById('gps-status').innerText = "⚠️ Check-in failed: " + err.message; },
                { enableHighAccuracy: true }
            );
        }

        function stopTracking() {
            running = false;
            clearInterval(timerInterval);
            if (watchId !== null) {
                navigator.geolocation.clearWatch(watchId);
                watchId = null;
            }
            document.getElementById('start-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;
            document.getElementById('gps-status').innerText = "🏁 Run Stopped! Enter your time & distance below.";
        }

        function resetTracking() {
            stopTracking();
            elapsedTime = 0;
            totalDistance = 0;
            lastPos = null;
            updateDisplay();
            document.getElementById('gps-status').innerText = "📍 GPS Reset — Ready for next run";
        }
    </script>
    """
    components.html(gps_stopwatch_html, height=275)

    # --- LOGGING FORM ---
    st.markdown("### 📝 Claim Your Match XP")
    with st.form("log_workout_form"):
        c1, c2 = st.columns(2)
        with c1:
            default_dist = 101 if "101m" in drill_type else (50 if "50m" in drill_type else (1000 if "1km" in drill_type else 200))
            dist_m = st.number_input("Distance Covered (metres)", min_value=10, max_value=20000, value=default_dist, step=10)
        with c2:
            time_sec = st.number_input("Time Taken (seconds)", min_value=1.0, max_value=7200.0, value=18.0, step=0.5)

        submitted = st.form_submit_button("🔥 CLAIM XP & UPGRADE CARD", use_container_width=True)

        if submitted:
            is_sprint = dist_m <= 400
            if is_sprint:
                # Pace XP boosted for fast sprints
                speed_mps = dist_m / max(1.0, time_sec)
                gained_pac = int(40 + (speed_mps * 8))
                gained_sta = int(dist_m / 10)
                gained_men = 35
                data["total_sprints"] += 1
                if dist_m >= 95 and dist_m <= 110:
                    if data["best_100m"] is None or time_sec < data["best_100m"]:
                        data["best_100m"] = round(time_sec, 1)
            else:
                # Stamina XP boosted for longer runs
                gained_pac = 25
                gained_sta = int(dist_m / 12)
                gained_men = 50
                data["total_runs"] += 1

            data["pac_xp"] += gained_pac
            data["sta_xp"] += gained_sta
            data["men_xp"] += gained_men
            data["total_distance_m"] += dist_m

            data["history"].insert(0, {
                "date": datetime.now().strftime("%d %b %H:%M"),
                "drill": drill_type.split("(")[0].strip(),
                "dist_m": dist_m,
                "time_s": time_sec,
                "xp": f"+{gained_pac} PAC | +{gained_sta} STA | +{gained_men} MEN"
            })

            save_data(data)
            st.balloons()
            st.success(f"Class effort Sonny! Earned +{gained_pac} PAC XP, +{gained_sta} STA XP, and +{gained_men} MEN XP!")
            st.rerun()

# ==========================================
# TAB 2: VIRTUAL TROPHY CABINET & STATS
# ==========================================
with tab2:
    st.subheader("🏟️ Anfield Virtual Progress")
    anfield_laps = round(data["total_distance_m"] / 101, 1)
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Distance", f"{data['total_distance_m']} m")
    m2.metric("Anfield Lengths", f"{anfield_laps} 🏟️")
    m3.metric("100m Sprint PB", f"{data['best_100m']}s" if data["best_100m"] else "Not set")

    st.subheader("🏆 Virtual Trophy Cabinet")
    trophies = [
        ("⚡", "Kirkby Speedster", "Complete your first sprint session", data["total_sprints"] >= 1),
        ("🏟️", "Length of the Pitch", "Cover at least 101m (1 Anfield Pitch)", data["total_distance_m"] >= 101),
        ("🚀", "Counter-Attack Threat", "Complete 5 sprint sessions", data["total_sprints"] >= 5),
        ("🫁", "Heavy Metal Football", "Cover 1,000m (1km) total distance", data["total_distance_m"] >= 1000),
        ("👑", "The Egyptian King's Pace", "Reach 80+ PAC Rating on your card", pac >= 80),
        ("🔥", " Kop End Engine", "Cover 5,000m (5km) total distance", data["total_distance_m"] >= 5000),
        ("⭐", "Anfield №9 Legend", "Reach 85+ Overall (OVR) Rating", ovr >= 85),
    ]

    for icon, title, desc, unlocked in trophies:
        status_cls = "trophy-unlocked" if unlocked else ""
        badge_state = "✅ UNLOCKED" if unlocked else "🔒 Locked"
        st.markdown(f"""
        <div class="trophy-card {status_cls}">
            <div class="trophy-icon">{icon}</div>
            <div style="flex-grow:1;">
                <div style="font-weight:bold; font-size:1.05rem; color:#F6EB61;">{title}</div>
                <div style="font-size:0.85rem; color:#ddd;">{desc}</div>
            </div>
            <div style="font-size:0.75rem; font-weight:bold;">{badge_state}</div>
        </div>
        """, unsafe_allow_html=True)

    if data["history"]:
        st.subheader("📋 Recent Match Logs")
        for item in data["history"][:6]:
            st.caption(f"**{item['date']}** — {item['drill']}: **{item['dist_m']}m** in **{item['time_s']}s** ({item['xp']})")

# ==========================================
# TAB 3: CLOUD SAVE CODE BACKUP
# ==========================================
with tab3:
    st.subheader("💾 Player Card Backup Code")
    st.write("If you host this on Streamlit Cloud, copy this code occasionally so Sonny never loses his stats if the server restarts.")
    
    save_code = base64.b64encode(json.dumps(data).encode("utf-8")).decode("utf-8")
    st.code(save_code, language="text")

    restore_input = st.text_input("Paste a Save Code here to restore stats:")
    if st.button("Restore Player Card"):
        try:
            restored_data = json.loads(base64.b64decode(restore_input.encode("utf-8")).decode("utf-8"))
            save_data(restored_data)
            st.success("Player Card restored!")
            st.rerun()
        except Exception:
            st.error("Invalid save code.")
