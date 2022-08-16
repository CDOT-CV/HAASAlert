FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY gunicorn.sh .
COPY . .
EXPOSE 8080
ENTRYPOINT [ "sh", "./gunicorn.sh" ]