import json
import networkx as nx

def test_realistic_data():
    """Test the realistic data structure"""
    try:
        # Load the realistic data
        with open('data/uttarakhand_realistic_data.json', 'r') as f:
            data = json.load(f)
        
        print("✅ Data loaded successfully")
        print(f"📊 Number of intersections: {len(data['intersections'])}")
        print(f"🛣️ Number of roads: {len(data['roads'])}")
        
        # Check a few sample nodes
        sample_nodes = list(data['intersections'].keys())[:5]
        for node_id in sample_nodes:
            node_data = data['intersections'][node_id]
            print(f"📍 {node_id}: {node_data['name']} - pos: {node_data['pos']}")
        
        # Create graph and test
        G = nx.DiGraph()
        
        # Add nodes
        for node_id, node_data in data["intersections"].items():
            node_attrs = {
                'pos': node_data["pos"],
                'name': node_data["name"],
                'type': node_data.get("type", "city"),
                'division': node_data.get("division", "Garhwal"),
                'elevation': node_data.get("elevation", 1000)
            }
            G.add_node(node_id, **node_attrs)
        
        # Add edges
        for road in data["roads"]:
            weight = road["distance"] * (1 + road["traffic"] * 2)
            edge_attrs = {
                'weight': weight,
                'distance': road["distance"],
                'traffic': road["traffic"],
                'name': road["name"],
                'type': road.get("type", "highway"),
                'condition': road.get("condition", "good"),
                'lanes': road.get("lanes", 2)
            }
            G.add_edge(road["from"], road["to"], **edge_attrs)
            G.add_edge(road["to"], road["from"], **edge_attrs)
        
        print(f"✅ Graph created successfully")
        print(f"📊 Graph nodes: {G.number_of_nodes()}")
        print(f"🛣️ Graph edges: {G.number_of_edges()}")
        
        # Test NetworkX functions
        try:
            largest_scc = max(nx.strongly_connected_components(G), key=len)
            print(f"✅ Strongly connected components: {len(largest_scc)} nodes in largest component")
        except Exception as e:
            print(f"❌ Error with strongly connected components: {e}")
        
        # Test centrality calculations
        try:
            degree_centrality = nx.degree_centrality(G)
            print(f"✅ Degree centrality calculated for {len(degree_centrality)} nodes")
        except Exception as e:
            print(f"❌ Error with degree centrality: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_realistic_data() 