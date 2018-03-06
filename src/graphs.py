from functools import partial
from random import choice

import matplotlib.pyplot as plt
from igraph import Graph
from influences import independent_cascade, linear_threshold


def random_graph(nodes=20):
    return Graph.GRG(nodes, 0.5)


def get_scale_metric(graph, func):
    metric = [func(v) for v in graph.vs]
    ref = max(metric)
    return [float(value)/ref for value in metric]


def find_the_boss(graph):
    return graph.evcent().index(1)


def draw_centralities_for_all_nodes(graph):
    degree = get_scale_metric(graph, lambda x: x.degree())
    betweenness = get_scale_metric(graph, lambda x: x.betweenness())
    closeness = get_scale_metric(graph, lambda x: x.closeness())
    eigenvector = graph.evcent()

    plt.plot(degree, label='degree')
    plt.plot(betweenness, label='betweenness')
    plt.plot(closeness, label='closeness')
    plt.plot(eigenvector, label='eigenvector')
    plt.legend()
    plt.show()


def remove_one_add_many(graph, evader, b):
    graph = graph.copy()

    # step 1
    evader_neighbors = graph.vs[evader].neighbors()
    if len(evader_neighbors) == 0:
        raise StopIteration()

    del_neigh = choice(evader_neighbors)
    graph.delete_edges([(evader, del_neigh.index)])

    # step 2
    for _ in range(b - 1):
        try:
            broker = choice(
                list(
                    set(evader_neighbors)
                    - set(del_neigh.neighbors())
                )
            )
        except IndexError:
            raise StopIteration()
        graph.add_edge(del_neigh.index, broker.index)

    return graph


def graphs_after_roam(graph, evader, b, executions):
    graphs = [graph]
    for _ in range(executions):
        try:
            graph = remove_one_add_many(graph, evader, b)
        except StopIteration:
            break
        graphs.append(graph)
    return graphs


def metric_ranking(graph, node_index, node_metric=None, graph_metric=None):
    if node_metric is not None:
        node = graph.vs[node_index]
        return sorted(graph.vs, key=node_metric, reverse=True).index(node)
    elif graph_metric is not None:
        metrics = graph_metric(graph)
        value = metrics[node_index]
        return sorted(metrics, reverse=True).index(value)


def metric_ranking_graph_list(node, graphs, **kwargs):
    return [metric_ranking(graph, node, **kwargs) for graph in graphs]


def get_roam_graphs(graph, boss, excecutions):
    roam1 = graphs_after_roam(graph, boss, 1, excecutions)
    roam2 = graphs_after_roam(graph, boss, 2, excecutions)
    roam3 = graphs_after_roam(graph, boss, 3, excecutions)
    roam4 = graphs_after_roam(graph, boss, 4, excecutions)
    return roam1, roam2, roam3, roam4


def add_metric_plot(roams, boss, metric_name, node_metric=None,
                    graph_metric=None):
    node_metric_ranking = partial(
        metric_ranking_graph_list,
        boss,
        node_metric=node_metric,
        graph_metric=graph_metric,
    )

    plt.figure()
    plt.title(metric_name)
    plt.plot(node_metric_ranking(roams[0]), label='roam1')
    plt.plot(node_metric_ranking(roams[1]), label='roam2')
    plt.plot(node_metric_ranking(roams[2]), label='roam3')
    plt.plot(node_metric_ranking(roams[3]), label='roam4')

    plt.legend()
    plt.savefig(metric_name + '.pdf')


def generate_metric_plots(graph, boss):
    roams = get_roam_graphs(graph, boss, 30)

    degree = lambda v: v.degree()
    betweenness = lambda v: v.betweenness()
    closeness = lambda v: v.closeness()
    eigenvector = lambda g: g.evcent()

    add_metric_plot(roams, boss, 'degree', node_metric=degree)
    add_metric_plot(roams, boss, 'betweenness', node_metric=betweenness)
    add_metric_plot(roams, boss, 'closeness', node_metric=closeness)
    add_metric_plot(roams, boss, 'eigenvector', graph_metric=eigenvector)


graph = random_graph()
boss = find_the_boss(graph)
generate_metric_plots(graph, boss)
print(independent_cascade(graph, boss))
print(linear_threshold(graph, boss))
