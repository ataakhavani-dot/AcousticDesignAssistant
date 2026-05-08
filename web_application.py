import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="ADA | Acoustic Design",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to mimic the Dark Dashboard aesthetic
st.markdown("""
<style>
    /* Main background and text */
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    /* Hide default Streamlit top menu and footer for a standalone app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Style the metric boxes */
    div[data-testid="stMetricValue"] {
        color: #3b82f6;
    }
    /* Headers */
    h1, h2, h3 {
        color: #f8fafc !important;
    }
    /* Custom tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #1e293b;
        padding: 10px 20px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LAYER ---
MATERIALS = {
    "Concrete (Reflective)": [0.01, 0.01, 0.01, 0.02, 0.02, 0.03],
    "Brick Wall (Reflective)": [0.03, 0.03, 0.03, 0.04, 0.05, 0.07],
    "Glass (Reflective)": [0.35, 0.25, 0.18, 0.12, 0.07, 0.04],
    "Wood Floor (Reflective)": [0.15, 0.11, 0.10, 0.07, 0.06, 0.07],
    "Drywall (Standard)": [0.29, 0.10, 0.05, 0.04, 0.07, 0.09],
    "Heavy Carpet (Absorptive)": [0.02, 0.06, 0.14, 0.37, 0.60, 0.65],
    "Acoustic Foam (Absorptive)": [0.08, 0.25, 0.60, 0.90, 0.95, 0.90],
    "Fiberglass 4in (Absorptive)": [0.25, 0.90, 1.10, 1.05, 1.00, 1.00],
    "Velvet Curtains (Absorptive)": [0.07, 0.31, 0.49, 0.75, 0.70, 0.60]
}
OCTAVE_BANDS = ['125', '250', '500', '1k', '2k', '4k']
SPEED_OF_SOUND = 343.0

# --- 3. PHYSICS ENGINE FUNCTIONS ---
def get_room_ratios(L, W, H):
    dims = sorted([L, W, H], reverse=True) # L > W > H
    return dims[1]/dims[2], dims[0]/dims[2] # W/H, L/H

def check_bolt_area(x, y):
    # Simplified bounding box check for the UI status
    if 1.14 < x < 1.6 and 1.12 < y < 1.54:
        return "Stable Zone", "normal"
    return "Unstable", "inverse"

def calculate_modes(L, W, H, max_freq=300):
    modes = []
    for n in range(1, 5):
        modes.append({'Freq': (SPEED_OF_SOUND/2)*(n/L), 'Axis': 'Length', 'Color': '#ef4444'})
        modes.append({'Freq': (SPEED_OF_SOUND/2)*(n/W), 'Axis': 'Width', 'Color': '#22c55e'})
        modes.append({'Freq': (SPEED_OF_SOUND/2)*(n/H), 'Axis': 'Height', 'Color': '#3b82f6'})
    
    df = pd.DataFrame(modes)
    return df[df['Freq'] <= max_freq].sort_values(by='Freq')

def calculate_sbir_curve(distances):
    freqs = np.array([40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800])
    resp = np.zeros(len(freqs))
    
    for d in distances:
        if d > 0:
            f_cancel = SPEED_OF_SOUND / (4 * d)
            # Simulate a notch filter dip
            for i, f in enumerate(freqs):
                diff = abs(f - f_cancel)
                if diff < (f_cancel * 0.3):
                    resp[i] -= 10 * (1 - (diff/(f_cancel*0.3)))
    return freqs, np.maximum(resp, -20)

# --- 4. APP LAYOUT & UI ---

# Sidebar
with st.sidebar:
    st.markdown("## 🌊 ADA")
    st.caption("Acoustic Design Assistant • Prototype")
    st.markdown("---")
    st.markdown("**Project Phase:** Core Logic Sprints")
    st.markdown("**Hot Reloading:** Active ⚡")
    
    # Store global materials state if we want to add presets later
    st.markdown("---")
    st.info("💡 Adjust the room dimensions in the main panel to see real-time updates across all tabs.")

# Main Content Header
st.title("Room Geometry")
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

with col1:
    L = st.slider("Length (m)", 2.0, 15.0, 5.0, 0.1)
with col2:
    W = st.slider("Width (m)", 2.0, 15.0, 4.0, 0.1)
with col3:
    H = st.slider("Height (m)", 2.0, 8.0, 3.0, 0.1)

volume = L * W * H
surface_area = 2 * (L*W + L*H + W*H)

with col4:
    st.metric("Volume", f"{volume:.1f} m³")
with col5:
    st.metric("Surface", f"{surface_area:.1f} m²")

st.markdown("---")

# Tabs
tab_modes, tab_rt60, tab_sbir = st.tabs([
    "📊 Modal Analysis", 
    "⏱️ RT60 Calculator", 
    "📡 SBIR Analysis"
])

# === TAB 1: MODAL ANALYSIS ===
with tab_modes:
    st.markdown("### Low-Frequency Behavior (0-300Hz)")
    
    mc1, mc2 = st.columns(2)
    
    with mc1:
        st.markdown("**Bolt Area Stability Zone**")
        x_ratio, y_ratio = get_room_ratios(L, W, H)
        status, delta_color = check_bolt_area(x_ratio, y_ratio)
        
        # Plotly Bolt Area
        fig_bolt = go.Figure()
        # Bolt Polygon
        fig_bolt.add_trace(go.Scatter(
            x=[1.14, 1.28, 1.60, 1.50, 1.14], 
            y=[1.39, 1.54, 1.28, 1.12, 1.39],
            fill='toself', fillcolor='rgba(34, 197, 94, 0.2)',
            line=dict(color='#22c55e', width=2),
            name="Stable Zone", hoverinfo="skip"
        ))
        # Current Room Point
        fig_bolt.add_trace(go.Scatter(
            x=[x_ratio], y=[y_ratio],
            mode='markers', marker=dict(color='#ef4444', size=12, line=dict(color='white', width=2)),
            name="Current Room"
        ))
        fig_bolt.update_layout(
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Width / Height Ratio", yaxis_title="Length / Height Ratio",
            xaxis=dict(range=[0.8, 2.0]), yaxis=dict(range=[0.8, 2.0]),
            margin=dict(l=0, r=0, t=0, b=0), height=350
        )
        st.plotly_chart(fig_bolt, use_container_width=True)
        st.metric("Status", status, delta="Ratio Check", delta_color=delta_color)

    with mc2:
        st.markdown("**Axial Modal Frequencies**")
        df_modes = calculate_modes(L, W, H)
        
        # Plotly Bar Chart (Stem Plot style)
        fig_modes = go.Figure()
        for axis, color in zip(['Length', 'Width', 'Height'], ['#ef4444', '#22c55e', '#3b82f6']):
            axis_data = df_modes[df_modes['Axis'] == axis]
            fig_modes.add_trace(go.Bar(
                x=axis_data['Freq'], y=[1]*len(axis_data),
                marker_color=color, name=axis, width=3
            ))
        fig_modes.update_layout(
            template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Frequency (Hz)", yaxis=dict(showticklabels=False, range=[0, 1.1]),
            margin=dict(l=0, r=0, t=0, b=0), height=350, barmode='overlay'
        )
        st.plotly_chart(fig_modes, use_container_width=True)
    
    st.info("💡 **Glass Box Physics:** The Rayleigh Equation")
    st.latex(r"f = \frac{c}{2} \sqrt{\left(\frac{n_x}{L}\right)^2 + \left(\frac{n_y}{W}\right)^2 + \left(\frac{n_z}{H}\right)^2}")

# === TAB 2: RT60 CALCULATOR ===
with tab_rt60:
    st.markdown("### Reverberation Time")
    
    rc1, rc2, rc3 = st.columns(3)
    with rc1: mat_wall = st.selectbox("Walls", list(MATERIALS.keys()), index=4)
    with rc2: mat_floor = st.selectbox("Floor", list(MATERIALS.keys()), index=3)
    with rc3: mat_ceil = st.selectbox("Ceiling", list(MATERIALS.keys()), index=4)
    
    a_wall = np.array(MATERIALS[mat_wall])
    a_floor = np.array(MATERIALS[mat_floor])
    a_ceil = np.array(MATERIALS[mat_ceil])
    
    area_walls = 2 * (L*H + W*H)
    area_floor = L * W
    area_ceil = L * W
    
    # Target RT60 (IEC standard approximation)
    target_rt = 0.25 * (volume/100)**(1/3)
    
    sabine_rt = []
    eyring_rt = []
    
    for i in range(6):
        abs_total = (a_wall[i]*area_walls) + (a_floor[i]*area_floor) + (a_ceil[i]*area_ceil)
        alpha_avg = abs_total / surface_area
        
        # Sabine
        sabine_rt.append((0.161 * volume) / abs_total)
        # Eyring
        e_rt = (0.161 * volume) / (-surface_area * np.log(1 - alpha_avg)) if alpha_avg < 0.99 else 0
        eyring_rt.append(e_rt)
    
    # Plotly Line Chart
    fig_rt = go.Figure()
    fig_rt.add_trace(go.Scatter(x=OCTAVE_BANDS, y=sabine_rt, mode='lines+markers', name='Sabine', line=dict(color='#3b82f6', width=3)))
    fig_rt.add_trace(go.Scatter(x=OCTAVE_BANDS, y=eyring_rt, mode='lines+markers', name='Eyring', line=dict(color='#8b5cf6', width=3, dash='dash')))
    fig_rt.add_trace(go.Scatter(x=OCTAVE_BANDS, y=[target_rt]*6, mode='lines', name='Target', line=dict(color='#22c55e', width=2)))
    
    fig_rt.update_layout(
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Time (Seconds)", yaxis=dict(rangemode='tozero'),
        margin=dict(l=0, r=0, t=30, b=0), height=350
    )
    st.plotly_chart(fig_rt, use_container_width=True)
    
    st.info("💡 **Glass Box Physics:** The Sabine Formula")
    st.latex(r"RT_{60} = \frac{0.161 \times V}{\sum (S_i \times \alpha_i)}")

# === TAB 3: SBIR ANALYSIS ===
with tab_sbir:
    st.markdown("### Speaker-Boundary Interference Response")
    
    sc1, sc2, sc3 = st.columns(3)
    with sc1: d_front = st.slider("Dist to Front Wall (m)", 0.1, 5.0, 1.0, 0.1)
    with sc2: d_side = st.slider("Dist to Side Wall (m)", 0.1, 5.0, 0.8, 0.1)
    with sc3: d_floor = st.slider("Dist to Floor (m)", 0.1, 3.0, 1.2, 0.1)
    
    f_front = round(SPEED_OF_SOUND / (4 * d_front)) if d_front > 0 else 0
    f_side = round(SPEED_OF_SOUND / (4 * d_side)) if d_side > 0 else 0
    f_floor = round(SPEED_OF_SOUND / (4 * d_floor)) if d_floor > 0 else 0
    
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Front Wall Dip", f"{f_front} Hz")
    mc2.metric("Side Wall Dip", f"{f_side} Hz")
    mc3.metric("Floor Dip", f"{f_floor} Hz")
    
    freqs, resp = calculate_sbir_curve([d_front, d_side, d_floor])
    
    fig_sbir = go.Figure()
    fig_sbir.add_trace(go.Scatter(
        x=freqs, y=resp, mode='lines', fill='tozeroy',
        line=dict(color='#ef4444', width=3), fillcolor='rgba(239, 68, 68, 0.2)'
    ))
    
    fig_sbir.update_layout(
        template="plotly_dark", plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Frequency (Hz)", yaxis_title="Amplitude (dB)",
        xaxis=dict(type='log', tickvals=[40, 60, 100, 200, 400, 800]), yaxis=dict(range=[-20, 2]),
        margin=dict(l=0, r=0, t=30, b=0), height=300
    )
    st.plotly_chart(fig_sbir, use_container_width=True)
    
    st.info("💡 **Glass Box Physics:** Quarter-Wavelength Cancellation")
    st.latex(r"f_{cancel} = \frac{c}{4d}")