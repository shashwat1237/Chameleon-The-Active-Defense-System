# Dockerfile - corrected to use tini as PID 1 and to run start.sh
FROM python:3.11-slim

# install tini for proper signal handling and graphviz system packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    tini \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# create app user for safety
RUN useradd --create-home appuser
WORKDIR /app

# copy project files
COPY . /app

# install python deps
RUN pip install --no-cache-dir -r requirements.txt

# ensure start.sh is executable
RUN chmod +x /app/start.sh

# use tini as PID 1 so signals are forwarded to children
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/app/start.sh"]
