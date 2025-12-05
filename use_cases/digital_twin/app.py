"""
Digital Twin Assembly-Line Simulation
Simulate throughput under varying parameters
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import random
import time
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'digital-twin-secret'
CORS(app)

@dataclass
class AssemblyStation:
    """Represents a station in the assembly line"""
    id: str
    name: str
    cycle_time: float  # seconds
    downtime_probability: float  # 0-1
    current_status: str  # 'idle', 'working', 'down'
    units_processed: int = 0
    total_downtime: float = 0
    work_start_time: float = 0

@dataclass
class Product:
    """Represents a product moving through the line"""
    id: str
    start_time: float
    current_station: int
    completed: bool = False
    end_time: float = 0

class AssemblyLineSimulation:
    def __init__(self, num_stations=5, batch_size=10):
        self.num_stations = num_stations
        self.batch_size = batch_size
        self.stations: List[AssemblyStation] = []
        self.products: List[Product] = []
        self.simulation_time = 0
        self.completed_units = 0
        self.total_products_created = 0
        self.is_running = False
        self.initialize_stations()
    
    def initialize_stations(self):
        """Initialize assembly line stations"""
        station_names = [
            "Material Loading",
            "Component Assembly",
            "Quality Check",
            "Finishing",
            "Packaging"
        ]
        
        for i in range(self.num_stations):
            station = AssemblyStation(
                id=f"ST-{i+1}",
                name=station_names[i] if i < len(station_names) else f"Station {i+1}",
                cycle_time=random.uniform(30, 90),  # 30-90 seconds
                downtime_probability=random.uniform(0.01, 0.05),
                current_status='idle'
            )
            self.stations.append(station)
    
    def update_station_params(self, station_id: str, cycle_time: float = None, 
                             downtime_prob: float = None):
        """Update station parameters"""
        for station in self.stations:
            if station.id == station_id:
                if cycle_time is not None:
                    station.cycle_time = cycle_time
                if downtime_prob is not None:
                    station.downtime_probability = downtime_prob
                break
    
    def add_product(self):
        """Add a new product to the line"""
        product_id = f"PROD-{self.total_products_created + 1:04d}"
        product = Product(
            id=product_id,
            start_time=self.simulation_time,
            current_station=0
        )
        self.products.append(product)
        self.total_products_created += 1
    
    def simulate_step(self, delta_time: float = 1.0):
        """Simulate one time step"""
        if not self.is_running:
            return
        
        self.simulation_time += delta_time
        
        # Add new products based on batch size
        if len([p for p in self.products if not p.completed]) < self.batch_size:
            self.add_product()
        
        # Update each station
        for i, station in enumerate(self.stations):
            # Check for random downtime
            if station.current_status != 'down' and random.random() < station.downtime_probability * delta_time:
                station.current_status = 'down'
                station.work_start_time = self.simulation_time
            
            # Recover from downtime (5-30 seconds)
            if station.current_status == 'down':
                downtime_duration = random.uniform(5, 30)
                if self.simulation_time - station.work_start_time > downtime_duration:
                    station.current_status = 'idle'
                    station.total_downtime += downtime_duration
            
            # Process products at this station
            if station.current_status != 'down':
                products_at_station = [p for p in self.products 
                                      if p.current_station == i and not p.completed]
                
                if products_at_station:
                    station.current_status = 'working'
                    product = products_at_station[0]
                    
                    # Check if work is complete
                    if station.work_start_time == 0:
                        station.work_start_time = self.simulation_time
                    
                    work_duration = self.simulation_time - station.work_start_time
                    if work_duration >= station.cycle_time:
                        # Move product to next station
                        product.current_station += 1
                        station.units_processed += 1
                        station.work_start_time = 0
                        
                        # Check if product is complete
                        if product.current_station >= self.num_stations:
                            product.completed = True
                            product.end_time = self.simulation_time
                            self.completed_units += 1
                else:
                    station.current_status = 'idle'
                    station.work_start_time = 0
        
        # Remove completed products older than 60 seconds
        self.products = [p for p in self.products 
                        if not p.completed or (self.simulation_time - p.end_time < 60)]
    
    def get_state(self) -> Dict:
        """Get current simulation state"""
        active_products = [p for p in self.products if not p.completed]
        
        # Calculate throughput (units per hour)
        throughput = 0
        if self.simulation_time > 0:
            throughput = (self.completed_units / self.simulation_time) * 3600
        
        # Find bottleneck
        bottleneck = max(self.stations, key=lambda s: s.cycle_time)
        
        # Calculate average cycle time
        avg_cycle_time = sum(s.cycle_time for s in self.stations) / len(self.stations)
        
        return {
            'simulation_time': round(self.simulation_time, 2),
            'completed_units': self.completed_units,
            'active_products': len(active_products),
            'throughput_per_hour': round(throughput, 2),
            'bottleneck_station': bottleneck.name,
            'avg_cycle_time': round(avg_cycle_time, 2),
            'stations': [asdict(s) for s in self.stations],
            'products': [asdict(p) for p in active_products[:20]]  # Limit to 20 for display
        }
    
    def reset(self):
        """Reset simulation"""
        self.simulation_time = 0
        self.completed_units = 0
        self.total_products_created = 0
        self.products = []
        for station in self.stations:
            station.current_status = 'idle'
            station.units_processed = 0
            station.total_downtime = 0
            station.work_start_time = 0

# Global simulation instance
sim = AssemblyLineSimulation()

@app.route('/')
def index():
    """Main simulation page"""
    return render_template('simulation.html')

@app.route('/api/state')
def get_state():
    """Get current simulation state"""
    return jsonify(sim.get_state())

@app.route('/api/start', methods=['POST'])
def start_simulation():
    """Start simulation"""
    sim.is_running = True
    return jsonify({'status': 'started'})

@app.route('/api/stop', methods=['POST'])
def stop_simulation():
    """Stop simulation"""
    sim.is_running = False
    return jsonify({'status': 'stopped'})

@app.route('/api/reset', methods=['POST'])
def reset_simulation():
    """Reset simulation"""
    sim.reset()
    sim.is_running = False
    return jsonify({'status': 'reset'})

@app.route('/api/step', methods=['POST'])
def simulation_step():
    """Execute one simulation step"""
    delta = request.json.get('delta', 1.0) if request.json else 1.0
    sim.simulate_step(delta)
    return jsonify(sim.get_state())

@app.route('/api/configure', methods=['POST'])
def configure():
    """Configure simulation parameters"""
    data = request.json
    
    if 'batch_size' in data:
        sim.batch_size = int(data['batch_size'])
    
    if 'num_stations' in data and not sim.is_running:
        sim.num_stations = int(data['num_stations'])
        sim.reset()
        sim.initialize_stations()
    
    if 'station_updates' in data:
        for update in data['station_updates']:
            sim.update_station_params(
                update['station_id'],
                update.get('cycle_time'),
                update.get('downtime_probability')
            )
    
    return jsonify({'status': 'configured', 'state': sim.get_state()})

if __name__ == '__main__':
    print("=" * 60)
    print("Digital Twin Assembly-Line Simulation")
    print("=" * 60)
    print(f"Stations: {sim.num_stations}")
    print(f"Batch size: {sim.batch_size}")
    print(f"Dashboard: http://localhost:5002")
    print(f"API: http://localhost:5002/api/state")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5002, debug=True)
