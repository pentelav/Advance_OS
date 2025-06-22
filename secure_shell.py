import os
import time
import threading
import getpass
from collections import OrderedDict
from subprocess import Popen, PIPE

# ------------------------- Security Setup ---------------------------- #
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "pass123", "role": "user"}
}

PERMISSIONS = {
    "admin": {"read": True, "write": True, "execute": True},
    "user": {"read": True, "write": False, "execute": True}
}

# ------------------------- Authentication ---------------------------- #
def authenticate():
    print("Welcome to the Secure Shell")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    user = USERS.get(username)
    if user and user["password"] == password:
        print(f"Login successful! Role: {user['role']}")
        return username, user["role"]
    else:
        print("Authentication Failed.")
        exit()

# ------------------------- File Permissions -------------------------- #
def check_permission(role, action, filename):
    perms = PERMISSIONS[role]
    if not perms.get(action, False):
        print(f"Permission Denied: You do not have {action} access to '{filename}'")
        return False
    return True

# ------------------------- Paging System ----------------------------- #
class MemoryManager:
    def __init__(self, frame_count=4, mode="FIFO"):
        self.frames = []
        self.max_frames = frame_count
        self.mode = mode
        self.page_faults = 0
        self.frame_map = OrderedDict()

    def access_page(self, pid, page):
        key = (pid, page)
        if key in self.frame_map:
            if self.mode == "LRU":
                self.frame_map.move_to_end(key)
        else:
            self.page_faults += 1
            if len(self.frame_map) >= self.max_frames:
                evicted = self.frame_map.popitem(last=False)
                print(f"Evicting page: {evicted[0]}")
            self.frame_map[key] = True
            print(f"Loaded page: {key}")

    def print_status(self):
        print("\nFinal Memory State:")
        for key in self.frame_map:
            print(f"Process {key[0]} -> Page {key[1]}")
        print(f"Total Page Faults: {self.page_faults}")

# ------------------------- Process Simulation ------------------------ #
class SimulatedProcess:
    def __init__(self, pid, pages, shared_lock, memory_manager):
        self.pid = pid
        self.pages = pages
        self.shared_lock = shared_lock
        self.memory_manager = memory_manager
        self.execution_time = 0

    def run(self):
        start = time.time()
        for page in self.pages:
            time.sleep(1)
            self.memory_manager.access_page(self.pid, page)
            with self.shared_lock:
                print(f"[Process {self.pid}] Accessing shared resource...")
                time.sleep(1)
        end = time.time()
        self.execution_time = end - start
        print(f"[Process {self.pid}] Completed in {self.execution_time:.2f} sec")

# ------------------------- Piping Commands --------------------------- #
def execute_piped_command(command_line):
    try:
        proc = Popen(command_line, shell=True, stdout=PIPE, stderr=PIPE)
        output, error = proc.communicate()
        if output:
            print(output.decode())
        if error:
            print(error.decode())
    except Exception as e:
        print(f"Error: {e}")

# ------------------------- Main Shell Loop --------------------------- #
def main():
    username, role = authenticate()

    memory_manager = MemoryManager(mode="LRU")  # Or FIFO
    shared_lock = threading.Lock()

    # Start simulated processes
    p1 = SimulatedProcess(1, [1, 2, 3], shared_lock, memory_manager)
    p2 = SimulatedProcess(2, [2, 4], shared_lock, memory_manager)
    p3 = SimulatedProcess(3, [1, 3], shared_lock, memory_manager)

    threads = []
    for proc in [p1, p2, p3]:
        t = threading.Thread(target=proc.run)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    memory_manager.print_status()

    # Begin command loop
    while True:
        command = input("$ ")
        if command.strip() == "exit":
            break
        elif '|' in command:
            execute_piped_command(command)
        elif command.startswith("read"):
            parts = command.split()
            if len(parts) > 1 and check_permission(role, "read", parts[1]):
                print(f"Reading file: {parts[1]} (simulated)")
        elif command.startswith("write"):
            parts = command.split()
            if len(parts) > 1 and check_permission(role, "write", parts[1]):
                print(f"Writing to file: {parts[1]} (simulated)")
        else:
            print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()