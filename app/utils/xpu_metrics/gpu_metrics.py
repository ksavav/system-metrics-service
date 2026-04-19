import time
from collections import defaultdict
from pathlib import Path

from utils.logger import log
from .xpu_interface import XpuInterface
from .gpu_drivers.gpu_nvidia import GpuNvidia
from .gpu_drivers.gpu_xe import GpuXe
from .gpu_drivers.gpu_i915 import Gpui915


class GpuMetrics(XpuInterface):
    DRIVER_CLASS_MAP = {
        "nvidia": GpuNvidia,
        "xe": GpuXe,
        "i915": Gpui915,
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = self._get_gpu_driver()
        log.info(f"Detected GPU drivers: {self.driver}")
        self._driver_instances = {}


    def monitor_utilization(self):
        while self.keep_running:
            time.sleep(self.interval)
            self.get_usage()


    def get_usage(self):
        for card, driver in self.driver.items():
            driver_class = self.DRIVER_CLASS_MAP.get(driver)
            if driver_class:
                if driver not in self._driver_instances:
                    self._driver_instances[driver] = driver_class()
                instance = self._driver_instances[driver]
                self.utilization_data["gpu"].append(instance._get_gpu_usage())
            else:
                log.warning(f"Unsupported GPU driver '{driver}' for card '{card}'. Skipping utilization collection.")


    def _get_gpu_usage(self):
        pass


    def _get_gpu_driver(self):
        drivers = defaultdict()
        cards = [card.name for card in Path.iterdir(Path('/dev/dri')) if "card" in str(card)]
        for card in cards:
            driver_path = Path(f'/sys/class/drm/{str(card)}/device/driver')
            if driver_path.is_symlink():
                drivers[card] = driver_path.readlink().name
        return drivers
