"""
Enhanced Generator IoT Monitoring Demo - Complete Business System
Advanced demo with AI predictions, failure simulations, and crisis management.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pydeck as pdk
import json
import os
from datetime import datetime, timedelta
import time
import threading
from typing import Dict, List, Optional
from pathlib import Path
import random
import math

# Page configuration
st.set_page_config(
    page_title="AI-Powered Generator Monitoring",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .crisis-mode {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        border: 2px solid #ff4757;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
    }
    .success-card {
        background: linear-gradient(135deg, #2ed573 0%, #1e90ff 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .prediction-card {
        background: linear-gradient(135deg, #ffa726 0%, #fb8c00 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    .demo-control {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Enhanced configuration
CONFIG_FILE = DATA_DIR / "config.json"
DEFAULT_CONFIG = {
    "refresh_seconds": 5,  # Faster for demo
    "demo_mode": "executive",  # executive, technical, mobile, crisis
    "auto_scenarios": True,
    "ai_predictions": True,
    "crisis_simulation": False,
    "demo_speed": 1.0,  # Time acceleration
    "guided_tour": False,
    "pricing": {"subscription": 1500, "premium": 5000, "upsell_avg": 2500},
    "thresholds_default": {
        "fuel_low": 20,
        "temp_high": 95, 
        "overload_pct": 90,
        "battery_low": 11.8,
        "efficiency_drop": 15,
        "vibration_high": 5.0
    },
    "per_customer_thresholds": {},
    "ai_models": {
        "bearing_failure": {"accuracy": 94.2, "confidence": 87.3},
        "fuel_efficiency": {"accuracy": 91.8, "confidence": 82.1},
        "maintenance_schedule": {"accuracy": 89.5, "confidence": 90.2}
    }
}

def load_config() -> Dict:
    """Load configuration from file or create default."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Merge with defaults for new keys
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config: Dict):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_seed_data():
    """Load or create enhanced seed data files."""
    
    # Enhanced Generators data with more realistic details
    generators_file = DATA_DIR / "generators.csv"
    if not generators_file.exists():
        generators_data = {
            'id': [f'GEN-{i:03d}' for i in range(1, 25)],  # Expanded to 24 units
            'name': [
                'Hospital Main ICU', 'Hospital Backup ICU', 'Hospital Surgery Wing', 'Hospital Emergency',
                'Mall Primary HVAC', 'Mall Secondary HVAC', 'Mall Food Court', 'Mall Security',
                'Factory Line-A Critical', 'Factory Line-B Critical', 'Factory Backup Power', 'Factory Emergency',
                'Data Center Primary', 'Data Center Backup', 'Data Center Cooling', 'Data Center UPS',
                'Office Building Main', 'Office Building Backup', 'Warehouse Refrigeration', 'Warehouse Backup',
                'Clinic Main Power', 'Emergency Services Backup', 'Airport Terminal', 'Airport Runway Lights'
            ],
            'customer': [
                'Saudi Medical Complex', 'Saudi Medical Complex', 'Saudi Medical Complex', 'Saudi Medical Complex',
                'Al Nakheel Mall', 'Al Nakheel Mall', 'Al Nakheel Mall', 'Al Nakheel Mall',
                'Advanced Manufacturing', 'Advanced Manufacturing', 'Advanced Manufacturing', 'Advanced Manufacturing',
                'NEOM Data Center', 'NEOM Data Center', 'NEOM Data Center', 'NEOM Data Center',
                'ARAMCO Offices', 'ARAMCO Offices', 'Logistics Hub KSA', 'Logistics Hub KSA',
                'Riyadh Healthcare', 'Emergency Services KSA', 'King Khalid Airport', 'King Khalid Airport'
            ],
            'model': [
                'CAT C32 ACERT', 'CAT C18 ACERT', 'Cummins QSX15', 'Cummins QSK19',
                'Perkins 2806C', 'Perkins 2506C', 'MTU 12V2000', 'MTU 8V2000',
                'Kohler 30RESAL', 'Kohler 25RESAL', 'Generac MD300', 'Generac MD200',
                'Detroit Diesel DD15', 'Detroit Diesel DD13', 'Yanmar 6EY26W', 'Yanmar 4TNV98',
                'Volvo Penta D13', 'Volvo Penta D8', 'Liebherr D9508', 'Liebherr D9406',
                'John Deere 6135', 'Kubota V3800', 'MAN D2676', 'MAN D2066'
            ],
            'controller_protocol': ['Modbus'] * 8 + ['CAN'] * 8 + ['RS485'] * 8,
            'rated_kw': [
                2000, 1500, 1000, 800, 1200, 800, 600, 400,
                2500, 2000, 1800, 1200, 3000, 2500, 2000, 1500,
                1000, 750, 800, 600, 500, 400, 1500, 800
            ],
            'lat': [
                24.7136, 24.7126, 24.7146, 24.7156,  # Riyadh Medical
                21.4858, 21.4868, 21.4848, 21.4878,  # Jeddah Mall
                26.4207, 26.4217, 26.4197, 26.4227,  # Dammam Industrial
                25.2854, 25.2864, 25.2844, 25.2874,  # NEOM
                24.6877, 24.6887, 21.4225, 21.4235,  # ARAMCO & Logistics
                24.7284, 24.7294, 24.9573, 24.9583   # Healthcare & Airport
            ],
            'lon': [
                46.6753, 46.6763, 46.6743, 46.6773,
                39.1925, 39.1935, 39.1915, 39.1945,
                50.0888, 50.0898, 50.0878, 50.0908,
                35.3254, 35.3264, 35.3244, 35.3274,
                46.7219, 46.7229, 39.2563, 39.2573,
                46.6384, 46.6394, 46.6198, 46.6208
            ],
            'install_date': [
                '2020-01-15', '2020-02-20', '2019-06-10', '2019-07-15',
                '2021-03-20', '2021-04-25', '2020-09-12', '2018-11-30',
                '2019-01-15', '2020-05-08', '2021-08-22', '2019-10-05',
                '2022-03-15', '2022-04-20', '2021-12-10', '2021-11-25',
                '2020-07-18', '2020-08-22', '2019-09-30', '2019-10-15',
                '2021-05-12', '2020-12-08', '2022-01-20', '2022-02-25'
            ],
            'status': [
                'Running', 'Running', 'Running', 'Standby',
                'Running', 'Running', 'Standby', 'Running',
                'Running', 'Running', 'Standby', 'Running',
                'Running', 'Running', 'Running', 'Standby',
                'Running', 'Standby', 'Running', 'Running',
                'Fault', 'Running', 'Running', 'Maintenance'
            ],
            'subscription_tier': [
                'Premium', 'Premium', 'Pro', 'Basic',
                'Pro', 'Pro', 'Basic', 'Premium',
                'Premium', 'Premium', 'Pro', 'Basic',
                'Premium', 'Premium', 'Premium', 'Pro',
                'Pro', 'Basic', 'Pro', 'Basic',
                'Premium', 'Premium', 'Premium', 'Pro'
            ],
            'criticality': [
                'Critical', 'Critical', 'Critical', 'High',
                'Medium', 'Medium', 'Low', 'Medium',
                'Critical', 'Critical', 'High', 'Medium',
                'Critical', 'Critical', 'Critical', 'High',
                'Medium', 'Low', 'High', 'Medium',
                'High', 'Critical', 'High', 'Medium'
            ],
            'maintenance_contract': ['Full Service'] * 16 + ['Basic'] * 8,
            'next_service_hours': [random.randint(-200, 500) for _ in range(24)]
        }
        pd.DataFrame(generators_data).to_csv(generators_file, index=False)
    
    # Enhanced Customers data
    customers_file = DATA_DIR / "customers.csv"
    if not customers_file.exists():
        customers_data = {
            'id': ['CUST-001', 'CUST-002', 'CUST-003', 'CUST-004', 'CUST-005', 'CUST-006'],
            'name': ['Saudi Medical Complex', 'Al Nakheel Mall', 'Advanced Manufacturing', 
                    'NEOM Data Center', 'ARAMCO Offices', 'King Khalid Airport'],
            'contact_email': ['ops@saudimedical.sa', 'facility@alnakheel.sa', 'maint@advmfg.sa',
                            'ops@neom.sa', 'facility@aramco.com', 'ops@riyadhairport.sa'],
            'city': ['Riyadh', 'Jeddah', 'Dammam', 'NEOM', 'Riyadh', 'Riyadh'],
            'country': ['Saudi Arabia'] * 6,
            'industry': ['Healthcare', 'Retail', 'Manufacturing', 'Technology', 'Energy', 'Transportation'],
            'contract_value': [2500000, 800000, 1200000, 3000000, 1800000, 1500000],
            'sla_uptime': [99.9, 99.5, 99.7, 99.95, 99.8, 99.9],
            'criticality_level': ['Critical', 'Medium', 'High', 'Critical', 'High', 'Critical']
        }
        pd.DataFrame(customers_data).to_csv(customers_file, index=False)
    
    # Initialize empty data files
    for filename, columns in [
        ('telemetry.parquet', ['ts', 'generator_id', 'fuel_pct', 'load_pct', 'temp_c', 
                              'voltage', 'run_hours', 'status', 'lat', 'lon', 'efficiency_pct',
                              'vibration_level', 'noise_db', 'hours_since_service']),
        ('alerts.csv', ['id', 'generator_id', 'rule', 'severity', 'message', 'ts',
                       'ack_by', 'ack_ts', 'status', 'notes', 'predicted', 'confidence',
                       'cost_impact', 'root_cause']),
        ('maintenance.csv', ['id', 'generator_id', 'type', 'due_by_date', 'due_at_run_hours',
                           'completed_ts', 'assigned_to', 'priority', 'notes', 'cost_estimate',
                           'parts_required', 'downtime_estimate']),
        ('tickets.csv', ['id', 'generator_id', 'created_by_role', 'created_ts', 'summary',
                        'status', 'assigned_to', 'parts_suggested', 'priority', 'eta',
                        'customer_impact', 'technician_location']),
        ('predictions.csv', ['id', 'generator_id', 'prediction_type', 'predicted_failure',
                           'confidence', 'time_to_failure', 'recommended_action', 'cost_savings',
                           'created_ts', 'model_version']),
        ('scenarios.csv', ['id', 'name', 'description', 'active', 'start_time', 'duration',
                         'affected_generators', 'severity', 'auto_resolve'])
    ]:
        filepath = DATA_DIR / filename
        if not filepath.exists():
            empty_df = pd.DataFrame(columns=columns)
            if filename.endswith('.parquet'):
                empty_df.to_parquet(filepath, index=False)
            else:
                empty_df.to_csv(filepath, index=False)

