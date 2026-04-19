import time
from pathlib import Path

from utils.logger import log

from .xpu_interface import XpuInterface


class NpuMetrics(XpuInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.npu_path = self._find_npu_path()
        if self.npu_path is None:
            log.error("No NPU busy time file found. NPU monitoring will be disabled.")
        else:
            log.info(f"Found NPU busy time file at: {self.npu_path}")
            self.prev_busy_us = self._read_busy_time()
            self.prev_time = time.time()


    def monitor_utilization(self):
        while self.keep_running:
            time.sleep(self.interval)
            self.get_usage()


    def get_usage(self):
        current_busy_us = self._read_busy_time()
        current_time = time.time()

        if current_busy_us is not None and self.prev_busy_us is not None:
            delta_busy_us = current_busy_us - self.prev_busy_us
            delta_time_s = current_time - self.prev_time

            utilization = ((delta_busy_us / 1_000_000) / delta_time_s) * 100.0

            utilization = max(0.0, min(100.0, utilization))

            self.utilization_data["npu"].append(utilization)
            log.info(f"NPU Utilization: {utilization:.2f}%")

        self.prev_busy_us = current_busy_us
        self.prev_time = current_time


    def _read_busy_time(self):
        try:
            with Path.open(self.npu_path, 'r') as f:
                return int(f.read().strip())
        except PermissionError as e:
            log.error(f"Permission denied when reading NPU file {self.npu_path}: {e}")
            return None
        except FileNotFoundError as e:
            log.error(f"NPU file not found {self.npu_path}: {e}")
            return None


    def _find_npu_path(self):
        paths = Path.glob("/sys/class/accel/accel*/device/npu_busy_time_us") + \
                Path.glob("/sys/class/accel/accel*/npu_busy_time_us")
        if paths:
            return Path(paths[0])
        return None
