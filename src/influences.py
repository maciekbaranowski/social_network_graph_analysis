import random

import cairo
import igraph


def independent_cascade(g, boss, mean_influence=0.2):
    recently_activated = {boss}
    active = {boss}

    g.es["weight"] = 1.0
    for e in g.es:
        g[e.tuple[0], e.tuple[1]] = random.uniform(0, 1)

    while recently_activated:
        new_iteration = set()
        for v in recently_activated:
            not_active_neighbors = set(g.neighbors(v)) - active
            for neighbor in not_active_neighbors:
                if g[v, neighbor] < mean_influence:
                    new_iteration.add(neighbor)
                    active.add(neighbor)
        recently_activated = new_iteration

    # TODO: fix edge width mapping to probability of activation
    draw_graph(g, boss, active, "ic.png", edges=[int(x["weight"] / max(g.es["weight"]) * 4) + 1 for x in g.es])

    return active


def linear_threshold(g, boss):
    recently_activated = {boss}
    active = {boss}
    inactive = set(range(0, g.vcount())) - active

    thresholds = [random.randint(1, g.vcount()) for _ in range(0, g.vcount())]

    while recently_activated:
        new_iteration = set()
        for v in inactive:
            active_neighbors = set(g.neighbors(v)) & active
            if thresholds[v] <= len(active_neighbors):
                new_iteration.add(v)
        active |= new_iteration
        inactive -= new_iteration
        recently_activated = new_iteration

    draw_graph(g, boss, active, "lt.png", vertices=thresholds)

    return active


def draw_graph(g, boss, active, filename, edges=None, vertices=None):
    # prepare graph
    g.vs["color"] = ["red"]
    g.vs["label"] = [""]
    g.es["width"] = [1]

    for i in active:
        g.vs[i]["color"] = "green"

    g.vs[boss]["color"] = "purple"

    if vertices:
        g.vs["label"] = vertices

    if edges:
        g.es["width"] = edges

    layout = g.layout('kk')
    width, height = 900, 600
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.scale(width, height)
    ctx.rectangle(0, 0, 1, 1)
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.fill()
    plot = igraph.plot(g, surface, bbox=(width, height), layout=layout)
    plot.redraw()
    surface.write_to_png(filename)
