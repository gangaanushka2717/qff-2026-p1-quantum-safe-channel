from collections import deque

def build_adjacency(processor):
    count = processor.get("num_qubits", processor.get("qubit_count"))
    if not isinstance(count, int) or count < 1:
        raise ValueError("Invalid qubit count")

    graph = {q: set() for q in range(count)}
    for u, v in processor["coupling_map"]:
        if u not in graph or v not in graph:
            raise ValueError(f"Invalid coupling edge: {(u, v)}")
        graph[u].add(v)
        graph[v].add(u)
    return graph

def shortest_path(processor, source, target):
    graph = build_adjacency(processor)

    if source not in graph or target not in graph:
        raise ValueError("Source or target qubit is out of range")
    if source == target:
        return [source]

    queue = deque([source])
    parent = {source: None}

    while queue:
        current = queue.popleft()
        for neighbor in sorted(graph[current]):
            if neighbor in parent:
                continue
            parent[neighbor] = current
            if neighbor == target:
                path = [target]
                while parent[path[-1]] is not None:
                    path.append(parent[path[-1]])
                return path[::-1]
            queue.append(neighbor)

    return None

def routing_metrics(processor, source, target):
    path = shortest_path(processor, source, target)
    if path is None:
        return {
            "source": source,
            "target": target,
            "path": None,
            "hop_count": None,
            "intermediate_qubits": None,
        }

    hops = len(path) - 1
    return {
        "source": source,
        "target": target,
        "path": path,
        "hop_count": hops,
        "intermediate_qubits": max(0, hops - 1),
    }
