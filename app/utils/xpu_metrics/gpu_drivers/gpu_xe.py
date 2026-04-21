import os
from collections import defaultdict
from pathlib import Path

from utils.logger import log
from utils.xpu_metrics.xpu_interface import XpuInterface


class GpuXe(XpuInterface):
    def __init__(self):
        self.clients = {}


    def _get_gpu_usage(self):
        pids = self._get_pids()
        if pids is None:
            log.warning("Could not access /proc to get GPU usage")
            return
        for pid in pids:
            self._get_pid_usage(pid)


    def _get_pid_usage(self, pid):
        fd_dir = Path(f"{pid}/fd")
        fdinfo_dir = Path(f"{pid}/fdinfo")

        if not fd_dir.exists():
            print(pid)
            return {}, {}
        try:
            for fd in fd_dir.iterdir():
                try:
                    target = str(Path(fd_dir / fd).readlink())
                    if target.startswith("/dev/dri/"):
                        with Path.open(fdinfo_dir / fd) as f:
                            lines = f.readlines()

                        client_id = f"{pid}_{fd}"
                        for line in lines:
                            if line.startswith("drm-client-id:"):
                                client_id = line.split(":")[1].strip()
                                break

                        if client_id not in self.clients:
                            self.clients[client_id] = {
                                'engines': defaultdict(int),
                                'memory': defaultdict(int)
                            }

                        for line in lines:
                            if line.startswith("drm-engine-"):
                                parts = line.split(":")
                                engine_name = parts[0].replace("drm-engine-", "").strip()
                                if len(parts) == 2 and "ns" in parts[1]:
                                    val = int(parts[1].strip().split()[0])
                                    self.clients[client_id]['engines'][engine_name] = \
                                        max(self.clients[client_id]['engines'][engine_name], val)

                            elif line.startswith("drm-memory-"):
                                parts = line.split(":")
                                mem_type = parts[0].replace("drm-memory-", "").strip()
                                if len(parts) == 2 and "KiB" in parts[1]:
                                    val = int(parts[1].strip().split()[0])
                                    self.clients[client_id]['memory'][mem_type] = \
                                        max(self.clients[client_id]['memory'][mem_type], val)

                except (FileNotFoundError, OSError, ValueError) as e:
                    print(f"Error occurred while processing PID {pid} FD {fd}: {e}")
                    pass
        except PermissionError:
            pass

        total_engines_ns = defaultdict(int)
        total_memory_kib = defaultdict(int)

        for client in self.clients.values():
            for eng, val in client['engines'].items():
                total_engines_ns[eng] += val
            for mem, val in client['memory'].items():
                total_memory_kib[mem] += val

        return total_engines_ns, total_memory_kib


    def _get_pids(self):
        try:
            pids = [pid for pid in Path('/proc').iterdir() if pid.is_dir() and pid.name.isdigit()]
            return pids
        except FileNotFoundError:
            return None
