# ============================================================================
# ACOUSTIC DESIGN ASSISTANT (ADA) - Web Application
# A tool to help users understand how sound behaves in rooms
# ============================================================================

# SECTION 1: IMPORT EXTERNAL LIBRARIES
# These are tools/packages that other people wrote that we're using in our app
import streamlit as st           # Creates interactive web apps in Python (no HTML needed!)
import streamlit.components.v1 as components
import numpy as np               # For fast math calculations with lists of numbers
import pandas as pd              # For organizing data into tables (like Excel)
import plotly.graph_objects as go  # For creating interactive charts and graphs
import plotly.express as px      # A simpler way to make charts with plotly
# ============================================================================
# SECTION 2: PAGE CONFIGURATION & STYLING
# This sets up how the web page will look and behave
# ============================================================================

# Configure basic page settings that appear in the browser tab and layout
st.set_page_config(
    page_title="ADA | Acoustic Design Assistant",  # Text shown in browser tab
    page_icon="🌊",  # Small icon next to the title in browser tab
    layout="wide",  # Use full width of screen (instead of narrow center column)
    initial_sidebar_state="collapsed"  # Hide the sidebar by default to save space
)

# Initialize session state for navigation
if 'nav_target' not in st.session_state:
    st.session_state.nav_target = None

# No query params needed - we'll use hash-based navigation


# CUSTOM CSS STYLING
# This is special code (HTML/CSS) that makes the page look nice with colors and formatting
st.markdown("""
<style>
    /* ===== GLOBAL TYPOGRAPHY SCALING ===== */
    /* Increase the base text size by 15% across the entire app */
    html, body, .stApp, [data-testid="stAppViewContainer"] {
        font-size: 115% !important;
    }

    /* ===== MAIN PAGE COLORS ===== */
    /* These settings change the background and text colors of the entire app */
    .stApp {
        background-color: #0f172a;  /* Very dark blue background (like night sky) */
        color: #e2e8f0;  /* Light gray text color (easy on the eyes) */
    }
    
    /* HIDE DEFAULT STREAMLIT ELEMENTS */
    /* We hide these to make the app look more professional and custom */
    #MainMenu {visibility: hidden;}  /* Hide the Streamlit hamburger menu */
    footer {visibility: hidden;}  /* Hide "Made with Streamlit" footer */
    
    /* ===== METRIC BOXES STYLING ===== */
    /* Metrics are the boxes showing numbers like "Volume: 60 m³" */
    div[data-testid="stMetricValue"] {
        color: #60a5fa;  /* Match the blue used for slider labels and accents */
    }
    /* The labels above the numbers (like "Volume", "Surface") */
    div[data-testid="stMetric"] label {
        color: #e2e8f0 !important;  /* Keep labels bright and readable */
    }
    
    /* ===== INPUT CONTROLS STYLING ===== */
    /* These are sliders (Length, Width, Height) and dropdown menus */
    .stSlider > label {
        color: #e2e8f0 !important;  /* Label text for sliders */
    }
    .stSelectbox > label {
        color: #e2e8f0 !important;  /* Label text for dropdown menus */
    }
    
    /* ===== HEADERS STYLING ===== */
    /* H1/H2/H3 are the different heading sizes (### Room Geometry = H3) */
    h1, h2, h3 {
        color: #f8fafc !important;  /* Very light color for headers (brightest text) */
    }
    
    /* ===== TABS STYLING ===== */
    /* The tabs are the "📊 Modal Analysis", "⏱️ RT60 Calculator", etc buttons at top */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;  /* Space between tab buttons */
        background-color: #15223E;  /* Match the requested dark blue tone */
        padding: 10px 20px;  /* Space inside the tab area */
        border-radius: 10px;  /* Rounded corners */
    }
    /* The inactive tabs (not currently selected) */
    .stTabs [data-baseweb="tab"] {
        color: #94a3b8;  /* Grayish text for inactive tabs */
    }
    /* The active tab (currently selected) */
    .stTabs [aria-selected="true"] {
        color: #60a5fa !important;  /* Bright blue for active tab */
    }

    /* ===== ROOM GEOMETRY SECTION SPACING ===== */
    div[data-testid="stSlider"] {
        padding-top: 0.75rem;
        padding-bottom: 1rem;
    }
    div[data-testid="stMetric"] {
        padding: 1rem 1.1rem;
        min-height: 96px;
        margin-top: 0.5rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.32rem !important;
        line-height: 1.2;
    }

    /* Make the Room Geometry controls and metrics 15% larger while leaving the heading unchanged */
    div[data-testid="stSlider"] label,
    div[data-testid="stMetric"] label,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
        font-size: 115% !important;
    }

    /* ===== GLASS BOX DARK THEME OVERRIDES ===== */
    /* Target code blocks with multiple selector strategies to ensure coverage */
    
    /* Strategy 1: Direct element styling */
    code {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
        padding: 12px !important;
        border-radius: 8px !important;
        display: block !important;
        border: 1px solid #333 !important;
    }
    
    pre {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
        padding: 16px !important;
        border-radius: 8px !important;
        border: 1px solid #333 !important;
        overflow-x: auto !important;
    }
    
    pre code {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
    }
    
    /* Strategy 2: Target Streamlit's code block container */
    div[data-testid="stCodeBlock"],
    div[class*="code"],
    div[class*="Code"] {
        background-color: #1e1e1e !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    
    div[data-testid="stCodeBlock"] * {
        background-color: #1e1e1e !important;
        color: #e0e0e0 !important;
    }
    
    /* Copy button styling */
    div[data-testid="stCodeBlock"] button,
    button[aria-label*="Copy"],
    button[title*="Copy"] {
        color: #888 !important;
        background-color: transparent !important;
    }
    
    div[data-testid="stCodeBlock"] button:hover,
    button[aria-label*="Copy"]:hover,
    button[title*="Copy"]:hover {
        color: #ffffff !important;
    }

    /* Apply dark grey background to all containers */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: #1a2332 !important;
        border-radius: 8px !important;
    }
    
    /* Alternatively, target containers more generally */
    [data-testid="stContainer"] {
        background-color: #1a2332 !important;
    }

    div[data-testid="stExpander"] {
        background-color: #111827 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] > div {
        background-color: #111827 !important;
        color: #e2e8f0 !important;
    }

</style>
""", unsafe_allow_html=True)  # unsafe_allow_html=True lets us use custom HTML/CSS


# ============================================================================
# SECTION 3: DATA LAYER - CONSTANTS & MATERIAL PROPERTIES
# This is the data our app uses (like a phone book of information)
# ============================================================================

# MATERIALS DICTIONARY
# Stores information about different building materials and how much sound they absorb
# The numbers in the lists represent absorption coefficients at different frequencies
# (Higher number = material absorbs more sound at that frequency)
MATERIALS = {
    # REFLECTIVE MATERIALS (bounce sound back - not great for acoustics)
    "Concrete (Reflective)": [0.01, 0.01, 0.01, 0.02, 0.02, 0.03],  # Very reflective, absorbs almost no sound
    "Brick Wall (Reflective)": [0.03, 0.03, 0.03, 0.04, 0.05, 0.07],  # Hard surfaces reflect sound
    "Glass (Reflective)": [0.35, 0.25, 0.18, 0.12, 0.07, 0.04],  # Glass bounces a lot of sound
    "Wood Floor (Reflective)": [0.15, 0.11, 0.10, 0.07, 0.06, 0.07],  # Hard wood is somewhat reflective
    "Drywall (Standard)": [0.29, 0.10, 0.05, 0.04, 0.07, 0.09],  # Standard wall material
    
    # ABSORPTIVE MATERIALS (soak up sound - good for acoustics)
    "Heavy Carpet (Absorptive)": [0.02, 0.06, 0.14, 0.37, 0.60, 0.65],  # Absorbs more sound than reflective
    "Acoustic Foam (Absorptive)": [0.08, 0.25, 0.60, 0.90, 0.95, 0.90],  # Special foam designed to absorb sound
    "Fiberglass 4in (Absorptive)": [0.25, 0.90, 1.10, 1.05, 1.00, 1.00],  # Very thick and very absorptive
    "Velvet Curtains (Absorptive)": [0.07, 0.31, 0.49, 0.75, 0.70, 0.60]  # Soft fabric absorbs sound
}

# OCTAVE BANDS
# These are specific frequencies (Hz = cycles per second) that audio engineers use
# They divide the hearing range into bands - think of it like dividing a piano keyboard into sections
OCTAVE_BANDS = ['125', '250', '500', '1k', '2k', '4k']  # From low to high frequency

# SPEED OF SOUND
# How fast sound travels through air at room temperature
# This is a physics constant - you use it in many acoustic calculations
SPEED_OF_SOUND = 343.0  # meters per second at 20°C


# ============================================================================
# SECTION 4: AI RESPONSE GENERATOR
# Generates helpful responses to acoustic questions
# ============================================================================

