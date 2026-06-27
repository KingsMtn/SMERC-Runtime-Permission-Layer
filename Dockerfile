FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SMERC_AUDIT_DB=/data/smerc_audit.sqlite3

WORKDIR /app

RUN addgroup --system smerc && adduser --system --ingroup smerc smerc \
    && mkdir -p /data && chown smerc:smerc /data

COPY --chown=smerc:smerc . /app

USER smerc

EXPOSE 8788
VOLUME ["/data"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8788/health', timeout=2)"

CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8788"]
