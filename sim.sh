#!/bin/sh

while true; do
  VAL0=$(cat /tmp/accel/accel0/npu_busy_time_us)
  VAL1=$(cat /tmp/accel/accel1/npu_busy_time_us)

  echo "$((VAL0 + 350000))" > /tmp/accel/accel0/npu_busy_time_us
  echo "$((VAL1 + 550000))" > /tmp/accel/accel1/npu_busy_time_us

  sleep 1
done
