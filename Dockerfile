FROM python:3.12.6-slim

WORKDIR /app

RUN apt-get update && apt-get install -y python3-icu

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE $PORT

CMD python -m uvicorn api.app:app --host=0.0.0.0 --port=${PORT} --no-access-log
