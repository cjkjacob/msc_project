# backend Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY ./proof_of_effort /app
COPY ./requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN mkdir -p /app/static /app/media

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
