FROM python:3.13-alpine
WORKDIR /app
RUN addgroup -S app && adduser -S -G app app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt tzdata
COPY app.py start.py ./
COPY templates/ ./templates/
RUN mkdir -p /data /backups
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
EXPOSE 8888
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD wget -qO- http://127.0.0.1:8888/health || exit 1
# Docker socket access is intentionally required. QNAP socket group IDs vary,
# therefore the manager runs as root inside this tightly scoped container.
CMD ["python", "start.py"]
