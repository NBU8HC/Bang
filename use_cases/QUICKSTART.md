# 🚀 Quick Start Guide

## Fastest Way to Run All Three Systems

### Option 1: Run All at Once (Recommended)
```powershell
cd use_cases
.\run_all.ps1
```
This opens three PowerShell windows, one for each system.

### Option 2: Run Individually
```powershell
# Terminal 1
cd use_cases\vehicle_telemetry
.\run.ps1

# Terminal 2
cd use_cases\digital_twin
.\run.ps1

# Terminal 3
cd use_cases\resource_allocation
.\run.ps1
```

### Option 3: Manual Start
```powershell
# Install dependencies first
cd use_cases
pip install -r requirements.txt

# Then run each system
cd vehicle_telemetry
python app.py

# (In separate terminals)
cd digital_twin
python app.py

cd resource_allocation
python app.py
```

---

## 🌐 Access Dashboards

Once started, open these URLs in your browser:

| System | URL | Description |
|--------|-----|-------------|
| **Vehicle Telemetry** | http://localhost:5001 | Real-time fleet monitoring with GPS map |
| **Digital Twin** | http://localhost:5002 | Assembly line simulation with analytics |
| **Resource Allocation** | http://localhost:5003 | Drag-and-drop resource management |

---

## 🎮 How to Use Each System

### Vehicle Telemetry (Port 5001)
1. Dashboard loads with 10 simulated vehicles on a map
2. Watch real-time updates (speed, battery, GPS position)
3. Click a vehicle card to zoom to its location on the map
4. Red vehicles indicate critical battery (<10%)
5. Connection status shown in top-right corner

**What to Look For:**
- Live position updates on map
- Battery drain as vehicles move
- Speed variations over time
- Critical alerts for low battery

---

### Digital Twin Simulation (Port 5002)
1. Click **▶️ Start** to begin simulation
2. Watch products move through 5 assembly stations
3. Adjust **Simulation Speed** slider for faster/slower execution
4. Modify **Batch Size** to change product flow
5. Monitor throughput chart (bottom panel)
6. Click **🔄 Reset** to restart simulation

**What to Look For:**
- Stations changing status (idle → working → down)
- Throughput metrics (units/hour)
- Products flowing through the line
- Random downtime events (red stations)
- Real-time charting of performance

---

### Resource Allocation (Port 5003)
1. **Drag an operator** from left panel to a work order's operator slot
2. **Drag a machine** from left panel to the same work order's machine slot
3. Watch work order status change to **in_progress** (green border)
4. If materials insufficient, status shows **blocked** (red border)
5. Click **Release Resources** to unassign and free up resources
6. Monitor **Idle Resources** percentage (top stats)

**What to Look For:**
- Conflict detection (wrong skill level, machine type)
- Material availability checks
- Priority-based work order sorting (P1-P5 badges)
- Real-time activity log (right panel)
- Idle time reduction as resources are assigned

---

## ⚡ Common Tasks

### Stop All Systems
Close each PowerShell window or press `Ctrl+C` in each terminal.

### Restart a Single System
Close its PowerShell window and re-run the script:
```powershell
cd use_cases\vehicle_telemetry
.\run.ps1
```

### Check if Ports are Available
```powershell
netstat -ano | findstr ":5001 :5002 :5003"
```

### Kill Processes on Ports
```powershell
# Find PID
netstat -ano | findstr :5001

# Kill process
taskkill /PID <PID> /F
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Port already in use** | Stop the existing process or use `taskkill` |
| **Dependencies missing** | Run `pip install -r requirements.txt` |
| **WebSocket connection failed** | Check firewall, try `127.0.0.1` instead of `localhost` |
| **Map not loading** | Check internet connection (uses OpenStreetMap tiles) |
| **Drag-and-drop not working** | Use a modern browser (Chrome, Firefox, Edge) |

---

## 📊 System Overview

```
Vehicle Telemetry          Digital Twin            Resource Allocation
    (Port 5001)              (Port 5002)               (Port 5003)
         |                       |                          |
    Flask + SocketIO        Flask + Sim Engine       Flask + REST API
         |                       |                          |
    WebSocket Updates     Event-Driven Loop        Drag-Drop Interface
         |                       |                          |
  10 Vehicles/Realtime   5 Stations/Parametric    6 Ops + 10 Machines
```

---

## 🎯 Success Metrics

After starting all systems, you should see:

### Vehicle Telemetry ✅
- [ ] 10 vehicle markers on map
- [ ] Live position updates every second
- [ ] Battery percentage decreasing over time
- [ ] At least one vehicle entering critical status (<10%)

### Digital Twin ✅
- [ ] Assembly line with 5 stations
- [ ] Stations cycling through idle/working/down states
- [ ] Throughput chart populating over time
- [ ] Products flowing through the pipeline

### Resource Allocation ✅
- [ ] 6 operators and 10 machines listed
- [ ] Successful drag-and-drop assignments
- [ ] Work order status changing to "in_progress"
- [ ] Conflict detection messages appearing
- [ ] Idle percentage updating

---

## 🎓 Next Steps

1. **Experiment with parameters:**
   - Change batch size in Digital Twin
   - Adjust number of vehicles in Vehicle Telemetry
   - Add new work orders in Resource Allocation

2. **Explore the code:**
   - Each `app.py` is fully commented
   - HTML templates use modern CSS and vanilla JS
   - RESTful API patterns throughout

3. **Extend functionality:**
   - Add database persistence
   - Implement user authentication
   - Export reports/analytics
   - Mobile-responsive UI

---

## 📚 Full Documentation

See `README.md` for:
- Detailed API documentation
- Architecture explanations
- Configuration options
- Production deployment notes

---

Enjoy exploring the industrial use cases! 🏭🚀
