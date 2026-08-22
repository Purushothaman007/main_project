FROM python:3.11-slim

# Create a non-root user for security
RUN groupadd -r sandbox && useradd -r -g sandbox -u 1000 sandbox

# Set working directory
WORKDIR /app

# Change ownership to sandbox user
RUN chown -R sandbox:sandbox /app

# Switch to non-root user
USER sandbox

CMD ["python3"]
