FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir tensorflow opencv-python-headless numpy flask gunicorn

EXPOSE 8080

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]