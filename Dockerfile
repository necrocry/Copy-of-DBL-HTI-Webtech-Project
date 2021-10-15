FROM python:3.8-buster
WORKDIR /code
ENV FLASK_APP flaskr
ENV FLASK_ENV development
ENV FLASK_RUN_HOST 0.0.0.0
RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run"]
