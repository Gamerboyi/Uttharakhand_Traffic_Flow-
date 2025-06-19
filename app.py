import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time, json, random, os, io, base64
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
from matplotlib import cm
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation

# Import algorithms from separate modules
from algorithms.dijkstra import dijkstra_algorithm
from algorithms.astar import astar_algorithm
from algorithms.bellman_ford import bellman_ford_algorithm
from algorithms.traffic_prediction import get_future_traffic_predictions, get_road_specific_prediction
from algorithms.weather_impact import WeatherImpact

# Page configuration and simplified CSS
st.set_page_config(page_title="Uttarakhand Traffic Flow Optimizer", page_icon="🏔️", layout="wide")

# Enhanced CSS with modern branded design
CUSTOM_CSS = """
<style>
    /* Modern Branded Color Palette */
    :root {
        --primary-green: #2E7D32;      /* Go - Success */
        --primary-red: #D32F2F;        /* Stop - Danger */
        --primary-amber: #FF8F00;      /* Warning - Caution */
        --primary-blue: #1565C0;       /* Info - Navigation */
        --primary-purple: #7B1FA2;     /* Premium - Advanced */
        
        --light-green: #E8F5E8;
        --light-red: #FFEBEE;
        --light-amber: #FFF3E0;
        --light-blue: #E3F2FD;
        --light-purple: #F3E5F5;
        
        --background-color: #FAFAFA;
        --card-background: #FFFFFF;
        --text-primary: #212121;
        --text-secondary: #757575;
        --text-muted: #9E9E9E;
        
        --card-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        --card-shadow-hover: 0 4px 16px rgba(0, 0, 0, 0.15);
        --border-radius: 12px;
        --border-radius-small: 8px;
    }

    /* Global Styles */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: var(--text-primary);
    }

    /* Modern Headers */
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(135deg, var(--primary-green) 0%, var(--primary-blue) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1.5rem;
        position: relative;
    }

    .main-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-green), var(--primary-blue));
        border-radius: 2px;
    }

    .sub-header {
        font-size: 1.8rem;
        color: var(--text-primary);
        font-weight: 600;
        margin-bottom: 1.5rem;
        position: relative;
        padding-left: 1rem;
    }

    .sub-header::before {
        content: '';
        position: absolute;
        left: 0;
        top: 50%;
        transform: translateY(-50%);
        width: 4px;
        height: 60%;
        background: var(--primary-green);
        border-radius: 2px;
    }

    /* Modern Card System */
    .modern-card {
        background: var(--card-background);
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }

    .modern-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-green), var(--primary-blue));
    }

    .modern-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--card-shadow-hover);
    }

    .metric-card {
        background: var(--card-background);
        border-radius: var(--border-radius-small);
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: var(--card-shadow);
        border-left: 4px solid var(--primary-green);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateX(4px);
        box-shadow: var(--card-shadow-hover);
    }

    /* Enhanced Traffic Badges */
    .traffic-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .traffic-badge:hover {
        transform: scale(1.05);
    }

    .traffic-low {
        background: linear-gradient(135deg, var(--light-green), #C8E6C9);
        color: var(--primary-green);
        border: 1px solid #A5D6A7;
    }

    .traffic-medium {
        background: linear-gradient(135deg, var(--light-amber), #FFE0B2);
        color: var(--primary-amber);
        border: 1px solid #FFCC80;
    }

    .traffic-high {
        background: linear-gradient(135deg, var(--light-red), #FFCDD2);
        color: var(--primary-red);
        border: 1px solid #EF9A9A;
    }

    /* Modern Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-green), #388E3C);
        color: white;
        border: none;
        border-radius: var(--border-radius-small);
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.3);
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #388E3C, var(--primary-green));
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(46, 125, 50, 0.4);
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    /* Enhanced Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: var(--card-background);
        padding: 12px;
        border-radius: var(--border-radius);
        box-shadow: var(--card-shadow);
        border: 1px solid rgba(0, 0, 0, 0.05);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        background: transparent;
        border-radius: var(--border-radius-small);
        padding: 12px 20px;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid transparent;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--light-green);
        border-color: var(--primary-green);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-green), #388E3C) !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.3);
        transform: translateY(-1px);
    }

    /* Enhanced Metrics */
    .metric-container {
        background: var(--card-background);
        padding: 1.2rem;
        border-radius: var(--border-radius-small);
        box-shadow: var(--card-shadow);
        text-align: center;
        border: 1px solid rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }

    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: var(--card-shadow-hover);
    }

    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-green), var(--primary-blue));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
    }

    .metric-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Loading Animation */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }

    .loading-spinner::after {
        content: '';
        width: 40px;
        height: 40px;
        border: 4px solid var(--light-green);
        border-top: 4px solid var(--primary-green);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Enhanced Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }

    .tooltip .tooltip-text {
        visibility: hidden;
        background: rgba(33, 33, 33, 0.95);
        color: white;
        text-align: center;
        padding: 8px 12px;
        border-radius: var(--border-radius-small);
        position: absolute;
        z-index: 1000;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.85rem;
        white-space: nowrap;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        opacity: 0;
        transition: opacity 0.3s;
    }

    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

    /* Navigation Sidebar */
    .sidebar-nav {
        background: var(--card-background);
        border-radius: var(--border-radius);
        padding: 1rem;
        box-shadow: var(--card-shadow);
        margin-bottom: 1rem;
    }

    .nav-item {
        padding: 0.8rem 1rem;
        margin: 0.3rem 0;
        border-radius: var(--border-radius-small);
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid transparent;
    }

    .nav-item:hover {
        background: var(--light-green);
        border-color: var(--primary-green);
    }

    .nav-item.active {
        background: linear-gradient(135deg, var(--primary-green), #388E3C);
        color: white;
        box-shadow: 0 2px 8px rgba(46, 125, 50, 0.3);
    }

    /* Route Summary Panel */
    .route-summary {
        background: linear-gradient(135deg, var(--light-blue), #E1F5FE);
        border: 1px solid #B3E5FC;
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .route-step {
        background: var(--card-background);
        border-radius: var(--border-radius-small);
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid var(--primary-blue);
        transition: all 0.3s ease;
    }

    .route-step:hover {
        transform: translateX(4px);
        box-shadow: var(--card-shadow);
    }

    /* Dark Mode Toggle */
    .dark-mode-toggle {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1000;
        background: var(--card-background);
        border-radius: 50%;
        width: 50px;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: var(--card-shadow);
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .dark-mode-toggle:hover {
        transform: scale(1.1);
        box-shadow: var(--card-shadow-hover);
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        
        .modern-card {
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
    }

    /* Animation Classes */
    .fade-in {
        animation: fadeIn 0.6s ease-in-out;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .slide-in {
        animation: slideIn 0.5s ease-out;
    }

    @keyframes slideIn {
        from { transform: translateX(-100%); }
        to { transform: translateX(0); }
    }

    /* Enhanced Form Elements */
    .stSelectbox > div > div {
        border-radius: var(--border-radius-small);
        border: 1px solid rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }

    .stSelectbox > div > div:hover {
        border-color: var(--primary-green);
        box-shadow: 0 0 0 2px rgba(46, 125, 50, 0.1);
    }

    .stCheckbox > div {
        border-radius: var(--border-radius-small);
    }

    /* Progress Bars */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-green), #388E3C);
        border-radius: 10px;
    }

    /* Dataframe Styling */
    .stDataFrame {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--card-shadow);
    }
</style>
"""

