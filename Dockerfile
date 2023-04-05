FROM python:3.8

ENV PYTHONUNBUFFERED 1
ENV DOCKER true

RUN mkdir /app
WORKDIR /app
Add . /app

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8888
CMD [ "./wait-for-it.sh", "postgres:5432", "--", "python", "app.py" ]