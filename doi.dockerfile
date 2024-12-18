FROM python:3.1.3

ENV LANG=C.UTF-8

RUN apt-get update -qq && \
    apt-get install -y build-essential git python3-pip &&

WORKDIR /app

RUN git clone https://github.com/eawag-rdm/exdc.git
RUN python3 -m module pip install -r exdc/requirements.txt