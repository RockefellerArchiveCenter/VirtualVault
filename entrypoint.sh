#!/bin/bash

set -e

static-aid-build
apachectl -D FOREGROUND
