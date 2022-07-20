FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN export GOOGLE_APPLICATION_CREDENTIALS="/usr/src/app/haas_websocket/gcp_credentials.json"
# CMD [ "python", "-m", "haas_websocket.main" ]
ENTRYPOINT ["tail", "-f", "/dev/null"]