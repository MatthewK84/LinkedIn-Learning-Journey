import pandas as pd
import networkx as nx
from itertools import combinations
import pandas as pd

# Step 1: Load Network from File
def load_network(csv_path):
    df = pd.read_csv("/Users/matthewkolakowski/Documents/network_data.csv")
    G = nx.DiGraph()  # Use DiGraph to model bi-directional links
    for _, row in df.iterrows():
        # Add both directions since the network is bi-directional
        G.add_edge(row['Start'], row['End'], capacity=row['Capacity'], weight=row['Weight'])
        G.add_edge(row['End'], row['Start'], capacity=row['Capacity'], weight=row['Weight'])
    return G

# Step 2: Determine Paths through Network
def find_shortest_path(graph, source, destination):
    return nx.dijkstra_path(graph, source, destination, weight='weight')

# Step 3: Load Traffic Data
    def load_traffic(csv_path):
        return pd.read_csv(csv_path)

    # Step 4: Apply Traffic Flow and Model Traffic Load
    def model_traffic_load(graph, traffic_df):
        link_load = {edge: 0 for edge in graph.edges()}
        for _, demand in traffic_df.iterrows():
            path = find_shortest_path(graph, demand['Source'], demand['Destination'])
            # Add demand to each link in the path
            for i in range(len(path)-1):
                link_load[(path[i], path[i+1])] += demand['Demand']
        return link_load
    return link_load

# Step 5: Determine Worst Case Failure
def worst_case_failure(graph, traffic_df):
    original_graph = graph.copy()
    worst_case = {'link': None, 'unroutable': float('inf'), 'over_capacity': {}}
    for edge in original_graph.edges():
        graph = original_graph.copy()
        graph.remove_edge(*edge)
        link_load = model_traffic_load(graph, traffic_df)
        over_capacity = {e: load for e, load in link_load.items() if load > graph[e[0]][e[1]]['capacity']}
        unroutable = sum(1 for load in over_capacity.values())
        
        # Check if this failure scenario is worse than the previous worst case
        if unroutable < worst_case['unroutable'] or \
           (unroutable == worst_case['unroutable'] and len(over_capacity) > len(worst_case['over_capacity'])):
            worst_case = {'link': edge, 'unroutable': unroutable, 'over_capacity': over_capacity}
    
    return worst_case

# Usage Example
network_csv = '/Users/matthewkolakowski/Documents/network_data.csv'

# Define load_traffic function
def load_traffic(csv_path):
    return pd.read_csv(csv_path)

# Load network and traffic

# Define model_traffic_load function
def model_traffic_load(graph, traffic_df):
    link_load = {edge: 0 for edge in graph.edges()}
    for _, demand in traffic_df.iterrows():
        path = find_shortest_path(graph, demand['Source'], demand['Destination'])
        # Add demand to each link in the path
        for i in range(len(path)-1):
            link_load[(path[i], path[i+1])] += demand['Demand']
    return link_load

G = load_network(network_csv)
traffic_csv = '/Users/matthewkolakowski/Documents/traffic_data.csv'
traffic_df = load_traffic(traffic_csv)

# Model traffic load
link_load = model_traffic_load(G, traffic_df)
print("Link Load:")
for link, load in link_load.items():
    print(f"{link}: {load} units")

# Determine worst case failure
wcf = worst_case_failure(G, traffic_df)
print("\nWorst Case Failure:")
print(f"Link: {wcf['link']}")
print(f"Unroutable: {wcf['unroutable']}")
print(f"Link Loads during WCF:")

# Define model_traffic_load function
def model_traffic_load(graph, traffic_df):
    link_load = {edge: 0 for edge in graph.edges()}
    for _, demand in traffic_df.iterrows():
        path = find_shortest_path(graph, demand['Source'], demand['Destination'])
        # Add demand to each link in the path
        for i in range(len(path)-1):
            link_load[(path[i], path[i+1])] += demand['Demand']
    return link_load

# Load network and traffic

def load_traffic(csv_path):
    return pd.read_csv(csv_path)

traffic_csv = '/Users/matthewkolakowski/Documents/traffic_data.csv'

G = load_network(network_csv)
traffic_df = load_traffic(traffic_csv)

# Model traffic load
link_load = model_traffic_load(G, traffic_df)
print("Link Load:")
for link, load in link_load.items():
    print(f"{link}: {load} units")


# Determine worst case failure
wcf = worst_case_failure(G, traffic_df)

for link, load in wcf['over_capacity'].items():
    print(f"{link}: {load} units")

print("\nWorst Case Failure:")
print(f"Link: {wcf['link']}")
print(f"Unroutable: {wcf['unroutable']}")
print(f"Link Loads during WCF:")
def load_traffic(csv_path):
    return pd.read_csv(csv_path)

traffic_csv = '/Users/matthewkolakowski/Documents/traffic_data.csv'

# Load network and traffic
G = load_network(network_csv)
traffic_df = load_traffic(traffic_csv)

# Define model_traffic_load function
def model_traffic_load(graph, traffic_df):
    link_load = {edge: 0 for edge in graph.edges()}
    for _, demand in traffic_df.iterrows():
        path = find_shortest_path(graph, demand['Source'], demand['Destination'])
        # Add demand to each link in the path
        for i in range(len(path)-1):
            link_load[(path[i], path[i+1])] += demand['Demand']
    return link_load

# Model traffic load
link_load = model_traffic_load(G, traffic_df)
print("Link Load:")
for link, load in link_load.items():
    print(f"{link}: {load} units")

for link, load in wcf['over_capacity'].items():
    print(f"{link}: {load} units")

# Determine worst case failure
wcf = worst_case_failure(G, traffic_df)
print("\nWorst Case Failure:")
print(f"Link: {wcf['link']}")
print(f"Unroutable: {wcf['unroutable']}")
print(f"Link Loads during WCF:")
for link, load in wcf['over_capacity'].items():
    print(f"{link}: {load} units")