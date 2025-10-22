#!/bin/bash

set -e

static-aid-build
service cron start
apachectl -D FOREGROUND
