"""
Vehicle Telemetry Visualization System
Real-time fleet monitoring with WebSocket updates
"""
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import random
import time
from datetime import datetime
from threading import Thread
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vehicle-telemetry-secret'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Simulated vehicle fleet data
vehicles = {}
NUM_VEHICLES = 10

# GPS bounds for simulation (Vietnam including Hoàng Sa & Trường Sa)
GPS_BOUNDS = {
    'lat_min': 8.0, 'lat_max': 23.5,
    'lon_min': 102.0, 'lon_max': 117.0  # Extended to include Hoàng Sa & Trường Sa
}

def is_water_location(lat, lon):
    """Check if location is in water (for boat placement in Vietnam)"""
    # Quần đảo Hoàng Sa (Paracel Islands) - Lãnh thổ Việt Nam
    if 15.5 <= lat <= 17.5 and 111.0 <= lon <= 113.0:
        return True
    
    # Quần đảo Trường Sa (Spratly Islands) - Lãnh thổ Việt Nam
    if 7.0 <= lat <= 12.0 and 111.5 <= lon <= 117.0:
        return True
    
    # South China Sea / Biển Đông (East coast)
    if lon > 108.5:
        return True
    
    # Gulf of Tonkin / Vịnh Bắc Bộ (North Vietnam)
    if lat > 20.0 and lon > 106.5:
        return True
    
    # Mekong Delta water areas (South Vietnam)
    if lat < 10.5 and lon > 105.0:
        return True
    
    # Ha Long Bay area / Vịnh Hạ Long
    if 20.5 <= lat <= 21.0 and 106.8 <= lon <= 107.5:
        return True
    
    # Central coast (Da Nang area)
    if 15.5 <= lat <= 16.5 and lon > 108.0:
        return True
    
    return False

def initialize_vehicles():
    """Initialize fleet with boats in water and cars on land"""
    names = ["Quốc Két", "Dĩnh Hịp", "Tô Huấn", "Anh Quang Chửi", "Anh Tùng Sahur", "Anh Thịnh Bot"]
    
    # Water locations for boats (first 3 vehicles) in Vietnam
    water_locations = [
        {'lat': 16.50, 'lon': 112.00, 'type': 'boat'},  # Quần đảo Hoàng Sa
        {'lat': 10.00, 'lon': 114.50, 'type': 'boat'},  # Quần đảo Trường Sa
        {'lat': 20.95, 'lon': 107.05, 'type': 'boat'},  # Vịnh Hạ Long
    ]
    
    # Land locations for cars (remaining vehicles) in Vietnam
    land_locations = [
        {'lat': 21.03, 'lon': 105.85, 'type': 'car'},  # Hà Nội
        {'lat': 10.82, 'lon': 106.63, 'type': 'car'},  # TP Hồ Chí Minh
        {'lat': 16.07, 'lon': 108.22, 'type': 'car'},  # Đà Nẵng
    ]
    
    all_locations = water_locations + land_locations
    
    for i, name in enumerate(names):
        vehicle_id = f"BOSCHLER-{str(i+1).zfill(3)}"
        location = all_locations[i % len(all_locations)]
        
        # Cars are faster (60-120 km/h), boats are slower (30-60 km/h)
        if location['type'] == 'boat':
            speed = random.uniform(30, 60)
        else:
            speed = random.uniform(60, 120)
        
        vehicles[vehicle_id] = {
            'id': vehicle_id,
            'speed': speed,
            'battery': random.uniform(20, 100),
            'lat': location['lat'] + random.uniform(-0.02, 0.02),
            'lon': location['lon'] + random.uniform(-0.02, 0.02),
            'heading': random.uniform(0, 360),
            'target_lat': None,
            'target_lon': None,
            'status': 'active',
            'last_update': datetime.now().isoformat(),
            'odometer': random.uniform(1000, 50000),
            'driver': names[i],
            'vehicle_type': location['type']  # Track if boat or car
        }