def generate_ai_response(question):
    """
    Generate a response to acoustic questions based on keywords.
    This provides educational guidance on acoustic principles.
    """
    question_lower = question.lower()
    
    # Knowledge base with patterns and responses
    responses = {
        "rt60": "RT60 (reverberation time) is the time it takes for sound to decay by 60 dB in a room. Use Sabine's formula: RT60 = 0.161 * V / (α * S), where V is volume, α is average absorption coefficient, and S is total surface area. For a 60 m³ room with typical absorption, you'd expect RT60 of 0.5-2 seconds depending on treatment.",
        
        "mode": "Room modes are standing wave patterns that occur at specific frequencies determined by room dimensions. Axial modes involve sound bouncing between two parallel walls (simpler), while tangential modes bounce between four surfaces and oblique modes between all six. They cause reinforcement and cancellation at different frequencies, affecting bass response.",
        
        "absorber": "Porous absorbers (like foam and fiberglass) work by converting acoustic energy to heat as sound passes through the material. Thickness matters: at 100 Hz (3.4m wavelength), you'd need roughly 2-4 inches (5-10cm) of porous material for meaningful absorption. Lower frequencies require thicker materials.",
        
        "stc": "Sound Transmission Class (STC) measures how much sound a barrier blocks across 16 frequencies (125Hz-4kHz). IIC (Impact Isolation Class) measures impact noise like footsteps. Higher numbers = better isolation. A wall with STC 60 reduces sound by about 60dB, adequate for separating offices.",
        
        "measurement": "Use an SPL meter and pink noise to measure room response. Take measurements at multiple points (at least 3-5 locations). Plot frequency response to identify problem modes. Measure RT60 with tone bursts or music, recording how quickly sound decays after stopping playback.",
        
        "treatment": "Start by identifying problem frequencies using modal analysis. Place absorption at first-reflection points (where sound bounces from speakers to ears). Corner bass traps help with low-frequency modes. Diffusion randomizes reflections for better imaging without over-damping the room.",
        
        "isolation": "Decouple structures from the rest of the building using floating floors, resilient channels, or decoupled drywall layers. Seal all air gaps to prevent flanking paths. Increase mass with multiple drywall layers. Combine these techniques for 50+dB isolation.",
        
        "sbir": "Speaker-Boundary Interference Response (SBIR) occurs when direct speaker sound combines with reflections from nearby walls, causing cancellation at certain frequencies. Moving the speaker away from boundaries or treating reflective surfaces reduces SBIR. The problem frequency ≈ 343 Hz·m / (4 × distance in meters).",
        
        "default": "I can help with acoustic questions! Ask about RT60 calculation, room modes, absorbers, isolation, measurement techniques, SBIR, STC/IIC ratings, or treatment strategies. What would you like to know?"
    }
    
    # Check for keyword matches
    for keyword, response in responses.items():
        if keyword in question_lower:
            return response
    
    # If no keyword match, return default helpful response
    return responses["default"]


# ============================================================================
# SECTION 6: REUSABLE GLASS BOX CALCULATION CARD
# This renders the calculation as an explanatory info card with inputs and factors
# ============================================================================

def render_glass_box(title, inputs, formula_latex, formula_elements, substitution, calculation_steps):
    """
    Reusable function to render a Glass Box calculation card.
    It emphasizes the key factors behind the calculation and the workflow used to reach the result.
    """
    with st.container(border=True):
        st.subheader(title)

        st.markdown("**How this calculation is built**")
        st.write("This card explains the main factors that influence the result and shows the calculation path step by step.")

        st.markdown("**Key factors**")
        factor_items = [f"- **{k}:** {v}" for k, v in formula_elements.items()]
        st.write("\n".join(factor_items))

        st.markdown("**Inputs**")
        input_string = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
        st.code(input_string, language="plaintext")

        st.markdown("**Formula**")
        st.latex(formula_latex)

        with st.expander("Show substitution and steps"):
            st.markdown("**Substitution**")
            st.code(substitution, language="plaintext")

            st.markdown("**Calculation Steps**")
            steps_string = "\n".join(calculation_steps)
            st.code(steps_string, language="plaintext")


