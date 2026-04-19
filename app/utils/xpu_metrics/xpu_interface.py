import threading
from collections import defaultdict


class XpuInterface:
    def __init__(self, interval=1, db_store=False):
        self.interval = interval
        self.db_store = db_store
        self.utilization_data = defaultdict(list)
        self.keep_running = False
        self.thread = None


    def monitor_utilization(self):
        pass


    def start(self):
        self.keep_running = True
        self.thread = threading.Thread(target=self.monitor_utilization)
        self.thread.start()


    def stop(self):
        self.keep_running = False
        if self.thread:
            self.thread.join()
        return self.utilization_data
