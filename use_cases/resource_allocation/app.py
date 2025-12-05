"""
Shop-Floor Resource Allocation System
Real-time resource assignment and idle time monitoring
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import random
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'resource-allocation-secret'
CORS(app)

@dataclass
class Operator:
    id: str
    name: str
    skill_level: int  # 1-5
    status: str  # 'available', 'assigned', 'break'
    current_work_order: Optional[str] = None
    hours_worked: float = 0
    efficiency_rating: float = 1.0

@dataclass
class Machine:
    id: str
    name: str
    machine_type: str
    status: str  # 'available', 'in_use', 'maintenance'
    current_work_order: Optional[str] = None
    utilization: float = 0.0
    maintenance_due: bool = False

@dataclass
class Material:
    id: str
    name: str
    quantity: int
    unit: str
    location: str
    reserved_quantity: int = 0

@dataclass
class WorkOrder:
    id: str
    product_name: str
    quantity: int
    priority: int  # 1-5, 5 being highest
    status: str  # 'pending', 'in_progress', 'completed', 'blocked'
    required_skill: int
    required_machine_type: str
    required_materials: Dict[str, int]
    assigned_operator: Optional[str] = None
    assigned_machine: Optional[str] = None
    progress: float = 0.0
    start_time: Optional[str] = None
    estimated_duration: int = 0  # minutes
    blocked_reason: Optional[str] = None

class ResourceAllocationSystem:
    def __init__(self):
        self.operators: Dict[str, Operator] = {}
        self.machines: Dict[str, Machine] = {}
        self.materials: Dict[str, Material] = {}
        self.work_orders: Dict[str, WorkOrder] = {}
        self.idle_time_log: List[Dict] = []
        self.allocation_history: List[Dict] = []
        self.initialize_resources()
        self.initialize_work_orders()
    
    def initialize_resources(self):
        """Initialize operators, machines, and materials"""
        # Operators
        operator_names = ["John Smith", "Sarah Johnson", "Mike Davis", 
                         "Emily Chen", "David Wilson", "Maria Garcia"]
        for i, name in enumerate(operator_names):
            op = Operator(
                id=f"OP-{i+1:03d}",
                name=name,
                skill_level=random.randint(2, 5),
                status='available',
                efficiency_rating=random.uniform(0.8, 1.2)
            )
            self.operators[op.id] = op
        
        # Machines
        machine_types = [
            ("CNC Mill", "milling"),
            ("CNC Lathe", "turning"),
            ("Welding Station", "welding"),
            ("Assembly Table", "assembly"),
            ("Quality Control", "inspection")
        ]
        for i, (name, mtype) in enumerate(machine_types):
            for j in range(2):  # 2 of each type
                machine = Machine(
                    id=f"MC-{i*2+j+1:03d}",
                    name=f"{name} {j+1}",
                    machine_type=mtype,
                    status='available',
                    maintenance_due=random.random() < 0.1
                )
                self.machines[machine.id] = machine
        
        # Materials
        materials_list = [
            ("Steel Sheet", 500, "kg", "Warehouse A"),
            ("Aluminum Bar", 300, "kg", "Warehouse A"),
            ("Bolts M6", 10000, "pcs", "Storage B"),
            ("Welding Rod", 200, "kg", "Workshop"),
            ("Paint", 50, "L", "Storage C")
        ]
        for i, (name, qty, unit, loc) in enumerate(materials_list):
            mat = Material(
                id=f"MAT-{i+1:03d}",
                name=name,
                quantity=qty,
                unit=unit,
                location=loc
            )
            self.materials[mat.id] = mat
    
    def initialize_work_orders(self):
        """Initialize sample work orders"""
        products = [
            ("Bracket Assembly", "milling", {"MAT-001": 5, "MAT-003": 20}, 3, 120),
            ("Shaft Component", "turning", {"MAT-002": 10}, 4, 90),
            ("Frame Weld", "welding", {"MAT-001": 15, "MAT-004": 2}, 4, 180),
            ("Final Assembly", "assembly", {"MAT-003": 50, "MAT-005": 1}, 2, 60),
            ("Quality Check", "inspection", {}, 3, 30)
        ]
        
        for i, (name, machine_type, materials, skill, duration) in enumerate(products):
            wo = WorkOrder(
                id=f"WO-{i+1:04d}",
                product_name=name,
                quantity=random.randint(10, 50),
                priority=random.randint(1, 5),
                status='pending',
                required_skill=skill,
                required_machine_type=machine_type,
                required_materials=materials,
                estimated_duration=duration
            )
            self.work_orders[wo.id] = wo
    
    def assign_operator(self, work_order_id: str, operator_id: str) -> Dict:
        """Assign operator to work order"""
        if work_order_id not in self.work_orders:
            return {'success': False, 'error': 'Work order not found'}
        if operator_id not in self.operators:
            return {'success': False, 'error': 'Operator not found'}
        
        wo = self.work_orders[work_order_id]
        op = self.operators[operator_id]
        
        # Check if operator is available
        if op.status != 'available':
            return {'success': False, 'error': 'Operator not available'}
        
        # Check skill level
        if op.skill_level < wo.required_skill:
            return {'success': False, 'error': 'Operator skill level insufficient'}
        
        # Assign
        wo.assigned_operator = operator_id
        op.status = 'assigned'
        op.current_work_order = work_order_id
        
        # Check if fully allocated
        self._check_work_order_status(work_order_id)
        
        # Log allocation
        self.allocation_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'operator_assignment',
            'work_order': work_order_id,
            'resource': operator_id
        })
        
        return {'success': True, 'message': f'Operator {operator_id} assigned to {work_order_id}'}
    
    def assign_machine(self, work_order_id: str, machine_id: str) -> Dict:
        """Assign machine to work order"""
        if work_order_id not in self.work_orders:
            return {'success': False, 'error': 'Work order not found'}
        if machine_id not in self.machines:
            return {'success': False, 'error': 'Machine not found'}
        
        wo = self.work_orders[work_order_id]
        machine = self.machines[machine_id]
        
        # Check if machine is available
        if machine.status != 'available':
            return {'success': False, 'error': 'Machine not available'}
        
        # Check machine type
        if machine.machine_type != wo.required_machine_type:
            return {'success': False, 'error': 'Wrong machine type'}
        
        # Assign
        wo.assigned_machine = machine_id
        machine.status = 'in_use'
        machine.current_work_order = work_order_id
        
        # Check if fully allocated
        self._check_work_order_status(work_order_id)
        
        # Log allocation
        self.allocation_history.append({
            'timestamp': datetime.now().isoformat(),
            'type': 'machine_assignment',
            'work_order': work_order_id,
            'resource': machine_id
        })
        
        return {'success': True, 'message': f'Machine {machine_id} assigned to {work_order_id}'}
    
    def _check_work_order_status(self, work_order_id: str):
        """Check if work order can start"""
        wo = self.work_orders[work_order_id]
        
        # Check if all resources are assigned
        if wo.assigned_operator and wo.assigned_machine:
            # Check materials
            materials_ok = True
            blocked_materials = []
            for mat_id, required_qty in wo.required_materials.items():
                if mat_id in self.materials:
                    mat = self.materials[mat_id]
                    available = mat.quantity - mat.reserved_quantity
                    if available < required_qty:
                        materials_ok = False
                        blocked_materials.append(mat.name)
            
            if materials_ok:
                wo.status = 'in_progress'
                wo.start_time = datetime.now().isoformat()
                wo.blocked_reason = None
                # Reserve materials
                for mat_id, required_qty in wo.required_materials.items():
                    if mat_id in self.materials:
                        self.materials[mat_id].reserved_quantity += required_qty
            else:
                wo.status = 'blocked'
                wo.blocked_reason = f"Insufficient materials: {', '.join(blocked_materials)}"
    
    def unassign_resources(self, work_order_id: str) -> Dict:
        """Unassign all resources from work order"""
        if work_order_id not in self.work_orders:
            return {'success': False, 'error': 'Work order not found'}
        
        wo = self.work_orders[work_order_id]
        
        # Release operator
        if wo.assigned_operator and wo.assigned_operator in self.operators:
            op = self.operators[wo.assigned_operator]
            op.status = 'available'
            op.current_work_order = None
            wo.assigned_operator = None
        
        # Release machine
        if wo.assigned_machine and wo.assigned_machine in self.machines:
            machine = self.machines[wo.assigned_machine]
            machine.status = 'available'
            machine.current_work_order = None
            wo.assigned_machine = None
        
        # Release materials
        for mat_id, required_qty in wo.required_materials.items():
            if mat_id in self.materials:
                self.materials[mat_id].reserved_quantity = max(0, 
                    self.materials[mat_id].reserved_quantity - required_qty)
        
        wo.status = 'pending'
        wo.start_time = None
        wo.blocked_reason = None
        
        return {'success': True, 'message': f'Resources released from {work_order_id}'}
    
    def get_state(self) -> Dict:
        """Get current system state"""
        # Calculate idle time
        available_operators = [op for op in self.operators.values() if op.status == 'available']
        available_machines = [m for m in self.machines.values() if m.status == 'available']
        
        idle_percentage = ((len(available_operators) / len(self.operators) +
                          len(available_machines) / len(self.machines)) / 2) * 100
        
        return {
            'operators': [asdict(op) for op in self.operators.values()],
            'machines': [asdict(m) for m in self.machines.values()],
            'materials': [asdict(mat) for mat in self.materials.values()],
            'work_orders': [asdict(wo) for wo in self.work_orders.values()],
            'idle_percentage': round(idle_percentage, 1),
            'allocation_history': self.allocation_history[-20:]  # Last 20 events
        }

# Global system instance
system = ResourceAllocationSystem()

@app.route('/')
def index():
    """Main allocation interface"""
    return render_template('allocation.html')

@app.route('/api/state')
def get_state():
    """Get current system state"""
    return jsonify(system.get_state())

@app.route('/api/assign/operator', methods=['POST'])
def assign_operator():
    """Assign operator to work order"""
    data = request.json
    result = system.assign_operator(data['work_order_id'], data['operator_id'])
    return jsonify(result)

@app.route('/api/assign/machine', methods=['POST'])
def assign_machine():
    """Assign machine to work order"""
    data = request.json
    result = system.assign_machine(data['work_order_id'], data['machine_id'])
    return jsonify(result)

@app.route('/api/unassign/<work_order_id>', methods=['POST'])
def unassign(work_order_id):
    """Unassign resources from work order"""
    result = system.unassign_resources(work_order_id)
    return jsonify(result)

@app.route('/api/work_order/new', methods=['POST'])
def create_work_order():
    """Create new work order"""
    data = request.json
    wo_id = f"WO-{len(system.work_orders)+1:04d}"
    wo = WorkOrder(
        id=wo_id,
        product_name=data['product_name'],
        quantity=data['quantity'],
        priority=data.get('priority', 3),
        status='pending',
        required_skill=data['required_skill'],
        required_machine_type=data['required_machine_type'],
        required_materials=data.get('required_materials', {}),
        estimated_duration=data.get('estimated_duration', 60)
    )
    system.work_orders[wo_id] = wo
    return jsonify({'success': True, 'work_order_id': wo_id})

if __name__ == '__main__':
    print("=" * 60)
    print("Shop-Floor Resource Allocation System")
    print("=" * 60)
    print(f"Operators: {len(system.operators)}")
    print(f"Machines: {len(system.machines)}")
    print(f"Work Orders: {len(system.work_orders)}")
    print(f"Dashboard: http://localhost:5003")
    print(f"API: http://localhost:5003/api/state")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5003, debug=True)
