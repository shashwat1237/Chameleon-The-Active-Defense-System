# Dockerfile - Container definition for running the full Chameleon defense stack
FROM python:3.11-slim

# Install essential system utilities:
# - tini handles clean process signals inside containers
# - graphviz supports the topology visualization in the dashboard
# - procps provides tools like pkill used by shutdown routines
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    graphviz \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create an isolated non-root user to run the application securely
RUN useradd --create-home appuser
WORKDIR /app

# Bring all project files into the container
COPY . /app

# Install Python dependencies without caching to keep the image lightweight
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the startup script can be executed inside the container
RUN chmod +x /app/start.sh

# Tini becomes PID 1 to ensure proper signal handling and graceful shutdown
ENTRYPOINT ["/usr/bin/tini", "--"]

# Launch the full defense system through the orchestrator script
CMD ["/app/start.sh"]
