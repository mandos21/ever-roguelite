FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN apt-get update && apt-get install -y openssl && rm -rf /var/lib/apt/lists/*

RUN export SECRET_KEY=$(openssl rand -base64 32) && echo $SECRET_KEY > /app/secret_key.txt

COPY . /app

EXPOSE 8000

RUN export MONGODB_URI="mongodb://${MONGODB_HOST}:${MONGODB_PORT}/${MONGODB_DB_NAME}" && echo $MONGODB_URI > /app/mongodb_uri.txt

CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
