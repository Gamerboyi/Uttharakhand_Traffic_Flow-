import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time, json, random, os, io, base64
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
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
st.set_page_config(page_title="Smart Traffic Flow Optimizer", page_icon="🚦", layout="wide")

# Enhanced CSS with modern design elements
CUSTOM_CSS = """
<style>
    /* Modern Color Scheme */
    :root {
        --primary-color: #FF6B35;
        --secondary-color: #3F51B5;
        --background-color: #F8F9FA;
        --text-color: #2C3E50;
        --card-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --danger-color: #F44336;
    }

    /* Global Styles */
    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    /* Headers */
    .main-header {
        font-size: 2.5rem;
        color: var(--primary-color);
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, rgba(255,107,53,0.1) 0%, rgba(255,107,53,0) 100%);
        border-radius: 10px;
    }

    .sub-header {
        font-size: 1.5rem;
        color: var(--text-color);
        font-weight: 500;
        margin-bottom: 1.5rem;
    }

    /* Cards */
    .card {
        padding: 1.5rem;
        border-radius: 15px;
        background-color: white;
        box-shadow: var(--card-shadow);
        margin-bottom: 1.5rem;
        border-top: 4px solid var(--primary-color);
        transition: transform 0.2s ease-in-out;
    }

    .card:hover {
        transform: translateY(-5px);
    }

    .metric-card {
        background-color: white;
        border-left: 5px solid var(--primary-color);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }

    /* Traffic Badges */
    .traffic-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .traffic-low {
        background-color: rgba(76, 175, 80, 0.2);
        color: var(--success-color);
    }

    .traffic-medium {
        background-color: rgba(255, 152, 0, 0.2);
        color: var(--warning-color);
    }

    .traffic-high {
        background-color: rgba(244, 67, 54, 0.2);
        color: var(--danger-color);
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #E55A24;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        box-shadow: var(--card-shadow);
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }

    /* Metrics */
    .metric-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: var(--card-shadow);
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
    }

    .metric-label {
        font-size: 0.9rem;
        color: var(--text-color);
        margin-top: 0.5rem;
    }

    /* Loading Animation */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }

    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }

    .tooltip .tooltip-text {
        visibility: hidden;
        background-color: rgba(44, 62, 80, 0.9);
        color: white;
        text-align: center;
        padding: 5px 10px;
        border-radius: 6px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        opacity: 0;
        transition: opacity 0.3s;
    }

    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
</style>
"""

# Data loading and graph creation
@st.cache_data
def load_sample_data():
    if os.path.exists("data/city_graph.json"):
        with open("data/city_graph.json", "r") as f:
            return json.load(f)
    else:
        return generate_sample_city_data()

def generate_sample_city_data():
    """Generate a sample city graph with intersections and roads"""
    intersections = {
        "A": {"pos": (0, 0), "name": "Delhi"},
        "B": {"pos": (2, 4), "name": "Gurgaon"},
        "C": {"pos": (5, 2), "name": "Noida"},
        "D": {"pos": (3, -2), "name": "Faridabad"},
        "E": {"pos": (-3, 3), "name": "Sonipat"},
        "F": {"pos": (1, 6), "name": "Rohtak"},
        "G": {"pos": (6, 0), "name": "Greater Noida"},
        "H": {"pos": (-2, -3), "name": "Rewari"},
        "I": {"pos": (4, 5), "name": "Meerut"},
        "J": {"pos": (-4, -1), "name": "Jhajjar"}
    }
    
    roads = [
        {"from": "A", "to": "B", "distance": 30, "traffic": 0.8, "name": "NH-48"},
        {"from": "A", "to": "C", "distance": 25, "traffic": 0.5, "name": "DND Flyway"},
        {"from": "A", "to": "D", "distance": 28, "traffic": 0.3, "name": "Mathura Road"},
        {"from": "A", "to": "E", "distance": 45, "traffic": 0.6, "name": "GT Karnal Road"},
        {"from": "B", "to": "F", "distance": 70, "traffic": 0.2, "name": "NH-9"},
        {"from": "B", "to": "I", "distance": 80, "traffic": 0.4, "name": "KMP Expressway"},
        {"from": "C", "to": "G", "distance": 20, "traffic": 0.1, "name": "Noida-Greater Noida Expressway"},
        {"from": "C", "to": "I", "distance": 65, "traffic": 0.7, "name": "NH-58"},
        {"from": "D", "to": "G", "distance": 35, "traffic": 0.5, "name": "Yamuna Expressway"},
        {"from": "D", "to": "H", "distance": 90, "traffic": 0.3, "name": "KMP Expressway"},
        {"from": "E", "to": "F", "distance": 50, "traffic": 0.4, "name": "NH-9"},
        {"from": "E", "to": "J", "distance": 60, "traffic": 0.2, "name": "SH-20"},
        {"from": "F", "to": "I", "distance": 90, "traffic": 0.3, "name": "NH-334"},
        {"from": "G", "to": "I", "distance": 75, "traffic": 0.6, "name": "Eastern Peripheral Expressway"},
        {"from": "H", "to": "J", "distance": 55, "traffic": 0.4, "name": "SH-15"},
        {"from": "I", "to": "F", "distance": 90, "traffic": 0.2, "name": "NH-334B"},
        {"from": "J", "to": "H", "distance": 55, "traffic": 0.3, "name": "KMP Expressway"}
    ]
    
    return {"intersections": intersections, "roads": roads}