def render_audio_carousel():
    """
    Render a podcast-style audio card component with waveform animations.
    """
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {
        background-color: transparent;
        color: #e0e0e0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        margin: 0;
        padding: 0;
    }

    .card-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
        gap: 16px;
        margin-bottom: 16px;
    }

    .podcast-card {
        background: #1a1f2e;
        border: 1px solid #2a3544;
        border-radius: 12px;
        padding: 16px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .podcast-card:hover {
        border-color: var(--accent-color);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), 0 0 12px var(--glow-color);
        transform: translateY(-2px);
    }

    .card-content {
        display: flex;
        gap: 14px;
        align-items: flex-start;
    }

    .thumbnail {
        width: 90px;
        height: 90px;
        min-width: 90px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    .thumbnail svg {
        width: 32px;
        height: 32px;
        transition: transform 0.2s ease;
    }

    .podcast-card:hover .thumbnail svg {
        transform: scale(1.1);
    }

    .details {
        display: flex;
        flex-direction: column;
        gap: 3px;
    }

    .meta {
        font-size: 11px;
        color: #8b8d9b;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .title {
        font-size: 16px;
        font-weight: 700;
        color: #ffffff;
        margin: 2px 0;
        line-height: 1.2;
    }

    .author {
        font-size: 12px;
        color: #8b8d9b;
        margin-bottom: 4px;
    }

    .description {
        font-size: 11px;
        color: #9ea0b0;
        line-height: 1.4;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }

    /* Waveform styling */
    .waveform-container {
        display: flex;
        align-items: flex-end;
        gap: 3px;
        height: 24px;
        margin-top: 12px;
        padding-top: 8px;
    }

    .wave-bar {
        flex: 1;
        background-color: var(--wave-color);
        border-radius: 1px;
        height: 30%;
        opacity: 0.6;
        transition: height 0.2s ease, opacity 0.2s ease;
    }

    /* Active playing state animation */
    .podcast-card.playing .wave-bar {
        opacity: 1;
        animation: wave 1.2s ease-in-out infinite alternate;
    }

    @keyframes wave {
        0% { height: 15%; }
        100% { height: 100%; }
    }

    /* Player box */
    .player-box {
        background: #1a1f2e;
        border: 1px solid #2a3544;
        border-radius: 10px;
        padding: 12px 16px;
        margin-top: 8px;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }

    .now-playing-title {
        font-size: 12px;
        font-weight: 600;
        color: #60a5fa;
    }

    audio {
        width: 100%;
        height: 32px;
    }
    </style>
    </head>
    <body>

    <div class="card-grid">
        
        <!-- CARD 1 (Amber Theme) -->
        <div class="podcast-card" 
             style="--accent-color: #fbbf24; --glow-color: rgba(251, 191, 36, 0.2); --wave-color: #fbbf24;" 
             onclick="playAudio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', 'Understanding Room Modes', this)">
            <div class="card-content">
                <div class="thumbnail" style="background: linear-gradient(135deg, #fbbf24, #f59e0b);">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#1a1f2e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                </div>
                <div class="details">
                    <div class="meta">Ep. 001 · ⏱ 12 min</div>
                    <div class="title">Room Modes</div>
                    <div class="author">Acoustic Fundamentals</div>
                    <div class="description">Explore how sound waves bounce in a room and create standing wave patterns.</div>
                </div>
            </div>
            <div class="waveform-container">
                <div class="wave-bar" style="height: 40%;"></div>
                <div class="wave-bar" style="height: 70%; animation-delay: 0.1s;"></div>
                <div class="wave-bar" style="height: 30%; animation-delay: 0.3s;"></div>
                <div class="wave-bar" style="height: 90%; animation-delay: 0.2s;"></div>
                <div class="wave-bar" style="height: 50%; animation-delay: 0.4s;"></div>
                <div class="wave-bar" style="height: 80%; animation-delay: 0.1s;"></div>
                <div class="wave-bar" style="height: 35%; animation-delay: 0.5s;"></div>
                <div class="wave-bar" style="height: 60%; animation-delay: 0.2s;"></div>
            </div>
        </div>

        <!-- CARD 2 (Purple Theme) -->
        <div class="podcast-card" 
             style="--accent-color: #a78bfa; --glow-color: rgba(167, 139, 250, 0.2); --wave-color: #a78bfa;" 
             onclick="playAudio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3', 'Reverberation Time (RT60)', this)">
            <div class="card-content">
                <div class="thumbnail" style="background: linear-gradient(135deg, #a78bfa, #8b5cf6);">
                    <svg viewBox="0 0 24 24" fill="#1a1f2e">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"></path>
                    </svg>
                </div>
                <div class="details">
                    <div class="meta">Ep. 002 · ⏱ 15 min</div>
                    <div class="title">RT60 Limits</div>
                    <div class="author">Reverberation Basics</div>
                    <div class="description">Learn how long sound takes to decay and why it matters for your room.</div>
                </div>
            </div>
            <div class="waveform-container">
                <div class="wave-bar" style="height: 30%;"></div>
                <div class="wave-bar" style="height: 80%; animation-delay: 0.2s;"></div>
                <div class="wave-bar" style="height: 50%; animation-delay: 0.4s;"></div>
                <div class="wave-bar" style="height: 100%; animation-delay: 0.1s;"></div>
                <div class="wave-bar" style="height: 40%; animation-delay: 0.3s;"></div>
                <div class="wave-bar" style="height: 90%; animation-delay: 0.5s;"></div>
                <div class="wave-bar" style="height: 60%; animation-delay: 0.2s;"></div>
                <div class="wave-bar" style="height: 35%; animation-delay: 0.4s;"></div>
            </div>
        </div>

        <!-- CARD 3 (Blue Theme) -->
        <div class="podcast-card" 
             style="--accent-color: #60a5fa; --glow-color: rgba(96, 165, 250, 0.2); --wave-color: #60a5fa;" 
             onclick="playAudio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3', 'Speaker Boundary Interference Response (SBIR)', this)">
            <div class="card-content">
                <div class="thumbnail" style="background: linear-gradient(135deg, #60a5fa, #3b82f6);">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#1a1f2e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polygon points="23 7 16 12 23 17 23 7"></polygon>
                        <rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect>
                    </svg>
                </div>
                <div class="details">
                    <div class="meta">Ep. 003 · ⏱ 14 min</div>
                    <div class="title">SBIR Effects</div>
                    <div class="author">Speaker Placement</div>
                    <div class="description">Understand how speaker position affects bass response near walls and corners.</div>
                </div>
            </div>
            <div class="waveform-container">
                <div class="wave-bar" style="height: 45%;"></div>
                <div class="wave-bar" style="height: 75%; animation-delay: 0.15s;"></div>
                <div class="wave-bar" style="height: 60%; animation-delay: 0.3s;"></div>
                <div class="wave-bar" style="height: 85%; animation-delay: 0.2s;"></div>
                <div class="wave-bar" style="height: 55%; animation-delay: 0.35s;"></div>
                <div class="wave-bar" style="height: 78%; animation-delay: 0.1s;"></div>
                <div class="wave-bar" style="height: 42%; animation-delay: 0.4s;"></div>
                <div class="wave-bar" style="height: 72%; animation-delay: 0.25s;"></div>
            </div>
        </div>

        <!-- CARD 4 (Cyan Theme) -->
        <div class="podcast-card" 
             style="--accent-color: #22d3ee; --glow-color: rgba(34, 211, 238, 0.2); --wave-color: #22d3ee;" 
             onclick="playAudio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3', 'The Bolt Area Explained', this)">
            <div class="card-content">
                <div class="thumbnail" style="background: linear-gradient(135deg, #22d3ee, #06b6d4);">
                    <svg viewBox="0 0 24 24" fill="none" stroke="#1a1f2e" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                        <polyline points="13 2 13 9 20 9"></polyline>
                    </svg>
                </div>
                <div class="details">
                    <div class="meta">Ep. 004 · ⏱ 16 min</div>
                    <div class="title">Bolt Area</div>
                    <div class="author">Room Stability</div>
                    <div class="description">Discover the golden ratio for room dimensions that create stable acoustic conditions.</div>
                </div>
            </div>
            <div class="waveform-container">
                <div class="wave-bar" style="height: 35%;"></div>
                <div class="wave-bar" style="height: 65%; animation-delay: 0.12s;"></div>
                <div class="wave-bar" style="height: 55%; animation-delay: 0.25s;"></div>
                <div class="wave-bar" style="height: 88%; animation-delay: 0.18s;"></div>
                <div class="wave-bar" style="height: 48%; animation-delay: 0.38s;"></div>
                <div class="wave-bar" style="height: 72%; animation-delay: 0.08s;"></div>
                <div class="wave-bar" style="height: 52%; animation-delay: 0.45s;"></div>
                <div class="wave-bar" style="height: 82%; animation-delay: 0.2s;"></div>
            </div>
        </div>

    </div>

    <!-- Embedded Player -->
    <div class="player-box">
        <div id="player-title" class="now-playing-title">Select a topic to start listening</div>
        <audio id="audio-element" controls>
            <source id="audio-source" src="" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
    </div>

    <script>
    function playAudio(url, title, cardElement) {
        var player = document.getElementById('audio-element');
        var source = document.getElementById('audio-source');
        var titleDisplay = document.getElementById('player-title');
        
        // Remove 'playing' class from all cards
        var allCards = document.querySelectorAll('.podcast-card');
        allCards.forEach(c => c.classList.remove('playing'));
        
        // Add 'playing' class to the clicked card to trigger wave animation
        cardElement.classList.add('playing');
        
        // Update audio source and playback
        source.src = url;
        titleDisplay.innerHTML = "Now Playing: " + title;
        player.load();
        player.play();
    }
    </script>

    </body>
    </html>
    """
    components.html(html_code, height=520)


# ============================================================================
# SECTION 7: PHYSICS ENGINE FUNCTIONS
# These functions calculate acoustic properties based on physics principles
# ============================================================================

def get_room_ratios(L, W, H):
    """
    Calculate room dimension ratios to check if a room has good acoustic properties.
    
    Explanation for beginners:
    - Room ratios (proportions) affect how sound waves move and bounce
    - If a room is too cube-shaped or has bad ratios, it creates acoustic problems
    - This function sorts dimensions and calculates ratios used to check stability
    
    Args:
        L: Length of room (meters)
        W: Width of room (meters)
        H: Height of room (meters)
    
    Returns:
        Two ratios: (Width/Height, Length/Height)
    """
    dims = sorted([L, W, H], reverse=True)  # Sort from largest to smallest: [largest, middle, smallest]
    return dims[1]/dims[2], dims[0]/dims[2]  # Return: middle/smallest and largest/smallest


def check_bolt_area(x, y):
    """
    Check if room ratios fall within the "Bolt area" - a zone of good acoustic ratios.
    
    Explanation for beginners:
    - The Bolt area is a specific zone on a graph where room ratios sound good
    - It's named after acoustician Beranek Bolt
    - If your room point falls inside this zone, you're in good shape acoustically
    - If outside, your room proportions might cause acoustic problems
    
    Args:
        x: Width to Height ratio (first number)
        y: Length to Height ratio (second number)
    
    Returns:
        (status_text, color_indicator) - either "Stable Zone" or "Unstable"
    """
    # Check if the x,y point is inside the Bolt area polygon (the stable zone)
    # These numbers define the corners of a rectangle on the graph
    if 1.14 < x < 1.6 and 1.12 < y < 1.54:
        return "Stable Zone", "normal"  # Point is inside - good acoustics!
    return "Unstable", "inverse"  # Point is outside - potential acoustic issues


def calculate_modes(L, W, H, max_freq=300):
    """
    Calculate MODAL FREQUENCIES - frequencies where sound waves get "stuck" in the room.
    
    Explanation for beginners:
    - Sound in a room doesn't move randomly - it creates standing patterns (like waves on a guitar string)
    - Each length, width, and height of the room creates its own resonance frequencies
    - At these frequencies, certain spots get VERY loud and others are quiet (problem!)
    - This function calculates all modes from 0-300 Hz, which is where most problems happen
    
    How it works:
    - The formula: f = (c/2) * (n / dimension)
    - c = speed of sound, n = mode number (1, 2, 3...), dimension = room size
    - Each room dimension (L, W, H) creates its own set of modes
    - We calculate modes for each axis with different colors for easy visualization
    
    Args:
        L: Length (meters)
        W: Width (meters)  
        H: Height (meters)
        max_freq: Only show modes below this frequency (default 300 Hz)
    
    Returns:
        DataFrame with columns: Freq (Hz), Axis (which direction), Color (for plotting)
    """
    modes = []  # Empty list to store all our calculated modes
    
    # Loop from mode 1 to mode 4 (higher modes are less important)
    for n in range(1, 5):
        # Calculate mode along LENGTH axis (color = red)
        # Formula: frequency = (speed_of_sound / 2) * (mode_number / length)
        modes.append({'Freq': (SPEED_OF_SOUND/2)*(n/L), 'Axis': 'Length', 'Color': '#ef4444'})
        
        # Calculate mode along WIDTH axis (color = green)
        modes.append({'Freq': (SPEED_OF_SOUND/2)*(n/W), 'Axis': 'Width', 'Color': '#22c55e'})
        
        # Calculate mode along HEIGHT axis (color = blue)
        modes.append({'Freq': (SPEED_OF_SOUND/2)*(n/H), 'Axis': 'Height', 'Color': '#3b82f6'})
    
    # Convert the list of modes into a nice table (DataFrame)
    df = pd.DataFrame(modes)
    
    # Filter to keep only modes below max_freq and sort from lowest to highest frequency
    return df[df['Freq'] <= max_freq].sort_values(by='Freq')


def calculate_sbir_curve(distances):
    """
    Calculate SBIR (Speaker-Boundary Interference Response) curve.
    
    Explanation for beginners:
    - SBIR is what happens when sound from a speaker bounces off nearby walls
    - When direct sound and reflected sound arrive at the same time, they cancel each other out
    - This creates a "notch" (dip) in the frequency response at specific frequencies
    - These problem frequencies are calculated by: f = c / (4 * distance_to_wall)
    - This function simulates this acoustic effect across a range of frequencies
    
    Args:
        distances: List of distances to walls [distance_to_front, distance_to_side, distance_to_floor]
    
    Returns:
        (frequencies, response) - two arrays: frequencies (Hz) and amplitude response (dB)
    """
    # Create a list of important frequencies to analyze (audio range)
    freqs = np.array([40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800])
    
    # Create an array of response values, all starting at zero
    # We'll subtract from this array to show the "dips" (problem areas)
    resp = np.zeros(len(freqs))
    
    # For each distance to a wall, calculate the cancellation dip
    for d in distances:
        if d > 0:  # Only process if distance is greater than zero
            # Calculate the frequency where cancellation happens
            # Quarter-wavelength cancellation: f = c / (4 * distance)
            # This is the frequency most affected by this wall distance
            f_cancel = SPEED_OF_SOUND / (4 * d)
            
            # Loop through each frequency in our list
            for i, f in enumerate(freqs):
                # Calculate how far this frequency is from the problem frequency
                diff = abs(f - f_cancel)
                
                # Create a dip at the problem frequency (and some surrounding area)
                # 0.3 means the dip affects frequencies within 30% of the problem frequency
                if diff < (f_cancel * 0.3):
                    # Subtract from response: bigger dip right at f_cancel, smaller dip around it
                    # The response shows negative dB = quieter
                    resp[i] -= 10 * (1 - (diff/(f_cancel*0.3)))
    
    # Make sure response doesn't go lower than -20 dB (realistic limit)
    return freqs, np.maximum(resp, -20)



# ============================================================================
# SECTION 8: APP LAYOUT & USER INTERFACE
# This is where we build the actual web page that users interact with
# ============================================================================

# --- SIDEBAR (Left panel) ---
# The sidebar is an optional panel on the left side of most web apps
# We use "with st.sidebar:" to tell Streamlit to put everything inside in the sidebar
with st.sidebar:
    st.markdown("## 🌊 ADA")  # Main title for the app with an emoji
    st.caption("Acoustic Design Assistant • Prototype")  # Smaller subtitle explaining what it is
    st.markdown("---")  # This creates a horizontal line to separate sections
    st.markdown("**Project Phase:** Core Logic Sprints")  # Show what stage the project is in
    st.markdown("**Hot Reloading:** Active ⚡")  # Show that code changes update instantly
    
    # Store global materials state if we want to add presets later
    # This is a comment for future development
    st.markdown("---")  # Another divider line
    # This is an info box (💡 = light bulb) giving users helpful tips
    st.info("💡 Adjust the room dimensions in the main panel to see real-time updates across all tabs.")


# --- MAIN CONTENT AREA - HEADER & ROOM INPUTS ---
# Create banner with title on left and buttons on right inside the same banner
st.markdown("""
<div style="margin: -0.5rem -0.5rem 1rem -0.5rem; padding: 1rem 1.25rem; background-color: #0f172a; border-bottom: 1px solid rgba(96, 165, 250, 0.2); border-radius: 0 0 10px 10px;">
    <div style="display: flex; justify-content: space-between; align-items: center; gap: 2rem;">
        <div style="text-align: left;">
            <div style="font-size: 1.3rem; font-weight: 700; color: #f8fafc;">🎧 Acoustic Design Assistant</div>
            <div style="font-size: 0.95rem; color: #e2e8f0; margin-top: 0.2rem;">Room acoustics, modal behavior, and reverberation analysis.</div>
        </div>
        <div style="display: flex; gap: 0.5rem;" id="nav-buttons-container">
            <div data-nav-target="calculator-section" style="padding: 0.5rem 1rem; background: #60a5fa; color: white; border: 1px solid rgba(96, 165, 250, 0.5); border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; text-decoration: none; display: inline-block; transition: all 0.2s ease; user-select: none;">Calculator</div>
            <div data-nav-target="audio-explanation-section" style="padding: 0.5rem 1rem; background: #60a5fa; color: white; border: 1px solid rgba(96, 165, 250, 0.5); border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; text-decoration: none; display: inline-block; transition: all 0.2s ease; user-select: none;">Audio Explanation</div>
            <div data-nav-target="acoustic-insights-section" style="padding: 0.5rem 1rem; background: #60a5fa; color: white; border: 1px solid rgba(96, 165, 250, 0.5); border-radius: 6px; cursor: pointer; font-size: 0.9rem; font-weight: 500; text-decoration: none; display: inline-block; transition: all 0.2s ease; user-select: none;">Acoustic Insights</div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Find all nav buttons and add click handlers
    const navButtons = document.querySelectorAll('[data-nav-target]');
    navButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('data-nav-target');
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
</script>
""", unsafe_allow_html=True)

# Navigate to section if query param is set
if st.query_params.get("nav_to"):
    target_id = st.query_params.get("nav_to")
    # Use JavaScript with polling to wait for element and scroll to it correctly
    st.markdown(f"""
    <script>
        function findScrollContainerAndScroll(elem) {{
            if (!elem) return false;
            
            // Find scrollable container and calculate correct position
            let scrollContainer = null;
            let parent = elem;
            let topOffset = 0;
            
            while (parent) {{
                const styles = window.getComputedStyle(parent);
                const isScrollable = parent.scrollHeight > parent.clientHeight;
                
                // Accumulate offsets from all parents
                if (parent !== elem && parent !== window) {{
                    topOffset += parent.offsetTop || 0;
                }}
                
                // Find first scrollable container
                if (isScrollable && !scrollContainer) {{
                    scrollContainer = parent;
                }}
                
                parent = parent.parentElement;
            }}
            
            if (scrollContainer) {{
                // Calculate scroll position with 100px padding from top
                const targetScroll = Math.max(0, topOffset - 100);
                console.log('Scrolling to:', targetScroll, 'Current scroll:', scrollContainer.scrollTop);
                scrollContainer.scrollTop = targetScroll;
                return true;
            }}
            
            return false;
        }}
        
        function scrollToElement() {{
            const elem = document.getElementById('{target_id}');
            if (elem && findScrollContainerAndScroll(elem)) {{
                console.log('Successfully scrolled to {target_id}');
                return true;
            }}
            return false;
        }}
        
        // Poll for the element with increasing intervals
        let attempts = 0;
        const maxAttempts = 50;
        const pollIntervals = [100, 200, 300, 500, 500, 500, 1000, 1000];
        
        function pollForElement(attemptNum) {{
            if (scrollToElement()) {{
                console.log('Successfully scrolled after ' + attemptNum + ' attempts');
                // Clear the query param after scrolling completes
                setTimeout(() => {{
                    const url = new URL(window.location);
                    url.searchParams.delete('nav_to');
                    window.history.replaceState({{}}, '', url);
                    console.log('Cleared nav_to param');
                }}, 500);
                return;
            }}
            
            if (attemptNum < maxAttempts) {{
                const interval = pollIntervals[Math.min(attemptNum, pollIntervals.length - 1)];
                setTimeout(() => pollForElement(attemptNum + 1), interval);
                if (attemptNum % 10 === 0) {{
                    console.log('Polling attempt ' + attemptNum + ' for {target_id}');
                }}
            }} else {{
                console.log('Failed to find element {target_id} after ' + maxAttempts + ' attempts');
            }}
        }}
        
        // Start polling immediately
        pollForElement(0);
    </script>
    """, unsafe_allow_html=True)

# Handle navigation scrolling based on query params
# (Removed - using direct onclick handlers instead for better reliability)

# ============================================================================
# ONBOARDING & INTRODUCTION SECTION
# ============================================================================

# Add a little spacing below the nav bar
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Hero/Welcome section with modern styling
st.markdown("""
<div style='text-align: center; margin-bottom: 3rem;'>
    <h1 style='font-size: 3.5em; font-weight: 700; margin-bottom: 0.5rem; line-height: 1.2;'>
        Design rooms that <span style='color: #60a5fa;'>sound right.</span>
    </h1>
    <p style='font-size: 1.1em; color: #cbd5e1; margin-bottom: 0; line-height: 1.6; max-width: 700px; margin-left: auto; margin-right: auto;'>
        ADA bridges the gap between complex acoustic physics and accessible design. 
        Whether you are planning a control room or studying sound behavior, ADA gives 
        you the tools to make informed decisions.
    </p>
</div>

<div style='text-align: center; margin-bottom: 2.5rem;'>
    <h2 style='font-size: 1.8em; font-weight: 600; margin-bottom: 0.5rem;'>Four ways to explore acoustics</h2>
    <p style='color: #94a3b8; font-size: 1em;'>Everything you need to understand, measure, and design sound in a space</p>
</div>
""", unsafe_allow_html=True)

# Create 4 columns for feature cards
feature_col1, feature_col2, feature_col3, feature_col4 = st.columns(4, gap="medium")

with feature_col1:
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(96, 165, 250, 0.05)); 
                border: 1px solid rgba(96, 165, 250, 0.2); border-radius: 12px; padding: 1.5rem; height: 100%;'>
        <div style='font-size: 2.5em; margin-bottom: 1rem;'>📊</div>
        <h3 style='font-size: 1.2em; font-weight: 600; margin-bottom: 0.75rem; color: #e2e8f0;'>Calculators</h3>
        <p style='color: #cbd5e1; font-size: 0.95em; margin-bottom: 1.5rem; line-height: 1.5;'>
            Adjust room dimensions in real-time to analyze low-frequency modes, predict RT60 decay times, and map speaker boundary interference.
        </p>
        <a href='#room-geometry' style='color: #60a5fa; text-decoration: none; font-weight: 500; display: inline-flex; align-items: center; gap: 0.5rem;'>
            Explore calculators <span style='font-size: 1.2em;'>→</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

with feature_col2:
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(96, 165, 250, 0.05)); 
                border: 1px solid rgba(96, 165, 250, 0.2); border-radius: 12px; padding: 1.5rem; height: 100%;'>
        <div style='font-size: 2.5em; margin-bottom: 1rem;'>🔍</div>
        <h3 style='font-size: 1.2em; font-weight: 600; margin-bottom: 0.75rem; color: #e2e8f0;'>Analysis Tools</h3>
        <p style='color: #cbd5e1; font-size: 0.95em; margin-bottom: 1.5rem; line-height: 1.5;'>
            Dive deep into acoustic behavior. Visualize modal frequencies, SBIR effects, and room stability with interactive charts.
        </p>
        <a href='#room-geometry' style='color: #60a5fa; text-decoration: none; font-weight: 500; display: inline-flex; align-items: center; gap: 0.5rem;'>
            Explore analysis <span style='font-size: 1.2em;'>→</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

with feature_col3:
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(96, 165, 250, 0.05)); 
                border: 1px solid rgba(96, 165, 250, 0.2); border-radius: 12px; padding: 1.5rem; height: 100%;'>
        <div style='font-size: 2.5em; margin-bottom: 1rem;'>🎧</div>
        <h3 style='font-size: 1.2em; font-weight: 600; margin-bottom: 0.75rem; color: #e2e8f0;'>Audio Library</h3>
        <p style='color: #cbd5e1; font-size: 0.95em; margin-bottom: 1.5rem; line-height: 1.5;'>
            Listen and learn. Engage with our interactive carousel to hear podcast-style explanations of core acoustic concepts.
        </p>
        <a href='#audio-explanation-section' style='color: #60a5fa; text-decoration: none; font-weight: 500; display: inline-flex; align-items: center; gap: 0.5rem;'>
            Explore audio <span style='font-size: 1.2em;'>→</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

with feature_col4:
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(96, 165, 250, 0.05)); 
                border: 1px solid rgba(96, 165, 250, 0.2); border-radius: 12px; padding: 1.5rem; height: 100%;'>
        <div style='font-size: 2.5em; margin-bottom: 1rem;'>💡</div>
        <h3 style='font-size: 1.2em; font-weight: 600; margin-bottom: 0.75rem; color: #e2e8f0;'>Info Cards</h3>
        <p style='color: #cbd5e1; font-size: 0.95em; margin-bottom: 1.5rem; line-height: 1.5;'>
            Access acoustic insights covering industry standards, the Bolt Area stability zone, and material absorption guidelines.
        </p>
        <a href='#acoustic-insights-section' style='color: #60a5fa; text-decoration: none; font-weight: 500; display: inline-flex; align-items: center; gap: 0.5rem;'>
            Explore insights <span style='font-size: 1.2em;'>→</span>
        </a>
    </div>
    """, unsafe_allow_html=True)

