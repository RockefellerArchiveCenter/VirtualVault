#!/bin/sh

set -e

static-aid-build
crond -b
httpd -D FOREGROUND