class EnhancedTelemetrySimulator:
    """Advanced telemetry simulator with realistic failure patterns and AI predictions."""
    
    def __init__(self):
        try:
            self.generators_df = pd.read_csv(DATA_DIR / "generators.csv")
        except Exception as e:
            st.error(f"Error loading generators data: {str(e)}")
            self.generators_df = pd.DataFrame()
            return
            
        self.config = load_config()
        self.last_telemetry = {}
        self.consecutive_counts = {}
        self.failure_patterns = {}  # Track ongoing failure simulations
        self.ai_predictions = {}   # Store AI predictions
        
        # Initialize telemetry state with enhanced metrics
        for _, gen in self.generators_df.iterrows():
            self.last_telemetry[gen['id']] = {
                'fuel_pct': np.random.uniform(30, 90),
                'load_pct': np.random.uniform(20, 70),
                'temp_c': np.random.uniform(70, 85),
                'voltage': np.random.uniform(12.2, 13.8),
                'run_hours': np.random.uniform(1000, 8000),
                'efficiency_pct': np.random.uniform(85, 95),
                'vibration_level': np.random.uniform(1.0, 3.0),
                'noise_db': np.random.uniform(65, 75),
                'hours_since_service': np.random.uniform(0, 500)
            }
            self.consecutive_counts[gen['id']] = {
                'fuel_low': 0, 'temp_high': 0, 'overload': 0, 'overload_start': None
            }
            self.failure_patterns[gen['id']] = {
                'bearing_wear': {'active': False, 'progress': 0, 'start_time': None},
                'fuel_degradation': {'active': False, 'progress': 0, 'start_time': None},
                'cooling_failure': {'active': False, 'progress': 0, 'start_time': None}
            }
    
    def start_failure_scenario(self, generator_id: str, failure_type: str, duration_hours: int = 72):
        """Start a realistic failure scenario."""
        if generator_id in self.failure_patterns:
            self.failure_patterns[generator_id][failure_type] = {
                'active': True,
                'progress': 0,
                'start_time': datetime.now(),
                'duration': duration_hours
            }
    
    def generate_ai_predictions(self, generator_id: str, telemetry_data: Dict) -> List[Dict]:
        """Generate AI-powered predictions based on telemetry patterns."""
        predictions = []
        
        # Bearing failure prediction
        vibration = telemetry_data.get('vibration_level', 2.0)
        temp = telemetry_data.get('temp_c', 75)
        hours_since_service = telemetry_data.get('hours_since_service', 100)
        
        # Complex prediction algorithm simulation
        bearing_risk = (vibration - 2.0) * 20 + (temp - 80) * 5 + (hours_since_service / 100) * 10
        bearing_risk = max(0, min(100, bearing_risk + np.random.normal(0, 5)))
        
        if bearing_risk > 70:
            time_to_failure = max(24, 720 - bearing_risk * 8)  # Hours
            predictions.append({
                'id': f'PRED-{int(time.time())}-{generator_id}',
                'generator_id': generator_id,
                'prediction_type': 'Bearing Failure',
                'predicted_failure': 'Main bearing wear detected',
                'confidence': min(99, 60 + bearing_risk * 0.4),
                'time_to_failure': time_to_failure,
                'recommended_action': 'Schedule bearing inspection within 48 hours',
                'cost_savings': random.randint(15000, 45000),
                'created_ts': datetime.now(),
                'model_version': 'BearingAI-v2.1'
            })
        
        # Efficiency degradation prediction
        efficiency = telemetry_data.get('efficiency_pct', 90)
        if efficiency < 88:
            predictions.append({
                'id': f'PRED-{int(time.time())}-EFF-{generator_id}',
                'generator_id': generator_id,
                'prediction_type': 'Efficiency Drop',
                'predicted_failure': f'Performance declining: {efficiency:.1f}% efficiency',
                'confidence': 87.3,
                'time_to_failure': random.randint(168, 720),  # 1-4 weeks
                'recommended_action': 'Fuel system cleaning recommended',
                'cost_savings': random.randint(8000, 25000),
                'created_ts': datetime.now(),
                'model_version': 'EfficiencyAI-v1.8'
            })
        
        return predictions
    
    def apply_failure_patterns(self, gen_id: str, base_data: Dict) -> Dict:
        """Apply realistic failure progression to telemetry data."""
        data = base_data.copy()
        patterns = self.failure_patterns[gen_id]
        
        # Bearing wear progression
        if patterns['bearing_wear']['active']:
            progress = patterns['bearing_wear']['progress']
            data['vibration_level'] += progress * 0.1
            data['temp_c'] += progress * 0.05
            data['noise_db'] += progress * 0.02
            patterns['bearing_wear']['progress'] += 0.5
            
            if progress > 100:  # Complete failure
                data['status'] = 'Fault'
                patterns['bearing_wear']['active'] = False
        
        # Fuel system degradation
        if patterns['fuel_degradation']['active']:
            progress = patterns['fuel_degradation']['progress']
            data['efficiency_pct'] -= progress * 0.003
            data['load_pct'] *= (1 - progress * 0.002)
            patterns['fuel_degradation']['progress'] += 0.3
        
        # Cooling system issues
        if patterns['cooling_failure']['active']:
            progress = patterns['cooling_failure']['progress']
            data['temp_c'] += progress * 0.08
            if data['temp_c'] > 105:
                data['status'] = 'Fault'
            patterns['cooling_failure']['progress'] += 0.4
        
        return data
    
    def generate_tick(self) -> pd.DataFrame:
        """Generate enhanced telemetry with failure patterns and predictions."""
        new_data = []
        predictions = []
        current_time = datetime.now()
        
        # Check for active scenarios
        crisis_mode = self.config.get('crisis_simulation', False)
        demo_speed = self.config.get('demo_speed', 1.0)
        
        for _, gen in self.generators_df.iterrows():
            gen_id = gen['id']
            last = self.last_telemetry[gen_id]
            
            if gen['status'] == 'Running':
                # Base telemetry evolution
                fuel_consumption = np.random.uniform(0.05, 0.8) * demo_speed
                new_fuel = max(0, last['fuel_pct'] - fuel_consumption)
                
                # Random refuel events
                if np.random.random() < 0.03 or new_fuel < 5:
                    new_fuel = np.random.uniform(85, 100)
                
                # Enhanced load patterns with business logic
                hour = current_time.hour
                day_of_week = current_time.weekday()
                
                # Business hour patterns based on customer type
                customer = gen['customer']
                if 'Medical' in customer or 'Healthcare' in customer:
                    # Hospitals: high load 24/7 with peak during day
                    base_load = 60 + (20 if 6 <= hour <= 22 else 10)
                elif 'Mall' in customer:
                    # Retail: peak during shopping hours
                    if day_of_week < 5:  # Weekday
                        base_load = 40 + (30 if 10 <= hour <= 21 else 0)
                    else:  # Weekend
                        base_load = 50 + (40 if 10 <= hour <= 22 else 10)
                elif 'Data Center' in customer:
                    # Data centers: consistent high load
                    base_load = 70 + np.random.normal(0, 5)
                elif 'Manufacturing' in customer:
                    # Factories: high during work hours
                    base_load = 30 + (50 if 6 <= hour <= 18 and day_of_week < 5 else 5)
                else:
                    base_load = 40
                
                # Add variations and crisis scenarios
                load_variation = np.random.normal(0, 8)
                new_load = np.clip(base_load + load_variation, 5, 100)
                
                if crisis_mode:
                    new_load *= 1.3  # Increased load during crisis
                
                # Temperature with environmental factors
                ambient_temp = 25 + np.random.normal(0, 8)
                if crisis_mode:  # Heat wave simulation
                    ambient_temp += 15
                
                target_temp = 65 + (new_load * 0.25) + (ambient_temp * 0.1)
                temp_change = np.clip(target_temp - last['temp_c'], -3, 3)
                new_temp = last['temp_c'] + temp_change
                
                # Enhanced electrical parameters
                voltage_change = np.random.normal(0, 0.08)
                new_voltage = np.clip(last['voltage'] + voltage_change, 11.0, 14.5)
                
                # Battery issues during crisis
                if crisis_mode and np.random.random() < 0.02:
                    new_voltage = np.random.uniform(10.8, 11.9)
                
                # Efficiency tracking
                base_efficiency = 92 - (new_load / 100) * 5  # Efficiency drops with load
                efficiency_noise = np.random.normal(0, 1)
                new_efficiency = np.clip(base_efficiency + efficiency_noise, 70, 98)
                
                # Vibration and noise
                base_vibration = 2.0 + (new_load / 100) * 1.5
                new_vibration = base_vibration + np.random.normal(0, 0.3)
                
                base_noise = 68 + (new_load / 100) * 8
                new_noise = base_noise + np.random.normal(0, 2)
                
                # Run hours and service tracking
                new_run_hours = last['run_hours'] + np.random.uniform(0.08, 0.25) * demo_speed
                new_hours_since_service = last['hours_since_service'] + np.random.uniform(0.08, 0.25) * demo_speed
                
            else:
                # Stopped/Fault generators
                new_fuel = last['fuel_pct']
                new_load = 0
                new_temp = max(last['temp_c'] - np.random.uniform(1, 3), 20)
                new_voltage = last['voltage'] + np.random.normal(0, 0.03)
                new_efficiency = 0
                new_vibration = 0.5
                new_noise = 45
                new_run_hours = last['run_hours']
                new_hours_since_service = last['hours_since_service']
            
            # Apply failure patterns
            telemetry_dict = {
                'fuel_pct': new_fuel, 'load_pct': new_load, 'temp_c': new_temp,
                'voltage': new_voltage, 'run_hours': new_run_hours,
                'efficiency_pct': new_efficiency, 'vibration_level': new_vibration,
                'noise_db': new_noise, 'hours_since_service': new_hours_since_service
            }
            
            telemetry_dict = self.apply_failure_patterns(gen_id, telemetry_dict)
            
            # Update last telemetry
            self.last_telemetry[gen_id] = telemetry_dict
            
            # Generate AI predictions
            if self.config.get('ai_predictions', True) and np.random.random() < 0.1:  # 10% chance per tick
                ai_preds = self.generate_ai_predictions(gen_id, telemetry_dict)
                predictions.extend(ai_preds)
            
            # Create telemetry record
            record = {
                'ts': current_time,
                'generator_id': gen_id,
                'status': gen['status'],
                'lat': gen['lat'],
                'lon': gen['lon'],
                **telemetry_dict
            }
            new_data.append(record)
        
        # Save AI predictions
        if predictions:
            try:
                existing_predictions = pd.read_csv(DATA_DIR / "predictions.csv")
                combined_predictions = pd.concat([existing_predictions, pd.DataFrame(predictions)], ignore_index=True)
                combined_predictions.to_csv(DATA_DIR / "predictions.csv", index=False)
            except Exception:
                pd.DataFrame(predictions).to_csv(DATA_DIR / "predictions.csv", index=False)
        
        return pd.DataFrame(new_data)
    
    def check_enhanced_alerts(self, telemetry_df: pd.DataFrame) -> List[Dict]:
        """Generate enhanced alerts with AI insights and cost impact."""
        new_alerts = []
        alert_id_counter = 1
        
        try:
            existing_alerts = pd.read_csv(DATA_DIR / "alerts.csv")
            alert_id_counter = len(existing_alerts) + 1
        except Exception:
            pass
        
        for _, row in telemetry_df.iterrows():
            gen_id = row['generator_id']
            
            # Get generator info for context
            gen_info = self.generators_df[self.generators_df['id'] == gen_id].iloc[0]
            criticality = gen_info.get('criticality', 'Medium')
            customer = gen_info.get('customer', 'Unknown')
            
            # Enhanced alert generation with business impact
            alerts_to_generate = []
            
            # Critical temperature with cost impact
            if row['temp_c'] > 100:
                cost_impact = 25000 if criticality == 'Critical' else 10000
                alerts_to_generate.append({
                    'rule': 'Critical Temperature',
                    'severity': 'CRITICAL',
                    'message': f'Dangerous temperature: {row["temp_c"]:.1f}°C - Immediate shutdown required',
                    'predicted': False,
                    'confidence': 95,
                    'cost_impact': cost_impact,
                    'root_cause': 'Cooling system failure or blockage'
                })
            
            # AI-detected bearing issues
            if row['vibration_level'] > 4.5:
                cost_impact = 45000 if criticality == 'Critical' else 20000
                alerts_to_generate.append({
                    'rule': 'AI: Bearing Failure Risk',
                    'severity': 'WARNING',
                    'message': f'AI detected bearing anomaly: {row["vibration_level"]:.2f} level',
                    'predicted': True,
                    'confidence': 87,
                    'cost_impact': cost_impact,
                    'root_cause': 'Bearing wear detected by vibration analysis'
                })
            
            # Efficiency degradation
            if row['efficiency_pct'] < 82:
                cost_impact = 15000 if criticality == 'Critical' else 7500
                alerts_to_generate.append({
                    'rule': 'Performance Degradation',
                    'severity': 'WARNING',
                    'message': f'Efficiency dropped to {row["efficiency_pct"]:.1f}% - Service needed',
                    'predicted': False,
                    'confidence': 92,
                    'cost_impact': cost_impact,
                    'root_cause': 'Fuel system contamination or filter blockage'
                })
            
            # Critical fuel with customer impact
            if row['fuel_pct'] < 15:
                if 'Medical' in customer or 'Hospital' in customer:
                    cost_impact = 100000  # Patient safety impact
                    message = f'CRITICAL: Hospital backup power at {row["fuel_pct"]:.1f}% - Patient safety risk'
                elif 'Data Center' in customer:
                    cost_impact = 500000  # SLA penalties
                    message = f'CRITICAL: Data center fuel at {row["fuel_pct"]:.1f}% - SLA breach imminent'
                else:
                    cost_impact = 25000
                    message = f'Low fuel level: {row["fuel_pct"]:.1f}%'
                
                alerts_to_generate.append({
                    'rule': 'Critical Fuel Level',
                    'severity': 'CRITICAL',
                    'message': message,
                    'predicted': False,
                    'confidence': 100,
                    'cost_impact': cost_impact,
                    'root_cause': 'Fuel consumption higher than expected or delivery delay'
                })
            
            # Generate alert records
            for alert_data in alerts_to_generate:
                alert = {
                    'id': f'ALT-{alert_id_counter:06d}',
                    'generator_id': gen_id,
                    'ts': row['ts'],
                    'ack_by': '',
                    'ack_ts': '',
                    'status': 'OPEN',
                    'notes': '',
                    **alert_data
                }
                new_alerts.append(alert)
                alert_id_counter += 1
        
        return new_alerts

