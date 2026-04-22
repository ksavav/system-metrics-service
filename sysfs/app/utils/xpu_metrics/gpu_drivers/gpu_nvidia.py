import pynvml

from utils.logger import log
from utils.xpu_metrics.xpu_interface import XpuInterface


class GpuNvidia(XpuInterface):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            pynvml.nvmlInit()
        except pynvml.NVMLError as e:
            log.error(f"Use docker-compose with NVIDIA runtime to enable GPU monitoring: {e}")


    def __del__(self):
        pynvml.nvmlShutdown()


    def _get_gpu_usage(self):
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)

            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            utilization = util.gpu
            log.info(f"GPU Utilization: {utilization:.2f}%")
            return utilization
        return None
