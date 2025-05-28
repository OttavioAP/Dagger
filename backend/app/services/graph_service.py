from typing import Dict, List, Set


def find_connected_nodes(graph: Dict[str, List[str]], start_node: str) -> Set[str]:
    visited = set()
    to_visit = {start_node}
    while to_visit:
        current = to_visit.pop()
        if current not in visited:
            visited.add(current)
            to_visit.update(graph.get(current, []))
    return visited


def split_graph(graph: Dict[str, List[str]], first: str, second: str):
    # Remove the edge
    if first in graph and second in graph[first]:
        graph[first].remove(second)
    # Find all nodes connected to first node
    first_connected = find_connected_nodes(graph, first)
    # Create two new graphs
    first_graph = {
        k: [v for v in graph[k] if v in first_connected]
        for k in first_connected
        if k in graph
    }
    second_graph = {
        k: [v for v in graph[k] if v not in first_connected]
        for k in graph
        if k not in first_connected
    }
    return first_graph, second_graph


def merge_graphs(
    graph1: Dict[str, List[str]], graph2: Dict[str, List[str]], first: str, second: str
) -> Dict[str, List[str]]:
    merged = graph1.copy()
    merged.update(graph2)
    # Add the new edge
    if first not in merged:
        merged[first] = []
    if second not in merged:
        merged[second] = []
    if second not in merged[first]:
        merged[first].append(second)
    return merged


def connected_components(graph: Dict[str, List[str]]):
    seen = set()
    components = []
    for node in graph:
        if node not in seen:
            queue = [node]
            comp = set()
            while queue:
                n = queue.pop()
                if n not in comp:
                    comp.add(n)
                    queue.extend(graph.get(n, []))
            seen |= comp
            components.append(comp)
    return components
