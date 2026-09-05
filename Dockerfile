ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim AS builder

WORKDIR /build
COPY . .

RUN pip install --upgrade pip setuptools wheel && pip install build && python -m build --wheel

FROM python:${PYTHON_VERSION}-slim AS runtime

WORKDIR /app

COPY --from=builder /build/dist/*.whl /app/
RUN pip install /app/*.whl && rm /app/*.whl

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["cauterule"]
CMD ["--help"]