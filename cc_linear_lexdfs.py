from typing import List
from llist import dllist


class Vertex:
    def __init__(self, id):
        # basic fields of vertex
        self.id = id
        self.label = 0
        self.edges = []

        # fields for partition method
        self.processed_right_edges = False
        self.right_edges_in_sigma = 0
        self.partitioned = False
        self.bin_node = None

        # field for reorder
        self.reordered_edges = []

        # fields for refinement
        self.partition_node = None
        self.partition = None
        self.refined = False

    def __repr__(self):
        return self.id

    def add_edge(self, vertex):
        self.edges.append(vertex)


class Partition:
    def __init__(self, elements):
        # fields for keeping and splitting vertices
        self.elements = dllist()
        for u in elements:
            u.partition_node = self.elements.append(u)
        self.split_place = self.elements.first
        self.splittable = False

        # fields for updating stacks
        self.stack = []
        self.last_modified_stack = None

    def __repr__(self):
        return str(list(self.elements))

    def move_vertex(self, u):
        if u.partition_node is self.split_place:
            if self.split_place is self.elements.last:
                self.splittable = False
                return
            self.split_place = self.split_place.next

        self.elements.remove(u.partition_node)
        u.partition_node = self.elements.insert(u, self.split_place)
        self.splittable = True

    def split(self):
        left = []
        for el in self.elements:
            if el is not self.split_place.value:
                left.append(el)
            else:
                break

        for _ in left:
            self.elements.popleft()

        return left

    def update_partition_link(self, partition):
        for el in self.elements:
            el.partition = partition

    def update_stack(self, modified_by: Vertex, point: Vertex):
        if self.last_modified_stack is modified_by:
            self.stack[-1].append(point)
        else:
            self.last_modified_stack = modified_by
            self.stack.append([point])


def create_bins(sigma):
    """Parameters:
    sigma -an umbrella-free ordering of a graph
    Returns:
        a list of bins(double linked lists) with vertices
    """
    n = len(sigma) - 1
    bins = [dllist() for _ in range(n)]
    for i in range(n, -1, -1):
        sigma[i].label = n - i - sigma[i].right_edges_in_sigma
        sigma[i].bin_node = bins[sigma[i].label].append(sigma[i])
        sigma[i].processed_right_edges = True

        for v in sigma[i].edges:
            if not v.processed_right_edges:
                v.right_edges_in_sigma += 1
    return bins


def create_partition_classes(sigma: List[Vertex]):
    """Parameters:
    sigma - an umbrella-free ordering of a graph
    graph - graph as a list of vertices
    """
    partitions = []

    bins = create_bins(sigma)

    for i in range(len(bins)):
        bin = list(bins[i])
        if not bin:
            continue

        partitions.append(Partition(bin))
        partitions[-1].update_partition_link(partitions[-1])

        for u in bin:
            u.partitioned = True

        for u in bin:
            for v in u.edges:
                if not v.partitioned:
                    bins[v.label].remove(v.bin_node)
                    v.label += 1
                    v.bin_node = bins[v.label].append(v)
    return partitions


def reorder_edges(partitions: List[Partition], graph: List[Vertex]):
    for partition in partitions:
        for u in partition.elements:
            for v in u.edges:
                v.reordered_edges.append(u)

    for u in graph:
        u.edges = u.reordered_edges


def refine(partition):
    """Parameters:
    partition -  a partition class with vertices
    stack - a stack is lists of friends"""
    partitions = dllist([partition])
    partitions.first.value.update_partition_link(partitions.first)

    while partition.stack:
        top = partition.stack.pop()
        for u in top:
            u.partition.value.move_vertex(u)

        for u in top:
            if u.partition.value.splittable:
                u.partition.value.splittable = False
                left = u.partition.value.split()
                u.partition = partitions.insert(Partition(left), u.partition)
                u.partition.value.update_partition_link(u.partition)

    for partition in partitions:
        for u in partition.elements:
            u.refined = True

    return [partition.elements for partition in partitions]


def set_up_graph():
    adjecency_list = [[1, 2, 3],
                      [0, 2, 4],
                      [0, 1, 3],
                      [0, 2, 4, 5, 6],
                      [1, 3, 5],
                      [3, 4, 6, 7],
                      [3, 5, 8],
                      [5, 8, 9, 10],
                      [6, 7],
                      [7],
                      [7], ]
    graph = [Vertex('a'),  # 0
             Vertex('b'),  # 1
             Vertex('c'),  # 2
             Vertex('d'),  # 3
             Vertex('e'),  # 4
             Vertex('f'),  # 5
             Vertex('g'),  # 6
             Vertex('h'),  # 7
             Vertex('i'),  # 8
             Vertex('j'),  # 9
             Vertex('k')]  # 10
    for u in range(len(adjecency_list)):
        for v in adjecency_list[u]:
            graph[u].add_edge(graph[v])
    return graph


def get_sigma_ordering(graph):
    """For the graph in the example this is a correct umbrella-free ordering.
    It is not implemented for others"""
    return graph


def main():
    graph = set_up_graph()
    sigma = get_sigma_ordering(graph)

    partitions = create_partition_classes(sigma)
    reorder_edges(partitions, graph)

    lex_dfs_order = []
    for partition in partitions:
        refined = refine(partition)

        for ref in refined:
            for u in ref:
                lex_dfs_order.append(u)
                for v in u.edges:
                    if not v.refined:
                        v.partition.update_stack(u, v)
    print(lex_dfs_order)


if __name__ == "__main__":
    main()

