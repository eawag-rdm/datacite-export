FROM ruby:3.1.6

ENV LANG=C.UTF-8 \
    BUNDLER_VERSION=2.5.6 \
    BOLOGNESE_VERSION=2.3.2

RUN apt-get update -qq && \
    apt-get install -y build-essential git && \
    gem install bundler -v "$BUNDLER_VERSION"

WORKDIR /app

RUN git clone https://github.com/datacite/bolognese.git
RUN git -C bolognese checkout "$BOLOGNESE_VERSION"
RUN cd bolognese && bundle install

RUN gem install bolognese

ENTRYPOINT ["bolognese"]