FROM python:3.10.13-slim-bookworm
LABEL authors="fabianhintringer"

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

WORKDIR /app
RUN mkdir /database
COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
