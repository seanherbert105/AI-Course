FROM docker.io/python:3.11

# Set working directory
WORKDIR /app

# Prevent Python from writing pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Copy application files
COPY server.py /app/
COPY requirements.txt /app/

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Expose MCP stdio port if needed (optional)
# EXPOSE 8000

# Set default command
CMD [ "python3", "server.py" ]