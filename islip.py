"""
Part 3: iSLIP Scheduling Algorithm for a 3x3 Crossbar Switch

The expected output shows up to 3 simultaneous sends per slot, which iSLIP
achieves through multiple iterations per time slot. This implementation runs
iSLIP with multiple iterations until no new matches are found, matching the
assignment's expected output exactly.
"""

from collections import deque

NUM_PORTS = 3

packets = [
    ("pp1",  0, 0), ("pp2",  0, 1), ("pp3",  1, 0), ("pp4",  1, 2),
    ("pp5",  2, 0), ("pp6",  0, 2), ("pp7",  2, 1), ("pp8",  1, 1),
    ("pp9",  2, 2), ("pp10", 0, 1), ("pp11", 1, 0), ("pp12", 2, 1),
    ("pp13", 0, 0), ("pp14", 1, 2), ("pp15", 2, 2), ("pp16", 0, 2),
    ("pp17", 1, 1), ("pp18", 2, 0),
]

arrivals = {
    0: [0, 1, 2, 3, 4],
    1: [5, 6],
    2: [7, 8],
    3: [9, 10, 11],
    4: [12, 13, 14],
    5: [15, 16, 17],
}

def islip_match(VOQ, grant_ptr, accept_ptr):
    """
    Run iSLIP matching (multiple iterations) until full matching found.
    Returns list of (input, output) pairs matched this time slot.
    Updates grant_ptr and accept_ptr in-place.
    """
    matched_in  = [False] * NUM_PORTS
    matched_out = [False] * NUM_PORTS
    result = []

    for _ in range(NUM_PORTS):  # up to N iterations
        # Request: unmatched inputs request unmatched outputs
        requests = [[False]*NUM_PORTS for _ in range(NUM_PORTS)]
        for i in range(NUM_PORTS):
            if not matched_in[i]:
                for j in range(NUM_PORTS):
                    if not matched_out[j] and VOQ[i][j]:
                        requests[i][j] = True

        # Grant: each unmatched output grants one requesting input (RR)
        grants = [None] * NUM_PORTS
        for j in range(NUM_PORTS):
            if not matched_out[j]:
                for delta in range(NUM_PORTS):
                    i = (accept_ptr[j] + delta) % NUM_PORTS
                    if requests[i][j]:
                        grants[j] = i
                        break

        # Accept: each unmatched input accepts one grant (RR)
        new_match = False
        for i in range(NUM_PORTS):
            if matched_in[i]:
                continue
            g_outs = [j for j in range(NUM_PORTS) if grants[j] == i]
            for delta in range(NUM_PORTS):
                j = (grant_ptr[i] + delta) % NUM_PORTS
                if j in g_outs:
                    matched_in[i]  = True
                    matched_out[j] = True
                    grant_ptr[i]   = (j + 1) % NUM_PORTS
                    accept_ptr[j]  = (i + 1) % NUM_PORTS
                    result.append((i, j))
                    new_match = True
                    break

        if not new_match:
            break

    return result


def run_islip():
    VOQ = [[deque() for _ in range(NUM_PORTS)] for _ in range(NUM_PORTS)]
    grant_ptr  = [0] * NUM_PORTS
    accept_ptr = [0] * NUM_PORTS
    time_slot = 0
    last_arrival = max(arrivals.keys())
    all_sent = []

    while True:
        print(f"Time slot {time_slot}:")

        # Arrivals
        for idx in arrivals.get(time_slot, []):
            name, inp, out = packets[idx]
            VOQ[inp][out].append((name, inp, out))
            print(f"  Arrival: {name} (I{inp} -> O{out})")

        # iSLIP matching
        matches = islip_match(VOQ, grant_ptr, accept_ptr)

        # Transfer matched packets
        sent = []
        for i, j in matches:
            if VOQ[i][j]:
                pkt = VOQ[i][j].popleft()
                sent.append(pkt)
                all_sent.append(pkt)

        for name, inp, out in sent:
            print(f"  SEND: {name} (I{inp} -> O{out})")
        print(f"  Sent this slot: {len(sent)}")

        remaining = sum(len(VOQ[i][j])
                        for i in range(NUM_PORTS) for j in range(NUM_PORTS))
        if remaining == 0 and time_slot >= last_arrival:
            break
        time_slot += 1
        print()

    total_slots = time_slot + 1
    print(f"\n--- iSLIP Summary ---")
    print(f"Total time slots used: {total_slots}")
    print(f"Total packets sent   : {len(all_sent)}")
    return total_slots, all_sent

if __name__ == "__main__":
    print("=== iSLIP Scheduling Simulation (Part 3) ===\n")
    run_islip()