# CTA buttons section
st.markdown("""
<div style='text-align: center; margin-top: 3rem; margin-bottom: 2rem;'>
    <p style='color: #94a3b8; font-size: 0.95em;'>Ready to get started?</p>
</div>
""", unsafe_allow_html=True)

cta_col1, cta_col2, cta_col3 = st.columns([1, 2, 1])
with cta_col2:
    st.markdown("""
    <div style='display: flex; gap: 1rem; justify-content: center;'>
        <a href='#room-geometry' style='
            display: inline-block;
            background: #60a5fa;
            color: #fff;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95em;
            transition: background 0.3s ease;
        '>Start designing</a>
        <a href='https://github.com' target='_blank' style='
            display: inline-block;
            background: transparent;
            color: #e2e8f0;
            padding: 0.75rem 1.5rem;
            border: 1px solid #475569;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.95em;
            transition: border 0.3s ease;
        '>View the documentation</a>
    </div>
    """, unsafe_allow_html=True)

# Add spacing before the Room Geometry section starts
st.markdown("<div style='height: 2rem;'></div>", unsafe_allow_html=True)

# Keep a breathable layout without making the section feel disconnected
# st.title() creates a big heading at the top of the page
st.title("Room Geometry")  # Title of this section
st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

# Create 5 columns with different widths to organize the layout nicely
# [2, 2, 2, 1, 1] means: first 3 columns are equal width, last 2 are half that width
col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 1, 1])

