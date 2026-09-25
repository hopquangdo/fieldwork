# Backend photo-sort (graphrun HTTP API) — code chỉ còn .pyc, rules nhúng trong bytecode.
#   docker compose up -d --build        (xem docker-compose.yml)
FROM python:3.12-slim AS build
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /bin/uv
WORKDIR /src
COPY pyproject.toml uv.lock ./
COPY src ./src
COPY rules ./rules
COPY scripts/build_dist.py ./scripts/
RUN uv venv /opt/venv \
 && uv export --frozen --no-dev --no-hashes --no-emit-project -o req.txt \
 && uv pip install --python /opt/venv/bin/python --no-deps -r req.txt \
 && uv pip install --python /opt/venv/bin/python --no-deps . \
 && /opt/venv/bin/python scripts/build_dist.py --harden /opt/venv/lib/python3.12/site-packages

FROM python:3.12-slim
COPY --from=build /opt/venv /opt/venv
ENV PATH=/opt/venv/bin:$PATH PYTHONUTF8=1 PYTHONUNBUFFERED=1
WORKDIR /work
EXPOSE 8765
CMD ["python", "-m", "interfaces.cli.commands", "serve", "--host", "0.0.0.0", "--port", "8765"]
