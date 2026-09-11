ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /build
COPY . .

RUN pip install --upgrade pip setuptools wheel && pip install build && python -m build --wheel

FROM python:${PYTHON_VERSION}-slim AS runtime

LABEL org.opencontainers.image.title="CauterRule" \
      org.opencontainers.image.description="Self-improving rule engine for AI agents" \
      org.opencontainers.image.source="https://github.com/deghosal-2026/CauterRule" \
      org.opencontainers.image.licenses="MIT"

# git needed for store/git.py promotion (commit/rollback) — #524
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /build/dist/*.whl /app/
RUN pip install --upgrade pip && pip install /app/*.whl && rm /app/*.whl

# Non-root runtime user — #524
RUN useradd --create-home --uid 1000 cauterule \
    && chown -R cauterule:cauterule /app
USER cauterule

ENV PYTHONUNBUFFERED=1

# Portable healthcheck (no procps needed) — #524/#607
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD cauterule --help > /dev/null 2>&1 || exit 1

ENTRYPOINT ["cauterule"]
CMD ["--help"]
