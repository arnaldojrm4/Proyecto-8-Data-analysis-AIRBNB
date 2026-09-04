FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

WORKDIR /workspace

RUN pip install --no-cache-dir uv==0.12.1

COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

COPY config ./config
COPY notebooks ./notebooks
COPY tests ./tests

ENTRYPOINT ["uv", "run", "--locked", "airbnb-supply"]
CMD ["--help"]