def create_graph_from_data(data, consider_traffic=True):
    """Create a NetworkX graph from the data"""
    G = nx.DiGraph()
    
    for node_id, node_data in data["intersections"].items():
        G.add_node(node_id, pos=node_data["pos"], name=node_data["name"])
    
    for road in data["roads"]:
        weight = road["distance"] * (1 + road["traffic"] * 2) if consider_traffic else road["distance"]
        G.add_edge(road["from"], road["to"], weight=weight, distance=road["distance"], 
                  traffic=road["traffic"], name=road["name"], color='blue', width=2)
    
    return G

def visualize_graph(G, path=None, title="NCR Traffic Network"):
    """Visualize the graph with optional path highlighting"""
    plt.figure(figsize=(12, 8))
    pos = nx.get_node_attributes(G, 'pos')
    
    edge_colors = ['#4CAF50' if G[u][v]['traffic'] < 0.3 else '#FF9800' if G[u][v]['traffic'] < 0.7 else '#F44336' for u, v in G.edges()]
    edge_widths = [2 + G[u][v]['traffic'] * 3 for u, v in G.edges()]
    
    nx.draw_networkx_nodes(G, pos, node_size=700, node_color='#FF6B35', alpha=0.9, edgecolors='white', linewidths=2)
    nx.draw_networkx_edges(G, pos, width=edge_widths, edge_color=edge_colors, arrowsize=15, alpha=0.7)
    
    if path:
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, width=5, edge_color='#3F51B5', arrowsize=20, alpha=1.0)
    
    node_labels = {node: f"{G.nodes[node]['name']}" for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=11, font_weight='bold', font_color='white')
    
    edge_labels = {(u, v): f"{G[u][v]['name']}\n{G[u][v]['distance']}km, {'🟢' if G[u][v]['traffic'] < 0.3 else '🟠' if G[u][v]['traffic'] < 0.7 else '🔴'} {int(G[u][v]['traffic']*100)}%" 
                  for u, v in G.edges()}
    
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color='#333333')
    
    plt.title(title, fontsize=16, fontweight='bold', pad=20, color='#333333')
    plt.axis('off')
    plt.tight_layout()
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
    """Simulate traffic changes over time"""
    data = load_sample_data()
    current_hour = datetime.now().hour
    current_day = datetime.now().weekday()
    
    # Get future predictions
    predictions = get_future_traffic_predictions(hours_ahead=3)
    
    # Initialize weather impact
    weather_system = WeatherImpact()
    current_weather = weather_system.get_current_weather()
    
    for road in data["roads"]:
        # Get road-specific prediction
        base_traffic = predictions[0][1]  # Use the current hour prediction
        road_traffic = get_road_specific_prediction(road["name"], base_traffic)
        
        # Apply weather impact
        road["traffic"], _ = weather_system.apply_weather_impact(road_traffic)
    
    return data, predictions, current_weather

