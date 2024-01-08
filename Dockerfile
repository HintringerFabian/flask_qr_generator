FROM python:3.10.13-slim-bookworm
LABEL authors="fabianhintringer"

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 5000

CMD ["python3", "app.py"]
