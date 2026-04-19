import time

import psutil

from utils.logger import log
from .xpu_interface import XpuInterface


class CpuMetrics(XpuInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def monitor_utilization(self):
        while self.keep_running:
            time.sleep(self.interval)
            self.get_usage()


    def get_usage(self):
        utilization = psutil.cpu_percent(interval=None)
        self.utilization_data["cpu"].append(utilization)
        log.info(f"CPU Utilization: {utilization:.2f}%")

    # def get_cpu_count(self):
    #     return psutil.cpu_count(logical=True)

    # def get_cpu_freq(self):
    #     freq = psutil.cpu_freq()
    #     return {
    #         'current': freq.current,
    #         'min': freq.min,
    #         'max': freq.max
    #     }

    # def get_cpu_stats(self):
    #     stats = psutil.cpu_stats()
    #     return {
    #         'ctx_switches': stats.ctx_switches,
    #         'interrupts': stats.interrupts,
    #         'soft_interrupts': stats.soft_interrupts,
    #         'syscalls': stats.syscalls
    #     }

    # def get_cpu_times(self):
    #     times = psutil.cpu_times()
    #     return {
    #         'user': times.user,
    #         'system': times.system,
    #         'idle': times.idle,
    #         'iowait': getattr(times, 'iowait', 0.0),
    #         'irq': getattr(times, 'irq', 0.0),
    #         'softirq': getattr(times, 'softirq', 0.0),
    #         'steal': getattr(times, 'steal', 0.0),
    #         'guest': getattr(times, 'guest', 0.0),
    #         'guest_nice': getattr(times, 'guest_nice', 0.0)
    #     }
