#!/bin/sh

mkdir -p /tmp/accel/accel0/
mkdir -p /tmp/accel/accel1/

touch /tmp/accel/accel0/npu_busy_time_us
touch /tmp/accel/accel1/npu_busy_time_us

while true; do
  VAL0=$(cat /tmp/accel/accel0/npu_busy_time_us)
  VAL1=$(cat /tmp/accel/accel1/npu_busy_time_us)

  echo "$((VAL0 + $(shuf -i 100000-700000 -n 1)))" > /tmp/accel/accel0/npu_busy_time_us
  echo "$((VAL1 + $(shuf -i 100000-700000 -n 1)))" > /tmp/accel/accel1/npu_busy_time_us

  sleep 1
done
