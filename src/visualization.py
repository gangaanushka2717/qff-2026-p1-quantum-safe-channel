import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

def draw_processor(processor, output_path, route=None):
    count = processor.get("num_qubits", processor.get("qubit_count"))
    graph = nx.Graph()
    graph.add_nodes_from(range(count))
    graph.add_edges_from(tuple(edge) for edge in processor["coupling_map"])

    plt.figure(figsize=(7, 5))
    positions = nx.spring_layout(graph, seed=42)

    nx.draw_networkx(
        graph, positions, with_labels=True,
        node_size=900, font_size=10
    )

    if route and len(route) > 1:
        route_edges = list(zip(route, route[1:]))
        nx.draw_networkx_edges(
            graph, positions, edgelist=route_edges,
            edge_color="red", width=3
        )

    plt.title(f"{processor.get('name', 'Processor')} topology")
    plt.axis("off")
    plt.tight_layout()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close()
    return output_path
