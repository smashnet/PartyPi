FROM python:3
MAINTAINER Nicolas Inden <nicolas@inden.one>

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

VOLUME ["/usr/src/app/data"]

EXPOSE 8080

ENTRYPOINT [ "python", "./partypi.py" ]