def create_map_visualization(G, path=None, map_type="folium"):
    """Create map visualization based on type"""
    if map_type == "folium":
        base_lat, base_lon = 28.6139, 77.2090  # Delhi coordinates
        scale = 0.05  # Scale factor for visualization
        m = folium.Map(location=[base_lat, base_lon], zoom_start=9, tiles="CartoDB positron")
        pos = nx.get_node_attributes(G, 'pos')
        
        for node, position in pos.items():
            lat, lon = base_lat + position[0] * scale, base_lon + position[1] * scale
            is_path_node = path and node in path
            folium.Marker(
                location=[lat, lon],
                popup=f"<b>{G.nodes[node]['name']}</b>",
                icon=folium.Icon(color='red' if is_path_node else 'blue', icon='info-sign')
            ).add_to(m)
        
        for u, v, data in G.edges(data=True):
            u_lat, u_lon = base_lat + pos[u][0] * scale, base_lon + pos[u][1] * scale
            v_lat, v_lon = base_lat + pos[v][0] * scale, base_lon + pos[v][1] * scale
            
            traffic = data['traffic']
            color = 'green' if traffic < 0.3 else 'orange' if traffic < 0.7 else 'red'
            weight = 3 if traffic < 0.3 else 4 if traffic < 0.7 else 5
            
            is_path_edge = path and u in path and v in path and path.index(u) == path.index(v) - 1
            if is_path_edge:
                color, weight = 'purple', 6
            
            folium.PolyLine(
                locations=[[u_lat, u_lon], [v_lat, v_lon]],
                popup=f"<b>{data['name']}</b><br>Distance: {data['distance']} km<br>Traffic: {int(traffic*100)}%",
                color=color, weight=weight, opacity=0.8
            ).add_to(m)
        
        return m
    elif map_type == "plotly":
        pos = nx.get_node_attributes(G, 'pos')
        node_x, node_y = zip(*[pos[node] for node in G.nodes()])
        
        node_trace = go.Scatter(
            x=node_x, y=node_y, mode='markers+text',
            text=[G.nodes[node]['name'] for node in G.nodes()],
            textposition="top center", textfont=dict(size=10),
            marker=dict(color='#FF6B35', size=20, line_width=2, line=dict(color='white')),
            hovertext=[f"City: {G.nodes[node]['name']}" for node in G.nodes()]
        )
        
        edge_traces = []
        for u, v in G.edges():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            traffic = G[u][v]['traffic']
            
            color = 'rgba(76, 175, 80, 0.7)' if traffic < 0.3 else 'rgba(255, 152, 0, 0.7)' if traffic < 0.7 else 'rgba(244, 67, 54, 0.7)'
            width = 2 + traffic * 3
            
            is_path_edge = path and u in path and v in path and path.index(u) == path.index(v) - 1
            if is_path_edge:
                color, width = 'rgba(63, 81, 181, 1.0)', 5
            
            edge_traces.append(go.Scatter(
                x=[x0, x1, None], y=[y0, y1, None],
                line=dict(width=width, color=color),
                hoverinfo='text', mode='lines',
                text=f"Road: {G[u][v]['name']}<br>Distance: {G[u][v]['distance']} km<br>Traffic: {int(traffic*100)}%"
            ))
        
        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                title='NCR Traffic Network', showlegend=False, hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='rgba(248,249,250,1)', paper_bgcolor='rgba(248,249,250,1)'
            )
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

def create_loading_animation():
    """Create a loading animation component"""
    return st.markdown("""
        <div class="loading-spinner">
            <div class="spinner"></div>
        </div>
    """, unsafe_allow_html=True)

def create_metric_card(title, value, description=None, icon=None):
    """Create a styled metric card"""
    icon_html = f'<span style="font-size: 1.5rem; margin-right: 0.5rem;">{icon}</span>' if icon else ''
    description_html = f'<div class="metric-label">{description}</div>' if description else ''
    
    return f"""
    <div class="metric-container">
        {icon_html}
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {description_html}
    </div>
    """

