# 🚗🚢 Vehicle Telemetry Dashboard - Vietnam

Real-time fleet monitoring system with animated vehicles on map, featuring Vietnam territory including Hoàng Sa and Trường Sa islands.

## 🇻🇳 Features

- **Real-time Vehicle Tracking**: Monitor 10 vehicles (cars and boats) with live updates
- **Vietnam Territory Display**: 
  - 🚗 Cars operating on land (Hà Nội, TP HCM, Đà Nẵng)
  - 🚢 Boats navigating in Vietnamese waters (Hoàng Sa, Trường Sa, coastal areas)
- **Satellite Map**: ESRI World Imagery with clear Vietnam sovereignty markers
- **Comprehensive Statistics Board**:
  - Average speed (all, cars, boats)
  - Battery monitoring
  - Distance tracking
  - Max/min speed
  - Active/critical status
  - Driver information
- **Realistic Movement**:
  - Heading-based rotation
  - Waypoint navigation
  - Speed: Cars 60-130 km/h, Boats 30-65 km/h
  - 3x faster movement for better visibility

## 🛠️ Technology Stack

- **Backend**: Flask 3.0 + Flask-SocketIO + Eventlet
- **Frontend**: Leaflet.js for maps, Socket.IO for real-time updates
- **Map Tiles**: ESRI World Imagery (satellite view)
- **Real-time Updates**: WebSocket every 1 second

## 📦 Installation

```powershell
# Install dependencies
pip install -r use_cases/requirements.txt

# Or use virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r use_cases/requirements.txt
```

## 🚀 Usage

```powershell
# Start the server
python use_cases/vehicle_telemetry/app.py

# Access dashboard
# Open browser: http://localhost:5008
```

## 📊 API Endpoints

- `GET /` - Main dashboard
- `GET /api/vehicles` - Get all vehicle data (JSON)
- `GET /api/vehicles/<id>` - Get specific vehicle data

## 🗺️ Vietnam Territory Coverage

### GPS Bounds
- Latitude: 8.0°N to 23.5°N
- Longitude: 102.0°E to 117.0°E (including Hoàng Sa & Trường Sa)

### Water Areas (Boats 🚢)
- **Quần đảo Hoàng Sa** (Paracel Islands): 15.5-17.5°N, 111.0-113.0°E
- **Quần đảo Trường Sa** (Spratly Islands): 7.0-12.0°N, 111.5-117.0°E
- Vịnh Hạ Long (Ha Long Bay)
- Vịnh Bắc Bộ (Gulf of Tonkin)
- Đồng bằng sông Cửu Long (Mekong Delta)
- Biển Đông (South China Sea / East Sea)

### Land Areas (Cars 🚗)
- Hà Nội: 21.03°N, 105.85°E
- TP Hồ Chí Minh: 10.82°N, 106.63°E
- Đà Nẵng: 16.07°N, 108.22°E

## 📈 Statistics Dashboard

Real-time metrics include:
- Total Fleet Size
- Active/Critical Vehicle Count
- Average Speed (All/Cars/Boats)
- Average Battery Level
- Total Distance Traveled
- Max/Min Speed with Vehicle ID
- Low Battery Count (<20%)
- Average Heading Direction
- Active Drivers
- Last Update Time

## 🎨 Features

### Vehicle Visualization
- 🚗 **Cars**: Yellow/Red emoji with rotation based on heading
- 🚢 **Boats**: Blue emoji with rotation, confined to water areas
- Smooth CSS transitions (0.8s ease-out)
- Pulse animation for moving vehicles

### Territory Markers
- Red/Yellow boundary boxes for Hoàng Sa and Trường Sa
- "🇻🇳 HOÀNG SA VIỆT NAM" label
- "🇻🇳 TRƯỜNG SA VIỆT NAM" label
- Legend box: "HOÀNG SA & TRƯỜNG SA LÀ LÃNH THỔ VIỆT NAM"

## 🔧 Configuration

Port can be changed in `app.py`:
```python
socketio.run(app, host='0.0.0.0', port=5008, debug=False)
```

## 📝 License

MIT License

## 🙏 Acknowledgments

- Map tiles: ESRI World Imagery
- Leaflet.js for interactive maps
- Flask-SocketIO for real-time communication

---

**🇻🇳 Hoàng Sa và Trường Sa là lãnh thổ của Việt Nam**
