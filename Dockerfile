FROM docker.io/python:3.11-slim

# Install system dependencies for textract (.doc, .ppt parsing)
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    antiword \
    unrtf \
    poppler-utils \
    pstotext \
    tesseract-ocr \
    flac \
    ffmpeg \
    lame \
    libmad0 \
    libsox-fmt-mp3 \
    sox \
    libjpeg-dev \
    swig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/ /app
RUN pip3 install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/docs
COPY docs /app/docs

CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]