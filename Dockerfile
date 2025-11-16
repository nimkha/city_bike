FROM python:3.13

# Install CA certificates (needed for HTTPS outbound calls)
RUN apt update && apt install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create a non‑root user
ARG UID=1000
ARG GID=1000
RUN groupadd -g ${GID} appgroup && \
    useradd -u ${UID} -g ${GID} -m appuser

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ ./app/

# Switch to non‑root user
USER appuser

# Expose the port the service listens on
EXPOSE 5000

# Run Gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:5000", "app:create_app()"]