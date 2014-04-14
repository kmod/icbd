import collections

DEBUG = 0

def get_scc(edges):
    reverse_edges = {}
    for n, s in edges.iteritems():
        for n2 in s:
            assert n2 in edges
            reverse_edges.setdefault(n2, set()).add(n)


    visited_set = set()
    finished_order = []
    for n in edges:
        if n in visited_set:
            continue
        queue = collections.deque([("visit", n)])

        while queue:
            verb, n = queue.popleft()
            if verb == "finish":
                finished_order.append(n)
                if DEBUG:
                    for n2 in edges.get(n, []):
                        assert n2 in visited_set, (n, n2)
                continue

            assert verb == "visit"
            if n in visited_set:
                continue
            visited_set.add(n)
            queue.appendleft(("finish", n))
            for n2 in edges.get(n, []):
                queue.appendleft(("visit", n2))
    assert len(finished_order) == len(visited_set) == len(edges), (len(finished_order), len(visited_set), len(edges))

    scc = dict((n, -1) for n in edges)
    num_scc = 0
    finished_order.reverse()
    for n in finished_order:
        if scc[n] != -1:
            continue

        c = num_scc
        num_scc += 1

        queue = collections.deque([n])
        while queue:
            n = queue.popleft()
            scc[n] = c
            for n2 in reverse_edges.get(n, ()):
                if scc[n2] == -1:
                    queue.append(n2)

    scc_nodes = {}
    for n, c in scc.iteritems():
        scc_nodes.setdefault(c, []).append(n)

    return scc, scc_nodes