def load_data_files():
    """Load all data files with enhanced error handling."""
    data = {}
    
    # Load generators with auto-regeneration
    try:
        data['generators'] = pd.read_csv(DATA_DIR / "generators.csv")
        if data['generators'].empty:
            load_seed_data()
            data['generators'] = pd.read_csv(DATA_DIR / "generators.csv")
    except Exception:
        load_seed_data()
        try:
            data['generators'] = pd.read_csv(DATA_DIR / "generators.csv")
        except Exception as e:
            st.error(f"Failed to load generators: {str(e)}")
            data['generators'] = pd.DataFrame()
    
    # Load all other data files
    file_configs = [
        ('customers', 'csv'), ('telemetry', 'parquet'), ('alerts', 'csv'),
        ('maintenance', 'csv'), ('tickets', 'csv'), ('predictions', 'csv'), ('scenarios', 'csv')
    ]
    
    for name, file_type in file_configs:
        try:
            if file_type == 'parquet':
                data[name] = pd.read_parquet(DATA_DIR / f"{name}.parquet")
            else:
                data[name] = pd.read_csv(DATA_DIR / f"{name}.csv")
        except Exception:
            data[name] = pd.DataFrame()
    
    return data

def save_telemetry(new_data: pd.DataFrame):
    """Save telemetry with enhanced data retention."""
    try:
        telemetry_file = DATA_DIR / "telemetry.parquet"
        if telemetry_file.exists():
            existing = pd.read_parquet(telemetry_file)
            combined = pd.concat([existing, new_data], ignore_index=True)
            # Keep last 72 hours for better demo experience
            cutoff = datetime.now() - timedelta(hours=72)
            combined = combined[pd.to_datetime(combined['ts']) > cutoff]
            combined.to_parquet(telemetry_file, index=False)
        else:
            new_data.to_parquet(telemetry_file, index=False)
    except Exception as e:
        st.error(f"Error saving telemetry: {str(e)}")

