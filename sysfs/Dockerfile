FROM python:3.12-slim-trixie

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    libgl1 \
    pciutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./app /app

ADD https://astral.sh/uv/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

RUN uv sync --locked

EXPOSE 12345

CMD ["uv", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "12345"]
