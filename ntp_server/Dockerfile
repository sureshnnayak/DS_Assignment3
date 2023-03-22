FROM python:3.9

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

RUN pip3 install --upgrade pip

COPY . /usr/src/app

EXPOSE 1234

ENTRYPOINT ["python3"]

CMD ["-u", "ntp_server.py"]