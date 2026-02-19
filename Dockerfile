FROM python:3.12-alpine

ENV PYTHONUNBUFFERED=1
ENV APPLICATION_NAME=virtualvault

RUN apk add --no-cache \
    make \
    gcc \
    musl-dev \
    linux-headers \
    build-base \
    apache2 \
    python3 \
    python3-dev \
    ruby \
    ruby-dev \
    nodejs \
    npm \
    sassc

WORKDIR /code

COPY requirements.txt Gemfile ./
RUN pip install -r requirements.txt
RUN gem install bundler && bundle install
RUN npm install lunr

RUN find /etc/apache2/conf.d/ -type f -name "*.conf" -print0 | xargs -0 -I {} mv {} {}.disabled
COPY ./apache/${APPLICATION_NAME}.conf /etc/apache2/conf.d/${APPLICATION_NAME}.conf

COPY crontab /etc/crontabs/root

COPY scripts/* /usr/local/bin/
COPY entrypoint.sh setup.py ./
COPY static_aid ./static_aid
COPY site ./site

RUN pip install setuptools
RUN python3 setup.py install

EXPOSE 4000

CMD ["pytest"]
