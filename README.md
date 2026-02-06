

# 🚦 Smart Traffic Optimizer (Uttarakhand)

## 📌 About Project

This is a **Smart Traffic Flow Optimization System** made for **Uttarakhand**.
Uttarakhand has mountains, tourist rush, weather issues (rain, fog, landslides), so normal routing doesn’t always work best.

This project uses **Graph Algorithms + Traffic + Weather + Road Conditions** to give the best route and traffic analysis.

---

## ✅ Features

### 🔹 1. Route Finder (Shortest Path)

You can find best route between two places using:

* Dijkstra Algorithm
* A* Algorithm
* Bellman Ford Algorithm

Also route changes depending on:

* Traffic level
* Weather effect
* Road condition

---

### 🔹 2. Traffic Monitoring + Prediction

* Shows current traffic condition
* Calculates delay / speed
* Gives **future traffic prediction (next 3 hours)**

---

### 🔹 3. Network / Graph Analysis

This project also shows graph analysis like:

* Degree Centrality
* Betweenness Centrality
* Closeness Centrality

And also:

* Component analysis
* Density
* Average path length

---

### 🔹 4. Visualization

* Interactive map using **Folium**
* Traffic heatmap
* Route highlighting
* Graph plots + charts using **Plotly / Matplotlib**

---

## 🏗️ Tech Stack

### Frontend

* Streamlit (UI)
* Plotly (charts)
* Folium (maps)
* Matplotlib (graphs)

### Backend

* Python
* NetworkX (graph operations)
* Custom traffic + weather logic
* JSON based road data

---

## ⚙️ Installation

### Requirements

* Python 3.8+
* pip
* Git

### Steps

```bash
git clone https://github.com/Gamerboyi/Uttharakhand_Traffic_Flow-.git
```

Create venv:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run app:

```bash
streamlit run app.py
```

---

## 📖 How to Use

### ✅ Route Optimization

1. Select source and destination
2. Choose algorithm
3. Enable traffic / weather option
4. It will show best route + total distance + time

---

### ✅ Traffic Prediction

1. Open Traffic tab
2. See current traffic
3. Check next 3 hours prediction
4. Weather impact also shown

---

### ✅ Network Analysis

1. Open Network Analysis tab
2. See centrality values
3. See graph structure + stats
4. Export results if needed

---

## 🧠 Algorithms Used

### 1. Dijkstra

* Finds shortest path
* Time Complexity: **O((V + E) log V)**
* Best for normal shortest route

---

### 2. A*

* Faster shortest path with heuristic
* Good for traffic-based route planning

---

### 3. Bellman Ford

* Works even if negative weights exist
* Complexity: **O(VE)**
* Useful for complex scenarios

---

### 4. Traffic Prediction Model

* Time series based prediction
* Factors:

  * time
  * season
  * weather
  * tourist rush

---

## 📂 Data Format (JSON)

### Road Network Structure

```json
{
  "intersections": {
    "node_id": {
      "pos": [x, y],
      "name": "City Name",
      "type": "city_type",
      "division": "region",
      "elevation": height
    }
  },
  "roads": [
    {
      "from": "node_id",
      "to": "node_id",
      "distance": length,
      "traffic": level,
      "name": "Road Name",
      "type": "road_type",
      "condition": "road_condition",
      "lanes": number
    }
  ]
}
```

---

## 🔌 Main Functions (API)

### Route Optimization Example

```python
def dijkstra_algorithm(G, source, destination):
    """
    Finds shortest path using Dijkstra
    """
```

### Traffic Prediction

```python
def get_future_traffic_predictions(hours_ahead=3):
    """
    Predict traffic for next hours
    """
```

### Weather Impact

```python
def apply_weather_impact(traffic, elevation, route_type):
    """
    Applies weather effect on traffic
    """
```

---

## 🤝 Contribution

If you want to contribute:

1. Fork repo
2. Create branch
3. Commit changes
4. Push
5. Create PR

---

## 📜 License

This project is under **MIT License**.

---

## 📧 Contact

For any help or query:

* **Name:** Vedant Nautiyal
* **Email:** [itsvedantnautiyal@gmail.com](mailto:itsvedantnautiyal@gmail.com)
* **GitHub:** Gamerboyi

---

⭐ If you like this project, give it a star.

---


