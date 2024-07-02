import copy
class MinHeap:

    class EmptyHeapError(Exception):
        pass

    def __init__(self, list_in=None):
        if list_in is None:
            self.heap_list = [None]
            self.size = 0
        else:
            self.heap_list = copy.deepcopy(list_in)
            self.size = len(list_in)
            self.heap_list.insert(0, 0)
            self.order_heap()

    def order_heap(self):
        for i in range(self.size // 2, 0, -1):
            self.percolate_down(i)

    def insert(self, data):
        self.heap_list.append(None)
        self.size += 1
        child_index = self.size
        while child_index > 1 and data < self.heap_list[child_index // 2]:
            self.heap_list[child_index] = self.heap_list[child_index // 2]
            child_index = child_index // 2
        self.heap_list[child_index] = data

    def percolate_down(self, hole):
        data = self.heap_list[hole]
        while 2 * hole <= self.size:
            min_child_index = self.min_child(hole)
            if self.heap_list[min_child_index] < data:
                self.heap_list[hole] = self.heap_list[min_child_index]
            else:
                break
            hole = min_child_index
        self.heap_list[hole] = data

    def min_child(self, node_index):
        if node_index * 2 + 1 > self.size:
            return node_index * 2
        else:
            if self.heap_list[node_index * 2] < self.heap_list[node_index * 2 + 1]:
                return node_index * 2
            else:
                return node_index * 2 + 1

    def remove(self):
        if self.size == 0:
            raise MinHeap.EmptyHeapError
        return_value = self.heap_list[1]
        self.heap_list[1] = self.heap_list[self.size]
        self.size -= 1
        self.heap_list.pop()
        if self.size > 0:
            self.percolate_down(1)
        return return_value