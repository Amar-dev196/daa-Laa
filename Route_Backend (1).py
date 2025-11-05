import sys

# Constants
INT_MAX = 2147483647
MAX_CITIES = 50

# Memoization cache for storing computed distances
memo = [[INT_MAX for _ in range(MAX_CITIES)] for _ in range(MAX_CITIES)]

class Edge:
   
    def __init__(self, src=0, dest=0, weight=0):
        self.src = src
        self.dest = dest
        self.weight = weight

class Graph:
    
    def __init__(self, V, E):
        self.V = V  # Number of vertices (cities)
        self.E = E  # Number of edges (roads)
        self.edge = [Edge() for _ in range(E)]

def initialize_memo(V):
   
    for i in range(V):
        for j in range(V):
            memo[i][j] = INT_MAX

def display_results(src, dist, city_names, V):
   
    print(f"\n{'='*50}")
    print(f"Shortest Distances from {city_names[src]}")
    print(f"{'='*50}")
    print(f"{'Destination':<20} {'Distance':<10}")
    print(f"{'-'*50}")
    
    for i in range(V):
        if dist[i] == INT_MAX:
            print(f"{city_names[i]:<20} {'INF':<10}")
        else:
            print(f"{city_names[i]:<20} {dist[i]:<10}")
    print(f"{'='*50}\n")

    # Export results to CSV for visualization
    with open("route_results.csv", "w") as f:
        f.write("City,Distance\n")
        for i in range(V):
            distance_str = "INF" if dist[i] == INT_MAX else str(dist[i])
            f.write(f"{city_names[i]},{distance_str}\n")

def bellman_ford(graph, src, city_names):
   
    V = graph.V
    E = graph.E
    dist = [INT_MAX] * V

    # Check if we already computed this source
    is_memoized = all(memo[src][i] != INT_MAX or i == src for i in range(V))
    
    if is_memoized and memo[src][src] == 0:
        print(f"\n✓ Using cached results for {city_names[src]}")
        display_results(src, memo[src], city_names, V)
        return

    # Initialize distances
    dist[src] = 0

    # Relax edges V-1 times
    for iteration in range(V - 1):
        updated = False
        for j in range(E):
            u = graph.edge[j].src
            v = graph.edge[j].dest
            w = graph.edge[j].weight
            
            if dist[u] != INT_MAX and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        
        if not updated:
            break  # Early termination if no updates

    # Check for negative weight cycles
    for j in range(E):
        u = graph.edge[j].src
        v = graph.edge[j].dest
        w = graph.edge[j].weight
        
        if dist[u] != INT_MAX and dist[u] + w < dist[v]:
            print("\n⚠ WARNING: Negative weight cycle detected!")
            print("Cannot compute shortest paths reliably.\n")
            return

    # Store results in memo
    for i in range(V):
        memo[src][i] = dist[i]

    display_results(src, dist, city_names, V)

def find_city_index(city_names, name):
   
    try:
        return city_names.index(name)
    except ValueError:
        return -1

def save_graph_data(graph, city_names, V, E, src_city):
   
    # Save edges
    with open("route_edges.csv", "w") as f:
        f.write("Source,Destination,Weight\n")
        for i in range(E):
            src_name = city_names[graph.edge[i].src]
            dest_name = city_names[graph.edge[i].dest]
            weight = graph.edge[i].weight
            f.write(f"{src_name},{dest_name},{weight}\n")
    
    # Save metadata
    with open("route_meta.txt", "w") as f:
        f.write(f"{V}\n{src_city}\n")
        f.write(" ".join(city_names))

def main():
    print("\n" + "="*50)
    print(" SHORTEST PATH FINDER - Bellman-Ford Algorithm")
    print("="*50 + "\n")
    
    # Input graph size
    try:
        V, E = map(int, input("Enter number of cities and roads: ").split())
        if V <= 0 or E <= 0 or V > MAX_CITIES:
            print("Invalid input! Please enter positive numbers.")
            return
    except ValueError:
        print("Invalid input format! Use: <cities> <roads>")
        return

    graph = Graph(V, E)
    city_names = []

    # Input city names
    print(f"\nEnter {V} city names:")
    for i in range(V):
        city = input(f"  City {i + 1}: ").strip()
        if not city:
            print("City name cannot be empty!")
            return
        city_names.append(city)

    # Input roads
    print(f"\nEnter {E} roads (format: SourceCity DestCity Distance):")
    for i in range(E):
        try:
            src_name, dest_name, distance = input(f"  Road {i + 1}: ").split()
            distance = int(distance)
            
            src_idx = find_city_index(city_names, src_name)
            dest_idx = find_city_index(city_names, dest_name)
            
            if src_idx == -1 or dest_idx == -1:
                print(f"Error: Invalid city name(s)!")
                return
            
            graph.edge[i].src = src_idx
            graph.edge[i].dest = dest_idx
            graph.edge[i].weight = distance
            
        except ValueError:
            print("Invalid input format!")
            return

    initialize_memo(V)

    # Input source city
    src_city = input("\nEnter source city: ").strip()
    src_idx = find_city_index(city_names, src_city)
    
    if src_idx == -1:
        print(f"Error: '{src_city}' not found in city list!")
        return

    # Save graph data for visualization
    save_graph_data(graph, city_names, V, E, src_city)

    # Run Bellman-Ford algorithm
    bellman_ford(graph, src_idx, city_names)

    print("✓ Results saved to 'route_results.csv'")
    print("✓ Graph data saved to 'route_edges.csv'")
    print("\nRun 'python route_visualizer.py' to visualize the network!\n")

if __name__ == "__main__":
    main()