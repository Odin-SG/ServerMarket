#!/usr/bin/env sh
flask run --host=0.0.0.0 &

trap "kill %1; exit 0" TERM INT

while true; do
  flask generate-reports
  sleep 20
done
