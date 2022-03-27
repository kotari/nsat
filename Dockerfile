FROM ubuntu:latest

RUN apt-get update -y && \
    apt-get install -y python3-pip python-dev \
    && cd /usr/local/bin \
    && ln -s /usr/bin/python3 python \
    && pip3 --no-cache-dir install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY ./src/app.py /app/src/app.py

# ENTRYPOINT [ "python",  "src/app.py"]
CMD gunicorn --chdir ./src --certfile=/certs/servercrt.pem --keyfile=/certs/serverkey.pem --bind 0.0.0.0:5000 app:app
