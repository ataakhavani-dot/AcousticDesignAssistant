# ---- Build stage ----
FROM python:3.11-slim AS build

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage ----
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from build stage
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application source. Every module web_application.py imports must be
# listed here, plus static/ for the room simulator's JS and CSS assets.
COPY acoustic_ai.py acoustic_ai_chat.py audio_library.py digital_lab.py \
     experiment_simulator.py room_simulator.py web_application.py ./
COPY static/ ./static/

# Cloud Run injects PORT env var; default to 8080
ENV PORT=8080

EXPOSE 8080

# Run Streamlit on the Cloud Run port
CMD streamlit run web_application.py \
    --server.port=${PORT} \
    --server.headless=true \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
