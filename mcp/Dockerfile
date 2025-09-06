FROM docker.io/python:3.11

# Prevent Python from writing pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 
ENV PYTHONUNBUFFERED=1

# Copy application files
COPY server.py /
COPY requirements.txt /

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Set default command
CMD [ "python3", "server.py" ]