# --- INPUT CONTROLS: ROOM DIMENSIONS ---
# Sliders let users adjust values by dragging or typing
# st.slider(label, min, max, default, step_size)
with col1:
    # Slider for room LENGTH
    # Users can pick any value from 2.0 to 15.0 meters
    # Default value is 5.0, and smallest change is 0.1 meters
    L = st.slider("Length (m)", 2.0, 15.0, 5.0, 0.1)

with col2:
    # Slider for room WIDTH
    W = st.slider("Width (m)", 2.0, 15.0, 4.0, 0.1)

with col3:
    # Slider for room HEIGHT
    H = st.slider("Height (m)", 2.0, 8.0, 3.0, 0.1)

# --- CALCULATE ROOM PROPERTIES ---
# Now that we have L, W, H, we can calculate properties of the room

# Volume = length × width × height (basic geometry)
# Think of it like: how much air fits in this room?
volume = L * W * H

# Surface Area is the total area of all walls, floor, and ceiling
# Formula: 2 × (LW + LH + WH)
# - LW = floor and ceiling area (length × width) × 2 surfaces
# - LH = front and back walls (length × height) × 2 surfaces
# - WH = left and right walls (width × height) × 2 surfaces
# Then multiply by 2 to get both sides
surface_area = 2 * (L*W + L*H + W*H)

# --- DISPLAY ROOM METRICS ---
# Metrics are boxes that display important numbers
with col4:
    # Display the calculated volume
    st.metric("Volume", f"{volume:.1f} m³")  # .1f means show 1 decimal place

with col5:
    # Display the calculated surface area
    st.metric("Surface", f"{surface_area:.1f} m²")

# Keep a light amount of separation before the next section
st.markdown("<div style='height: 0.75rem;'></div>", unsafe_allow_html=True)

# Draw a horizontal dividing line
st.markdown("---")


# --- CREATE TABS ---
# Tabs are like pages within a page - clicking each tab shows different content
# st.tabs() creates the tab buttons at the top
tab_modes, tab_rt60, tab_sbir, tab_ai, tab_resources = st.tabs([
    "📊 Modal Analysis",  # Tab 1: Analyze room modes
    "⏱️ RT60 Calculator",  # Tab 2: Calculate how long sound lasts in the room
    "📡 SBIR Analysis",  # Tab 3: Analyze speaker-wall interference
    "🤖 Acoustics AI",  # Tab 4: AI chat assistant
    "📚 Resources"  # Tab 5: Acoustic learning resources
])

