import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

def compute_shortest_paths(G, source):
    
    try:
        distances = nx.single_source_dijkstra_path_length(G, source)
        paths = nx.single_source_dijkstra_path(G, source)
        return distances, paths
    except nx.NodeNotFound:
        print(f"Error: Source node '{source}' not found in graph!")
        return {}, {}

def extract_path_edges(G, source):
   
    _, paths = compute_shortest_paths(G, source)
    path_edges = set()
    
    for path in paths.values():
        for i in range(len(path) - 1):
            path_edges.add((path[i], path[i + 1]))
    
    return path_edges

def create_layout(G, source):
    
    levels = defaultdict(list)
    
    try:
        distances = nx.single_source_shortest_path_length(G, source)
    except nx.NodeNotFound:
        print(f"Warning: Source '{source}' not found. Using default layout.")
        return nx.spring_layout(G)
    
    max_level = 0
    for node, level in distances.items():
        levels[level].append(node)
        max_level = max(max_level, level)
    
    # Handle unreachable nodes
    unreachable = set(G.nodes()) - set(distances.keys())
    if unreachable:
        max_level += 1
        levels[max_level].extend(sorted(unreachable))

    # Calculate node positions
    pos = {}
    for level, nodes in levels.items():
        nodes.sort()
        num_nodes = len(nodes)
        
        for i, node in enumerate(nodes):
            x = level
            # Center nodes vertically
            y = (i - (num_nodes - 1) / 2) / max(1, num_nodes - 1)
            pos[node] = (x, y)
    
    return pos

def visualize_network():
   
    print("\n" + "="*50)
    print(" ROUTE NETWORK VISUALIZATION")
    print("="*50 + "\n")
    
    # Load data files
    try:
        results_df = pd.read_csv("route_results.csv")
        edges_df = pd.read_csv("route_edges.csv")
    except FileNotFoundError as e:
        print(f"Error: Required CSV files not found!")
        print("Please run 'python route_backend.py' first.\n")
        return
    
    if edges_df.empty:
        print("Error: No edges found in route_edges.csv")
        return

    # Build complete graph
    G_full = nx.DiGraph()
    for _, row in edges_df.iterrows():
        G_full.add_edge(row['Source'], row['Destination'], 
                       weight=row['Weight'])

    # Identify source city
    source_city = edges_df['Source'].iloc[0]
    
    # Extract shortest path edges
    path_edges = extract_path_edges(G_full, source_city)
    
    # Create visualization graph with only path edges
    G = nx.DiGraph()
    for u, v in path_edges:
        weight = G_full[u][v]['weight']
        G.add_edge(u, v, weight=weight)

    # Parse distances
    reachable_cities = set()
    city_distances = {}
    
    for _, row in results_df.iterrows():
        city = row['City']
        dist = row['Distance']
        
        if isinstance(dist, str):
            if dist.upper() != 'INF':
                try:
                    reachable_cities.add(city)
                    city_distances[city] = float(dist)
                except ValueError:
                    pass
        elif not pd.isna(dist):
            reachable_cities.add(city)
            city_distances[city] = dist

    # Generate layout
    pos = create_layout(G, source_city)

    # Configure plot with dark theme
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14, 9), facecolor='#1a1a1a')
    ax = plt.gca()
    ax.set_facecolor('#1a1a1a')
    plt.suptitle(f'Shortest Path Network from {source_city}', 
                fontsize=16, fontweight='bold', color='white')

    # Determine node colors and sizes
    node_colors = []
    node_sizes = []
    
    for node in G.nodes():
        if node == source_city:
            node_colors.append('#FF6B6B')  # Bright red for source
            node_sizes.append(1200)
        elif node in reachable_cities:
            node_colors.append('#4ECDC4')  # Cyan for reachable
            node_sizes.append(1000)
        else:
            node_colors.append('#95A5A6')  # Gray for unreachable
            node_sizes.append(800)

    # Draw graph components
    nx.draw_networkx_nodes(G, pos, 
                          node_color=node_colors,
                          node_size=node_sizes,
                          edgecolors='#ECF0F1',
                          linewidths=2.5)
    
    nx.draw_networkx_labels(G, pos, 
                           font_size=10,
                           font_weight='bold',
                           font_color='#1a1a1a')
    
    # Draw edges with custom styling
    nx.draw_networkx_edges(G, pos,
                          edge_color='#F39C12',
                          arrows=True,
                          arrowsize=20,
                          width=2.5,
                          connectionstyle='arc3,rad=0.1')
    
    # Add edge labels (weights)
    edge_labels = {(u, v): f"[{w}]" 
                   for (u, v), w in nx.get_edge_attributes(G, 'weight').items()}
    
    nx.draw_networkx_edge_labels(G, pos,
                                edge_labels=edge_labels,
                                font_size=9,
                                font_color='#F39C12',
                                font_weight='bold')

    # Create legend with dark theme colors
    legend_items = [
        plt.Line2D([0], [0], marker='o', color='w',
                  markerfacecolor='#FF6B6B', markersize=12,
                  label='Source City', markeredgecolor='#ECF0F1', markeredgewidth=2),
        plt.Line2D([0], [0], marker='o', color='w',
                  markerfacecolor='#4ECDC4', markersize=12,
                  label='Reachable', markeredgecolor='#ECF0F1', markeredgewidth=2),
        plt.Line2D([0], [0], marker='o', color='w',
                  markerfacecolor='#95A5A6', markersize=12,
                  label='Unreachable', markeredgecolor='#ECF0F1', markeredgewidth=2),
        plt.Line2D([0], [0], color='#F39C12', linewidth=2.5,
                  label='Shortest Path')
    ]
    
    legend = plt.legend(handles=legend_items,
              loc='upper center',
              bbox_to_anchor=(0.5, -0.05),
              ncol=4,
              frameon=True,
              fancybox=True,
              shadow=True)
    
    # Style the legend for dark theme
    legend.get_frame().set_facecolor('#2C3E50')
    legend.get_frame().set_edgecolor('#ECF0F1')
    for text in legend.get_texts():
        text.set_color('#ECF0F1')

    # Final adjustments
    plt.axis('off')
    plt.margins(0.15)
    plt.tight_layout()
    
    print("✓ Visualization generated successfully!")
    print("  Close the plot window to exit.\n")
    
    plt.show()

if __name__ == "__main__":
    visualize_network()