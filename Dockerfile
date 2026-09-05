FROM python:3.12-slim AS builder

WORKDIR /build
COPY . .

RUN pip install --upgrade pip setuptools wheel && pip install build && python -m build --wheel

FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /build/dist/*.whl /app/
RUN pip install /app/*.whl && rm /app/*.whl

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["cauterule"]
CMD ["--help"]