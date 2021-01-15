FROM python:3-alpine
COPY app /app
COPY config /config
CMD ["python", "/app/garage_server.py"]

