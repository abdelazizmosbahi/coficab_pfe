# ========================================
# Cable Manufacturing AI - Dockerfile
# Production-ready with Microsoft ODBC Driver 18
# ========================================

FROM python:3.11-slim

WORKDIR /app

# ========================================
# Step 1: Install system dependencies
# ========================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# ========================================
# Step 2: Install Microsoft ODBC Driver 18
# ========================================
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
    > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

# ========================================
# Step 3: Install Python dependencies
# ========================================
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ========================================
# Step 4: Copy application code
# ========================================
COPY . .

# ========================================
# Step 5: Health check
# ========================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import sqlalchemy; print('OK')" || exit 1

# ========================================
# Step 6: Expose and run
# ========================================
EXPOSE 8501
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
