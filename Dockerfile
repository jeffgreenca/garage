FROM python:3-alpine
RUN echo 'nameserver 8.8.8.8' > /etc/resolv.conf && pip3 install requests
COPY app /app
COPY ui /ui
COPY config /config
CMD ["python", "/app/garage_server.py"]

