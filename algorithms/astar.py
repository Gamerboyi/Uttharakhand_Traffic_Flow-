import networkx as nx
import numpy as np
from math import sqrt
from datetime import datetime

def euclidean_distance(pos1, pos2):
    """Calculate Euclidean distance between two points"""
    return sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def get_seasonal_factor(edge_data, current_month=None):
    """Calculate seasonal impact on road conditions"""
    if current_month is None:
        current_month = datetime.now().month
    
    # Default seasonal factors
    seasonal_factor = 1.0
    
    # Monsoon season (June to September)
    if current_month in [6, 7, 8, 9]:
        if edge_data['type'] == 'mountain':
            seasonal_factor *= 1.8  # Significant impact on mountain roads
        elif edge_data['type'] == 'hill':
            seasonal_factor *= 1.4  # Moderate impact on hill roads
    
    # Winter season (December to February)
    elif current_month in [12, 1, 2]:
        if edge_data['type'] == 'mountain':
            seasonal_factor *= 1.6  # Snow and ice on mountain roads
        elif edge_data['type'] == 'hill':
            seasonal_factor *= 1.3  # Cold weather impact on hill roads
    
    # Tourist/Yatra season (April to September)
    if current_month in [4, 5, 6, 7, 8, 9]:
        if edge_data.get('name') in ['NH-7', 'NH-58', 'NH-109']:  # Main pilgrimage routes
            seasonal_factor *= 1.4  # Higher traffic on pilgrimage routes
    
    return seasonal_factor

def terrain_aware_heuristic(node1, node2, G):
    """
    A heuristic that considers both distance and terrain characteristics
    Specifically designed for Uttarakhand's mountainous terrain
    """
    # Get node data
    node1_data = G.nodes[node1]
    node2_data = G.nodes[node2]
    
    # Basic distance
    base_distance = euclidean_distance(node1_data['pos'], node2_data['pos'])
    
    # Elevation difference factor
    elevation_diff = abs(node1_data['elevation'] - node2_data['elevation'])
    elevation_factor = 1.0
    
    # Significant elevation changes
    if elevation_diff > 1000:  # More than 1000m difference
        elevation_factor = 2.0
    elif elevation_diff > 500:  # More than 500m difference
        elevation_factor = 1.5
    
    # Division crossing penalty (between Garhwal and Kumaon)
    division_factor = 1.2 if node1_data['division'] != node2_data['division'] else 1.0
    
    # Special destination types
    destination_factor = 1.0
    if node2_data['type'] in ['char_dham', 'pilgrimage']:
        destination_factor = 1.3  # Account for religious traffic
    elif node2_data['type'] == 'tourist':
        destination_factor = 1.2  # Account for tourist traffic
    
    return base_distance * elevation_factor * division_factor * destination_factor

def astar_algorithm(G, start, end, current_month=None):
    """
    A* pathfinding algorithm optimized for Uttarakhand's mountain terrain
    Considers elevation, road conditions, seasonal factors, and special routes
    """
    if start not in G or end not in G:
        return float('inf'), []
    
    # Initialize data structures
    frontier = {start: 0}  # Priority queue
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    while frontier:
        current = min(frontier, key=frontier.get)
        
        if current == end:
            break
        
        del frontier[current]
        
        for next_node in G[current]:
            edge_data = G[current][next_node]
            
            # Base cost calculation
            base_cost = edge_data['distance']
            
            # Traffic factor
            traffic_factor = 1 + edge_data['traffic']
            
            # Road type and condition factors
            road_factors = {
                'highway': {'excellent': 0.8, 'good': 0.9, 'moderate': 1.0},
                'hill': {'excellent': 0.9, 'good': 1.1, 'moderate': 1.3},
                'mountain': {'excellent': 1.0, 'good': 1.3, 'moderate': 1.6, 'challenging': 2.0}
            }
            
            road_type = edge_data['type']
            road_condition = edge_data['condition']
            road_factor = road_factors.get(road_type, {}).get(road_condition, 1.0)
            
            # Lane factor
            lane_factor = 1.5 if edge_data['lanes'] == 1 else 1.0
            
            # Seasonal impact
            seasonal_factor = get_seasonal_factor(edge_data, current_month)
            
            # Elevation consideration
            current_elevation = G.nodes[current]['elevation']
            next_elevation = G.nodes[next_node]['elevation']
            elevation_diff = abs(next_elevation - current_elevation)
            
            elevation_factor = 1.0
            if elevation_diff > 1000:
                elevation_factor = 2.0
            elif elevation_diff > 500:
                elevation_factor = 1.5
            elif elevation_diff > 200:
                elevation_factor = 1.2
            
            # Special route types
            route_factor = 1.0
            if G.nodes[next_node]['type'] == 'char_dham':
                route_factor = 1.4  # Char Dham routes
            elif G.nodes[next_node]['type'] == 'pilgrimage':
                route_factor = 1.2  # Other pilgrimage sites
            elif G.nodes[next_node]['type'] == 'tourist':
                route_factor = 1.1  # Tourist destinations
            
            # Calculate total cost
            new_cost = (cost_so_far[current] + 
                       base_cost * traffic_factor * road_factor * 
                       lane_factor * seasonal_factor * elevation_factor * 
                       route_factor)
            
            if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost
                priority = new_cost + terrain_aware_heuristic(next_node, end, G)
                frontier[next_node] = priority
                came_from[next_node] = current
    
    # Reconstruct path
    if end not in came_from:
        return float('inf'), []
    
    path = []
    current = end
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    
    return cost_so_far[end], path