# ============================================================================
# TAB 1: MODAL ANALYSIS
# This tab shows low-frequency acoustic problems in the room
# ============================================================================
with tab_modes:
    # Tab heading
    st.markdown("### Low-Frequency Behavior (0-300Hz)")
    # Explain why we care about low frequencies:
    # Low frequencies (0-300 Hz) are most problematic in rooms because the wavelengths are large
    # This means standing waves and modes have strong effects
    
    # Create 2 columns to show charts side by side
    mc1, mc2 = st.columns(2)
    
    # ===== LEFT COLUMN: BOLT AREA DIAGRAM =====
    with mc1:
        st.markdown("**Bolt Area Stability Zone**")
        
        # Calculate this room's ratio and check if it's in the Bolt area
        x_ratio, y_ratio = get_room_ratios(L, W, H)
        status, delta_color = check_bolt_area(x_ratio, y_ratio)
        
        # Create an interactive chart using Plotly
        fig_bolt = go.Figure()  # Start a new figure (blank canvas for drawing)
        
        # Draw the BOLT AREA POLYGON (the green stable zone)
        # This creates a filled shape with specific corner points
        fig_bolt.add_trace(go.Scatter(
            x=[1.14, 1.28, 1.60, 1.50, 1.14],  # X coordinates of the polygon corners (closes at end)
            y=[1.39, 1.54, 1.28, 1.12, 1.39],  # Y coordinates of the polygon corners
            fill='toself',  # Fill the area inside the shape
            fillcolor='rgba(34, 197, 94, 0.2)',  # Light green fill color (semi-transparent)
            line=dict(color='#22c55e', width=2),  # Green border line
            name="Stable Zone",  # Name for the legend
            hoverinfo="skip"  # Don't show hover info when mouse is over the zone
        ))
        
        # Draw YOUR ROOM'S CURRENT POSITION (red dot)
        # This shows where your room's ratios fall on the graph
        fig_bolt.add_trace(go.Scatter(
            x=[x_ratio],  # X position of the point (width/height ratio)
            y=[y_ratio],  # Y position of the point (length/height ratio)
            mode='markers',  # Show as a point (not a line)
            marker=dict(
                color='#ef4444',  # Red color (stands out)
                size=12,  # Size of the dot
                line=dict(color='white', width=2)  # White outline around the dot
            ),
            name="Current Room"  # Name for the legend
        ))
        
        # Configure the chart appearance and axes
        fig_bolt.update_layout(
            template="plotly_dark",  # Use dark theme (matches our app's dark style)
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper background
            xaxis_title="Width / Height Ratio",  # Label for horizontal axis
            yaxis_title="Length / Height Ratio",  # Label for vertical axis
            xaxis=dict(range=[0.8, 2.0]),  # Show this range on X axis
            yaxis=dict(range=[0.8, 2.0]),  # Show this range on Y axis
            margin=dict(l=0, r=0, t=0, b=0),  # Minimize margins (use full space)
            height=350,  # Height of the chart in pixels
            legend=dict(font=dict(color='#d1d5db'))  # Light gray legend text
        )
        
        # Display the chart in the Streamlit app
        st.plotly_chart(fig_bolt, use_container_width=True)
        
        # Show status: is the room in the Bolt area or unstable?
        st.metric("Status", status, delta="Ratio Check", delta_color=delta_color)

    # ===== RIGHT COLUMN: MODAL FREQUENCIES CHART =====
    with mc2:
        st.markdown("**Axial Modal Frequencies**")
        
        # Calculate all the modal frequencies for this room
        df_modes = calculate_modes(L, W, H)
        
        # Create a new chart for modal frequencies
        fig_modes = go.Figure()  # Start new figure
        
        # Add bars for each axis (Length, Width, Height) with different colors
        # Each axis (L, W, H) creates its own set of mode frequencies
        for axis, color in zip(['Length', 'Width', 'Height'], ['#ef4444', '#22c55e', '#3b82f6']):
            # Filter data to get only modes from this axis
            axis_data = df_modes[df_modes['Axis'] == axis]
            
            # Add bars to the chart
            fig_modes.add_trace(go.Bar(
                x=axis_data['Freq'],  # X position = frequency
                y=[1]*len(axis_data),  # Y value = 1 for all (just showing presence)
                marker_color=color,  # Color specific to this axis
                name=axis,  # Name for legend (Length/Width/Height)
                width=3  # Width of each bar
            ))
        
        # Configure the chart
        fig_modes.update_layout(
            template="plotly_dark",  # Dark theme
            plot_bgcolor="rgba(0,0,0,0)",  # Transparent
            paper_bgcolor="rgba(0,0,0,0)",  # Transparent
            xaxis_title="Frequency (Hz)",  # X axis label
            yaxis=dict(showticklabels=False, range=[0, 1.1]),  # Hide Y axis labels
            margin=dict(l=0, r=0, t=0, b=0),  # No margins
            height=350,  # Chart height
            barmode='overlay',  # Stack bars on top of each other
            legend=dict(font=dict(color='#d1d5db'))  # Gray legend
        )
        
        st.markdown("<div id='calculator-section'></div>", unsafe_allow_html=True)

        # Display the modal analysis chart
        st.plotly_chart(fig_modes, use_container_width=True)
    
    first_mode = round(SPEED_OF_SOUND / (2 * L), 1)
    st.markdown("<div id='glass-box-section'></div>", unsafe_allow_html=True)
    render_glass_box(
        title="Rayleigh Equation (Axial Modes)",
        inputs={
            "Length (L)": f"{L:.2f} m",
            "Width (W)": f"{W:.2f} m",
            "Height (H)": f"{H:.2f} m",
            "Mode number": "1"
        },
        formula_latex=r"f = \frac{c}{2} \sqrt{\left(\frac{n_x}{L}\right)^2 + \left(\frac{n_y}{W}\right)^2 + \left(\frac{n_z}{H}\right)^2}",
        formula_elements={
            "f": "Frequency (Hz)",
            "c": "Speed of sound in air",
            "L, W, H": "Room dimensions",
            "n_x, n_y, n_z": "Mode numbers"
        },
        substitution=rf"f = \frac{{343}}{{2}} \sqrt{{\left(\frac{{1}}{{{L:.2f}}}\right)^2 + \left(\frac{{0}}{{{W:.2f}}}\right)^2 + \left(\frac{{0}}{{{H:.2f}}}\right)^2}}",
        calculation_steps=[
            f"Use the first axial mode along the room length: {first_mode:.1f} Hz",
            "Compare the result against the room's low-frequency behavior and potential resonance."
        ]
    )

    st.markdown("<div id='audio-explanation-section'></div>", unsafe_allow_html=True)
    render_audio_carousel()

    # Add two native informational cards beneath the Glass Box section
    st.markdown("<div id='acoustic-insights-section'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Modal Analysis Insights**")
            st.write("This panel highlights how room proportions influence resonant modes and low-frequency behavior.")
            st.caption("Read more...")

    with col2:
        with st.container(border=True):
            st.markdown("**Room Geometry Notes**")
            st.write("Adjust the dimensions to see how modal spacing shifts as the room becomes more or less proportionate.")
            st.caption("Read more...")


