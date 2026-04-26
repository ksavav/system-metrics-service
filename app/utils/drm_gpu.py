from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass
class Pid:
    pid: str
    fd: str

    def __post_init__(self):
        self.fd = self.fd.rstrip('u')    

def get_gpu_pids() -> list[Pid]:
    output = subprocess.run(
        "sudo lsof /dev/dri/* | awk -F' ' '{print $2,$4}'",
        text=True,
        capture_output=True,
        shell=True
    )
    pids_list = output.stdout.strip().split('\n')[1:]

    return [Pid(*row.split()) for row in pids_list]

def get_drm_data(pid: Pid):
    with Path.open(f"/proc/{pid.pid}/fdinfo/{pid.fd}") as f:
        lines = f.readlines()
    
    for line in lines:
        if line.startswith("drm-"):
            print(line)


pids = get_gpu_pids()
for pid in pids:
    get_drm_data(pid)