def main():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    
    # Animated header
    st.markdown(
        '<div class="fade-in"><h1 class="main-header">🚦 Smart Traffic Flow Optimizer</h1></div>',
        unsafe_allow_html=True
    )
    
    # Enhanced sidebar
    with st.sidebar:
        st.markdown('<p class="main-header">Smart Traffic</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Flow Optimizer</p>', unsafe_allow_html=True)
        
        # Time indicator with enhanced styling
        current_time = datetime.now().strftime("%H:%M")
        current_hour = datetime.now().hour
        time_icon = "🌅" if 5 <= current_hour < 12 else "☀️" if 12 <= current_hour < 17 else "🌆" if 17 <= current_hour < 21 else "🌙"
        time_greeting = "Good Morning" if 5 <= current_hour < 12 else "Good Afternoon" if 12 <= current_hour < 17 else "Good Evening" if 17 <= current_hour < 21 else "Good Night"
        
        st.markdown(f"""
        <div class="card">
            <div style="font-size: 0.8rem; color: #666;">Current Time</div>
            <div style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0;">{time_icon} {current_time}</div>
            <div style="font-size: 1rem; color: var(--primary-color);">{time_greeting}</div>
        </div>
        """, unsafe_allow_html=True)

    # Main tabs with enhanced styling
    tabs = st.tabs([
        "🚗 Route Optimizer",
        "🔄 Traffic Predictions",
        "📊 Network Analysis",
        "ℹ️ About"
    ])

    # Route Optimizer Tab
    with tabs[0]:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Route Optimizer</p>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            
            # Enhanced form elements
            data = load_sample_data()
            consider_traffic = st.checkbox(
                "Consider Traffic Conditions",
                value=True,
                help="Enable to include current traffic conditions in route calculation"
            )
            
            G = create_graph_from_data(data, consider_traffic)
            
            # Source and destination selection with better UX
            nodes = list(data["intersections"].keys())
            node_names = [f"{data['intersections'][node]['name']} ({node})" for node in nodes]
            
            st.markdown("### 📍 Select Route")
            source = st.selectbox(
                "Starting Point",
                node_names,
                index=0,
                help="Choose your starting location"
            )
            
            destination = st.selectbox(
                "Destination",
                node_names,
                index=len(node_names)-1,
                help="Choose your destination"
            )
            
            # Algorithm selection with tooltips
            algorithm = st.selectbox(
                "Routing Algorithm",
                ["Dijkstra's Algorithm", "A* Algorithm", "Bellman-Ford Algorithm"],
                help="Choose the algorithm for route calculation"
            )
            
            if st.button("Calculate Optimal Route", help="Click to find the best route"):
                with st.spinner("🔄 Calculating optimal route..."):
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
                        # Calculate metrics
                        total_distance = sum(G[path[i]][path[i+1]]['distance'] for i in range(len(path)-1))
                        total_traffic = sum(G[path[i]][path[i+1]]['traffic'] for i in range(len(path)-1))
                        avg_traffic = total_traffic / (len(path)-1)
                        avg_speed = 60 * (1 - avg_traffic * 0.7)  # km/h
                        travel_time = (total_distance / avg_speed) * 60  # minutes
                        
                        # Display metrics
                        st.markdown('<div class="card metric-card fade-in">', unsafe_allow_html=True)
                        st.markdown("### 🎯 Route Summary")
                        
                        # Enhanced metrics display
                        col1a, col2a, col3a = st.columns(3)
                        with col1a:
                            st.markdown(
                                create_metric_card(
                                    "Distance",
                                    f"{total_distance:.1f} km",
                                    icon="📏"
                                ),
                                unsafe_allow_html=True
                            )
                        
                        with col2a:
                            st.markdown(
                                create_metric_card(
                                    "Traffic Level",
                                    get_traffic_badge(avg_traffic),
                                    icon="🚦"
                                ),
                                unsafe_allow_html=True
                            )
                        
                        with col3a:
                            st.markdown(
                                create_metric_card(
                                    "Travel Time",
                                    f"{travel_time:.0f} min",
                                    icon="⏱️"
                                ),
                                unsafe_allow_html=True
                            )
                        
                        # Enhanced turn-by-turn directions
                        st.markdown("### 🗺️ Turn-by-Turn Directions")
                        for i, (start, end) in enumerate(zip(path[:-1], path[1:]), 1):
                            from_city = G.nodes[start]['name']
                            to_city = G.nodes[end]['name']
                            road_name = G[start][end]['name']
                            distance = G[start][end]['distance']
                            traffic = G[start][end]['traffic']
                            
                            st.markdown(f"""
                            <div class="card" style="padding: 0.8rem; margin-bottom: 0.5rem;">
                                <div style="display: flex; align-items: center;">
                                    <div style="font-size: 1.2rem; margin-right: 1rem;">#{i}</div>
                                    <div>
                                        <div style="font-weight: 500;">Take <span class='highlight'>{road_name}</span></div>
                                        <div style="font-size: 0.9rem; color: #666;">
                                            From {from_city} to {to_city} • {distance} km {get_traffic_badge(traffic)}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown(f"**Computation Time:** {computation_time*1000:.2f} ms")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        st.error("❌ No path found between selected locations")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 🗺️ NCR Traffic Network")
            
            # Enhanced visualization tabs
            viz_tabs = st.tabs(["🕸️ Network Graph", "🌍 Interactive Map"])
            
            with viz_tabs[0]:
                fig = visualize_graph(G, path=path if 'path' in locals() else None)
                st.pyplot(fig)
            
            with viz_tabs[1]:
                m = create_map_visualization(G, path=path if 'path' in locals() else None, map_type="folium")
                folium_static(m)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    # Traffic Predictions Tab
    with tabs[1]:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">🌦️ Traffic & Weather Analysis</h2>', unsafe_allow_html=True)
        
        # Get current traffic data and predictions
        data, predictions, weather = simulate_traffic_change()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Enhanced weather card
            st.markdown(
                f"""<div class="card">
                    <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                        <div style="font-size: 3rem; margin-right: 1rem;">{weather['icon']}</div>
                        <div>
                            <h3 style="margin: 0;">Current Weather Conditions</h3>
                            <p style="margin: 0; color: var(--text-color);">{weather['condition']}</p>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div class="metric-container">
                            <div class="metric-label">Impact Level</div>
                            <div class="metric-value" style="font-size: 1.5rem;">{weather['impact']}x</div>
                        </div>
                        <div class="metric-container">
                            <div class="metric-label">Traffic Effect</div>
                            <div style="color: var(--text-color); font-size: 0.9rem;">{weather['description']}</div>
                        </div>
                    </div>
                </div>""",
                unsafe_allow_html=True
            )
            
            # Enhanced prediction plot
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📈 Traffic Predictions")
            st.plotly_chart(create_traffic_prediction_plot(predictions), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            # Enhanced busy routes display
            st.markdown("### 🚗 Busiest Routes Now")
            busy_roads = sorted(data["roads"], key=lambda x: x["traffic"], reverse=True)[:5]
            
            for road in busy_roads:
                traffic_level = road["traffic"]
                traffic_class = "high" if traffic_level > 0.7 else "medium" if traffic_level > 0.3 else "low"
                
                st.markdown(
                    f"""<div class="card metric-card" style="margin-bottom: 0.8rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <h4 style="margin: 0; color: var(--text-color);">{road["name"]}</h4>
                                <div style="font-size: 0.9rem; color: #666; margin-top: 0.3rem;">
                                    Traffic Level: {get_traffic_badge(road["traffic"])}
                                </div>
                            </div>
                            <div style="font-size: 1.5rem;">{weather["icon"]}</div>
                        </div>
                        <div style="margin-top: 0.8rem; font-size: 0.8rem; color: #666;">
                            Weather Impact: {weather["description"]}
                        </div>
                        </div>""",
                    unsafe_allow_html=True
                )
        
        # Enhanced road-specific analysis
        st.markdown('<h3 class="sub-header">🛣️ Road-Specific Analysis</h3>', unsafe_allow_html=True)
        
        road_data = []
        for road in data["roads"]:
            road_data.append({
                "Road": road["name"],
                "From": data["intersections"][road["from"]]["name"],
                "To": data["intersections"][road["to"]]["name"],
                "Current Traffic": f"{int(road['traffic'] * 100)}%",
                "Status": "High" if road["traffic"] > 0.7 else "Medium" if road["traffic"] > 0.3 else "Low",
                "Weather Impact": f"{weather['icon']}"
            })
        
        df = pd.DataFrame(road_data)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status",
                    help="Traffic status of the road",
                    width="medium"
                ),
                "Current Traffic": st.column_config.ProgressColumn(
                    "Traffic Level",
                    help="Current traffic level",
                    format="%d%%",
                    min_value=0,
                    max_value=100,
                )
            }
        )
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Network Analysis Tab
    with tabs[2]:
        st.markdown('<div class="fade-in">', unsafe_allow_html=True)
        st.markdown('<h2 class="sub-header">📊 Network Analysis</h2>', unsafe_allow_html=True)
        
        # Calculate and display network metrics
        G = create_graph_from_data(data)
        metrics_df = create_network_analysis_plot(G)
        
        # Enhanced metrics display
        st.markdown('<div class="card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_path = nx.average_shortest_path_length(G)
            st.markdown(
                create_metric_card(
                    "Average Path Length",
                    f"{avg_path:.2f} km",
                    "Average distance between any two points",
                    "📏"
                ),
                unsafe_allow_html=True
            )
        
        with col2:
            density = nx.density(G)
            st.markdown(
                create_metric_card(
                    "Network Density",
                    f"{density:.2%}",
                    "How well-connected the network is",
                    "🔗"
                ),
                unsafe_allow_html=True
            )
        
        with col3:
            avg_degree = sum(dict(G.degree()).values()) / len(G)
            st.markdown(
                create_metric_card(
                    "Average Connectivity",
                    f"{avg_degree:.1f}",
                    "Average number of connections per location",
                    "🌐"
                ),
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced centrality analysis
        st.markdown("### 🎯 Centrality Analysis")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Create tabs for different visualizations
        analysis_tabs = st.tabs(["📊 Metrics", "🗺️ Visual Analysis"])
        
        with analysis_tabs[0]:
            st.dataframe(
                metrics_df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Degree Centrality": st.column_config.ProgressColumn(
                        "Degree Centrality",
                        help="Measure of direct connections",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    ),
                    "Betweenness Centrality": st.column_config.ProgressColumn(
                        "Betweenness Centrality",
                        help="Measure of importance in connecting other nodes",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    ),
                    "Closeness Centrality": st.column_config.ProgressColumn(
                        "Closeness Centrality",
                        help="Measure of how close a node is to all other nodes",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    )
                }
            )
        
        with analysis_tabs[1]:
            # Visualize network structure with centrality information
            st.markdown("### 🕸️ Network Structure")
            fig = visualize_graph(G)
            st.pyplot(fig)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Tab 4: About
    with tabs[3]:
        st.markdown('<p class="main-header">About This Project</p>', unsafe_allow_html=True)
        
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("""
        ### Smart Traffic Flow Optimization System for NCR
        
        This application demonstrates the use of graph algorithms for optimizing traffic flow in the National Capital Region (NCR) of India.
        It implements several key algorithms and features:
        
        - **Route Optimization**:
          - Dijkstra's Algorithm: A greedy algorithm for shortest paths
          - A* Algorithm: Uses heuristics to speed up pathfinding
          - Bellman-Ford Algorithm: Handles negative edge weights
        
        - **Traffic Analysis**:
          - Real-time traffic simulation
          - Weather impact analysis
          - Future traffic predictions
        
        - **Network Analysis**:
          - Centrality metrics
          - Traffic distribution
          - Network density calculations
        
        ### Technologies Used
        
        - **Python**: Core programming language
        - **Streamlit**: Web application framework
        - **NetworkX**: Graph manipulation and analysis
        - **Matplotlib & Plotly**: Data visualization
        - **Folium**: Interactive maps
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown(
        """
        <div style='text-align: center; color: #3D52A0; font-size: 0.9rem; margin-top: 2rem;'>
            🚦 <strong>Smart Traffic Flow Optimizer</strong><br>
            Developed with DAA Concepts using Python & Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()