# ============================================================================
# TAB 2: RT60 CALCULATOR
# This tab calculates how long sound takes to fade away in the room
# ============================================================================
with tab_rt60:
    st.markdown("### Reverberation Time")
    # RT60 is how long it takes for sound to become 60 decibels quieter
    # (60 dB is considered "silent" - you can't hear it anymore)
    # Important: shorter RT = room absorbs sound well, longer RT = room is live/echoey
    
    # Create 3 columns for material selection
    rc1, rc2, rc3 = st.columns(3)
    
    # --- MATERIAL SELECTORS ---
    with rc1:
        # Dropdown menu to choose wall material
        # index=4 means "Drywall (Standard)" is selected by default
        mat_wall = st.selectbox("Walls", list(MATERIALS.keys()), index=4)
    
    with rc2:
        # Dropdown for floor material
        # index=3 means "Wood Floor (Reflective)" is selected by default
        mat_floor = st.selectbox("Floor", list(MATERIALS.keys()), index=3)
    
    with rc3:
        # Dropdown for ceiling material
        # index=4 means "Drywall (Standard)" is selected by default
        mat_ceil = st.selectbox("Ceiling", list(MATERIALS.keys()), index=4)
    
    # --- GET ABSORPTION COEFFICIENTS ---
    # Convert the selected materials into arrays of absorption values
    # Each material has 6 values (one for each frequency band)
    a_wall = np.array(MATERIALS[mat_wall])
    a_floor = np.array(MATERIALS[mat_floor])
    a_ceil = np.array(MATERIALS[mat_ceil])
    
    # --- CALCULATE SURFACE AREAS ---
    # We need the area of each surface to calculate total absorption
    area_walls = 2 * (L*H + W*H)  # All 4 walls (front, back, left, right)
    area_floor = L * W  # Bottom surface
    area_ceil = L * W  # Top surface
    
    # --- TARGET RT60 ---
    # Different rooms need different RT60 values for good acoustics
    # This uses a standard formula: RT60 = 0.25 × (V/100)^(1/3)
    # It's an approximation of good acoustic conditions
    target_rt = 0.25 * (volume/100)**(1/3)
    
    # --- CALCULATE RT60 FOR EACH FREQUENCY BAND ---
    # Create empty lists to store calculations for each frequency
    sabine_rt = []  # Using Sabine formula (common approximation)
    eyring_rt = []  # Using Eyring formula (more accurate for absorbent rooms)
    
    # Loop through each of the 6 frequency bands
    for i in range(6):
        # Calculate total absorption at this frequency
        # (absorption coefficient) × (surface area) for each surface, then add them up
        abs_total = (a_wall[i]*area_walls) + (a_floor[i]*area_floor) + (a_ceil[i]*area_ceil)
        
        # Calculate average absorption coefficient across all surfaces
        # This tells us what percentage of sound is absorbed on average
        alpha_avg = abs_total / surface_area
        
        # --- SABINE FORMULA ---
        # RT60 = (0.161 × Volume) / (Total Absorption)
        # 0.161 is a constant that converts units correctly
        # This is the most commonly used formula in practice
        sabine_rt.append((0.161 * volume) / abs_total)
        
        # --- EYRING FORMULA ---
        # RT60 = (0.161 × Volume) / (-Surface Area × ln(1 - alpha_avg))
        # This formula is more accurate when the room has a lot of absorption
        # ln() is the natural logarithm (math function)
        # We check that alpha_avg < 0.99 to avoid math errors
        e_rt = (0.161 * volume) / (-surface_area * np.log(1 - alpha_avg)) if alpha_avg < 0.99 else 0
        eyring_rt.append(e_rt)
    
    # --- CREATE VISUALIZATION CHART ---
    fig_rt = go.Figure()  # Create new figure
    
    # Add SABINE line (solid blue line)
    fig_rt.add_trace(go.Scatter(
        x=OCTAVE_BANDS,  # Frequency bands on X axis
        y=sabine_rt,  # Calculated RT60 values on Y axis
        mode='lines+markers',  # Show both lines and dots
        name='Sabine',  # Name for legend
        line=dict(color='#3b82f6', width=3)  # Blue solid line
    ))
    
    # Add EYRING line (dashed purple line)
    fig_rt.add_trace(go.Scatter(
        x=OCTAVE_BANDS,
        y=eyring_rt,
        mode='lines+markers',
        name='Eyring',
        line=dict(color='#8b5cf6', width=3, dash='dash')  # Purple dashed line
    ))
    
    # Add TARGET line (green line - ideal RT60)
    fig_rt.add_trace(go.Scatter(
        x=OCTAVE_BANDS,
        y=[target_rt]*6,  # Same value across all frequencies
        mode='lines',
        name='Target',  # The recommended RT60 for this room
        line=dict(color='#22c55e', width=2)  # Green
    ))
    
    # Configure the chart appearance
    fig_rt.update_layout(
        template="plotly_dark",  # Dark theme
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper
        yaxis_title="Time (Seconds)",  # Y axis shows time
        yaxis=dict(rangemode='tozero'),  # Start Y axis from 0
        margin=dict(l=0, r=0, t=30, b=0),  # Minimal margins
        height=350  # Chart height
    )
    
    # Display the RT60 chart
    st.plotly_chart(fig_rt, use_container_width=True)
    
    render_glass_box(
        title="Sabine Formula",
        inputs={
            "Volume (V)": f"{volume:.1f} m³",
            "Total absorption (A)": f"{surface_area:.1f} m²",
            "Room type": "Rectangular enclosure"
        },
        formula_latex=r"RT_{60} = \frac{0.161 \cdot V}{A}",
        formula_elements={
            "RT_{60}": "Reverberation time (seconds)",
            "V": "Room volume",
            "A": "Total absorption of the room",
            "0.161": "Empirical constant for metric units"
        },
        substitution=rf"RT_{{60}} = \frac{{0.161 \cdot {volume:.1f}}}{{{surface_area:.1f}}}",
        calculation_steps=[
            f"Use the room volume: {volume:.1f} m³",
            f"Use the total absorption area: {surface_area:.1f} m²",
            "Calculate the reverberation time from the simplified Sabine relation."
        ]
    )

    # Add two native informational cards beneath the Glass Box section
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**RT60 Insights**")
            st.write("This view summarizes how different surface materials affect the perceived liveliness of the room.")
            st.caption("Read more...")

    with col2:
        with st.container(border=True):
            st.markdown("**Absorption Guidance**")
            st.write("Use the material selectors to compare how reflective and absorptive finishes change reverberation.")
            st.caption("Read more...")


# ============================================================================
# TAB 3: SBIR ANALYSIS
# This tab analyzes Speaker-Boundary Interference Response (SBIR)
# ============================================================================
with tab_sbir:
    st.markdown("### Speaker-Boundary Interference Response")
    # SBIR happens when speaker sound bounces off nearby walls
    # Direct sound + reflected sound = cancellation (quiet) or reinforcement (loud)
    # This creates frequency-dependent problems in the bass range
    
    # Create 3 columns for speaker distance controls
    sc1, sc2, sc3 = st.columns(3)
    
    # --- SPEAKER DISTANCE SLIDERS ---
    with sc1:
        # How far the speaker is from the front wall (in meters)
        # Closer to wall = lower problem frequencies
        d_front = st.slider("Dist to Front Wall (m)", 0.1, 5.0, 1.0, 0.1)
    
    with sc2:
        # How far the speaker is from the side wall
        d_side = st.slider("Dist to Side Wall (m)", 0.1, 5.0, 0.8, 0.1)
    
    with sc3:
        # How far the speaker is from the floor
        d_floor = st.slider("Dist to Floor (m)", 0.1, 3.0, 1.2, 0.1)
    
    # --- CALCULATE PROBLEM FREQUENCIES ---
    # Using the quarter-wavelength formula: f = c / (4 * distance)
    # These are the frequencies most affected by SBIR
    
    # Problem frequency from front wall
    # If result would be division by zero, use 0 instead
    f_front = round(SPEED_OF_SOUND / (4 * d_front)) if d_front > 0 else 0
    
    # Problem frequency from side wall
    f_side = round(SPEED_OF_SOUND / (4 * d_side)) if d_side > 0 else 0
    
    # Problem frequency from floor
    f_floor = round(SPEED_OF_SOUND / (4 * d_floor)) if d_floor > 0 else 0
    
    # --- DISPLAY PROBLEM FREQUENCIES ---
    # Show each problem frequency in a nice box
    mc1, mc2, mc3 = st.columns(3)
    mc1.metric("Front Wall Dip", f"{f_front} Hz")  # Dip = frequency that gets quiet
    mc2.metric("Side Wall Dip", f"{f_side} Hz")
    mc3.metric("Floor Dip", f"{f_floor} Hz")
    
    # --- CALCULATE SBIR CURVE ---
    # This calculates the frequency response (amplitude vs frequency) with SBIR effects
    # Pass all three distances to the function
    freqs, resp = calculate_sbir_curve([d_front, d_side, d_floor])
    
    # --- CREATE VISUALIZATION ---
    fig_sbir = go.Figure()  # New figure
    
    # Add area fill chart showing the SBIR effect
    fig_sbir.add_trace(go.Scatter(
        x=freqs,  # Frequencies on X axis
        y=resp,  # Amplitude response on Y axis (in dB, negative = quieter)
        mode='lines',  # Connect points with lines
        fill='tozeroy',  # Fill area from line down to zero
        line=dict(color='#ef4444', width=3),  # Red line
        fillcolor='rgba(239, 68, 68, 0.2)'  # Semi-transparent red fill
    ))
    
    # Configure the chart appearance
    fig_sbir.update_layout(
        template="plotly_dark",  # Dark theme
        plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
        paper_bgcolor="rgba(0,0,0,0)",  # Transparent paper
        xaxis_title="Frequency (Hz)",  # X axis label
        yaxis_title="Amplitude (dB)",  # Y axis label (dB = decibels, measure of loudness)
        # Use logarithmic frequency scale (standard for audio) with specific tick values
        xaxis=dict(type='log', tickvals=[40, 60, 100, 200, 400, 800]),
        yaxis=dict(range=[-20, 2]),  # Y axis from -20 dB to +2 dB
        margin=dict(l=0, r=0, t=30, b=0),  # Minimal margins
        height=300  # Chart height
    )
    
    # Display the SBIR analysis chart
    st.plotly_chart(fig_sbir, use_container_width=True)
    
    render_glass_box(
        title="SBIR Cancellation Frequency",
        inputs={
            "Distance to front wall (d)": f"{d_front:.2f} m",
            "Speed of sound (c)": f"{SPEED_OF_SOUND:.0f} m/s"
        },
        formula_latex=r"f_c = \frac{c}{4d}",
        formula_elements={
            "f_c": "Cancellation center frequency",
            "c": "Speed of sound",
            "d": "Distance to the reflecting boundary",
            "4": "Quarter-wavelength scaling"
        },
        substitution=rf"f_c = \frac{{{SPEED_OF_SOUND:.0f}}}{{4 \cdot {d_front:.2f}}}",
        calculation_steps=[
            f"Use the measured distance to the boundary: {d_front:.2f} m",
            f"Apply the quarter-wavelength relationship to estimate the dip frequency: {f_front} Hz"
        ]
    )

    # Add two native informational cards beneath the Glass Box section
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**SBIR Insights**")
            st.write("The analysis highlights how nearby boundaries create cancellation dips in the bass response.")
            st.caption("Read more...")

    with col2:
        with st.container(border=True):
            st.markdown("**Boundary Notes**")
            st.write("Move the speaker closer to or farther from surfaces to see how the problem frequencies shift.")
            st.caption("Read more...")