def update_telemetry():
    """Continuously update vehicle telemetry with realistic movement"""
    import math
    
    while True:
        for vehicle_id, data in vehicles.items():
            vehicle_type = data.get('vehicle_type', 'car')
            
            # Update speed (gradual changes) - cars faster than boats
            if data['status'] == 'active':
                speed_delta = random.uniform(-5, 5)
                if vehicle_type == 'boat':
                    data['speed'] = max(25, min(65, data['speed'] + speed_delta))
                else:  # car
                    data['speed'] = max(50, min(130, data['speed'] + speed_delta))
            
            # Update battery (drain based on speed)
            battery_drain = (0.008 * (data['speed'] / 60)) if data['speed'] > 0 else 0
            data['battery'] = max(0, data['battery'] - battery_drain)
            
            # If battery critical, stop vehicle
            if data['battery'] < 10:
                data['status'] = 'critical'
                data['speed'] = 0
            else:
                data['status'] = 'active'
            
            # Set new target waypoint based on vehicle type
            if data['target_lat'] is None or (
                abs(data['lat'] - data['target_lat']) < 0.005 and 
                abs(data['lon'] - data['target_lon']) < 0.005
            ):
                # Boats must stay in water
                if vehicle_type == 'boat':
                    # Choose random water target in Vietnam
                    water_targets = [
                        {'lat': 16.50, 'lon': 112.00},  # Quần đảo Hoàng Sa
                        {'lat': 10.00, 'lon': 114.50},  # Quần đảo Trường Sa
                        {'lat': 8.50, 'lon': 113.00},   # Trường Sa (South)
                        {'lat': 20.95, 'lon': 107.05},  # Vịnh Hạ Long
                        {'lat': 16.05, 'lon': 108.25},  # Đà Nẵng coast
                        {'lat': 10.05, 'lon': 106.80},  # Đồng bằng sông Cửu Long
                        {'lat': 21.20, 'lon': 107.50},  # Vịnh Bắc Bộ
                        {'lat': 12.25, 'lon': 109.20},  # Biển Đông
                    ]
                    target = random.choice(water_targets)
                    data['target_lat'] = target['lat'] + random.uniform(-0.05, 0.05)
                    data['target_lon'] = target['lon'] + random.uniform(-0.05, 0.05)
                else:
                    # Cars can go anywhere on land
                    data['target_lat'] = random.uniform(GPS_BOUNDS['lat_min'], GPS_BOUNDS['lat_max'])
                    data['target_lon'] = random.uniform(GPS_BOUNDS['lon_min'], GPS_BOUNDS['lon_max'])
            
            # Move vehicle towards target with realistic heading
            if data['speed'] > 0 and data['target_lat'] is not None:
                # Calculate direction to target
                lat_diff = data['target_lat'] - data['lat']
                lon_diff = data['target_lon'] - data['lon']
                target_heading = math.degrees(math.atan2(lon_diff, lat_diff)) % 360
                
                # Smoothly adjust heading (vehicles don't turn instantly)
                heading_diff = (target_heading - data['heading'] + 180) % 360 - 180
                data['heading'] = (data['heading'] + heading_diff * 0.1) % 360
                
                # Move in the direction of heading (3x faster movement)
                # Speed affects distance traveled: km/h to degrees per second
                distance_per_sec = (data['speed'] / 111000) * 3  # 3x faster
                heading_rad = math.radians(data['heading'])
                
                new_lat = data['lat'] + math.cos(heading_rad) * distance_per_sec
                new_lon = data['lon'] + math.sin(heading_rad) * distance_per_sec
                
                # For boats, ensure they stay in water
                if vehicle_type == 'boat':
                    if is_water_location(new_lat, new_lon):
                        data['lat'] = new_lat
                        data['lon'] = new_lon
                    else:
                        # If about to leave water, pick new water target
                        data['target_lat'] = None
                else:
                    # Cars can move freely
                    data['lat'] = new_lat
                    data['lon'] = new_lon
                
                # Keep within bounds
                data['lat'] = max(GPS_BOUNDS['lat_min'], min(GPS_BOUNDS['lat_max'], data['lat']))
                data['lon'] = max(GPS_BOUNDS['lon_min'], min(GPS_BOUNDS['lon_max'], data['lon']))
            
            # Update odometer
            data['odometer'] += data['speed'] / 3600  # km per second
            
            data['last_update'] = datetime.now().isoformat()
        
        # Broadcast updates to all connected clients
        socketio.emit('telemetry_update', list(vehicles.values()))
        socketio.sleep(1)  # Update every second

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/vehicles')
def get_vehicles():
    """REST API endpoint for current vehicle data"""
    return jsonify(list(vehicles.values()))

@app.route('/api/vehicles/<vehicle_id>')
def get_vehicle(vehicle_id):
    """Get specific vehicle data"""
    if vehicle_id in vehicles:
        return jsonify(vehicles[vehicle_id])
    return jsonify({'error': 'Vehicle not found'}), 404

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {id}')
    emit('initial_data', list(vehicles.values()))

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnect"""
    print(f'Client disconnected')

@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request from client"""
    emit('telemetry_update', list(vehicles.values()))

if __name__ == '__main__':
    initialize_vehicles()
    
    # Start telemetry update thread
    telemetry_thread = Thread(target=update_telemetry, daemon=True)
    telemetry_thread.start()
    
    print("=" * 60)
    print("Vehicle Telemetry Visualization System")
    print("=" * 60)
    print(f"Fleet size: {NUM_VEHICLES} vehicles")
    print(f"Dashboard: http://localhost:5008")
    print(f"API: http://localhost:5008/api/vehicles")
    print("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5008, debug=False)
