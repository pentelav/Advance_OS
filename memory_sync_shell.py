import time
import threading
import heapq
from collections import deque, OrderedDict, defaultdict

# ================== Memory Management =====================
# Class to represent a memory page allocated to a process
class Page:
    def __init__(self, pid, page_id):
        self.pid = pid
        self.page_id = page_id
        self.timestamp = time.time()
        
# Handles paging and page replacement algorithms for FIFO and LRU
class MemoryManager:
    def __init__(self, total_frames):
        self.total_frames = total_frames
        self.frames = deque()
        self.lru_map = OrderedDict()
        self.page_faults = 0
        self.per_process_memory = defaultdict(list)

# FIFO Page Loading
    def load_page_fifo(self, page: Page):
        if len(self.frames) >= self.total_frames:
            evicted = self.frames.popleft()
            self.per_process_memory[evicted.pid].remove(evicted.page_id)
            print(f"[FIFO] Evicted page {evicted.page_id} of process {evicted.pid}")
        self.frames.append(page)
        self.per_process_memory[page.pid].append(page.page_id)
        self.page_faults += 1
        print(f"[FIFO] Loaded page {page.page_id} for process {page.pid}")

# LRU Page Loading
    def load_page_lru(self, page: Page):
        key = (page.pid, page.page_id)
        if key in self.lru_map:
            self.lru_map.move_to_end(key)
        else:
            if len(self.lru_map) >= self.total_frames:
                evicted = self.lru_map.popitem(last=False)
                self.per_process_memory[evicted[0][0]].remove(evicted[0][1])
                print(f"[LRU] Evicted page {evicted[0][1]} of process {evicted[0][0]}")
            self.lru_map[key] = page
            self.per_process_memory[page.pid].append(page.page_id)
            self.page_faults += 1
            print(f"[LRU] Loaded page {page.page_id} for process {page.pid}")

# Gives total page faults that occurred
    def get_page_faults(self):
        return self.page_faults

# Displays the current memory usage of each process
    def print_memory_usage(self):
        print("\n=== Memory Usage Per Process ===")
        for pid, pages in self.per_process_memory.items():
            print(f"Process {pid}: Pages in memory -> {pages}")

# ==================== Synchronization =====================
# A shared mutex lock that simulates shared resource with synchronized access
shared_resource_lock = threading.Lock()

# ================ Simulated Process Class =================
# Represents processes that have memory and CPU requirements
class SimulatedProcess:
    def __init__(self, pid, name, burst_time, priority=0, memory_manager=None, paging_mode="LRU"):
        self.pid = pid
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.arrival_time = time.time()
        self.start_time = None
        self.completion_time = None
        self.memory_manager = memory_manager
        self.paging_mode = paging_mode
        self.page_counter = 0

# Simulates process execution for the designated time slice.
    def run_for(self, quantum):
        if self.start_time is None:
            self.start_time = time.time()

        run_time = min(self.remaining_time, quantum)

        for _ in range(run_time):
            # Simulates page loads on execution.
            page = Page(self.pid, self.page_counter)
            if self.paging_mode == "FIFO":
                self.memory_manager.load_page_fifo(page)
            else:
                self.memory_manager.load_page_lru(page)
            self.page_counter += 1
            
            # Simulates access to the shared resource
            with shared_resource_lock:
                print(f"{self.name} (PID {self.pid}) is accessing shared resource...")
            time.sleep(1)

        self.remaining_time -= run_time
        
        # Marks process as complete when finished.
        if self.remaining_time <= 0:
            self.completion_time = time.time()
            print(f"Process {self.name} (PID {self.pid}) completed.")
            return True
        return False
    
 # Calculates timing metrics
    def get_metrics(self):
        turnaround = self.completion_time - self.arrival_time
        waiting = turnaround - self.burst_time
        response = self.start_time - self.arrival_time
        return waiting, turnaround, response

# ================ Priority Scheduler =================
# Runs processes based on priority using a heap queue.
class PriorityScheduler:
    def __init__(self):
        self.heap = []
        self.completed = []

    def add_process(self, process):
        heapq.heappush(self.heap, (process.priority, process.arrival_time, process))

    def run(self):
        while self.heap:
            _, _, process = heapq.heappop(self.heap)
            while process.remaining_time > 0:
                process.run_for(1)
            self.completed.append(process)

# ================== Main Execution ===================
if __name__ == "__main__":
    print("\n=== Running Priority Scheduler with Memory and Sync ===")
    mem_mgr = MemoryManager(total_frames=4)
    # Defines 3 processes with arbitrary burst times and priority levels.
    processes = [
        SimulatedProcess(1, "P1", 4, 2, mem_mgr, "FIFO"),
        SimulatedProcess(2, "P2", 3, 1, mem_mgr, "FIFO"),
        SimulatedProcess(3, "P3", 5, 3, mem_mgr, "FIFO")
    ]
    
    # Runs with priority schedule.
    scheduler = PriorityScheduler()
    for p in processes:
        scheduler.add_process(p)
    scheduler.run()
    
    # Outputs performance metrics for each process.
    print("\n=== Metrics ===")
    for p in scheduler.completed:
        w, t, r = p.get_metrics()
        print(f"{p.name} -> Waiting: {w:.2f}s, Turnaround: {t:.2f}s, Response: {r:.2f}s")
        
    # Outputs number of page faults count and memory usage by process.
    print(f"\nTotal Page Faults: {mem_mgr.get_page_faults()}")
    mem_mgr.print_memory_usage()