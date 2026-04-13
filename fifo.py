from collections import deque

class Packet:
    def __init__(self, pid, arrival, inp, out):
        self.id = pid
        self.arrival = arrival
        self.input = inp
        self.output = out

packets = [
    Packet("p1",0,0,0), Packet("p2",0,0,1), Packet("p3",0,1,0),
    Packet("p4",0,1,2), Packet("p5",0,2,0),
    Packet("p6",1,0,2), Packet("p7",1,2,1),
    Packet("p8",2,1,1), Packet("p9",2,2,2),
    Packet("p10",3,0,1), Packet("p11",3,1,0), Packet("p12",3,2,1),
    Packet("p13",4,0,0), Packet("p14",4,1,2), Packet("p15",4,2,2),
    Packet("p16",5,0,2), Packet("p17",5,1,1), Packet("p18",5,2,0)
]

input_queues = [deque() for _ in range(3)]

t = 0
delivered = 0
total_packets = len(packets)

while delivered < total_packets:
    print(f"\n========== Time Slot {t} ==========")

    # Add arrivals
    for p in packets:
        if p.arrival == t:
            input_queues[p.input].append(p)

    # Print queues
    print("Queues:")
    for i in range(3):
        q = [f"{p.id}(O{p.output})" for p in input_queues[i]]
        print(f"  I{i}: {q}")

    output_busy = [False]*3
    input_sent = [False]*3

    # Transmission
    print("\nTransmissions:")
    for i in range(3):
        if input_queues[i]:
            p = input_queues[i][0]

            if not output_busy[p.output]:
                print(f"  {p.id}: I{i} → O{p.output}")
                output_busy[p.output] = True
                input_sent[i] = True
                input_queues[i].popleft()
                delivered += 1

    # HoL Blocking Detection
    print("\nHoL Blocking:")
    hol_found = False

    for i in range(3):
        if input_queues[i] and not input_sent[i]:
            queue = list(input_queues[i])
            front = queue[0]

            if output_busy[front.output] and len(queue) > 1:
                for p in queue[1:]:
                    if not output_busy[p.output]:
                        print(f"  At I{i}: {front.id} blocks {p.id}")
                        hol_found = True
                        break

    if not hol_found:
        print("  None")

    t += 1

print("\nTotal Service Time =", t)