#!/bin/sh

INTERVAL="4"
NPU_BASE_PATH="/tmp/accel" # /sys/class/accel

if [ ! -d "$NPU_BASE_PATH" ] || ! ls $NPU_BASE_PATH/accel* >/dev/null 2>&1; then
    printf "[{\"accel_id\":\"none\",\"npu_util\":0.00,\"status\":\"not_found\"}]\n"
    exit 0
fi

PREV_DATA=$(for dev in $NPU_BASE_PATH/accel*; do
    ID=$(basename "$dev")
    BUSY=$(cat "$dev/npu_busy_time_us" 2>/dev/null || echo 0)
    TIME=$(date +%s.%N 2>/dev/null)
    printf "%s %s %s\n" "$ID" "$TIME" "$BUSY"
done)

sleep "$INTERVAL"

printf "["
FIRST=true

echo "$PREV_DATA" | while read -r P_ID P_TIME P_BUSY; do
    [ -z "$P_ID" ] && continue

    C_BUSY=$(cat "$NPU_BASE_PATH/$P_ID/npu_busy_time_us" 2>/dev/null || echo 0)
    C_TIME=$(date +%s.%N 2>/dev/null)
    
    UTIL="0.00"
    
    if [ "$C_BUSY" -gt "$P_BUSY" ] 2>/dev/null; then
        UTIL=$(awk -v cb="$C_BUSY" -v pb="$P_BUSY" -v ct="$C_TIME" -v pt="$P_TIME" \
            'BEGIN { printf "%.2f", ((cb - pb) / 1000000) / (ct - pt) * 100 }' 2>/dev/null)
    fi

    case $UTIL in
        .*) UTIL="0$UTIL" ;;
        "") UTIL="0.00" ;;
    esac

    if [ "$FIRST" = "true" ]; then
        FIRST=false
    else
        printf ","
    fi

    printf "{\"accel_id\":\"%s\",\"npu_util\":%s}" "$P_ID" "$UTIL"
done

printf "]\n"