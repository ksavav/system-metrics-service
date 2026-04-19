from fastapi import FastAPI
from utils.config import get_config
from utils.xpu_metrics.cpu_metrics import CpuMetrics
from utils.xpu_metrics.gpu_metrics import GpuMetrics
from utils.xpu_metrics.npu_metrics import NpuMetrics


app = FastAPI()

ENABLE_CPU = get_config("ENABLE_CPU_METRICS", "true").lower() == "true"
ENABLE_GPU = get_config("ENABLE_GPU_METRICS", "false").lower() == "true"
ENABLE_NPU = get_config("ENABLE_NPU_METRICS", "false").lower() == "true"

cpu_metrics = CpuMetrics() if ENABLE_CPU else None
gpu_metrics = GpuMetrics() if ENABLE_GPU else None
npu_metrics = NpuMetrics() if ENABLE_NPU else None


@app.get("/usage/cpu")
def get_cpu_usage():
    if not cpu_metrics:
        return {"error": "CPU metrics not enabled"}
    cpu_metrics.get_usage()
    return {"cpu": cpu_metrics.utilization_data["cpu"][-1]}


@app.get("/usage/gpu")
def get_gpu_usage():
    if not gpu_metrics:
        return {"error": "GPU metrics not enabled"}
    gpu_metrics.get_usage()
    return {"gpu": gpu_metrics.utilization_data["gpu"][-1]}


@app.get("/usage/npu")
def get_npu_usage():
    if not npu_metrics:
        return {"error": "NPU metrics not enabled"}
    npu_metrics.get_usage()
    return {"npu": npu_metrics.utilization_data["npu"][-1]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=12345, reload=True)
