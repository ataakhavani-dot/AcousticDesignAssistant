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

# Copy application source
COPY acoustic_ai.py acoustic_ai_chat.py web_application.py ./

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
