FROM docker.io/python:3.11

# Install deps for fpdf + requests (lightweight, no heavy C libs needed)
RUN apt-get update && apt-get install -y \
        build-essential \
        curl \
        libpulse-dev \
        swig \
        wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app
COPY --chmod=755 scripts/entrypoint.sh /app

CMD [ "/app/entrypoint.sh" ]