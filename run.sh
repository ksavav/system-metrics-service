#!/bin/bash
source .env

sed -i -r "/scrape_interval/ s/([0-9]+)/$INTERVAL/" ./configs/prometheus.yml
sed -i -r "/interval/ s/([0-9]+)/$INTERVAL/" ./configs/telegraf.conf


if ls /dev/nvidiactl >/dev/null 2>&1; then
    docker compose -f docker-compose.yml -f docker-compose.nvidia.yaml up -d
else
    docker compose -f docker-compose.yml up -d
fi
