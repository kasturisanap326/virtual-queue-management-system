import heapq

class PriorityQueue:
    def __init__(self):
        self.queue = []

    def get_priority(self, priority):
        if priority == "Emergency":
            return 1
        elif priority == "VIP":
            return 2
        else:
            return 3

    def add_customer(self, name, priority):
        pr = self.get_priority(priority)
        heapq.heappush(self.queue, (pr, name))
        return f"{name} added with {priority}"

    def serve_customer(self):
        if self.queue:
            return heapq.heappop(self.queue)
        return None

    def view_queue(self):
        return self.queue