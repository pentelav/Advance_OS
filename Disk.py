import argparse
import math

# Default disk parameters
DEFAULT_SEEK_RATE = 10        # ms per track
DEFAULT_ROT_RATE = 0.01       # seconds per full rotation
TRANSFER_TIME = 0.1           # ms, constant

# Convert rotation rate (seconds/rev) to avg rotational latency
def rotation_time(rot_rate):
    return (rot_rate * 1000) / 2  # ms

# Seek time (distance * seek rate)
def compute_seek(current, target, seek_rate):
    return abs(target - current) * seek_rate

# Simulate scheduling policies
def schedule(requests, current, policy, seek_rate, rot_rate):
    time = 0
    order = []
    pos = current
    pending = list(requests)

    while pending:
        if policy == "FIFO":
            next_req = pending.pop(0)
        elif policy == "SSTF":
            next_req = min(pending, key=lambda r: abs(r - pos))
            pending.remove(next_req)
        elif policy == "SATF":
            next_req = min(
                pending,
                key=lambda r: compute_seek(pos, r, seek_rate) + rotation_time(rot_rate)
            )
            pending.remove(next_req)
        else:
            raise ValueError("Unknown policy")

        seek = compute_seek(pos, next_req, seek_rate)
        rotate = rotation_time(rot_rate)
        total = seek + rotate + TRANSFER_TIME

        print(f"Request {next_req} → Seek: {seek:.2f} ms, Rotate: {rotate:.2f} ms, Transfer: {TRANSFER_TIME:.2f} ms, Total: {total:.2f} ms")

        time += total
        pos = next_req
        order.append(next_req)

    print(f"\nTotal Access Time: {time:.2f} ms")
    print(f"Order of Execution: {order}")

def main():
    parser = argparse.ArgumentParser(description="Disk Scheduling Simulator")
    parser.add_argument("-a", "--accesses", type=str, required=True, help="Comma-separated list of requests (track numbers)")
    parser.add_argument("-S", "--seek_rate", type=float, default=DEFAULT_SEEK_RATE, help="Seek rate in ms per track")
    parser.add_argument("-R", "--rot_rate", type=float, default=DEFAULT_ROT_RATE, help="Rotation rate in sec per rev")
    parser.add_argument("-p", "--policy", type=str, default="FIFO", choices=["FIFO", "SSTF", "SATF"], help="Scheduling policy")

    args = parser.parse_args()

    requests = list(map(int, args.accesses.split(",")))
    seek_rate = args.seek_rate
    rot_rate = args.rot_rate
    policy = args.policy

    print(f"Accessing tracks: {requests}")
    print(f"Seek rate: {seek_rate} ms/track, Rotation rate: {rot_rate} sec/rev, Policy: {policy}\n")
    
    schedule(requests, current=0, policy=policy, seek_rate=seek_rate, rot_rate=rot_rate)

if __name__ == "__main__":
    main()