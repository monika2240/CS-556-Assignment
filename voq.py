"""
Part 2: Virtual Output Queue (VOQ) - Optimal Exhaustive Search
3x3 crossbar switch simulation using VOQ architecture.

Strategy:
  1. First run a greedy pass to get an upper bound.
  2. DFS exhaustive search pruned by:
       - current_t >= best_time
       - lower bound: t + ceil(remaining/3) >= best_time
  3. Only try MAXIMAL matchings (maximises throughput).
  4. Memoize visited (voq_state, t) states.
"""

from collections import defaultdict

NUM_PORTS = 3

PACKETS = [
    ("p1",  0, 0, 0), ("p2",  0, 0, 1), ("p3",  0, 1, 0),
    ("p4",  0, 1, 2), ("p5",  0, 2, 0), ("p6",  1, 0, 2),
    ("p7",  1, 2, 1), ("p8",  2, 1, 1), ("p9",  2, 2, 2),
    ("p10", 3, 0, 1), ("p11", 3, 1, 0), ("p12", 3, 2, 1),
    ("p13", 4, 0, 0), ("p14", 4, 1, 2), ("p15", 4, 2, 2),
    ("p16", 5, 0, 2), ("p17", 5, 1, 1), ("p18", 5, 2, 0),
]

by_time = defaultdict(list)
for pid, arr, src, dst in PACKETS:
    by_time[arr].append((pid, arr, src, dst))

MAX_ARRIVAL = max(arr for _, arr, _, _ in PACKETS)


def enqueue(voq, t):
    nv = [[list(q) for q in row] for row in voq]
    for pid, arr, src, dst in by_time.get(t, []):
        nv[src][dst].append(pid)
    return nv


def total_packets(voq):
    return sum(len(voq[i][o]) for i in range(NUM_PORTS) for o in range(NUM_PORTS))


def get_maximal_matchings(voq):
    feasible = [(i, o) for i in range(NUM_PORTS)
                for o in range(NUM_PORTS) if voq[i][o]]
    if not feasible:
        return [{}]
    maximal = []

    def bt(k, used_in, used_out, cur):
        can_extend = any(i not in used_in and o not in used_out
                         for i, o in feasible[k:])
        if not can_extend:
            maximal.append(dict(cur))
            return
        for idx in range(k, len(feasible)):
            i, o = feasible[idx]
            if i not in used_in and o not in used_out:
                used_in.add(i); used_out.add(o); cur[i] = o
                bt(idx + 1, used_in, used_out, cur)
                used_in.remove(i); used_out.remove(o); del cur[i]

    bt(0, set(), set(), {})
    return maximal if maximal else [{}]


def apply_matching(voq, matching):
    nv = [[list(q) for q in row] for row in voq]
    sent = []
    for i, o in matching.items():
        pkt = nv[i][o].pop(0)
        sent.append((pkt, i, o))
    return nv, sent


def voq_size_vector(voq):
    """Use queue *lengths* for memo key (order within queue doesn't affect optimality bound)."""
    return tuple(len(voq[i][o]) for i in range(NUM_PORTS) for o in range(NUM_PORTS))


best = [999, []]
visited = {}   # (size_vector, t) -> best_time achieved from this state


def search(voq, t, log):
    if t >= best[0]:
        return
    voq = enqueue(voq, t)
    rem = total_packets(voq)
    if rem == 0:
        if t < best[0]:
            best[0] = t
            best[1] = list(log)
        return
    lb = (rem + NUM_PORTS - 1) // NUM_PORTS
    if t + lb >= best[0]:
        return

    # Memoization: if we've visited this (state, t) and already achieved a
    # better or equal finish time, skip.
    key = (voq_size_vector(voq), t)
    if key in visited and visited[key] <= best[0]:
        return
    visited[key] = best[0]

    for matching in get_maximal_matchings(voq):
        nv, sent = apply_matching(voq, matching)
        log.append((t, matching, sent))
        search(nv, t + 1, log)
        log.pop()


def greedy_ub():
    voq = [[[] for _ in range(NUM_PORTS)] for _ in range(NUM_PORTS)]
    t = 0
    log = []
    while True:
        voq = enqueue(voq, t)
        if total_packets(voq) == 0 and t > MAX_ARRIVAL:
            return t, log
        ms = get_maximal_matchings(voq)
        m = max(ms, key=len)
        nv, sent = apply_matching(voq, m)
        log.append((t, m, sent))
        voq = nv
        t += 1
        if t > 60:
            return t, log


def run_part2():
    print("=" * 60)
    print("PART 2: VOQ — Exhaustive Optimal Search")
    print("=" * 60)

    ub, ub_log = greedy_ub()
    print(f"Greedy upper bound: {ub} slots\n")
    best[0] = ub
    best[1] = ub_log

    voq0 = [[[] for _ in range(NUM_PORTS)] for _ in range(NUM_PORTS)]
    search(voq0, 0, [])

    best_time, best_log = best
    print(f"Optimal Total Service Time: t = {best_time}\n")
    print("Optimal Sequence of Matchings:")
    print("-" * 60)
    for t, matching, sent in best_log:
        pairs = ", ".join(f"I{i}→O{o}" for i, o in sorted(matching.items()))
        print(f"t = {t}:  Matching: [{pairs}]")
        for pid, inp, out in sent:
            print(f"    Sent {pid}  (I{inp} → O{out})")
    print("-" * 60)
    print(f"\nSwitch empties at the start of t = {best_time}  ({best_time} time slots used)")

    # Backlog
   
    voq = [[[] for _ in range(NUM_PORTS)] for _ in range(NUM_PORTS)]
    log_idx = 0
   
    for t in range(best_time + 1):
        voq = enqueue(voq, t)
        rem = total_packets(voq)
       
        if rem == 0:
            break
        matching = {}
        if log_idx < len(best_log) and best_log[log_idx][0] == t:
            matching = best_log[log_idx][1]
            log_idx += 1
        voq, _ = apply_matching(voq, matching)


if __name__ == "__main__":
    run_part2()