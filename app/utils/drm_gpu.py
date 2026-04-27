import time
import subprocess
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field

@dataclass
class Pid:
    pid: str
    fd: str
    render: str

    def __post_init__(self):
        self.fd = self.fd.rstrip('u')
        self.render = self.render.split('/')[-1]


@dataclass
class Engine:
    engine_name: str
    curr_metric: list[str] = field(default_factory=list)
    prev_metric: list[str] = field(default_factory=list)


@dataclass
class Gpu:
    card: str
    render: str
    driver: str
    engines: list[Engine] = field(default_factory=list)


GPUS_LIST = defaultdict(str)
INTERVAL = 5

def map_render_to_card():
    drm_path = Path("/sys/class/drm")
    gpu_groups = defaultdict(list)

    if not drm_path.exists():
        return

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
            GPUS_LIST[render] = Gpu(
                card=card,
                render=render,
                driver=get_gpu_driver(card)
            )

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

def get_drm_data(pid: Pid) -> list[Engine]:
    target_gpu = GPUS_LIST[pid.render]

    with Path.open(f"/proc/{pid.pid}/fdinfo/{pid.fd}") as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith("drm-"):
            name, value, *_ = line.strip().split()
            if target_gpu.engines is not None:
                engine = next((e for e in target_gpu.engines if e.engine_name == name), None)
                if engine is not None:
                    engine.curr_metric.append(value)
                else:
                    new_engine = Engine(engine_name=name, curr_metric=[value])
                    target_gpu.engines.append(new_engine)

def calculate_gpu_metrics():
    # Logic to calculate usage and memory (cycles and ns)
    pass

def monitor_gpu_metrics():
    pids = get_gpu_pids()
    for pid in pids:
        get_drm_data(pid)

    while True:
        time.sleep(INTERVAL)
        for engine in GPUS_LIST["renderD128"]:
            engine.prev_metric = engine.curr_metric
            engine.curr_metric = list()

        pids = get_gpu_pids()
        for pid in pids:
            get_drm_data(pid)

        calculate_gpu_metrics()


# ns
# drm-engine-
# (engine time now - engine time then) / (global time now - global time then) * 100

# cycles
# drm-total-cycles-
# drm-cycles-
# (active cycles now - active cycles then) / (total cycles now - total cycles then) * 100
