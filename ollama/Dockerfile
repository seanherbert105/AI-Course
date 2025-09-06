FROM docker.io/ubuntu:latest

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install -y \
        ca-certificates \
        curl \
        wget \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV OLLAMA_HOST=0.0.0.0:11434

COPY --chmod=755 entrypoint.sh /

EXPOSE 11434

ENTRYPOINT ["/entrypoint.sh"]