# ============================================================================
# TAB 4: ACOUSTICS AI CHAT
# AI-powered assistant for acoustics questions and guidance
# ============================================================================
with tab_ai:
    st.markdown("### 🤖 Acoustics AI Assistant")
    st.markdown(
        "Ask questions about room acoustics, treatment, isolation, measurement, and live sound. "
        "Get instant guidance backed by acoustic principles."
    )
    
    # Initialize chat history in session state if it doesn't exist
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []
    
    # Suggested questions
    st.markdown("**Suggested Questions:**")
    
    suggestions = [
        "How do I calculate RT60 for a 60 m³ control room?",
        "Explain axial vs tangential room modes with an example.",
        "What's the difference between STC and IIC ratings?",
        "How thick should a porous absorber be to work at 100 Hz?"
    ]
    
    # Create 2x2 grid for suggestions
    cols = st.columns(2)
    for idx, suggestion in enumerate(suggestions):
        with cols[idx % 2]:
            if st.button(suggestion, key=f"suggestion_{idx}", use_container_width=True):
                st.session_state.ai_messages.append({"role": "user", "content": suggestion})
                st.rerun()
    
    # Display chat history
    st.markdown("---")
    st.markdown("**Conversation**")
    
    chat_container = st.container(height=400, border=True)
    
    with chat_container:
        for message in st.session_state.ai_messages:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**AI Assistant:** {message['content']}")
    
    # Chat input area
    st.markdown("---")
    
    col_input, col_send = st.columns([5, 1])
    
    with col_input:
        user_input = st.text_area(
            "Ask about acoustics...",
            placeholder="Ask about RT60, room modes, absorbers, measurement...",
            height=80,
            label_visibility="collapsed"
        )
    
    with col_send:
        st.write("")  # Spacing
        if st.button("Send", use_container_width=True, type="primary"):
            if user_input.strip():
                st.session_state.ai_messages.append({"role": "user", "content": user_input})
                
                # Simple AI response system
                response = generate_ai_response(user_input)
                st.session_state.ai_messages.append({"role": "assistant", "content": response})
                st.rerun()

# ============================================================================
# TAB 5: ACOUSTIC RESOURCES
# Learning hub with tutorials, guides, and reference materials
# ============================================================================
with tab_resources:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h2 style='font-size: 2em; font-weight: 700; color: #e2e8f0; margin-bottom: 0.5rem;'>📚 Acoustic Resources</h2>
        <p style='color: #cbd5e1; font-size: 1.05em; margin: 0;'>Learn acoustic principles, standards, and best practices</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create 3 resource categories
    res_col1, res_col2, res_col3 = st.columns(3, gap="medium")
    
    with res_col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05)); 
                    border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 12px; padding: 1.5rem; height: 100%;'>
            <div style='font-size: 2.5em; margin-bottom: 1rem;'>📖</div>
            <h3 style='font-size: 1.2em; font-weight: 600; margin-bottom: 0.75rem; color: #e2e8f0;'>Fundamentals</h3>
            <p style='color: #cbd5e1; font-size: 0.95em; margin-bottom: 1rem; line-height: 1.5;'>
                Master the core concepts of room acoustics, sound behavior, and acoustic measurements.
            </p>
            <ul style='color: #cbd5e1; font-size: 0.9em; margin: 0; padding-left: 1.2rem;'>
                <li>Sound waves & propagation</li>
                <li>Room modes & standing waves</li>
                <li>Reverberation basics</li>
                <li>Frequency response</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with res_col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(168, 85, 247, 0.1), rgba(168, 85, 247, 0.05)); 
                    border: 1px solid rgba(168, 85, 247, 0.2); border-radius: 12px; padding: 1.5rem; height: 100%;'>
            <div style='font-size: 2.5em; margin-bottom: 1rem;'>🛠️</div>
            <h3 style='font-size: 1.2em; font-weight: 600; margin-bottom: 0.75rem; color: #e2e8f0;'>Design & Treatment</h3>
            <p style='color: #cbd5e1; font-size: 0.95em; margin-bottom: 1rem; line-height: 1.5;'>
                Practical guides for designing acoustically optimized spaces and treating acoustic problems.
            </p>
            <ul style='color: #cbd5e1; font-size: 0.9em; margin: 0; padding-left: 1.2rem;'>
                <li>Absorption materials</li>
                <li>Bass traps & diffusion</li>
                <li>Room layout strategies</li>
                <li>Isolation techniques</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with res_col3:
        st.markdown("""
        <div style='background: linear-gradient(135deg, rgba(34, 197, 94, 0.1), rgba(34, 197, 94, 0.05)); 
                    border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 12px; padding: 1.5rem; height: 100%;'>
            <div style='font-size: 2.5em; margin-bottom: 1rem;'>⚙️</div>
            <h3 style='font-size: 1.2em; font-weight: 600; margin-bottom: 0.75rem; color: #e2e8f0;'>Standards & Reference</h3>
            <p style='color: #cbd5e1; font-size: 0.95em; margin-bottom: 1rem; line-height: 1.5;'>
                Industry standards, measurement protocols, and technical reference materials.
            </p>
            <ul style='color: #cbd5e1; font-size: 0.9em; margin: 0; padding-left: 1.2rem;'>
                <li>STC & IIC ratings</li>
                <li>Measurement standards</li>
                <li>Building codes</li>
                <li>ISO specifications</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 1.5rem;'></div>", unsafe_allow_html=True)
    
    # Key concepts section
    st.markdown("### Key Acoustic Concepts")
    
    concepts_col1, concepts_col2 = st.columns(2)
    
    with concepts_col1:
        with st.expander("🎵 **RT60 (Reverberation Time)**", expanded=False):
            st.markdown("""
            **RT60** is the time it takes for sound to decay by 60 decibels in a room.
            
            - **Formula**: RT60 = 0.161 × V / (α × S)
            - **V**: Room volume (m³)
            - **α**: Average absorption coefficient (0-1)
            - **S**: Total surface area (m²)
            
            **Typical values:**
            - Living room: 0.4-0.8 seconds
            - Recording studio: 0.1-0.3 seconds
            - Concert hall: 1.5-2.0 seconds
            """)
        
        with st.expander("📈 **Room Modes**", expanded=False):
            st.markdown("""
            **Room modes** are standing wave patterns at frequencies determined by room dimensions.
            
            - **Axial modes**: Between 2 parallel walls (strongest)
            - **Tangential modes**: Between 4 surfaces (moderate)
            - **Oblique modes**: Between 6 surfaces (weakest)
            
            **Problem frequency**: f = c / (2 × distance)
            - **c**: Speed of sound (343 m/s at 20°C)
            - **distance**: Distance between parallel surfaces
            """)
    
    with concepts_col2:
        with st.expander("🛡️ **Sound Isolation (STC)**", expanded=False):
            st.markdown("""
            **Sound Transmission Class (STC)** measures how much sound a barrier blocks.
            
            - **STC 30-35**: Poor (normal voices audible)
            - **STC 40-45**: Fair (loud voices faintly audible)
            - **STC 50-60**: Good (loud music barely audible)
            - **STC 70+**: Excellent (almost no sound transmission)
            
            **Techniques for improvement:**
            - Increase mass (thicker walls)
            - Decouple structures (floating floors)
            - Seal air leaks (acoustic caulk)
            - Use absorption (reduce flanking)
            """)
        
        with st.expander("🎯 **SBIR (Speaker-Boundary Interference)**", expanded=False):
            st.markdown("""
            **SBIR** occurs when direct speaker sound combines with wall reflections.
            
            **Problem frequency**: f ≈ 343 Hz·m / (4 × distance)
            
            **Example**: Speaker 1m from wall
            - f ≈ 343 / (4 × 1) = 86 Hz (cancellation dip)
            
            **Solutions:**
            - Move speaker farther from walls
            - Treat reflective surfaces (absorption/diffusion)
            - Use acoustic room correction
            - Strategic furniture placement
            """)
    
    st.markdown("---")
    
    # Quick reference section
    st.markdown("### Quick Reference: Speed of Sound")
    st.markdown("""
    | Medium | Temperature | Speed |
    |--------|-------------|-------|
    | Air | 0°C | 331 m/s |
    | Air | 20°C | 343 m/s |
    | Air | 25°C | 346 m/s |
    | Water | 20°C | 1,480 m/s |
    | Steel | 20°C | 5,000 m/s |
    """)
    
    st.markdown("---")
    
    # Tips section
    st.markdown("### Pro Tips for Acoustic Design")
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.info("""
        **🎵 For Recording Studios:**
        - Target RT60: 0.1-0.3 seconds
        - Use bass traps in corners (8-12 inches thick)
        - Place absorption at first reflection points
        - Avoid parallel walls (use splayed walls or diffusion)
        """)
    
    with tips_col2:
        st.success("""
        **🎶 For Listening Rooms:**
        - Target RT60: 0.3-0.6 seconds
        - Balance absorption and diffusion
        - Place monitor speakers ±30° from listening position
        - Maintain 38% absorption to avoid over-damping
        """)