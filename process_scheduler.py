import time
import heapq
from collections import deque

# Simulated Process Class
class SimulatedProcess:
    def __init__(self, pid, name, burst_time, priority=0):
        self.pid = pid
        self.name = name
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.arrival_time = time.time()
        self.start_time = None
        self.completion_time = None
    
    # Simulate running the process for a given quantum time
    def run_for(self, quantum):
        if self.start_time is None:
            self.start_time = time.time()

        run_time = min(self.remaining_time, quantum)
        print(f"Running {self.name} (PID {self.pid}) for {run_time} seconds")
        time.sleep(run_time)
        self.remaining_time -= run_time

        if self.remaining_time <= 0:
            self.completion_time = time.time()
            print(f"Process {self.name} (PID {self.pid}) completed.")
            return True
        return False

    def get_metrics(self):
        turnaround = self.completion_time - self.arrival_time
        waiting = turnaround - self.burst_time
        response = self.start_time - self.arrival_time
        return waiting, turnaround, response

# Scheduling Algorithms
class RoundRobinScheduler:
    def __init__(self, time_slice):
        self.queue = deque()
        self.time_slice = time_slice
        self.completed = []

    def add_process(self, process):
        self.queue.append(process)

    def run(self):
        while self.queue:
            process = self.queue.popleft()
            completed = process.run_for(self.time_slice)
            if completed:
                self.completed.append(process)
            else:
                self.queue.append(process)

class PriorityScheduler:
    def __init__(self):
        self.heap = []
        self.current_process = None
        self.completed = []
    
    
    def add_process(self, process):
        # heapq sorts by (priority, arrival_time) to use FCFS for equal priority
        heapq.heappush(self.heap, (process.priority, process.arrival_time, process))

    def run(self):
        while self.heap:
            _, _, process = heapq.heappop(self.heap)
            self.current_process = process

            while process.remaining_time > 0:
                # Check for preemption
                if self.heap and self.heap[0][0] < process.priority:
                    print(f"Preempting {process.name} (PID {process.pid}) for higher-priority process.")
                    heapq.heappush(self.heap, (process.priority, process.arrival_time, process))
                    break
                process.run_for(1)

            if process.remaining_time <= 0:
                process.completion_time = time.time()
                self.completed.append(process)

# Main execution block to simulate the scheduling algorithms
if __name__ == "__main__":
    processes = [
        SimulatedProcess(1, "P1", 5, 2),
        SimulatedProcess(2, "P2", 3, 1),
        SimulatedProcess(3, "P3", 7, 3),
    ]

    print("\n=== Round Robin Scheduling ===")
    rr = RoundRobinScheduler(time_slice=2)
    for p in processes:
        rr.add_process(SimulatedProcess(p.pid, p.name, p.burst_time, p.priority))
    rr.run()
    for p in rr.completed:
        w, t, r = p.get_metrics()
        print(f"{p.name} -> Waiting: {w:.2f}s, Turnaround: {t:.2f}s, Response: {r:.2f}s")

    print("\n=== Priority Scheduling with Preemption ===")
    pr = PriorityScheduler()
    for p in processes:
        pr.add_process(SimulatedProcess(p.pid, p.name, p.burst_time, p.priority))
    pr.run()
    for p in pr.completed:
        w, t, r = p.get_metrics()
        print(f"{p.name} -> Waiting: {w:.2f}s, Turnaround: {t:.2f}s, Response: {r:.2f}s")