def save_alerts(alerts_df: pd.DataFrame):
    """Save alerts with enhanced tracking."""
    try:
        alerts_df.to_csv(DATA_DIR / "alerts.csv", index=False)
    except Exception as e:
        st.error(f"Error saving alerts: {str(e)}")

def authenticate():
    """Enhanced authentication with demo personas."""
    st.title("🤖 AI-Powered Generator Monitoring System")
    st.markdown("### Next-Generation Predictive Maintenance Platform")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        
        demo_accounts = {
            "executive@demo": "👔 Executive Dashboard - C-Suite View",
            "operator@demo": "🔧 Operations Center - Technical View", 
            "technician@demo": "📱 Field Technician - Mobile Interface",
            "customer@demo": "🏢 Customer Portal - Client View"
        }
        
        selected_account = st.selectbox(
            "Select Demo Persona:",
            options=list(demo_accounts.keys()),
            format_func=lambda x: demo_accounts[x]
        )
        
        if st.button("🚀 Launch Demo", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = selected_account
            st.session_state.role_name = demo_accounts[selected_account]
            
            # Set demo mode based on persona
            config = load_config()
            if "executive" in selected_account:
                config['demo_mode'] = 'executive'
            elif "operator" in selected_account:
                config['demo_mode'] = 'technical'
            elif "technician" in selected_account:
                config['demo_mode'] = 'mobile'
            else:
                config['demo_mode'] = 'customer'
            save_config(config)
            
            st.rerun()
        
        st.markdown("---")
        
        # Demo features preview
        st.markdown("### ✨ Demo Features")
        features = [
            "🧠 **AI Failure Prediction** - 94% accuracy rate",
            "⚡ **Real-time Crisis Management** - Emergency response protocols",
            "📊 **Predictive Analytics** - 30-day failure forecasting",
            "📱 **Mobile-First Design** - Field technician interface",
            "💰 **ROI Calculator** - Real cost impact analysis",
            "🎭 **Guided Scenarios** - Interactive failure simulations"
        ]
        for feature in features:
            st.markdown(feature)

def show_demo_control_center():
    """Demo master control panel for impressive demonstrations."""
    if st.session_state.get('user_role') == 'executive@demo':
        with st.sidebar.expander("🎭 Demo Control Center", expanded=False):
            st.markdown("### Scenario Controls")
            
            config = load_config()
            
            # Crisis simulation toggle
            crisis_mode = st.toggle("🚨 Crisis Mode", value=config.get('crisis_simulation', False))
            if crisis_mode != config.get('crisis_simulation', False):
                config['crisis_simulation'] = crisis_mode
                save_config(config)
                if crisis_mode:
                    st.success("🚨 Crisis mode activated!")
                    # Start multiple failures
                    simulator = EnhancedTelemetrySimulator()
                    simulator.start_failure_scenario('GEN-001', 'bearing_wear', 48)
                    simulator.start_failure_scenario('GEN-005', 'cooling_failure', 24)
                else:
                    st.info("Crisis mode deactivated")
            
            # Demo speed control
            demo_speed = st.slider("⏱️ Time Acceleration", 0.5, 5.0, config.get('demo_speed', 1.0), 0.5)
            if demo_speed != config.get('demo_speed', 1.0):
                config['demo_speed'] = demo_speed
                save_config(config)
            
            st.markdown("### Quick Scenarios")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🏥 Hospital Emergency"):
                    simulator = EnhancedTelemetrySimulator()
                    simulator.start_failure_scenario('GEN-001', 'fuel_degradation', 36)
                    st.success("Hospital emergency triggered!")
                
                if st.button("🌡️ Heat Wave"):
                    config['crisis_simulation'] = True
                    save_config(config)
                    st.success("Heat wave simulation started!")
            
            with col2:
                if st.button("⚡ Grid Failure"):
                    # Simulate multiple generators under high load
                    st.success("Grid failure simulation started!")
                
                if st.button("🔧 Maintenance Alert"):
                    # Trigger predictive maintenance alerts
                    st.success("Maintenance alerts generated!")
            
            # AI prediction controls
            st.markdown("### AI Features")
            ai_enabled = st.toggle("🧠 AI Predictions", value=config.get('ai_predictions', True))
            if ai_enabled != config.get('ai_predictions', True):
                config['ai_predictions'] = ai_enabled
                save_config(config)

def show_executive_dashboard():
    """Enhanced executive dashboard with business metrics."""
    config = load_config()
    
    # Crisis mode banner
    if config.get('crisis_simulation', False):
        st.markdown("""
        <div class="crisis-mode">
            <h2>🚨 CRISIS MODE ACTIVE</h2>
            <p>Multiple generator failures detected - Emergency protocols activated</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.title("👔 Executive Command Center")
    st.markdown("### Real-time Fleet Performance & Business Impact")
    
    # Load data
    data = load_data_files()
    generators_df = data['generators']
    
    if generators_df.empty:
        st.error("No generator data available")
        return
    
    telemetry_df = data['telemetry']
    alerts_df = data['alerts']
    predictions_df = data['predictions']
    
    # Executive KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate business metrics
    total_capacity = generators_df['rated_kw'].sum()
    critical_units = len(generators_df[generators_df['criticality'] == 'Critical'])
    
    # Contract values
    customers_df = data['customers']
    total_contract_value = customers_df['contract_value'].sum() if not customers_df.empty else 0
    
    # Availability calculation
    online_units = len(generators_df[generators_df['status'] == 'Running'])
    availability = (online_units / len(generators_df) * 100) if len(generators_df) > 0 else 0
    
    # Alert metrics
    critical_alerts = len(alerts_df[(alerts_df['severity'] == 'CRITICAL') & (alerts_df['status'] == 'OPEN')])
    ai_predictions = len(predictions_df[predictions_df['confidence'] > 80]) if not predictions_df.empty else 0
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Fleet Availability</h3>
            <h1>{:.1f}%</h1>
            <p>Target: 99.5%</p>
        </div>
        """.format(availability), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Capacity</h3>
            <h1>{:,.0f} kW</h1>
            <p>{} Critical Units</p>
        </div>
        """.format(total_capacity, critical_units), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Contract Value</h3>
            <h1>${:,.0f}</h1>
            <p>Annual Revenue</p>
        </div>
        """.format(total_contract_value), unsafe_allow_html=True)
    
    with col4:
        alert_color = "crisis-mode" if critical_alerts > 0 else "success-card"
        st.markdown("""
        <div class="{}">
            <h3>Critical Alerts</h3>
            <h1>{}</h1>
            <p>Immediate attention</p>
        </div>
        """.format(alert_color, critical_alerts), unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="prediction-card">
            <h3>AI Predictions</h3>
            <h1>{}</h1>
            <p>High confidence</p>
        </div>
        """.format(ai_predictions), unsafe_allow_html=True)
    
    # Business Impact Section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Financial Impact Analysis")
        
        # Calculate cost avoidance
        if not alerts_df.empty and 'cost_impact' in alerts_df.columns:
            prevented_costs = alerts_df[alerts_df['predicted'] == True]['cost_impact'].sum()
            reactive_costs = alerts_df[alerts_df['predicted'] == False]['cost_impact'].sum()
        else:
            prevented_costs = 250000
            reactive_costs = 125000
        
        # ROI calculation
        annual_service_cost = 180000  # Platform cost
        savings = prevented_costs + (reactive_costs * 0.6)  # 60% reduction in reactive costs
        roi = ((savings - annual_service_cost) / annual_service_cost) * 100
        
        metrics_data = {
            'Metric': ['Prevented Downtime Costs', 'Reactive Maintenance Savings', 'Annual Platform Cost', 'Net Savings', 'ROI'],
            'Value': [f'${prevented_costs:,.0f}', f'${reactive_costs * 0.6:,.0f}', f'${annual_service_cost:,.0f}', 
                     f'${savings - annual_service_cost:,.0f}', f'{roi:.0f}%'],
            'Status': ['✅ Prevented', '✅ Reduced', '💰 Investment', '💚 Profit', '📈 Return']
        }
        
        st.dataframe(pd.DataFrame(metrics_data), hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("🎯 SLA Performance by Customer")
        
        if not customers_df.empty:
            # Mock SLA performance data
            sla_data = customers_df.copy()
            sla_data['Current_Uptime'] = np.random.uniform(99.1, 99.9, len(sla_data))
            sla_data['SLA_Status'] = sla_data.apply(
                lambda x: '✅ Met' if x['Current_Uptime'] >= x['sla_uptime'] else '⚠️ Risk', axis=1
            )
            
            fig = px.bar(sla_data, x='name', y='Current_Uptime', 
                        color='SLA_Status', title="Customer SLA Performance",
                        color_discrete_map={'✅ Met': '#2ed573', '⚠️ Risk': '#ffa726'})
            fig.update_layout(height=400, xaxis_tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
    
    # Predictive Analytics Section
    st.markdown("---")
    st.subheader("🔮 AI-Powered Predictive Analytics")
    
    if not predictions_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Prediction confidence distribution
            fig = px.histogram(predictions_df, x='confidence', nbins=10,
                             title="AI Prediction Confidence Distribution")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Top predictions table
            top_predictions = predictions_df.nlargest(5, 'confidence')[
                ['generator_id', 'prediction_type', 'confidence', 'cost_savings']
            ]
            st.write("**Top AI Predictions:**")
            st.dataframe(top_predictions, hide_index=True, use_container_width=True)

def show_crisis_management():
    """Crisis management dashboard for emergency situations."""
    st.title("🚨 Crisis Management Center")
    st.markdown("### Emergency Response & Recovery Operations")
    
    data = load_data_files()
    generators_df = data['generators']
    alerts_df = data['alerts']
    
    # Crisis status overview
    critical_generators = generators_df[generators_df['status'].isin(['Fault', 'Maintenance'])]
    critical_alerts = alerts_df[alerts_df['severity'] == 'CRITICAL']
    
    if len(critical_generators) > 0 or len(critical_alerts) > 0:
        st.markdown("""
        <div class="crisis-mode">
            <h2>⚠️ ACTIVE CRISIS SITUATION</h2>
            <p>Multiple critical issues detected - Emergency protocols in effect</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Emergency metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Affected Units", len(critical_generators), delta="🚨" if len(critical_generators) > 0 else "✅")
    
    with col2:
        affected_customers = critical_generators['customer'].nunique() if not critical_generators.empty else 0
        st.metric("Impacted Customers", affected_customers)
    
    with col3:
        lost_capacity = critical_generators['rated_kw'].sum() if not critical_generators.empty else 0
        st.metric("Lost Capacity", f"{lost_capacity:,.0f} kW")
    
    with col4:
        estimated_cost = len(critical_alerts) * 50000  # Rough estimate
        st.metric("Est. Impact Cost", f"${estimated_cost:,.0f}")
    
    # Crisis timeline and actions
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Priority Actions")
        
        if not critical_alerts.empty:
            for _, alert in critical_alerts.head(5).iterrows():
                with st.container():
                    st.markdown(f"**🚨 {alert['rule']}**")
                    st.write(f"Generator: {alert['generator_id']}")
                    st.write(f"Impact: ${alert.get('cost_impact', 25000):,.0f}")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"Dispatch Team", key=f"dispatch_{alert['id']}"):
                            st.success("Technician dispatched!")
                    with col_b:
                        if st.button(f"Notify Customer", key=f"notify_{alert['id']}"):
                            st.success("Customer notified!")
                    st.markdown("---")
    
    with col2:
        st.subheader("📊 Load Redistribution")
        
        # Show how load is being redistributed
        if not generators_df.empty:
            working_generators = generators_df[generators_df['status'] == 'Running']
            
            if not working_generators.empty:
                load_data = working_generators.copy()
                load_data['Current_Load'] = np.random.uniform(60, 95, len(load_data))
                load_data['Capacity_Available'] = 100 - load_data['Current_Load']
                
                fig = px.bar(load_data.head(10), x='id', y=['Current_Load', 'Capacity_Available'],
                           title="Generator Load Distribution",
                           color_discrete_map={'Current_Load': '#ff6b6b', 'Capacity_Available': '#51cf66'})
                fig.update_layout(height=400, xaxis_tickangle=45)
                st.plotly_chart(fig, use_container_width=True)

def show_mobile_interface():
    """Mobile-optimized technician interface."""
    st.title("📱 Field Technician Interface")
    st.markdown("### Mobile-Optimized Work Management")
    
    # Technician info
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/100x100/007bff/white?text=👨‍🔧", width=100)
    with col2:
        st.write("**Ahmad Al-Rashid**")
        st.write("Senior Technician")
        st.write("📍 Riyadh Region")
        st.write("🕐 Shift: 08:00 - 17:00")
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Today's Jobs", "3", delta="1 urgent")
    with col2:
        st.metric("Completion Rate", "94%", delta="+2%")
    with col3:
        st.metric("Response Time", "18 min", delta="-5 min")
    
    # Active work orders
    st.subheader("🔧 Active Work Orders")
    
    work_orders = [
        {
            'id': 'WO-2024-1247',
            'generator': 'GEN-001',
            'customer': 'Saudi Medical Complex',
            'priority': 'URGENT',
            'issue': 'High temperature alert - Cooling system check required',
            'eta': '45 min',
            'distance': '12 km'
        },
        {
            'id': 'WO-2024-1248', 
            'generator': 'GEN-005',
            'customer': 'Al Nakheel Mall',
            'priority': 'HIGH',
            'issue': 'Scheduled maintenance - Filter replacement',
            'eta': '2 hrs',
            'distance': '28 km'
        },
        {
            'id': 'WO-2024-1249',
            'generator': 'GEN-012',
            'customer': 'NEOM Data Center',
            'priority': 'MEDIUM',
            'issue': 'Vibration sensors indicating bearing wear',
            'eta': '4 hrs',
            'distance': '45 km'
        }
    ]
    
    for wo in work_orders:
        with st.expander(f"🎯 {wo['id']} - {wo['priority']} Priority"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Generator:** {wo['generator']}")
                st.write(f"**Customer:** {wo['customer']}")
                st.write(f"**Issue:** {wo['issue']}")
            
            with col2:
                st.write(f"**ETA:** {wo['eta']}")
                st.write(f"**Distance:** {wo['distance']}")
                
                priority_color = {'URGENT': '🔴', 'HIGH': '🟡', 'MEDIUM': '🟢'}
                st.write(f"**Priority:** {priority_color.get(wo['priority'], '⚪')} {wo['priority']}")
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📍 Navigate", key=f"nav_{wo['id']}"):
                    st.success("Opening GPS navigation...")
            with col2:
                if st.button("📞 Call Customer", key=f"call_{wo['id']}"):
                    st.success("Calling customer...")
            with col3:
                if st.button("✅ Start Job", key=f"start_{wo['id']}"):
                    st.success("Job started!")
    
    # Digital forms
    st.subheader("📋 Digital Work Forms")
    
    with st.form("maintenance_form"):
        st.write("**Maintenance Completion Form**")
        
        col1, col2 = st.columns(2)
        with col1:
            work_order = st.selectbox("Work Order:", [wo['id'] for wo in work_orders])
            completion_status = st.selectbox("Status:", ["Completed", "Partial", "Escalated"])
        
        with col2:
            time_spent = st.number_input("Time Spent (hours):", min_value=0.5, max_value=8.0, value=2.0, step=0.5)
            parts_used = st.text_input("Parts Used:", placeholder="List parts...")
        
        work_performed = st.text_area("Work Performed:", placeholder="Describe the work completed...")
        
        # Photo upload simulation
        st.write("**Documentation Photos:**")
        uploaded_files = st.file_uploader("Upload photos", accept_multiple_files=True, type=['jpg', 'png'])
        
        # Customer signature
        st.write("**Customer Signature:**")
        signature_placeholder = st.empty()
        with signature_placeholder.container():
            st.text_input("Customer Name:", placeholder="Customer representative name")
            
        if st.form_submit_button("📄 Submit Report"):
            st.success("✅ Work order completed and submitted!")
            st.balloons()

def show_ai_predictions_center():
    """Advanced AI predictions and analytics center."""
    st.title("🧠 AI Prediction Center")
    st.markdown("### Machine Learning Powered Maintenance Forecasting")
    
    data = load_data_files()
    predictions_df = data['predictions']
    generators_df = data['generators']
    
    # AI model status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="success-card">
            <h3>Bearing Failure Model</h3>
            <h1>94.2%</h1>
            <p>Accuracy Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="success-card">
            <h3>Efficiency Model</h3>
            <h1>91.8%</h1>
            <p>Accuracy Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="success-card">
            <h3>Maintenance Model</h3>
            <h1>89.5%</h1>
            <p>Accuracy Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    if not predictions_df.empty:
        st.subheader("🎯 Active Predictions")
        
        # High confidence predictions
        high_confidence = predictions_df[predictions_df['confidence'] > 80].copy()
        
        if not high_confidence.empty:
            for _, pred in high_confidence.head(5).iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**{pred['prediction_type']}**: {pred['predicted_failure']}")
                        st.write(f"Generator: {pred['generator_id']}")
                        
                        # Progress bar for time to failure
                        if pred['time_to_failure'] > 0:
                            days_remaining = pred['time_to_failure'] / 24
                            max_days = 30
                            progress = max(0, min(1, 1 - (days_remaining / max_days)))
                            st.progress(progress, text=f"{days_remaining:.1f} days remaining")
                    
                    with col2:
                        confidence_color = "🟢" if pred['confidence'] > 90 else "🟡" if pred['confidence'] > 75 else "🟠"
                        st.metric("Confidence", f"{pred['confidence']:.1f}%", delta=confidence_color)
                    
                    with col3:
                        st.metric("Potential Savings", f"${pred['cost_savings']:,.0f}")
                        
                        if st.button(f"Create Work Order", key=f"create_wo_{pred['id']}"):
                            st.success("Work order created!")
                    
                    st.markdown("---")
        
        # Prediction trends
        st.subheader("📈 Prediction Trends")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Prediction types distribution
            pred_types = predictions_df['prediction_type'].value_counts()
            fig = px.pie(values=pred_types.values, names=pred_types.index,
                        title="Prediction Types Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Confidence over time
            predictions_df['created_ts'] = pd.to_datetime(predictions_df['created_ts'])
            daily_confidence = predictions_df.groupby(predictions_df['created_ts'].dt.date)['confidence'].mean().reset_index()
            
            fig = px.line(daily_confidence, x='created_ts', y='confidence',
                         title="Average Prediction Confidence Over Time")
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No predictions available yet. AI models are learning from your data...")
        
        # Show what the AI is analyzing
        st.subheader("🔍 AI Analysis in Progress")
        
        analysis_metrics = [
            "🌡️ Temperature patterns and thermal stress analysis",
            "🔊 Vibration signatures and bearing health assessment", 
            "⚡ Load distribution and efficiency optimization",
            "🛢️ Fuel consumption patterns and quality indicators",
            "⏰ Runtime cycles and maintenance timing optimization",
            "🌍 Environmental factors and performance correlation"
        ]
        
        for metric in analysis_metrics:
            st.write(metric)
            st.progress(np.random.uniform(0.6, 0.95))

def show_fleet_monitoring():
    """Enhanced real-time fleet monitoring with AI insights."""
    config = load_config()
    
    # Show demo control center for executives
    show_demo_control_center()
    
    st.title("⚡ AI-Enhanced Fleet Monitoring")
    
    # Auto-refresh with enhanced speed control
    refresh_interval = config['refresh_seconds']
    demo_speed = config.get('demo_speed', 1.0)
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = 0
    
    # Auto-refresh trigger
    current_time = time.time()
    if current_time - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = current_time
        
        try:
            # Generate enhanced telemetry
            simulator = EnhancedTelemetrySimulator()
            if not simulator.generators_df.empty:
                new_telemetry = simulator.generate_tick()
                save_telemetry(new_telemetry)
                
                # Generate enhanced alerts
                new_alerts = simulator.check_enhanced_alerts(new_telemetry)
                if new_alerts:
                    try:
                        existing_alerts = pd.read_csv(DATA_DIR / "alerts.csv")
                    except Exception:
                        existing_alerts = pd.DataFrame()
                    
                    combined_alerts = pd.concat([existing_alerts, pd.DataFrame(new_alerts)], ignore_index=True)
                    save_alerts(combined_alerts)
                
                st.rerun()
        except Exception as e:
            st.error(f"Simulation error: {str(e)}")
    
    # Load current data
    data = load_data_files()
    generators_df = data['generators']
    
    if generators_df.empty:
        st.error("⚠️ No generator data found!")
        return
    
    telemetry_df = data['telemetry']
    alerts_df = data['alerts']
    predictions_df = data['predictions']
    
    # Enhanced KPI Dashboard
    st.subheader("📊 Real-time Performance Dashboard")
    
    # Calculate enhanced KPIs
    total_units = len(generators_df)
    online_units = len(generators_df[generators_df['status'] == 'Running'])
    critical_units = len(generators_df[generators_df['criticality'] == 'Critical'])
    
    active_alerts = len(alerts_df[alerts_df['status'] == 'OPEN']) if not alerts_df.empty else 0
    ai_predictions = len(predictions_df) if not predictions_df.empty else 0
    
    # Enhanced metrics
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        availability = (online_units / total_units * 100) if total_units > 0 else 0
        st.metric("Fleet Availability", f"{availability:.1f}%", 
                 delta="🎯 Target: 99.5%")
    
    with col2:
        total_capacity = generators_df['rated_kw'].sum()
        st.metric("Total Capacity", f"{total_capacity:,.0f} kW",
                 delta=f"{critical_units} Critical")
    
    with col3:
        alert_color = "🚨" if active_alerts > 5 else "⚠️" if active_alerts > 0 else "✅"
        st.metric("Active Alerts", active_alerts, delta=alert_color)
    
    with col4:
        st.metric("AI Predictions", ai_predictions, delta="🧠 Learning")
    
    with col5:
        next_refresh = max(0, refresh_interval - (current_time - st.session_state.last_refresh))
        st.metric("Auto-Refresh", f"{refresh_interval}s", 
                 delta=f"Next: {next_refresh:.0f}s")
    
    with col6:
        speed_emoji = "🚀" if demo_speed > 2 else "⚡" if demo_speed > 1 else "🕐"
        st.metric("Demo Speed", f"{demo_speed:.1f}x", delta=speed_emoji)
    
    # Enhanced fleet visualization
    if not telemetry_df.empty:
        st.subheader("🏭 Enhanced Fleet Status")
        
        # Get latest telemetry
        latest_telemetry = telemetry_df.sort_values('ts').groupby('generator_id').tail(1)
        
        # Merge with generator info
        enhanced_fleet = generators_df.merge(latest_telemetry, left_on='id', right_on='generator_id', how='left')
        
        # Add health scoring
        def calculate_health_score(row):
            if pd.isna(row.get('efficiency_pct')):
                return 85  # Default for no data
            
            score = 100
            score -= max(0, (95 - row.get('efficiency_pct', 95)) * 2)  # Efficiency impact
            score -= max(0, (row.get('temp_c', 75) - 90) * 3)  # Temperature impact
            score -= max(0, (row.get('vibration_level', 2) - 3) * 10)  # Vibration impact
            score -= max(0, (12.5 - row.get('voltage', 13)) * 20)  # Voltage impact
            
            return max(20, min(100, score))
        
        enhanced_fleet['health_score'] = enhanced_fleet.apply(calculate_health_score, axis=1)
        
        # Create enhanced display
        display_columns = ['id', 'name', 'customer', 'status', 'criticality', 'health_score', 
                          'efficiency_pct', 'temp_c', 'load_pct', 'fuel_pct']
        
        display_data = enhanced_fleet[display_columns].copy()
        display_data.columns = ['ID', 'Name', 'Customer', 'Status', 'Priority', 'Health', 
                               'Efficiency %', 'Temp °C', 'Load %', 'Fuel %']
        
        # Format numeric columns
        numeric_cols = ['Health', 'Efficiency %', 'Temp °C', 'Load %', 'Fuel %']
        for col in numeric_cols:
            if col in display_data.columns:
                display_data[col] = pd.to_numeric(display_data[col], errors='coerce').round(1).fillna(0)
        
        # Color coding function
        def highlight_status(row):
            colors = []
            for val in row:
                if isinstance(val, str):
                    if val == 'Running':
                        colors.append('background-color: #d4edda')
                    elif val == 'Fault':
                        colors.append('background-color: #f8d7da')
                    elif val == 'Critical':
                        colors.append('background-color: #fff3cd')
                    else:
                        colors.append('')
                else:
                    colors.append('')
            return colors
        
        # Display enhanced table
        styled_table = display_data.style.apply(highlight_status, axis=1)
        st.dataframe(styled_table, use_container_width=True, hide_index=True)
        
        # Quick insights
        st.subheader("💡 AI Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Health distribution
            health_bins = pd.cut(enhanced_fleet['health_score'], bins=[0, 60, 80, 100], 
                               labels=['At Risk', 'Monitor', 'Healthy'])
            health_counts = health_bins.value_counts()
            
            fig = px.pie(values=health_counts.values, names=health_counts.index,
                        title="Fleet Health Distribution",
                        color_discrete_map={'Healthy': '#2ed573', 'Monitor': '#ffa726', 'At Risk': '#ff6b6b'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Performance vs Load analysis
            performance_data = enhanced_fleet[['load_pct', 'efficiency_pct']].dropna()
            
            if not performance_data.empty:
                fig = px.scatter(performance_data, x='load_pct', y='efficiency_pct',
                               title="Efficiency vs Load Analysis",
                               labels={'load_pct': 'Load %', 'efficiency_pct': 'Efficiency %'})
                fig.add_hline(y=85, line_dash="dash", line_color="red", annotation_text="Min Efficiency")
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Waiting for telemetry data...")

def main():
    """Enhanced main application with multiple demo modes."""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Initialize data
    load_seed_data()
    
    # Authentication check
    if not st.session_state.authenticated:
        authenticate()
        return
    
    # Enhanced sidebar with persona-based navigation
    config = load_config()
    demo_mode = config.get('demo_mode', 'technical')
    
    # Sidebar styling
    st.sidebar.markdown(f"### {st.session_state.role_name}")
    st.sidebar.write(f"Mode: {demo_mode.title()}")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.role_name = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Persona-based navigation
    if st.session_state.user_role == "executive@demo":
        pages = {
            "👔 Executive Dashboard": show_executive_dashboard,
            "🚨 Crisis Management": show_crisis_management,
            "⚡ Fleet Monitoring": show_fleet_monitoring,
            "🧠 AI Predictions": show_ai_predictions_center,
            "📊 Business Analytics": show_executive_dashboard
        }
    elif st.session_state.user_role == "technician@demo":
        pages = {
            "📱 Mobile Interface": show_mobile_interface,
            "⚡ Fleet Status": show_fleet_monitoring,
            "🔧 Work Orders": show_mobile_interface,
            "📋 Digital Forms": show_mobile_interface
        }
    elif st.session_state.user_role == "operator@demo":
        pages = {
            "⚡ Fleet Monitoring": show_fleet_monitoring,
            "🧠 AI Predictions": show_ai_predictions_center,
            "🚨 Alert Center": show_crisis_management,
            "📊 Analytics": show_executive_dashboard
        }
    else:  # customer@demo
        pages = {
            "⚡ Fleet Monitoring": show_fleet_monitoring,
            "📊 Performance": show_executive_dashboard,
            "🔧 Service Status": show_mobile_interface
        }
    
    selected_page = st.sidebar.selectbox("🧭 Navigation:", list(pages.keys()))
    
    # Display selected page
    pages[selected_page]()
    
    # Footer with demo info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎭 Demo Features Active")
    st.sidebar.markdown("✅ AI Failure Prediction")
    st.sidebar.markdown("✅ Real-time Simulation") 
    st.sidebar.markdown("✅ Crisis Management")
    st.sidebar.markdown("✅ Mobile Interface")
    st.sidebar.markdown("✅ Executive Analytics")

if __name__ == "__main__":
    main()
