FROM ubuntu:22.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -y update && apt-get -y install \
    make gcc apache2 \
    python3-pip \
    ruby ruby-dev

WORKDIR /code

COPY requirements.txt Gemfile ./
RUN pip install -r requirements.txt
RUN gem install bundler && bundler install

COPY apache/apache2.conf /etc/apache2/sites-enabled/000-default.httpd.conf

COPY scripts/* /usr/local/bin/
COPY local_settings.default entrypoint.sh setup.py ./
COPY static_aid ./static_aid
COPY site ./site

RUN python3 setup.py install

EXPOSE 4000

CMD ["pytest"]
