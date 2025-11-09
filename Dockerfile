# syntax=docker/dockerfile:1

# ---------- Build stage ----------
    FROM python:3.12-slim AS builder
    WORKDIR /app
    
    # avoid caching pip downloads across builds when requirements haven't changed
    COPY requirements.txt .
    
    # Install build dependencies, pip wheel cache
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        && rm -rf /var/lib/apt/lists/*
    
    # Install dependencies into a wheelhouse to copy to final image
    RUN python -m pip install --upgrade pip setuptools wheel
    RUN pip wheel --wheel-dir=/wheels -r requirements.txt
    
    # ---------- Final stage ----------
    FROM python:3.12-slim
    ENV PYTHONDONTWRITEBYTECODE=1
    ENV PYTHONUNBUFFERED=1
    
    # Create non-root user
    RUN useradd --create-home appuser
    WORKDIR /home/appuser/app
    
    # Copy wheels and install
    COPY --from=builder /wheels /wheels
    COPY requirements.txt .
    RUN pip install --no-index --find-links=/wheels -r requirements.txt \
        && rm -rf /wheels
    
    # Copy app code
    COPY --chown=appuser:appuser . .
    
    # Expose Streamlit port
    EXPOSE 8501
    
    # Streamlit configuration (optional: suppress telemetry)
    ENV STREAMLIT_SERVER_RUN_ON_SAVE=false
    ENV STREAMLIT_SERVER_HEADLESS=true
    ENV STREAMLIT_SERVER_PORT=8501
    ENV STREAMLIT_SERVER_ENABLE_CORS=false
    
    # Don't store API keys in image — instruct to provide at runtime
    # Example: docker run -e GROQ_API_KEY="${GROQ_API_KEY}" <image>
    
    USER appuser
    
    # Default command
    CMD ["streamlit", "run", "streamlit.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
    