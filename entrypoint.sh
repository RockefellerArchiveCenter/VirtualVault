#!/bin/sh

set -e

static-aid-update
crond -b
httpd -D FOREGROUND