# Data loading and graph creation
@st.cache_data
def load_sample_data():
    """Load realistic Uttarakhand traffic data"""
    try:
        with open('data/uttarakhand_realistic_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Required data file not found: data/uttarakhand_realistic_data.json. Please ensure this file exists in the data/ directory.")
        st.stop()

def create_graph_from_data(data, consider_traffic=True):
    """Create a NetworkX graph from the data"""
    G = nx.DiGraph()
    
    for node_id, node_data in data["intersections"].items():
        # Add node with all available attributes
        node_attrs = {
            'pos': node_data["pos"],
            'name': node_data["name"],
            'type': node_data.get("type", "city"),  # Default to city if not specified
            'division': node_data.get("division", "Garhwal"),  # Default to Garhwal if not specified
            'elevation': node_data.get("elevation", 1000)  # Default elevation if not specified
        }
        G.add_node(node_id, **node_attrs)
    
    for road in data["roads"]:
        weight = road["distance"] * (1 + road["traffic"] * 2) if consider_traffic else road["distance"]
        # Add edge with all available attributes
        edge_attrs = {
            'weight': weight,
            'distance': road["distance"],
            'traffic': road["traffic"],
            'name': road["name"],
            'color': 'blue',
            'width': 2,
            'type': road.get("type", "highway"),  # Default to highway if not specified
            'condition': road.get("condition", "good"),  # Default to good if not specified
            'lanes': road.get("lanes", 2)  # Default to 2 lanes if not specified
        }
        # Add edges in both directions
        G.add_edge(road["from"], road["to"], **edge_attrs)
        # Add reverse direction with same attributes
        G.add_edge(road["to"], road["from"], **edge_attrs)
    
    return G

def visualize_graph(G, path=None, title="Uttarakhand Traffic Network", step=None):
    """Create a network visualization of the traffic graph, optionally animating the route step-by-step."""
    plt.figure(figsize=(12, 8))
    pos = nx.get_node_attributes(G, 'pos')
    node_types = nx.get_node_attributes(G, 'type')
    node_colors = {
        'capital': '#2E7D32',
        'char_dham': '#C62828',
        'pilgrimage': '#AD1457',
        'tourist': '#1565C0',
        'town': '#F57C00',
        'city': '#6A1B9A'
    }
    # Draw all nodes lightly
    for node_type in set(node_types.values()):
        node_list = [node for node in G.nodes() if node_types.get(node) == node_type]
        if node_list:
            nx.draw_networkx_nodes(G, pos, nodelist=node_list, node_color=node_colors.get(node_type, '#666666'), node_size=700, alpha=0.2)
    # Draw only the route if provided
    if path and len(path) > 1:
        if step is None:
            step = len(path)
        path = path[:step]
        path_edges = list(zip(path[:-1], path[1:]))
        for i, (u, v) in enumerate(path_edges):
            color = plt.cm.viridis(i / max(1, len(path_edges)-1))
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], edge_color=[color], width=4, alpha=0.9)
        # Highlight path nodes
        for i, node in enumerate(path):
            if i == 0:
                nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color='#4CAF50', node_size=1000, alpha=1.0)
            elif i == len(path) - 1:
                nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color='#F44336', node_size=1000, alpha=1.0)
            else:
                nx.draw_networkx_nodes(G, pos, nodelist=[node], node_color='#2196F3', node_size=800, alpha=0.9)
    # Add labels
    labels = {node: G.nodes[node].get('name', node) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    plt.title(title)
    plt.axis('off')
    return plt

def get_traffic_badge(traffic_level):
    """Return HTML for a traffic badge based on level"""
    level = int(traffic_level * 100)
    if level < 30:
        return f'<span class="traffic-badge traffic-low">{level}%</span>'
    elif level < 70:
        return f'<span class="traffic-badge traffic-medium">{level}%</span>'
    else:
        return f'<span class="traffic-badge traffic-high">{level}%</span>'

def simulate_traffic_change():
    """Simulate traffic changes over time with more realistic variations"""
    data = load_sample_data()
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    # Get future predictions
    predictions = get_future_traffic_predictions(hours_ahead=3)
    
    # Initialize weather impact
    weather_system = WeatherImpact()
    current_weather = weather_system.get_current_weather('medium')
    
    # Define realistic traffic patterns based on road types and time
    traffic_patterns = {
        'highway': {
            'peak_hours': (0.6, 0.9),    # 7-9 AM and 5-7 PM
            'off_peak': (0.3, 0.6),      # Other hours
            'weekend': (0.4, 0.7)         # Weekend traffic
        },
        'hill': {
            'peak_hours': (0.4, 0.7),
            'off_peak': (0.2, 0.4),
            'weekend': (0.3, 0.6)
        },
        'mountain': {
            'peak_hours': (0.3, 0.6),
            'off_peak': (0.1, 0.3),
            'weekend': (0.2, 0.5)
        }
    }
    
    # Add random variations to traffic
    def get_traffic_variation(base_traffic, road_type, hour, is_weekend):
        pattern = traffic_patterns.get(road_type, traffic_patterns['highway'])
        
        # Determine if current hour is peak hour
        is_peak = (7 <= hour <= 9) or (17 <= hour <= 19)
        
        # Get base range
        if is_weekend:
            min_traffic, max_traffic = pattern['weekend']
        elif is_peak:
            min_traffic, max_traffic = pattern['peak_hours']
        else:
            min_traffic, max_traffic = pattern['off_peak']
        
        # Add random variation (±10%)
        variation = random.uniform(-0.1, 0.1)
        traffic = base_traffic + variation
        
        # Ensure traffic stays within bounds
        return min(max_traffic, max(min_traffic, traffic))
    
    for road in data["roads"]:
        # Get base traffic prediction
        base_traffic = predictions[0][1]
        
        # Get road type and calculate traffic
        road_type = road.get("type", "highway")
        is_weekend = current_day >= 5  # Saturday or Sunday
        
        # Calculate traffic with variations
        road_traffic = get_traffic_variation(
            base_traffic,
            road_type,
            current_hour,
            is_weekend
        )
        
        # Apply weather impact
        road["traffic"], _ = weather_system.apply_weather_impact(
            road_traffic,
            elevation=1500,
            route_type=road_type
        )
        
        # Ensure final traffic value is between 0 and 1
        road["traffic"] = min(1.0, max(0.0, road["traffic"]))
        
        # Add road condition factor
        road["condition"] = random.choice(["excellent", "good", "fair", "poor"])
        
        # Add lane information
        road["lanes"] = random.choice([2, 3, 4]) if road_type == "highway" else 2
        
        # Add speed limit based on road type
        speed_limits = {
            "highway": (80, 100),
            "hill": (40, 60),
            "mountain": (30, 50)
        }
        road["speed_limit"] = random.randint(*speed_limits.get(road_type, (40, 60)))
    
    return data, predictions, current_weather

def create_map_visualization(G, path=None, map_type="folium"):
    """Create an interactive map visualization"""
    # Calculate center point
    lats = [data['pos'][0] for node, data in G.nodes(data=True)]
    lons = [data['pos'][1] for node, data in G.nodes(data=True)]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)
    
    if map_type == "folium":
        # Create a map centered on Uttarakhand
        m = folium.Map(location=[center_lat, center_lon], 
                      zoom_start=8,
                      tiles='cartodbpositron')
        
        # Add nodes (cities)
        for node, data in G.nodes(data=True):
            color = {
                'capital': 'darkgreen',
                'char_dham': 'red',
                'pilgrimage': 'purple',
                'tourist': 'blue',
                'town': 'orange',
                'city': 'darkpurple'
            }.get(data['type'], 'gray')
            
            popup_html = f"""
            <div style='font-family: Arial; font-size: 14px;'>
                <h4>{data['name']}</h4>
                <b>Elevation:</b> {data['elevation']}m<br>
                <b>Type:</b> {data['type']}<br>
                <b>Division:</b> {data['division']}
            </div>
            """
            
            folium.CircleMarker(
                location=data['pos'],
                radius=8,
                popup=folium.Popup(popup_html, max_width=300),
                color=color,
                fill=True,
                fillOpacity=0.7
            ).add_to(m)
        
        # Add edges (roads)
        for u, v, data in G.edges(data=True):
            points = [G.nodes[u]['pos'], G.nodes[v]['pos']]
            
            # Color based on traffic
            if data['traffic'] < 0.3:
                color = 'green'
            elif data['traffic'] < 0.6:
                color = 'orange'
            else:
                color = 'red'
            
            # Road info popup
            popup_html = f"""
            <div style='font-family: Arial; font-size: 14px;'>
                <h4>{data['name']}</h4>
                <b>Type:</b> {data['type']}<br>
                <b>Condition:</b> {data['condition']}<br>
                <b>Lanes:</b> {data['lanes']}<br>
                <b>Distance:</b> {data['distance']}km<br>
                <b>Traffic Level:</b> {data['traffic']:.2f}
            </div>
            """
            
            folium.PolyLine(
                points,
                weight=2 + data['traffic'] * 3,
                color=color,
                opacity=0.8,
                popup=folium.Popup(popup_html, max_width=300)
            ).add_to(m)
        
        return m
    
    elif map_type == "plotly":
        fig = go.Figure()
        
        # Add edges (roads)
        for u, v, data in G.edges(data=True):
            start = G.nodes[u]['pos']
            end = G.nodes[v]['pos']
            
            # Color based on traffic
            if data['traffic'] < 0.3:
                color = 'green'
            elif data['traffic'] < 0.6:
                color = 'orange'
            else:
                color = 'red'
            
            fig.add_trace(go.Scattermapbox(
                lon=[start[1], end[1]],
                lat=[start[0], end[0]],
                mode='lines',
                line=dict(width=2 + data['traffic'] * 3, color=color),
                hoverinfo='text',
                text=f"{data['name']}<br>Traffic: {data['traffic']:.2f}",
                showlegend=False
            ))
        
        # Add nodes (cities)
        for node_type in set(nx.get_node_attributes(G, 'type').values()):
            node_list = [node for node, data in G.nodes(data=True) if data['type'] == node_type]
            if not node_list:
                continue
                
            lats = [G.nodes[node]['pos'][0] for node in node_list]
            lons = [G.nodes[node]['pos'][1] for node in node_list]
            names = [G.nodes[node]['name'] for node in node_list]
            elevations = [G.nodes[node]['elevation'] for node in node_list]
            
            fig.add_trace(go.Scattermapbox(
                lon=lons,
                lat=lats,
                mode='markers',
                marker=dict(
                    size=10,
                    color={
                        'capital': '#2E7D32',
                        'char_dham': '#C62828',
                        'pilgrimage': '#AD1457',
                        'tourist': '#1565C0',
                        'town': '#F57C00',
                        'city': '#6A1B9A'
                    }.get(node_type, '#666666')
                ),
                text=[f"{name}<br>Elevation: {elev}m<br>Type: {node_type}" 
                      for name, elev in zip(names, elevations)],
                name=node_type.title(),
                hoverinfo='text'
            ))
        
        fig.update_layout(
            mapbox_style="carto-positron",
            mapbox=dict(
                center=dict(lat=center_lat, lon=center_lon),
                zoom=7
            ),
            title='Uttarakhand Traffic Network',
            showlegend=True,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        return fig

def create_traffic_prediction_plot(predictions):
    """Create a traffic prediction plot"""
    times = [pred[0].strftime("%H:%M") for pred in predictions]
    traffic_levels = [pred[1] for pred in predictions]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=times,
        y=[t * 100 for t in traffic_levels],
        mode='lines+markers',
        name='Predicted Traffic Level',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=10)
    ))
    
    fig.update_layout(
        title="Traffic Predictions for Next 3 Hours",
        xaxis_title="Time",
        yaxis_title="Traffic Level (%)",
        hovermode='x unified',
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    return fig

def create_network_analysis_plot(G):
    """Create network analysis visualizations"""
    # Calculate centrality metrics
    degree_cent = nx.degree_centrality(G)
    betweenness_cent = nx.betweenness_centrality(G)
    closeness_cent = nx.closeness_centrality(G)
    
    # Create a DataFrame for visualization
    metrics_df = pd.DataFrame({
        'Node': list(G.nodes()),
        'Degree Centrality': list(degree_cent.values()),
        'Betweenness Centrality': list(betweenness_cent.values()),
        'Closeness Centrality': list(closeness_cent.values())
    })
    
    return metrics_df

def get_network_metrics(G):
    """Calculate comprehensive network metrics for directed graphs"""
    # Basic metrics
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    
    # Calculate density
    density = nx.density(G)
    
    # For directed graphs, use strongly connected components
    try:
        largest_scc = max(nx.strongly_connected_components(G), key=len)
        subgraph = G.subgraph(largest_scc)
        
        if len(largest_scc) > 1:
            avg_path_length = nx.average_shortest_path_length(subgraph)
        else:
            avg_path_length = 0
    except (nx.NetworkXError, ValueError):
        # Fallback if strongly connected components calculation fails
        avg_path_length = 0
        largest_scc = set()
    
    # Calculate connectivity metrics
    try:
        num_components = nx.number_strongly_connected_components(G)
        connectivity = len(largest_scc) / num_nodes if num_nodes > 0 else 0
    except nx.NetworkXError:
        num_components = 1
        connectivity = 1.0
    
    return {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'density': density,
        'avg_path_length': avg_path_length,
        'connectivity': connectivity,
        'num_scc': num_components
    }

def create_loading_animation():
    """Create a loading animation component"""
    return st.markdown("""
        <div class="loading-spinner">
            <div class="spinner"></div>
        </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, description=None, icon=None):
    """Create a modern metric card with enhanced styling"""
    icon_html = f'<div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>' if icon else ''
    description_html = f'<div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;">{description}</div>' if description else ''
    
    return f"""
    <div class="metric-container">
        {icon_html}
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {description_html}
    </div>
    """

def calculate_traffic_distribution(data):
    """Calculate traffic distribution across roads"""
    traffic_levels = {"Low": 0, "Medium": 0, "High": 0}
    total_roads = len(data["roads"])
    
    for road in data["roads"]:
        traffic = road["traffic"]
        if traffic < 0.3:
            traffic_levels["Low"] += 1
        elif traffic < 0.7:
            traffic_levels["Medium"] += 1
        else:
            traffic_levels["High"] += 1
    
    return {
        "levels": traffic_levels,
        "total": total_roads,
        "clear_roads_percentage": (traffic_levels["Low"] / total_roads * 100) if total_roads > 0 else 0
    }

# --- LOGIN PAGE LOGIC ---
def login_page():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.markdown(
        '<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 80vh;">',
        unsafe_allow_html=True
    )
    st.image("https://img.icons8.com/color/96/traffic-jam.png", width=96)
    st.markdown('<h1 class="main-header" style="margin-bottom: 0.5rem;">Login to Traffic Optimizer</h1>', unsafe_allow_html=True)
    st.markdown('<div class="modern-card" style="max-width: 350px; margin: 2rem auto;">', unsafe_allow_html=True)
    username = st.text_input("Username", key="login_username")
    login_btn = st.button("🔓 Login", use_container_width=True)
    if 'login_error' not in st.session_state:
        st.session_state.login_error = False
    if login_btn:
        if username.strip() != '':
            st.session_state.logged_in = True
            st.session_state.login_error = False
            st.rerun()
        else:
            st.session_state.login_error = True
    if st.session_state.login_error:
        st.error("Please enter a username to login.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- WRAP MAIN WITH LOGIN CHECK ---
def main_with_login():
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login_page()
        return
    # Add logout button in sidebar
    with st.sidebar:
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
    main()

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Dark mode toggle
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False
    
    # Dark mode toggle button
    st.markdown(f"""
        <div class="dark-mode-toggle" onclick="document.dispatchEvent(new CustomEvent('toggleDarkMode'))">
            {'🌙' if not st.session_state.dark_mode else '☀️'}
        </div>
        <script>
            document.addEventListener('toggleDarkMode', function() {{
                // This would toggle dark mode in a real implementation
                console.log('Dark mode toggled');
            }});
        </script>
    """, unsafe_allow_html=True)
    
    # Animated header with enhanced styling
    st.markdown(
        '<div class="fade-in"><h1 class="main-header">🚦 Traffic Flow Optimizer</h1></div>',
        unsafe_allow_html=True
    )
    
    # Enhanced sidebar with modern navigation
    with st.sidebar:
        st.markdown('<div class="sidebar-nav">', unsafe_allow_html=True)
        st.markdown('<h3 style="margin-bottom: 1rem; color: var(--primary-green);">🧭 Navigation</h3>', unsafe_allow_html=True)
        # Time indicator with enhanced styling
        current_time = datetime.now().strftime("%H:%M")
        current_hour = datetime.now().hour
        time_icon = "🌅" if 5 <= current_hour < 12 else "☀️" if 12 <= current_hour < 17 else "🌆" if 17 <= current_hour < 21 else "🌙"
        time_greeting = "Good Morning" if 5 <= current_hour < 12 else "Good Afternoon" if 12 <= current_hour < 17 else "Good Evening" if 17 <= current_hour < 21 else "Good Night"
        st.markdown(f"""
<div class="modern-card" style="margin-bottom: 1rem;">
    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
        <div style="font-size: 2rem; margin-right: 0.8rem;">{time_icon}</div>
        <div>
            <div style="font-size: 0.9rem; color: var(--text-secondary);">Current Time</div>
            <div style="font-size: 1.8rem; font-weight: bold; color: var(--primary-green);">{current_time}</div>
        </div>
    </div>
    <div style="font-size: 1rem; color: var(--text-primary); font-weight: 500;">{time_greeting}</div>
    </div>
    """, unsafe_allow_html=True)
        # Quick stats
        st.markdown("""
            <div class="modern-card">
                <h4 style="margin-bottom: 1rem; color: var(--primary-blue);">📊 Quick Stats</h4>
                <div style="display: grid; gap: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: var(--text-secondary);">Active Routes:</span>
                        <span style="font-weight: bold; color: var(--primary-green);">24</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: var(--text-secondary);">Avg. Traffic:</span>
                        <span style="font-weight: bold; color: var(--primary-amber);">Medium</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: var(--text-secondary);">Weather:</span>
                        <span style="font-weight: bold; color: var(--primary-blue);">Clear</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    # Main navigation with enhanced tabs
    tabs = st.tabs([
        "🧠 Route Optimizer",
        "🔮 Traffic Predictions", 
        "📊 Network Analysis",
        "ℹ️ About"
    ])

    # Route Optimizer Tab with enhanced layout
    with tabs[0]:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">🧠 Traffic Route Optimization</h2>', unsafe_allow_html=True)
        
        # Responsive layout with columns
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: var(--primary-green); margin-bottom: 1.5rem;">📍 Route Configuration</h3>', unsafe_allow_html=True)
            
            # Enhanced form elements
            data = load_sample_data()
            consider_traffic = st.checkbox(
                "🚦 Consider Traffic Conditions",
                value=True,
                help="Enable real-time traffic analysis for optimal routing"
            )
            
            G = create_graph_from_data(data, consider_traffic)
            
            # Source and destination selection with better UX
            nodes = list(data["intersections"].keys())
            node_names = [f"{data['intersections'][node]['name']} ({node})" for node in nodes]
            
            st.markdown("### 🎯 Select Your Route")
            
            # Enhanced source selection
            source = st.selectbox(
                "🚀 Starting Point",
                node_names,
                index=0,
                help="Choose your departure location"
            )
            
            # Enhanced destination selection
            destination = st.selectbox(
                "🎯 Destination",
                node_names,
                index=len(node_names)-1,
                help="Choose your arrival location"
            )
            
            # Algorithm selection with enhanced tooltips
            algorithm = st.selectbox(
                "🧮 Routing Algorithm",
                ["Dijkstra's Algorithm", "A* Algorithm", "Bellman-Ford Algorithm"],
                help="Select the optimal pathfinding algorithm for your needs"
            )
            
            # Enhanced button with icon and loading state
            if st.button("🧠 Calculate Optimal Route", help="Find the best route considering all factors"):
                with st.spinner("🔄 Analyzing traffic patterns and calculating optimal route..."):
                    start_time = time.time()
                    
                    # Run selected algorithm
                    if algorithm == "Dijkstra's Algorithm":
                        distance, path = dijkstra_algorithm(G, source.split("(")[1].split(")")[0].strip(), destination.split("(")[1].split(")")[0].strip())
                    elif algorithm == "A* Algorithm":
                        distance, path = astar_algorithm(G, source.split("(")[1].split(")")[0].strip(), destination.split("(")[1].split(")")[0].strip())
                    else:  # Bellman-Ford
                        distance, path = bellman_ford_algorithm(G, source.split("(")[1].split(")")[0].strip(), destination.split("(")[1].split(")")[0].strip())
                    
                    computation_time = time.time() - start_time
                    
                    if path:
                        # Calculate enhanced metrics
                        total_distance = sum(G[path[i]][path[i+1]]['distance'] for i in range(len(path)-1))
                        total_traffic = sum(G[path[i]][path[i+1]]['traffic'] for i in range(len(path)-1))
                        avg_traffic = total_traffic / (len(path)-1)
                        avg_speed = 60 * (1 - avg_traffic * 0.7)  # km/h
                        travel_time = (total_distance / avg_speed) * 60  # minutes
                        
                        # Enhanced route summary panel
                        st.markdown('<div class="route-summary fade-in">', unsafe_allow_html=True)
                        st.markdown("### 🎯 Route Summary")
                        
                        # Enhanced metrics display with modern cards
                        col1a, col2a, col3a, col4a = st.columns(4)
                        with col1a:
                            st.markdown(
                                create_metric_card(
                                    "Distance",
                                    f"{total_distance:.1f} km",
                                    "Total route distance",
                                    "📏"
                                ),
                                unsafe_allow_html=True
                            )
                        
                        with col2a:
                            st.markdown(
                                create_metric_card(
                                    "Traffic Level",
                                    get_traffic_badge(avg_traffic),
                                    "Average traffic along route",
                                    "🚦"
                                ),
                                unsafe_allow_html=True
                            )
                        
                        with col3a:
                            st.markdown(
                                create_metric_card(
                                    "Travel Time",
                                    f"{travel_time:.0f} min",
                                    "Estimated travel duration",
                                    "⏱️"
                                ),
                                unsafe_allow_html=True
                            )
                        
                        with col4a:
                            st.markdown(
                                create_metric_card(
                                    "Efficiency",
                                    f"{computation_time*1000:.1f} ms",
                                    "Algorithm computation time",
                                    "⚡"
                                ),
                                unsafe_allow_html=True
                            )
                        
                        # Enhanced turn-by-turn directions with modern styling
                        st.markdown("### 🗺️ Turn-by-Turn Directions")
                        for i, (start, end) in enumerate(zip(path[:-1], path[1:]), 1):
                            from_city = G.nodes[start]['name']
                            to_city = G.nodes[end]['name']
                            road_name = G[start][end]['name']
                            distance = G[start][end]['distance']
                            traffic = G[start][end]['traffic']
                            
                            st.markdown(f"""
                            <div class="route-step">
                                <div style="display: flex; align-items: center;">
                                    <div style="font-size: 1.5rem; margin-right: 1rem; color: var(--primary-blue);">#{i}</div>
                                    <div style="flex: 1;">
                                        <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 0.3rem;">
                                            Take <span style="color: var(--primary-green);">{road_name}</span>
                                        </div>
                                        <div style="font-size: 0.9rem; color: var(--text-secondary);">
                                            From {from_city} to {to_city} • {distance} km {get_traffic_badge(traffic)}
                                        </div>
                                    </div>
                                    <div style="font-size: 1.2rem; color: var(--primary-blue);">→</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ No optimal route found between selected locations")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: var(--primary-blue); margin-bottom: 1.5rem;">🗺️ Network Visualization</h3>', unsafe_allow_html=True)
            
            # Enhanced visualization tabs
            viz_tabs = st.tabs(["🕸️ Network Graph", "🌍 Interactive Map"])
            
            with viz_tabs[0]:
                if 'path' in locals() and path:
                    step = st.slider('Step through route', 2, len(path), len(path), help='Move slider to animate the route')
                    fig = visualize_graph(G, path=path, step=step)
                else:
                    fig = visualize_graph(G)
                st.pyplot(fig)
            
            with viz_tabs[1]:
                m = create_map_visualization(G, path=path if 'path' in locals() else None, map_type="folium")
                st_folium(m, width=800)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
        st.markdown('</div>', unsafe_allow_html=True)

    # Traffic Predictions Tab with enhanced design
    with tabs[1]:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">🔮 Traffic & Weather Intelligence</h2>', unsafe_allow_html=True)
        
        # Get current traffic data and predictions
        data, predictions, weather = simulate_traffic_change()
        
        # Enhanced layout with better proportions
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Enhanced weather card with modern design
            st.markdown(
                f"""<div class="modern-card">
                    <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                        <div style="font-size: 4rem; margin-right: 1.5rem;">{weather['icon']}</div>
                        <div>
                            <h3 style="margin: 0; color: var(--primary-blue); font-size: 1.5rem;">Current Weather Conditions</h3>
                            <p style="margin: 0.3rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">{weather['condition']}</p>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                        <div class="metric-container">
                            <div class="metric-label">Weather Impact</div>
                            <div class="metric-value" style="font-size: 1.8rem;">{weather['impact']}x</div>
                            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;">Traffic multiplier</div>
                        </div>
                        <div class="metric-container">
                            <div class="metric-label">Traffic Effect</div>
                            <div style="color: var(--text-primary); font-size: 1rem; font-weight: 500;">{weather['description']}</div>
                            <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;">Current conditions</div>
                        </div>
                    </div>
                </div>""",
                unsafe_allow_html=True
            )
            
            # Enhanced prediction plot with modern styling
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: var(--primary-purple); margin-bottom: 1.5rem;">📈 Traffic Predictions (Next 3 Hours)</h3>', unsafe_allow_html=True)
            st.plotly_chart(create_traffic_prediction_plot(predictions), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Enhanced busy routes display with modern cards
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<h3 style="color: var(--primary-amber); margin-bottom: 1.5rem;">🚗 Busiest Routes Now</h3>', unsafe_allow_html=True)
            
            busy_roads = sorted(data["roads"], key=lambda x: x["traffic"], reverse=True)[:5]
            
            for i, road in enumerate(busy_roads, 1):
                traffic_level = road["traffic"]
                traffic_class = "high" if traffic_level > 0.7 else "medium" if traffic_level > 0.3 else "low"
                
                st.markdown(
                    f"""<div class="metric-card" style="margin-bottom: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <div style="display: flex; align-items: center;">
                                <div style="font-size: 1.2rem; margin-right: 0.8rem; color: var(--primary-blue);">#{i}</div>
                                <div>
                                    <h4 style="margin: 0; color: var(--text-primary); font-size: 1rem;">{road["name"]}</h4>
                                    <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.2rem;">
                                        Traffic Level: {get_traffic_badge(road["traffic"])}
                                    </div>
                                </div>
                            </div>
                            <div style="font-size: 1.8rem;">{weather["icon"]}</div>
                        </div>
                        <div style="margin-top: 0.8rem; font-size: 0.85rem; color: var(--text-secondary); padding: 0.5rem; background: var(--light-blue); border-radius: var(--border-radius-small);">
                            🌦️ Weather Impact: {weather["description"]}
                        </div>
                    </div>""",
                    unsafe_allow_html=True
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced road-specific analysis with modern design
        st.markdown('<h3 class="sub-header">🛣️ Road-Specific Analysis</h3>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<h4 style="color: var(--primary-green); margin-bottom: 1.5rem;">📊 Detailed Road Metrics</h4>', unsafe_allow_html=True)
            
            road_data = []
            for road in data["roads"]:
                # Calculate realistic travel metrics
                speed_limit = road["speed_limit"]
                base_speed = speed_limit * (1 - road["traffic"] * 0.7)  # Traffic reduces speed by up to 70%
                actual_speed = max(20, base_speed)  # Minimum speed of 20 km/h
                
                # Calculate travel times
                base_travel_time = road["distance"] / speed_limit  # Base time at speed limit
                actual_travel_time = road["distance"] / actual_speed
                delay = (actual_travel_time - base_travel_time) * 60  # Delay in minutes
                
                # Calculate reliability score (0-100)
                condition_factor = {
                    "excellent": 1.0,
                    "good": 0.9,
                    "fair": 0.7,
                    "poor": 0.5
                }.get(road["condition"], 0.7)
                
                reliability = int(100 * (1 - road["traffic"]) * condition_factor)
                
                road_data.append({
                    "Road Name": road["name"],
                    "From": data["intersections"][road["from"]]["name"],
                    "To": data["intersections"][road["to"]]["name"],
                    "Distance": f"{road['distance']} km",
                    "Speed Limit": f"{road['speed_limit']} km/h",
                    "Current Speed": f"{actual_speed:.0f} km/h",
                    "Traffic Level": road["traffic"] * 100,  # Convert to percentage
                    "Est. Delay": f"{delay:.1f} min",
                    "Condition": road["condition"].title(),
                    "Lanes": road["lanes"],
                    "Reliability": reliability,
                    "Status": "High" if road["traffic"] > 0.7 else "Medium" if road["traffic"] > 0.3 else "Low"
                })
            
            df = pd.DataFrame(road_data)
            
            # Enhanced dataframe display with custom formatting
            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Road Name": st.column_config.TextColumn(
                        "Road",
                        help="Name of the road",
                        width="medium"
                    ),
                    "Traffic Level": st.column_config.ProgressColumn(
                        "Traffic",
                        help="Current traffic level (0-100%)",
                        format="%.0f%%",
                        min_value=0,
                        max_value=100,
                        width="small"
                    ),
                    "Reliability": st.column_config.ProgressColumn(
                        "Reliability",
                        help="Road reliability score based on traffic and condition",
                        format="%.0f%%",
                        min_value=0,
                        max_value=100,
                        width="small"
                    ),
                    "Status": st.column_config.TextColumn(
                        "Status",
                        help="Traffic status of the road",
                        width="small"
                    ),
                    "Est. Delay": st.column_config.TextColumn(
                        "Delay",
                        help="Estimated delay due to traffic",
                        width="small"
                    ),
                    "Condition": st.column_config.TextColumn(
                        "Condition",
                        help="Current road condition",
                        width="small"
                    )
                }
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="modern-card">', unsafe_allow_html=True)
            st.markdown('<h4 style="color: var(--primary-purple); margin-bottom: 1.5rem;">📊 Traffic Distribution</h4>', unsafe_allow_html=True)
            
            # Calculate traffic distribution
            traffic_dist = calculate_traffic_distribution(data)
            
            # Create enhanced pie chart using plotly
            fig = go.Figure(data=[go.Pie(
                labels=list(traffic_dist["levels"].keys()),
                values=list(traffic_dist["levels"].values()),
                hole=.4,
                marker=dict(
                    colors=['#4CAF50', '#FF9800', '#F44336'],
                    line=dict(color='white', width=2)
                ),
                textinfo='label+percent',
                textfont=dict(size=14, color='white'),
                hoverinfo='label+value+percent'
            )])
            
            fig.update_layout(
                title={
                    'text': "Traffic Distribution",
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 16, 'color': 'var(--text-primary)'}
                },
                showlegend=True,
                margin=dict(t=40, l=0, r=0, b=0),
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Enhanced summary statistics
            st.markdown(f"""
                <div style='text-align: center; margin-top: 1.5rem; padding: 1rem; background: var(--light-green); border-radius: var(--border-radius-small);'>
                    <div style='font-size: 1rem; color: var(--text-secondary); font-weight: 500;'>Network Status</div>
                    <div style='font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0; color: var(--primary-green);'>
                        {traffic_dist["clear_roads_percentage"]:.1f}% Clear Roads
                    </div>
                    <div style='font-size: 0.9rem; color: var(--text-secondary); line-height: 1.5;'>
                        <div style='margin: 0.2rem 0;'>🚦 {traffic_dist["levels"]["High"]} roads with high traffic</div>
                        <div style='margin: 0.2rem 0;'>⚠️ {traffic_dist["levels"]["Medium"]} roads with medium traffic</div>
                        <div style='margin: 0.2rem 0;'>✅ {traffic_dist["levels"]["Low"]} roads with low traffic</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Network Analysis Tab with enhanced design
    with tabs[2]:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">📊 Network Intelligence & Analytics</h2>', unsafe_allow_html=True)
        
        # Calculate and display network metrics
        G = create_graph_from_data(data)
        metrics_df = create_network_analysis_plot(G)
        network_metrics = get_network_metrics(G)
        
        # Enhanced metrics display with modern cards
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: var(--primary-green); margin-bottom: 1.5rem;">📈 Network Performance Metrics</h3>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                create_metric_card(
                    "Average Path Length",
                    f"{network_metrics['avg_path_length']:.2f} km",
                    "Average distance in largest connected component",
                    "📏"
                ),
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                create_metric_card(
                    "Network Density",
                    f"{network_metrics['density']:.2%}",
                    "How well-connected the network is",
                    "🔗"
                ),
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                create_metric_card(
                    "Network Connectivity",
                    f"{network_metrics['connectivity']:.1%}",
                    f"Largest component ({network_metrics['num_scc']} components total)",
                    "🌐"
                ),
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                create_metric_card(
                    "Total Nodes",
                    f"{network_metrics['num_nodes']}",
                    "Number of intersections in network",
                    "📍"
                ),
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced centrality analysis with modern design
        st.markdown('<h3 class="sub-header">🎯 Centrality Analysis & Node Importance</h3>', unsafe_allow_html=True)
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        
        # Create enhanced tabs for different visualizations
        analysis_tabs = st.tabs(["📊 Centrality Metrics", "🗺️ Visual Analysis", "🔍 Node Details"])
        
        with analysis_tabs[0]:
            st.markdown('<h4 style="color: var(--primary-blue); margin-bottom: 1.5rem;">📊 Node Centrality Rankings</h4>', unsafe_allow_html=True)
            
            # Enhanced dataframe with better styling
            st.dataframe(
                metrics_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Node": st.column_config.TextColumn(
                        "Intersection",
                        help="Name of the intersection",
                        width="medium"
                    ),
                    "Degree Centrality": st.column_config.ProgressColumn(
                        "Degree Centrality",
                        help="Measure of direct connections (0-1)",
                        format="%.3f",
                        min_value=0,
                        max_value=1,
                        width="medium"
                    ),
                    "Betweenness Centrality": st.column_config.ProgressColumn(
                        "Betweenness Centrality",
                        help="Measure of importance in connecting other nodes (0-1)",
                        format="%.3f",
                        min_value=0,
                        max_value=1,
                        width="medium"
                    ),
                    "Closeness Centrality": st.column_config.ProgressColumn(
                        "Closeness Centrality",
                        help="Measure of how close a node is to all other nodes (0-1)",
                        format="%.3f",
                        min_value=0,
                        max_value=1,
                        width="medium"
                    )
                }
            )
            
            # Add centrality explanation
            st.markdown("""
                <div style="margin-top: 1.5rem; padding: 1rem; background: var(--light-blue); border-radius: var(--border-radius-small);">
                    <h5 style="color: var(--primary-blue); margin-bottom: 0.8rem;">📚 Centrality Metrics Explained</h5>
                    <div style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                        <div style="margin-bottom: 0.5rem;"><strong>Degree Centrality:</strong> Measures how many direct connections a node has. Higher values indicate more connected intersections.</div>
                        <div style="margin-bottom: 0.5rem;"><strong>Betweenness Centrality:</strong> Measures how often a node appears on shortest paths between other nodes. Higher values indicate critical routing points.</div>
                        <div><strong>Closeness Centrality:</strong> Measures how close a node is to all other nodes in the network. Higher values indicate better accessibility.</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with analysis_tabs[1]:
            st.markdown('<h4 style="color: var(--primary-purple); margin-bottom: 1.5rem;">🗺️ Network Structure Visualization</h4>', unsafe_allow_html=True)
            
            # Enhanced network visualization
            fig = visualize_graph(G)
            st.pyplot(fig)
            
            # Add visualization legend
            st.markdown("""
                <div style="margin-top: 1rem; padding: 1rem; background: var(--light-green); border-radius: var(--border-radius-small);">
                    <h5 style="color: var(--primary-green); margin-bottom: 0.8rem;">🎨 Visualization Legend</h5>
                    <div style="font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6;">
                        <div style="margin-bottom: 0.3rem;">🔵 <strong>Nodes:</strong> Intersections and cities</div>
                        <div style="margin-bottom: 0.3rem;">🔗 <strong>Edges:</strong> Roads and connections</div>
                        <div style="margin-bottom: 0.3rem;">🎯 <strong>Node Size:</strong> Based on degree centrality</div>
                        <div><strong>Edge Thickness:</strong> Based on traffic volume</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        
        with analysis_tabs[2]:
            st.markdown('<h4 style="color: var(--primary-amber); margin-bottom: 1.5rem;">🔍 Detailed Node Analysis</h4>', unsafe_allow_html=True)
            
            # Node selection for detailed analysis
            node_names = [f"{data['intersections'][node]['name']} ({node})" for node in data['intersections'].keys()]
            selected_node = st.selectbox(
                "Select a node for detailed analysis:",
                node_names,
                help="Choose an intersection to see detailed metrics"
            )
            
            if selected_node:
                node_id = selected_node.split("(")[1].split(")")[0].strip()
                node_data = data['intersections'][node_id]
                
                # Get centrality metrics for selected node
                node_metrics = metrics_df[metrics_df['Node'] == node_data['name']].iloc[0] if len(metrics_df[metrics_df['Node'] == node_data['name']]) > 0 else None
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                        <div class="modern-card" style="margin-bottom: 1rem;">
                            <h5 style="color: var(--primary-green); margin-bottom: 1rem;">📍 {node_data['name']}</h5>
                            <div style="display: grid; gap: 0.8rem;">
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="color: var(--text-secondary);">Coordinates:</span>
                                    <span style="font-weight: 500;">({node_data['pos'][0]:.4f}, {node_data['pos'][1]:.4f})</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="color: var(--text-secondary);">Type:</span>
                                    <span style="font-weight: 500;">{node_data.get('type', 'Intersection')}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="color: var(--text-secondary);">Division:</span>
                                    <span style="font-weight: 500;">{node_data.get('division', 'Uttarakhand')}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between;">
                                    <span style="color: var(--text-secondary);">Elevation:</span>
                                    <span style="font-weight: 500;">{node_data.get('elevation', 'N/A')} m</span>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    if node_metrics is not None:
                        st.markdown(f"""
                            <div class="modern-card">
                                <h5 style="color: var(--primary-blue); margin-bottom: 1rem;">📊 Centrality Metrics</h5>
                                <div style="display: grid; gap: 0.8rem;">
                                    <div style="display: flex; justify-content: space-between;">
                                        <span style="color: var(--text-secondary);">Degree:</span>
                                        <span style="font-weight: 500;">{node_metrics['Degree Centrality']:.3f}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between;">
                                        <span style="color: var(--text-secondary);">Betweenness:</span>
                                        <span style="font-weight: 500;">{node_metrics['Betweenness Centrality']:.3f}</span>
                                    </div>
                                    <div style="display: flex; justify-content: space-between;">
                                        <span style="color: var(--text-secondary);">Closeness:</span>
                                        <span style="font-weight: 500;">{node_metrics['Closeness Centrality']:.3f}</span>
                                    </div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # About Tab with enhanced design
    with tabs[3]:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">ℹ️ About Traffic Optimizer</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h3 style="color: var(--primary-green); font-size: 2rem; margin-bottom: 1rem;">🚦 Traffic Flow Optimization System</h3>
            <p style="color: var(--text-secondary); font-size: 1.1rem; line-height: 1.6;">
                An advanced traffic management system designed for modern urban environments, 
                leveraging cutting-edge algorithms and real-time data analysis to optimize traffic flow 
                and enhance transportation efficiency.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights with modern cards
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
                <div class="modern-card" style="margin-bottom: 1rem;">
                    <h4 style="color: var(--primary-green); margin-bottom: 1rem;">🧠 Route Optimization</h4>
                    <ul style="color: var(--text-secondary); line-height: 1.6; padding-left: 1.5rem;">
                        <li>Multiple algorithm support (Dijkstra, A*, Bellman-Ford)</li>
                        <li>Real-time traffic condition analysis</li>
                        <li>Weather impact consideration</li>
                        <li>Turn-by-turn navigation</li>
                        <li>Efficiency metrics calculation</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="modern-card">
                    <h4 style="color: var(--primary-blue); margin-bottom: 1rem;">🔮 Predictive Analytics</h4>
                    <ul style="color: var(--text-secondary); line-height: 1.6; padding-left: 1.5rem;">
                        <li>3-hour traffic predictions</li>
                        <li>Historical pattern analysis</li>
                        <li>Weather-based impact assessment</li>
                        <li>Seasonal traffic patterns</li>
                        <li>Road-specific analysis</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div class="modern-card" style="margin-bottom: 1rem;">
                    <h4 style="color: var(--primary-purple); margin-bottom: 1rem;">📊 Network Intelligence</h4>
                    <ul style="color: var(--text-secondary); line-height: 1.6; padding-left: 1.5rem;">
                        <li>Centrality metrics analysis</li>
                        <li>Network density calculations</li>
                        <li>Connectivity assessments</li>
                        <li>Node importance ranking</li>
                        <li>Visual network mapping</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="modern-card">
                    <h4 style="color: var(--primary-amber); margin-bottom: 1rem;">🎨 Modern Interface</h4>
                    <ul style="color: var(--text-secondary); line-height: 1.6; padding-left: 1.5rem;">
                        <li>Responsive design</li>
                        <li>Interactive visualizations</li>
                        <li>Real-time data updates</li>
                        <li>User-friendly navigation</li>
                        <li>Mobile-optimized layout</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        # Technology stack
        st.markdown('<h3 class="sub-header">🛠️ Technology Stack</h3>', unsafe_allow_html=True)
        
        tech_col1, tech_col2, tech_col3 = st.columns(3)
        
        with tech_col1:
            st.markdown("""
                <div class="metric-container">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🐍</div>
                    <div class="metric-label">Python</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.5rem;">Core programming language</div>
                </div>
            """, unsafe_allow_html=True)
        
        with tech_col2:
            st.markdown("""
                <div class="metric-container">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <div class="metric-label">Streamlit</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.5rem;">Web application framework</div>
                </div>
            """, unsafe_allow_html=True)
        
        with tech_col3:
            st.markdown("""
                <div class="metric-container">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🕸️</div>
                    <div class="metric-label">NetworkX</div>
                    <div style="font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.5rem;">Graph analysis library</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Additional technologies
        st.markdown("""
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem;">
                <div class="metric-container">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📈</div>
                    <div class="metric-label">Plotly</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Interactive visualizations</div>
                </div>
                <div class="metric-container">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🗺️</div>
                    <div class="metric-label">Folium</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Interactive maps</div>
                </div>
                <div class="metric-container">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
                    <div class="metric-label">Pandas</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Data manipulation</div>
                </div>
                <div class="metric-container">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🎨</div>
                    <div class="metric-label">Matplotlib</div>
                    <div style="font-size: 0.8rem; color: var(--text-secondary);">Static visualizations</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced footer with modern design
    st.markdown(
        """
        <div style="margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, var(--primary-green), var(--primary-blue)); border-radius: var(--border-radius); text-align: center; color: white;">
            <div style="font-size: 1.5rem; font-weight: bold; margin-bottom: 1rem;">
                🚦 Traffic Flow Optimizer
            </div>
            <div style="font-size: 1rem; margin-bottom: 1rem; opacity: 0.9;">
                Developed with Advanced Algorithms using Python & Streamlit
            </div>
            <div style="font-size: 0.9rem; opacity: 0.8;">
                Optimized for Modern Urban Traffic Management • Real-time Analytics • Predictive Intelligence
            </div>
            <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2); font-size: 0.8rem; opacity: 0.7;">
                © 2024  Traffic Optimizer • Built with ❤️ for better transportation by Team : EREMITES 
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main_with_login()