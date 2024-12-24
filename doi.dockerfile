FROM python:3.13

ENV LANG=C.UTF-8

RUN apt-get update -qq && \
    apt-get install -y build-essential git python3-pip

WORKDIR /app

RUN git clone https://github.com/eawag-rdm/datacite-export.git
RUN pip install -r datacite-export/requirements.txt