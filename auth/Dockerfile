FROM python:3.10-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential default-libmysqlclient-dev \
  && pip install --no-cache-dir --upgrade pip

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]