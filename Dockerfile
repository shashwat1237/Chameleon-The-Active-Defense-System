FROM python:3.9-slim

WORKDIR /app

# [VERIFIED] Installs system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    tini \
    graphviz \
    procps \
    sed \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# [VERIFIED] Installs Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create a non-root user and group
# [FIX] We explicitly set the home directory to /app so Streamlit has a place to write
RUN addgroup --system --gid 1000 appgroup && \
    adduser --system --uid 1000 --gid 1000 --home /app appuser

COPY . .

# [FIX] Clean up Streamlit Logs
# 1. Point the HOME variable to /app (where we have write permissions)
ENV HOME=/app
# 2. Disable telemetry to stop it from trying to write the 'machine_id' file
ENV STREAMLIT_GATHER_USAGE_STATS=false
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_SERVER_ENABLE_GATHER_USAGE_STATS=false

# Fix line endings for shell execution
RUN sed -i 's/\r$//' /app/start.sh

# Ensure script is executable and owned by the non-root user
RUN chmod +x /app/start.sh && \
    chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

ENV PORT=8501

# Final, simplified execution command structure
CMD ["/bin/sh", "-c", "/app/start.sh"]