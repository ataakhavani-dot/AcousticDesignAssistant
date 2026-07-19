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
    /* Keep the inputs and expandable explanation sections dark even if Streamlit uses a light theme */
    div[data-testid="stCodeBlock"] {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stCodeBlock"] pre,
    div[data-testid="stCodeBlock"] code {
        background-color: transparent !important;
        color: #e2e8f0 !important;
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
# SECTION 4: REUSABLE GLASS BOX CALCULATION CARD
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
    Render a Netflix-style audio carousel that plays concept clips when clicked.
    """
    html_code = """
    <!DOCTYPE html>
    <html>
    <head>
    <style>
    body {
        background-color: #0e1117;
        margin: 0;
        font-family: sans-serif;
    }
    .carousel-wrapper {
        margin: 1rem 0 0.5rem 0;
    }
    .carousel-title {
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1.35rem;
        padding-top: 0.25rem;
        letter-spacing: 0.01em;
    }
    .carousel-container {
        display: flex;
        overflow-x: auto;
        scroll-behavior: smooth;
        gap: 16px;
        padding: 0 4px 12px 4px;
    }
    .carousel-container::-webkit-scrollbar {
        height: 8px;
    }
    .carousel-container::-webkit-scrollbar-track {
        background: #1e1e1e;
        border-radius: 4px;
    }
    .carousel-container::-webkit-scrollbar-thumb {
        background: #555;
        border-radius: 4px;
    }
    .carousel-card {
        position: relative;
        flex: 0 0 auto;
        width: 150px;
        height: 220px;
        border-radius: 8px;
        background-color: #333;
        overflow: hidden;
        transition: transform 0.3s ease;
        cursor: pointer;
    }
    .carousel-card:hover {
        transform: scale(1.03);
    }
    .carousel-image {
        width: 100%;
        height: 100%;
        object-fit: cover;
        border-radius: 8px;
        opacity: 0.8;
        box-shadow: 2px 4px 10px rgba(0,0,0,0.5);
    }
    .carousel-card:hover .carousel-image {
        opacity: 1;
    }
    .carousel-number {
        position: absolute;
        bottom: -12px;
        left: -14px;
        font-size: 78px;
        font-weight: 900;
        line-height: 1;
        font-family: 'Arial Black', Impact, sans-serif;
        color: #0e1117;
        -webkit-text-stroke: 2px white;
        text-shadow: 2px 4px 6px rgba(0,0,0,0.6);
        z-index: 10;
        pointer-events: none;
    }
    .card-title-overlay {
        position: absolute;
        top: 10px;
        left: 10px;
        right: 10px;
        color: white;
        font-weight: bold;
        font-size: 13px;
        text-shadow: 1px 1px 3px black;
        pointer-events: none;
    }
    .play-icon {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 34px;
        color: white;
        opacity: 0;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }
    .carousel-card:hover .play-icon {
        opacity: 1;
    }
    .audio-player-container {
        margin-top: 12px;
        padding: 12px;
        background-color: #1e1e1e;
        border-radius: 8px;
        text-align: center;
    }
    .now-playing-text {
        color: #4CAF50;
        font-size: 13px;
        margin-bottom: 8px;
        font-weight: bold;
        display: none;
    }
    audio {
        width: 100%;
        height: 40px;
        outline: none;
    }
    </style>
    </head>
    <body>
    <div class="carousel-wrapper">
        <div class="carousel-title">Audio Explanation</div>
        <div class="carousel-container">
            <div class="carousel-card" onclick="playAudio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', 'Understanding Room Modes')">
                <img class="carousel-image" src="https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?w=500&q=80" />
                <div class="card-title-overlay">Room Modes</div>
                <div class="play-icon">▶</div>
                <div class="carousel-number">1</div>
            </div>
            <div class="carousel-card" onclick="playAudio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3', 'Reverberation Time (RT60)')">
                <img class="carousel-image" src="https://images.unsplash.com/photo-1601058268499-e52658b8bb88?w=500&q=80" />
                <div class="card-title-overlay">RT60 Limits</div>
                <div class="play-icon">▶</div>
                <div class="carousel-number">2</div>
            </div>
            <div class="carousel-card" onclick="playAudio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3', 'Speaker Boundary Interference Response (SBIR)')">
                <img class="carousel-image" src="https://images.unsplash.com/photo-1516280440502-a2798e404b90?w=500&q=80" />
                <div class="card-title-overlay">SBIR Effects</div>
                <div class="play-icon">▶</div>
                <div class="carousel-number">3</div>
            </div>
            <div class="carousel-card" onclick="playAudio('https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3', 'The Bolt Area Explained')">
                <img class="carousel-image" src="https://images.unsplash.com/photo-1520523839897-bd0b52f945a0?w=500&q=80" />
                <div class="card-title-overlay">Bolt Area</div>
                <div class="play-icon">▶</div>
                <div class="carousel-number">4</div>
            </div>
        </div>
    </div>
    <div class="audio-player-container">
        <div id="now-playing" class="now-playing-text">Select a topic to start listening</div>
        <audio id="main-audio-player" controls>
            <source id="audio-source" src="" type="audio/mpeg">
            Your browser does not support the audio element.
        </audio>
    </div>
    <script>
        function playAudio(audioUrl, topicTitle) {
            var player = document.getElementById('main-audio-player');
            var source = document.getElementById('audio-source');
            var textDisplay = document.getElementById('now-playing');
            source.src = audioUrl;
            textDisplay.style.display = 'block';
            textDisplay.innerHTML = 'Now Playing: ' + topicTitle;
            player.load();
            player.play();
        }
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=450)


# ============================================================================
# SECTION 5: PHYSICS ENGINE FUNCTIONS
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
# SECTION 5: APP LAYOUT & USER INTERFACE
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
# Replace the old info callout with a compact top banner
st.markdown("""
<div style="margin: -0.5rem -0.5rem 1rem -0.5rem; padding: 1rem 1.25rem; background: linear-gradient(90deg, #06090f 0%, #111827 100%); border-bottom: 1px solid rgba(255,255,255,0.12); border-radius: 0 0 10px 10px; box-shadow: 0 4px 16px rgba(0,0,0,0.25);">
    <div style="display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;">
        <div style="text-align: left;">
            <div style="font-size: 1.3rem; font-weight: 700; color: #f8fafc;">🎧 Acoustic Design Assistant</div>
            <div style="font-size: 0.95rem; color: #cbd5e1; margin-top: 0.2rem;">Room acoustics, modal behavior, and reverberation analysis.</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Create navigation buttons using st.button with query params
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    if st.button("Calculator", key="nav_calc", use_container_width=True):
        st.query_params["nav_to"] = "calculator-section"
with col_btn2:
    if st.button("Glass Box", key="nav_glass", use_container_width=True):
        st.query_params["nav_to"] = "glass-box-section"
with col_btn3:
    if st.button("Audio Explanation", key="nav_audio", use_container_width=True):
        st.query_params["nav_to"] = "audio-explanation-section"
with col_btn4:
    if st.button("Acoustic Insights", key="nav_insights", use_container_width=True):
        st.query_params["nav_to"] = "acoustic-insights-section"

# Navigate to section if query param is set
if st.query_params.get("nav_to"):
    target_id = st.query_params.get("nav_to")
    # Use JavaScript with multiple attempts to scroll to the target element
    st.markdown(f"""
    <script>
        function scrollToElement() {{
            const elem = document.getElementById('{target_id}');
            if (elem) {{
                // Found it - scroll with multiple attempts to ensure it works
                for (let i = 0; i < 3; i++) {{
                    setTimeout(() => {{
                        elem.scrollIntoView({{behavior: 'smooth', block: 'start'}});
                    }}, i * 200);
                }}
            }}
        }}
        // Try to scroll at different times to catch when page is ready
        setTimeout(scrollToElement, 500);
        setTimeout(scrollToElement, 1000);
        setTimeout(scrollToElement, 1500);
        
        // Also try when page finishes loading
        if (document.readyState === 'loading') {{
            document.addEventListener('DOMContentLoaded', scrollToElement);
        }}
    </script>
    """, unsafe_allow_html=True)

# Handle navigation scrolling based on query params
# (Removed - using direct onclick handlers instead for better reliability)

st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)

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
tab_modes, tab_rt60, tab_sbir = st.tabs([
    "📊 Modal Analysis",  # Tab 1: Analyze room modes
    "⏱️ RT60 Calculator",  # Tab 2: Calculate how long sound lasts in the room
    "📡 SBIR Analysis"  # Tab 3: Analyze speaker-wall interference
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