FROM python:3.9-slim-buster
WORKDIR /app

RUN pip install flask gunicorn requests dateformat

COPY app.py app.py
COPY templates/index.html templates/index.html

ENV PORT=5000

CMD gunicorn -b :$PORT app:app
