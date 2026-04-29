import subprocess
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Pid:
    pid: str
    fd: str
    render: str

    def __post_init__(self):
        self.fd = self.fd.rstrip('u')
        self.render = self.render.split('/')[-1]


@dataclass
class Client:
    client_id: str
    curr_metrics: dict[str] = field(default_factory=dict)
    prev_metrics: dict[str] = field(default_factory=dict)


@dataclass
class Gpu:
    card: str
    render: str
    driver: str
    clients: dict[Client] = field(default_factory=dict)


def map_render_to_card():
    drm_path = Path("/sys/class/drm")
    gpus_list = defaultdict(str)
    gpu_groups = defaultdict(list)

    if not drm_path.exists():
        return None

    for node in drm_path.iterdir():
        if node.name.startswith(('card', 'renderD')):
            try:
                device_id = (node / "device").resolve().name
                gpu_groups[device_id].append(node.name)
            except (FileNotFoundError, OSError):
                continue

    for _, nodes in gpu_groups.items():
        card = next((n for n in nodes if n.startswith('card')), None)
        render = next((n for n in nodes if n.startswith('render')), None)

        if card is not None and render is not None:
            gpus_list[render] = Gpu(
                card=card,
                render=render,
                driver=get_gpu_driver(card)
            )
    return gpus_list


def get_gpu_driver(card: str) -> str:
    return Path(f"/sys/class/drm/{card}/device/driver").readlink().name


def get_gpu_pids() -> list[Pid]:
    output = subprocess.run(
        "sudo lsof /dev/dri/render* | awk -F' ' '{print $2,$4,$9}'",
        text=True,
        capture_output=True,
        shell=True
    )
    pids_list = output.stdout.strip().split('\n')[1:]

    return [
        Pid(*row.split()) for row in pids_list if row.split()[1].rstrip('u').isdigit()
    ]


def get_drm_data(pid: Pid, gpus_list: dict) -> dict[str]:
    target_gpu = gpus_list[pid.render]
    drm_data = defaultdict(str)
    client_id = None

    with Path.open(f"/proc/{pid.pid}/fdinfo/{pid.fd}") as f:
        lines = f.readlines()

    for line in lines:
        name, value, *_ = line.strip().split()
        name = name.rstrip(':')

        if name == "drm-client-id":
            client_id = value
            continue

        if value.isdigit():
            drm_data[name] = value

    client = next((client for id, client in target_gpu.clients.items() if id == client_id), None)

    if client is not None:
        client.curr_metrics = drm_data
    else:
        client = Client(
            client_id=client_id,
            curr_metrics=drm_data,
            prev_metrics=None
        )

    gpus_list[pid.render].clients[client_id] = client

    return gpus_list


def shift_data(gpus_list: dict) -> dict:
    for render, drm_data in gpus_list.items():
        if not drm_data:
            continue

        for client_id, data in drm_data.clients.items():
            data.prev_metrics = data.curr_metrics
            data.curr_metrics = defaultdict(str)
            gpus_list[render].clients[client_id] = data

    return gpus_list


def calculate_gpu_metrics(gpus_list: dict, interval: int) -> dict[str]:
    interval_ns = interval * 1_000_000_000
    result_metrics = defaultdict(str)

    for render, gpu_data in gpus_list.items():
        result_metrics[render] = defaultdict(str)
        result_metrics[render]["total-gpu-util"] = 0
        result_metrics[render]["total-memory-util"] = 0
        result_metrics[render]["total-vram-util"] = 0

        for _, client in gpu_data.clients.items():
            curr = client.curr_metrics
            prev = client.prev_metrics

            if not prev:
                continue

            for key, curr_val in curr.items():
                if "vram" in key:
                    vram_util = result_metrics[render].get(key, 0) + int(curr_val)
                    result_metrics[render][key] = vram_util
                    result_metrics[render]["total-vram-util"] += vram_util

                elif "memory" in key:
                    memory_util = result_metrics[render].get(key, 0) + int(curr_val)
                    result_metrics[render][key] = memory_util
                    result_metrics[render]["total-memory-util"] += memory_util

                elif "drm-cycles" in key:
                    if key in prev:
                        engine = key.split("-")[-1]
                        curr_total_cycles = next(
                            c for k, c in curr.items() if "total" in k and engine in k
                        )
                        prev_total_cycles = next(
                            c for k, c in prev.items() if "total" in k and engine in k
                        )
                        engine_usage_percent = ((int(curr_val) - int(prev[key])) / \
                            (int(curr_total_cycles) - int(prev_total_cycles))) * 100
                        result_metrics[render][key] = result_metrics[render].get(key, 0) + \
                            float(engine_usage_percent)
                        result_metrics[render]["total-gpu-util"] += engine_usage_percent

                elif "drm-engine" in key:
                    if key in prev:
                        engine_usage_percent = ((int(curr_val) - int(prev[key])) / interval_ns) \
                            * 100
                        result_metrics[render][key] = result_metrics[render].get(key, 0) + \
                            float(engine_usage_percent)
                        result_metrics[render]["total-gpu-util"] += float(engine_usage_percent)

    return result_metrics


def monitor_gpu_metrics(gpus_list: dict, interval: int):
    shift_data(gpus_list)

    pids = get_gpu_pids()

    for pid in pids:
        gpus_list = get_drm_data(pid, gpus_list)


    calculated_metrics = calculate_gpu_metrics(gpus_list, interval)

    return gpus_list, calculated_metrics


gpus_list = map_render_to_card()
gpus_list, _ = monitor_gpu_metrics(gpus_list, 1)

time.sleep(2)

gpus_list, data = monitor_gpu_metrics(gpus_list, 1)
print(data)
