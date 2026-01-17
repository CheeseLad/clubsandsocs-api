FROM python:3.13.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y python3-icu

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 4000

CMD [ "granian", "--interface", "asgi", "api.app:app", "--loop", "uvloop", "--host", "0.0.0.0", "--port", "4000" ]
