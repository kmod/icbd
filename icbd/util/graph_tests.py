from graph_utils import get_scc

def test_edges(edges):
    scc, scc_nodes = get_scc(edges)
    test_scc(scc, scc_nodes, edges)

def test_scc(scc, scc_nodes, edges):
    INF = 1e9
    distances = [[INF] * len(edges) for e in edges]
    for n, s in edges.iteritems():
        for n2 in s:
            assert scc[n2] >= scc[n]
            distances[n][n2] = 1
    for k in edges:
        print k
        for i in edges:
            for j in edges:
                distances[i][j] = min(distances[i][j], distances[i][k] + distances[k][j])
    for i in edges:
        for j in edges:
            if i >= j:
                continue
            if scc[i] == scc[j]:
                assert distances[i][j] < INF and distances[j][i] < INF, (i, j, scc[i], scc[j], distances[i][j], distances[j][i])
            elif scc[i] < scc[j]:
                assert distances[j][i] >= INF
            else:
                assert distances[i][j] >= INF
    # print distances


if __name__ == "__main__":
    edges = {0: [1], 1: [1, 2, 13], 2: [], 3: [4], 4: [1, 5], 5: [], 6: [7], 7: [7, 8], 8: [], 9: [10], 10: [1, 11], 11: [], 12: [13], 13: [1, 7, 13, 14, 19], 14: [], 15: [16], 16: [1, 17], 17: [], 18: [19], 19: [7, 19, 20], 20: []}

    test_edges(edges)
