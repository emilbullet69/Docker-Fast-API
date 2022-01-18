# syntax=docker/dockerfile:1
FROM python:3.8-buster
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8090"]