#!/bin/sh
set -e
# 볼륨 마운트 시 vendor/bundle이 비어있을 수 있으므로 매번 bundle install
bundle config set --local path 'vendor/bundle'
bundle install
exec "$@"
