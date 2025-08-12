"""
Cloud-Connected Generator Monitoring Demo
Real-time Streamlit application with role-based access and live simulation.
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

# Page configuration
st.set_page_config(
    page_title="Generator Monitoring Demo",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Global configuration
CONFIG_FILE = DATA_DIR / "config.json"
DEFAULT_CONFIG = {
    "refresh_seconds": 8,
    "pricing": {"subscription": 1500, "premium": 5000, "upsell_avg": 2500},
    "thresholds_default": {
        "fuel_low": 20,
        "temp_high": 95, 
        "overload_pct": 90,
        "battery_low": 11.8
    },
    "per_customer_thresholds": {}
}

def load_config() -> Dict:
    """Load configuration from file or create default."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

def save_config(config: Dict):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def load_seed_data():
    """Load or create seed data files."""
    
    # Generators data
    generators_file = DATA_DIR / "generators.csv"
    if not generators_file.exists():
        generators_data = {
            'id': [f'GEN-{i:03d}' for i in range(1, 13)],
            'name': [
                'Hospital Main', 'Hospital Backup', 'Mall Primary', 'Mall Secondary',
                'Factory Line-A', 'Factory Line-B', 'Office Building', 'Data Center Primary',
                'Data Center Backup', 'Warehouse', 'Clinic', 'Emergency Services'
            ],
            'customer': ['Riyadh Medical', 'Riyadh Medical', 'Jeddah Mall', 'Jeddah Mall',
                        'Dammam Industrial', 'Dammam Industrial', 'Riyadh Corp', 'Riyadh Tech',
                        'Riyadh Tech', 'Jeddah Logistics', 'Dammam Health', 'Riyadh Emergency'],
            'model': ['CAT-500', 'CAT-250', 'Cummins-750', 'Cummins-500', 'Perkins-1000', 'Perkins-1000',
                     'Kohler-300', 'MTU-1500', 'MTU-1000', 'Generac-400', 'Yanmar-200', 'Detroit-800'],
            'controller_protocol': ['Modbus', 'Modbus', 'CAN', 'CAN', 'RS485', 'RS485',
                                  'Modbus', 'CAN', 'CAN', 'RS485', 'Modbus', 'Modbus'],
            'lat': [24.7136, 24.7126, 21.4858, 21.4868, 26.4207, 26.4217,
                   24.7246, 24.7156, 24.7166, 21.4758, 26.4107, 24.7036],
            'lon': [46.6753, 46.6763, 39.1925, 39.1935, 50.0888, 50.0898,
                   46.6653, 46.6853, 46.6863, 39.1825, 50.0788, 46.6553],
            'install_date': ['2020-01-15', '2020-02-20', '2019-06-10', '2019-07-15',
                           '2021-03-20', '2021-04-25', '2020-09-12', '2018-11-30',
                           '2019-01-15', '2020-05-08', '2021-08-22', '2019-10-05'],
            'status': ['Running', 'Running', 'Running', 'Stopped', 'Running', 'Running',
                      'Stopped', 'Running', 'Fault', 'Running', 'Stopped', 'Running'],
            'subscription_tier': ['Premium', 'Basic', 'Pro', 'Basic', 'Premium', 'Premium',
                                'Pro', 'Premium', 'Premium', 'Basic', 'Pro', 'Premium']
        }
        pd.DataFrame(generators_data).to_csv(generators_file, index=False)
    
    # Customers data
    customers_file = DATA_DIR / "customers.csv"
    if not customers_file.exists():
        customers_data = {
            'id': ['CUST-001', 'CUST-002', 'CUST-003'],
            'name': ['Riyadh Medical', 'Jeddah Mall', 'Dammam Industrial'],
            'contact_email': ['admin@riyadhmed.sa', 'ops@jeddahmall.sa', 'maint@dammamind.sa'],
            'city': ['Riyadh', 'Jeddah', 'Dammam'],
            'country': ['Saudi Arabia', 'Saudi Arabia', 'Saudi Arabia']
        }
        pd.DataFrame(customers_data).to_csv(customers_file, index=False)
    
    # Initialize empty data files if they don't exist
    telemetry_file = DATA_DIR / "telemetry.parquet"
    if not telemetry_file.exists():
        empty_telemetry = pd.DataFrame(columns=[
            'ts', 'generator_id', 'fuel_pct', 'load_pct', 'temp_c', 
            'voltage', 'run_hours', 'status', 'lat', 'lon'
        ])
        empty_telemetry.to_parquet(telemetry_file, index=False)
    
    alerts_file = DATA_DIR / "alerts.csv"
    if not alerts_file.exists():
        empty_alerts = pd.DataFrame(columns=[
            'id', 'generator_id', 'rule', 'severity', 'message', 'ts',
            'ack_by', 'ack_ts', 'status', 'notes'
        ])
        empty_alerts.to_csv(alerts_file, index=False)
    
    maintenance_file = DATA_DIR / "maintenance.csv"
    if not maintenance_file.exists():
        empty_maintenance = pd.DataFrame(columns=[
            'id', 'generator_id', 'type', 'due_by_date', 'due_at_run_hours',
            'completed_ts', 'assigned_to', 'priority', 'notes'
        ])
        empty_maintenance.to_csv(maintenance_file, index=False)
    
    tickets_file = DATA_DIR / "tickets.csv"
    if not tickets_file.exists():
        empty_tickets = pd.DataFrame(columns=[
            'id', 'generator_id', 'created_by_role', 'created_ts', 'summary',
            'status', 'assigned_to', 'parts_suggested'
        ])
        empty_tickets.to_csv(tickets_file, index=False)

def load_data_files():
    """Load all data files with error handling."""
    data = {}
    
    try:
        data['generators'] = pd.read_csv(DATA_DIR / "generators.csv")
        if data['generators'].empty:
            st.warning("Generators file is empty. Regenerating...")
            load_seed_data()  # Regenerate if empty
            data['generators'] = pd.read_csv(DATA_DIR / "generators.csv")
    except Exception as e:
        st.warning(f"Error loading generators: {str(e)}. Regenerating...")
        load_seed_data()  # Regenerate on error
        try:
            data['generators'] = pd.read_csv(DATA_DIR / "generators.csv")
        except Exception as e2:
            st.error(f"Failed to regenerate generators: {str(e2)}")
            data['generators'] = pd.DataFrame()
    
    try:
        data['customers'] = pd.read_csv(DATA_DIR / "customers.csv")
    except Exception as e:
        st.warning(f"Error loading customers: {str(e)}")
        data['customers'] = pd.DataFrame()
    
    try:
        data['telemetry'] = pd.read_parquet(DATA_DIR / "telemetry.parquet")
    except Exception as e:
        # Try to create empty parquet file if it doesn't exist
        empty_telemetry = pd.DataFrame(columns=[
            'ts', 'generator_id', 'fuel_pct', 'load_pct', 'temp_c', 
            'voltage', 'run_hours', 'status', 'lat', 'lon'
        ])
        empty_telemetry.to_parquet(DATA_DIR / "telemetry.parquet", index=False)
        data['telemetry'] = empty_telemetry
    
    try:
        data['alerts'] = pd.read_csv(DATA_DIR / "alerts.csv")
    except Exception as e:
        data['alerts'] = pd.DataFrame(columns=[
            'id', 'generator_id', 'rule', 'severity', 'message', 'ts',
            'ack_by', 'ack_ts', 'status', 'notes'
        ])
    
    try:
        data['maintenance'] = pd.read_csv(DATA_DIR / "maintenance.csv")
    except Exception as e:
        data['maintenance'] = pd.DataFrame(columns=[
            'id', 'generator_id', 'type', 'due_by_date', 'due_at_run_hours',
            'completed_ts', 'assigned_to', 'priority', 'notes'
        ])
    
    try:
        data['tickets'] = pd.read_csv(DATA_DIR / "tickets.csv")
    except Exception as e:
        data['tickets'] = pd.DataFrame(columns=[
            'id', 'generator_id', 'created_by_role', 'created_ts', 'summary',
            'status', 'assigned_to', 'parts_suggested'
        ])
    
    return data

def save_telemetry(new_data: pd.DataFrame):
    """Append new telemetry data with error handling."""
    try:
        telemetry_file = DATA_DIR / "telemetry.parquet"
        if telemetry_file.exists():
            existing = pd.read_parquet(telemetry_file)
            combined = pd.concat([existing, new_data], ignore_index=True)
            # Keep only last 48 hours to prevent file from growing too large
            cutoff = datetime.now() - timedelta(hours=48)
            combined = combined[pd.to_datetime(combined['ts']) > cutoff]
            combined.to_parquet(telemetry_file, index=False)
        else:
            new_data.to_parquet(telemetry_file, index=False)
    except Exception as e:
        st.error(f"Error saving telemetry: {str(e)}")

def save_alerts(alerts_df: pd.DataFrame):
    """Save alerts data with error handling."""
    try:
        alerts_df.to_csv(DATA_DIR / "alerts.csv", index=False)
    except Exception as e:
        st.error(f"Error saving alerts: {str(e)}")

def save_tickets(tickets_df: pd.DataFrame):
    """Save tickets data with error handling."""
    try:
        tickets_df.to_csv(DATA_DIR / "tickets.csv", index=False)
    except Exception as e:
        st.error(f"Error saving tickets: {str(e)}")

def authenticate():
    """Simple authentication page."""
    st.title("🔐 Generator Monitoring System")
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Login")
        
        demo_accounts = {
            "customer@demo": "Customer Portal",
            "service@demo": "Business/Service Portal"
        }
        
        selected_account = st.selectbox(
            "Select Demo Account:",
            options=list(demo_accounts.keys()),
            format_func=lambda x: f"{x} ({demo_accounts[x]})"
        )
        
        if st.button("Login", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = selected_account
            st.session_state.role_name = demo_accounts[selected_account]
            st.rerun()
        
        st.markdown("---")
        st.info("This is a demo system. Select either account to explore different portal features.")

class TelemetrySimulator:
    """Real-time telemetry data simulator."""
    
    def __init__(self):
        try:
            self.generators_df = pd.read_csv(DATA_DIR / "generators.csv")
        except Exception as e:
            st.error(f"Error loading generators data: {str(e)}")
            self.generators_df = pd.DataFrame()
            return
            
        self.config = load_config()
        self.last_telemetry = {}
        self.consecutive_counts = {}  # For alert tracking
        
        # Initialize last telemetry state
        for _, gen in self.generators_df.iterrows():
            self.last_telemetry[gen['id']] = {
                'fuel_pct': np.random.uniform(30, 90),
                'load_pct': np.random.uniform(20, 70),
                'temp_c': np.random.uniform(70, 85),
                'voltage': np.random.uniform(12.2, 13.8),
                'run_hours': np.random.uniform(1000, 5000)
            }
            self.consecutive_counts[gen['id']] = {
                'fuel_low': 0,
                'temp_high': 0,
                'overload': 0,
                'overload_start': None
            }
    
    def generate_tick(self) -> pd.DataFrame:
        """Generate one tick of telemetry data."""
        new_data = []
        current_time = datetime.now()
        
        for _, gen in self.generators_df.iterrows():
            gen_id = gen['id']
            last = self.last_telemetry[gen_id]
            
            if gen['status'] == 'Running':
                # Fuel consumption
                fuel_consumption = np.random.uniform(0.05, 0.5)
                new_fuel = max(0, last['fuel_pct'] - fuel_consumption)
                
                # Random refuel events (5% chance)
                if np.random.random() < 0.05 or new_fuel < 5:
                    new_fuel = np.random.uniform(90, 100)
                
                # Load variations with occasional spikes
                load_change = np.random.normal(0, 5)
                new_load = np.clip(last['load_pct'] + load_change, 10, 100)
                
                # Occasional overload spikes (2% chance)
                if np.random.random() < 0.02:
                    new_load = np.random.uniform(90, 105)
                
                # Temperature correlates with load
                target_temp = 70 + (new_load * 0.3) + np.random.normal(0, 3)
                temp_change = np.clip(target_temp - last['temp_c'], -2, 2)
                new_temp = last['temp_c'] + temp_change
                
                # Voltage with occasional dips
                voltage_change = np.random.normal(0, 0.1)
                new_voltage = np.clip(last['voltage'] + voltage_change, 10.5, 14.2)
                
                # Battery low events (1% chance)
                if np.random.random() < 0.01:
                    new_voltage = np.random.uniform(10.8, 11.7)
                
                # Run hours increment
                new_run_hours = last['run_hours'] + np.random.uniform(0.05, 0.2)
                
            else:
                # Stopped/Fault generators
                new_fuel = last['fuel_pct']  # No fuel consumption
                new_load = 0
                # Temperature cools down
                new_temp = max(last['temp_c'] - np.random.uniform(0.5, 2), 25)
                new_voltage = last['voltage'] + np.random.normal(0, 0.05)
                new_run_hours = last['run_hours']  # No runtime
            
            # Update last telemetry
            self.last_telemetry[gen_id] = {
                'fuel_pct': new_fuel,
                'load_pct': new_load,
                'temp_c': new_temp,
                'voltage': new_voltage,
                'run_hours': new_run_hours
            }
            
            # Create telemetry record
            record = {
                'ts': current_time,
                'generator_id': gen_id,
                'fuel_pct': new_fuel,
                'load_pct': new_load,
                'temp_c': new_temp,
                'voltage': new_voltage,
                'run_hours': new_run_hours,
                'status': gen['status'],
                'lat': gen['lat'],
                'lon': gen['lon']
            }
            new_data.append(record)
        
        return pd.DataFrame(new_data)
    
    def check_alerts(self, telemetry_df: pd.DataFrame) -> List[Dict]:
        """Check telemetry for alert conditions."""
        new_alerts = []
        
        # Get current alert count safely
        try:
            existing_alerts = pd.read_csv(DATA_DIR / "alerts.csv")
            alert_id_counter = len(existing_alerts) + 1
        except (FileNotFoundError, pd.errors.EmptyDataError):
            alert_id_counter = 1
        
        for _, row in telemetry_df.iterrows():
            gen_id = row['generator_id']
            
            # Get thresholds (customer-specific or default)
            gen_customer = self.generators_df[self.generators_df['id'] == gen_id]['customer'].iloc[0]
            thresholds = self.config['per_customer_thresholds'].get(
                gen_customer, self.config['thresholds_default']
            )
            
            # Fuel Low Alert
            if row['fuel_pct'] < thresholds['fuel_low']:
                self.consecutive_counts[gen_id]['fuel_low'] += 1
                if self.consecutive_counts[gen_id]['fuel_low'] >= 2:
                    alert = {
                        'id': f'ALT-{alert_id_counter:06d}',
                        'generator_id': gen_id,
                        'rule': 'Fuel Low',
                        'severity': 'WARN',
                        'message': f'Fuel level low: {row["fuel_pct"]:.1f}%',
                        'ts': row['ts'],
                        'ack_by': '',
                        'ack_ts': '',
                        'status': 'OPEN',
                        'notes': ''
                    }
                    new_alerts.append(alert)
                    alert_id_counter += 1
            else:
                self.consecutive_counts[gen_id]['fuel_low'] = 0
            
            # High Temperature Alert
            if row['temp_c'] > thresholds['temp_high']:
                self.consecutive_counts[gen_id]['temp_high'] += 1
                if self.consecutive_counts[gen_id]['temp_high'] >= 3:
                    alert = {
                        'id': f'ALT-{alert_id_counter:06d}',
                        'generator_id': gen_id,
                        'rule': 'High Temperature',
                        'severity': 'CRITICAL',
                        'message': f'High temperature: {row["temp_c"]:.1f}°C',
                        'ts': row['ts'],
                        'ack_by': '',
                        'ack_ts': '',
                        'status': 'OPEN',
                        'notes': ''
                    }
                    new_alerts.append(alert)
                    alert_id_counter += 1
            else:
                self.consecutive_counts[gen_id]['temp_high'] = 0
            
            # Overload Alert (5+ minutes = ~40 ticks at 8-second intervals)
            if row['load_pct'] > thresholds['overload_pct']:
                if self.consecutive_counts[gen_id]['overload_start'] is None:
                    self.consecutive_counts[gen_id]['overload_start'] = row['ts']
                else:
                    duration = (row['ts'] - self.consecutive_counts[gen_id]['overload_start']).total_seconds()
                    if duration >= 300:  # 5 minutes
                        alert = {
                            'id': f'ALT-{alert_id_counter:06d}',
                            'generator_id': gen_id,
                            'rule': 'Overload',
                            'severity': 'WARN',
                            'message': f'Overload condition: {row["load_pct"]:.1f}% for {duration/60:.1f} min',
                            'ts': row['ts'],
                            'ack_by': '',
                            'ack_ts': '',
                            'status': 'OPEN',
                            'notes': ''
                        }
                        new_alerts.append(alert)
                        alert_id_counter += 1
                        self.consecutive_counts[gen_id]['overload_start'] = None
            else:
                self.consecutive_counts[gen_id]['overload_start'] = None
            
            # Battery Low Alert
            if row['voltage'] < thresholds['battery_low']:
                alert = {
                    'id': f'ALT-{alert_id_counter:06d}',
                    'generator_id': gen_id,
                    'rule': 'Battery Low',
                    'severity': 'WARN',
                    'message': f'Low battery voltage: {row["voltage"]:.1f}V',
                    'ts': row['ts'],
                    'ack_by': '',
                    'ack_ts': '',
                    'status': 'OPEN',
                    'notes': ''
                }
                new_alerts.append(alert)
                alert_id_counter += 1
        
        return new_alerts

def show_login_page():
    """Display login page."""
    authenticate()

def show_fleet_monitoring():
    """Real-time fleet monitoring page."""
    st.title("⚡ Real-Time Fleet Monitoring")
    
    # Auto-refresh setup
    config = load_config()
    refresh_interval = config['refresh_seconds']
    
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = 0
    
    # Auto-refresh trigger
    current_time = time.time()
    if current_time - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = current_time
        
        try:
            # Generate new telemetry
            simulator = TelemetrySimulator()
            if not simulator.generators_df.empty:  # Only run if generators loaded successfully
                new_telemetry = simulator.generate_tick()
                save_telemetry(new_telemetry)
                
                # Check for new alerts
                new_alerts = simulator.check_alerts(new_telemetry)
                if new_alerts:
                    # Append new alerts
                    try:
                        existing_alerts = pd.read_csv(DATA_DIR / "alerts.csv")
                    except (FileNotFoundError, pd.errors.EmptyDataError):
                        existing_alerts = pd.DataFrame(columns=[
                            'id', 'generator_id', 'rule', 'severity', 'message', 'ts',
                            'ack_by', 'ack_ts', 'status', 'notes'
                        ])
                    combined_alerts = pd.concat([existing_alerts, pd.DataFrame(new_alerts)], ignore_index=True)
                    save_alerts(combined_alerts)
                
                # Force rerun to show updated data
                st.rerun()
        except Exception as e:
            st.error(f"Simulation error: {str(e)}. Will retry on next refresh.")
            # Don't rerun on error to prevent infinite loop
    
    # Load current data
    data = load_data_files()
    
    # Debug information (remove in production)
    generators_df = data['generators']
    telemetry_df = data['telemetry']
    alerts_df = data['alerts']
    
    if generators_df.empty:
        st.error("⚠️ No generator data found! Please check if data files were created properly.")
        st.info("Try refreshing the page or restarting the application.")
        
        # Show debug info
        with st.expander("Debug Information"):
            st.write(f"Data directory: {DATA_DIR}")
            st.write(f"Generator file exists: {(DATA_DIR / 'generators.csv').exists()}")
            if (DATA_DIR / 'generators.csv').exists():
                try:
                    debug_df = pd.read_csv(DATA_DIR / 'generators.csv')
                    st.write(f"Generator file rows: {len(debug_df)}")
                    st.write("First few rows:")
                    st.dataframe(debug_df.head())
                except Exception as e:
                    st.write(f"Error reading generator file: {e}")
            
            if st.button("🔄 Force Regenerate Data"):
                try:
                    # Clear cache and regenerate
                    load_seed_data()
                    st.success("Data regenerated! Please refresh the page.")
                except Exception as e:
                    st.error(f"Error regenerating data: {e}")
        return
    
    # KPI Dashboard
    st.subheader("📊 Live Dashboard KPIs")
    
    # Calculate KPIs safely
    # (generators_df, telemetry_df, alerts_df already defined above)
    
    # Default values
    online_units = 0
    total_units = 0
    active_alerts = 0
    avg_load = 0.0
    fuel_low_count = 0
    
    try:
        if not generators_df.empty and 'status' in generators_df.columns:
            total_units = len(generators_df)
            online_units = len(generators_df[generators_df['status'] == 'Running'])
        
        if not alerts_df.empty and 'status' in alerts_df.columns:
            active_alerts = len(alerts_df[alerts_df['status'] == 'OPEN'])
        
        if not telemetry_df.empty:
            # Get latest telemetry for each generator
            latest_telemetry = telemetry_df.sort_values('ts').groupby('generator_id').tail(1)
            if 'load_pct' in latest_telemetry.columns:
                avg_load = latest_telemetry['load_pct'].mean()
            if 'fuel_pct' in latest_telemetry.columns:
                fuel_low_count = len(latest_telemetry[latest_telemetry['fuel_pct'] < 20])
    except Exception as e:
        st.warning(f"KPI calculation error: {str(e)}. Showing default values.")
    
    # KPI Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        percentage = f"{online_units/total_units*100:.1f}%" if total_units > 0 else "0%"
        st.metric("Online Units", f"{online_units}/{total_units}", delta=percentage)
    
    with col2:
        alert_delta = "🚨" if active_alerts > 0 else "✅"
        st.metric("Active Alerts", active_alerts, delta=alert_delta)
    
    with col3:
        st.metric("Avg Load %", f"{avg_load:.1f}%")
    
    with col4:
        fuel_delta = "⚠️" if fuel_low_count > 0 else "✅"
        st.metric("Fuel < 20%", fuel_low_count, delta=fuel_delta)
    
    with col5:
        next_refresh = max(0, refresh_interval - (current_time - st.session_state.last_refresh))
        st.metric("Auto-Refresh", f"{refresh_interval}s", delta=f"Next: {next_refresh:.0f}s")
    
    # Fleet Table
    st.subheader("🚛 Fleet Status")
    
    # Initialize fleet_display
    fleet_display = pd.DataFrame()
    
    try:
        # Always show generators, even without telemetry
        if not telemetry_df.empty and not generators_df.empty:
            # Get latest telemetry safely
            try:
                latest_telemetry = telemetry_df.sort_values('ts').groupby('generator_id').tail(1)
            except Exception:
                latest_telemetry = pd.DataFrame()
            
            if not latest_telemetry.empty:
                # Merge generators with latest telemetry
                fleet_status = generators_df.merge(latest_telemetry, left_on='id', right_on='generator_id', how='left')
                
                # Ensure all required columns exist with proper data types
                required_columns = {
                    'fuel_pct': 0.0,
                    'load_pct': 0.0,
                    'temp_c': 0.0,
                    'voltage': 0.0,
                    'run_hours': 0.0
                }
                
                for col, default_val in required_columns.items():
                    if col not in fleet_status.columns:
                        fleet_status[col] = default_val
                    else:
                        # Ensure numeric type and fill NaN values
                        fleet_status[col] = pd.to_numeric(fleet_status[col], errors='coerce').fillna(default_val)
                
                # Select and format display columns safely
                base_cols = ['id', 'name', 'customer', 'status']
                telemetry_cols = list(required_columns.keys())
                
                # Create display dataframe
                fleet_display = pd.DataFrame()
                for col in base_cols:
                    if col in fleet_status.columns:
                        fleet_display[col] = fleet_status[col]
                    else:
                        fleet_display[col] = 'N/A'
                
                for col in telemetry_cols:
                    if col in fleet_status.columns:
                        fleet_display[col] = fleet_status[col].round(1)
                    else:
                        fleet_display[col] = 0.0
                
                fleet_display.columns = ['ID', 'Name', 'Customer', 'Status', 'Fuel %', 'Load %', 'Temp °C', 'Battery V', 'Run Hours']
            else:
                # Fallback to basic generator info
                raise Exception("No latest telemetry available")
        else:
            # No telemetry data yet, show generators with placeholder values
            if not generators_df.empty:
                fleet_display = generators_df[['id', 'name', 'customer', 'status']].copy()
                fleet_display['Fuel %'] = 'N/A'
                fleet_display['Load %'] = 'N/A'
                fleet_display['Temp °C'] = 'N/A'
                fleet_display['Battery V'] = 'N/A'
                fleet_display['Run Hours'] = 'N/A'
                fleet_display.columns = ['ID', 'Name', 'Customer', 'Status', 'Fuel %', 'Load %', 'Temp °C', 'Battery V', 'Run Hours']
            else:
                st.warning("No generator data available. Please check data files.")
                return
    except Exception as e:
        # Final fallback - create basic display from generators only
        if not generators_df.empty:
            try:
                fleet_display = generators_df[['id', 'name', 'customer', 'status']].copy()
                fleet_display['Fuel %'] = 'N/A'
                fleet_display['Load %'] = 'N/A'
                fleet_display['Temp °C'] = 'N/A'
                fleet_display['Battery V'] = 'N/A'
                fleet_display['Run Hours'] = 'N/A'
                fleet_display.columns = ['ID', 'Name', 'Customer', 'Status', 'Fuel %', 'Load %', 'Temp °C', 'Battery V', 'Run Hours']
            except Exception as inner_e:
                st.error(f"Error creating fleet display: {str(inner_e)}")
                return
        else:
            st.warning("No generator data available.")
            return
        
    # Add search and filter
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("🔍 Search:", placeholder="Generator, Customer, Location...")
    with col2:
        status_filter = st.multiselect("Status Filter:", 
                                     options=['Running', 'Stopped', 'Fault'],
                                     default=['Running', 'Stopped', 'Fault'])
    with col3:
        # Get customer options safely
        try:
            if not generators_df.empty and 'customer' in generators_df.columns:
                customer_options = generators_df['customer'].unique().tolist()
            else:
                customer_options = []
        except Exception:
            customer_options = []
        
        customer_filter = st.multiselect("Customer Filter:",
                                       options=customer_options,
                                       default=customer_options)
    
    # Apply filters safely
    if not fleet_display.empty:
        try:
            if search_term:
                mask = (fleet_display['ID'].astype(str).str.contains(search_term, case=False, na=False) |
                       fleet_display['Name'].astype(str).str.contains(search_term, case=False, na=False) |
                       fleet_display['Customer'].astype(str).str.contains(search_term, case=False, na=False))
                fleet_display = fleet_display[mask]
            
            if status_filter and 'Status' in fleet_display.columns:
                fleet_display = fleet_display[fleet_display['Status'].isin(status_filter)]
            if customer_filter and 'Customer' in fleet_display.columns:
                fleet_display = fleet_display[fleet_display['Customer'].isin(customer_filter)]
        except Exception as e:
            st.warning(f"Filter error: {str(e)}. Showing unfiltered data.")
    
    # Display table
    if not fleet_display.empty:
        st.dataframe(fleet_display, use_container_width=True, hide_index=True)
    else:
        st.info("No data to display. Waiting for generator information...")
    
    # Fleet Map
    st.subheader("🗺️ Fleet Map")
    
    try:
        if not generators_df.empty and all(col in generators_df.columns for col in ['lat', 'lon', 'status']):
            # Prepare map data
            map_data = generators_df.copy()
            
            # Add status colors as separate RGB columns (pydeck format)
            def get_color_rgb(status):
                colors = {
                    'Running': [0, 255, 0, 160],    # Green
                    'Stopped': [255, 255, 0, 160],  # Yellow  
                    'Fault': [255, 0, 0, 160]       # Red
                }
                return colors.get(status, [128, 128, 128, 160])  # Gray default
            
            # Apply colors to each row
            colors = map_data['status'].apply(get_color_rgb)
            map_data['color'] = colors.tolist()
            
            # Create pydeck map
            view_state = pdk.ViewState(
                latitude=float(map_data['lat'].mean()),
                longitude=float(map_data['lon'].mean()),
                zoom=6,
                pitch=0
            )
            
            layer = pdk.Layer(
                'ScatterplotLayer',
                data=map_data,
                get_position='[lon, lat]',
                get_color='color',
                get_radius=15000,
                pickable=True,
                auto_highlight=True
            )
            
            deck = pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=view_state,
                layers=[layer],
                tooltip={
                    'html': '<b>{name}</b><br/>Status: {status}<br/>Customer: {customer}<br/>Model: {model}',
                    'style': {'backgroundColor': 'steelblue', 'color': 'white'}
                }
            )
            
            st.pydeck_chart(deck)
        else:
            st.info("Map unavailable - missing generator location data.")
    except Exception as e:
        st.warning(f"Error creating map: {str(e)}. Map unavailable.")

def show_alerts_page():
    """Alerts and notifications page."""
    st.title("🚨 Alerts & Notifications")
    
    # Load data
    data = load_data_files()
    alerts_df = data['alerts']
    generators_df = data['generators']
    
    # Alert summary
    if not alerts_df.empty:
        total_alerts = len(alerts_df)
        open_alerts = len(alerts_df[alerts_df['status'] == 'OPEN'])
        critical_alerts = len(alerts_df[(alerts_df['severity'] == 'CRITICAL') & (alerts_df['status'] == 'OPEN')])
        ack_rate = len(alerts_df[alerts_df['ack_by'] != '']) / total_alerts * 100 if total_alerts > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Alerts", total_alerts)
        with col2:
            st.metric("Open Alerts", open_alerts)
        with col3:
            st.metric("Critical Open", critical_alerts)
        with col4:
            st.metric("Ack Rate", f"{ack_rate:.1f}%")
    
    # Notifications Log Panel
    st.subheader("📢 Mock Notifications Log")
    
    if 'notification_log' not in st.session_state:
        st.session_state.notification_log = []
    
    # Show notification log
    if st.session_state.notification_log:
        with st.expander("Recent Notifications", expanded=True):
            for notification in reversed(st.session_state.notification_log[-5:]):  # Show last 5
                st.text(notification)
    else:
        st.info("No notifications sent yet.")
    
    # Alert filters
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.multiselect("Severity:", 
                                       ['CRITICAL', 'WARN', 'INFO'],
                                       default=['CRITICAL', 'WARN'])
    with col2:
        status_filter = st.selectbox("Status:", ['All', 'OPEN', 'ACKNOWLEDGED', 'CLOSED'])
    with col3:
        if not alerts_df.empty:
            available_rules = alerts_df['rule'].unique()
        else:
            available_rules = []
        rule_filter = st.multiselect("Rule Type:", available_rules, default=available_rules)
    
    # Filter alerts
    filtered_alerts = alerts_df.copy() if not alerts_df.empty else pd.DataFrame()
    
    if not filtered_alerts.empty:
        filtered_alerts = filtered_alerts[filtered_alerts['severity'].isin(severity_filter)]
        
        if status_filter != 'All':
            if status_filter == 'ACKNOWLEDGED':
                filtered_alerts = filtered_alerts[filtered_alerts['ack_by'] != '']
            else:
                filtered_alerts = filtered_alerts[filtered_alerts['status'] == status_filter]
        
        if rule_filter:
            filtered_alerts = filtered_alerts[filtered_alerts['rule'].isin(rule_filter)]
        
        # Sort by timestamp (newest first)
        filtered_alerts = filtered_alerts.sort_values('ts', ascending=False)
    
    # Alert List
    st.subheader("📋 Alert Queue")
    
    if not filtered_alerts.empty:
        for idx, alert in filtered_alerts.head(10).iterrows():
            # Get generator info
            gen_info = generators_df[generators_df['id'] == alert['generator_id']]
            gen_name = gen_info['name'].iloc[0] if not gen_info.empty else "Unknown"
            gen_customer = gen_info['customer'].iloc[0] if not gen_info.empty else "Unknown"
            
            # Alert card
            severity_color = {
                'CRITICAL': '#dc3545',
                'WARN': '#ffc107',
                'INFO': '#17a2b8'
            }.get(alert['severity'], '#6c757d')
            
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**<span style='color: {severity_color}'>{alert['severity']}</span>** - {alert['rule']}")
                    st.write(f"**{alert['generator_id']}** ({gen_name})")
                    st.caption(f"Customer: {gen_customer}")
                
                with col2:
                    st.write(alert['message'])
                    st.caption(f"Time: {alert['ts']}")
                
                with col3:
                    if alert['ack_by']:
                        st.success("✓ Acknowledged")
                        st.caption(f"By: {alert['ack_by']}")
                    else:
                        if st.button("Acknowledge", key=f"ack_{alert['id']}"):
                            # Update alert
                            alerts_df.loc[alerts_df['id'] == alert['id'], 'ack_by'] = st.session_state.user_role
                            alerts_df.loc[alerts_df['id'] == alert['id'], 'ack_ts'] = datetime.now()
                            save_alerts(alerts_df)
                            
                            # Mock notification
                            notification = f"[{datetime.now().strftime('%H:%M:%S')}] SMS/Email: Alert {alert['id']} acknowledged by {st.session_state.user_role}"
                            st.session_state.notification_log.append(notification)
                            
                            st.rerun()
                
                with col4:
                    if st.button("Create Ticket", key=f"ticket_{alert['id']}"):
                        # Create service ticket
                        tickets_df = data['tickets']
                        new_ticket = {
                            'id': f"TKT-{len(tickets_df)+1:05d}",
                            'generator_id': alert['generator_id'],
                            'created_by_role': st.session_state.user_role,
                            'created_ts': datetime.now(),
                            'summary': f"Alert: {alert['rule']} - {alert['message']}",
                            'status': 'OPEN',
                            'assigned_to': '',
                            'parts_suggested': get_suggested_parts(alert['rule'])
                        }
                        
                        tickets_df = pd.concat([tickets_df, pd.DataFrame([new_ticket])], ignore_index=True)
                        save_tickets(tickets_df)
                        
                        # Mock CRM/ERP integration
                        crm_payload = {
                            "ticket_id": new_ticket['id'],
                            "generator_id": alert['generator_id'],
                            "customer": gen_customer,
                            "priority": "HIGH" if alert['severity'] == 'CRITICAL' else "NORMAL",
                            "description": new_ticket['summary'],
                            "suggested_parts": new_ticket['parts_suggested']
                        }
                        
                        st.success(f"Ticket {new_ticket['id']} created!")
                        with st.expander("CRM/ERP Integration Payload"):
                            st.json(crm_payload)
                
                st.markdown("---")
    else:
        st.info("No alerts match the current filters.")

def get_suggested_parts(rule_type: str) -> str:
    """Get suggested parts based on alert rule."""
    suggestions = {
        'High Temperature': 'coolant,thermostat,radiator',
        'Fuel Low': 'fuel_pump,fuel_filter',
        'Battery Low': 'battery,battery_charger',
        'Overload': 'AVR,voltage_regulator'
    }
    return suggestions.get(rule_type, 'general_inspection')

def show_generator_detail():
    """Generator detail page."""
    st.title("🔧 Generator Detail")
    
    # Load data
    data = load_data_files()
    generators_df = data['generators']
    
    # Generator selection
    selected_gen = st.selectbox(
        "Select Generator:",
        options=generators_df['id'].tolist(),
        format_func=lambda x: f"{x} - {generators_df[generators_df['id']==x]['name'].iloc[0]}"
    )
    
    if selected_gen:
        gen_info = generators_df[generators_df['id'] == selected_gen].iloc[0]
        telemetry_df = data['telemetry'][data['telemetry']['generator_id'] == selected_gen]
        alerts_df = data['alerts'][data['alerts']['generator_id'] == selected_gen]
        
        # Generator header
        col1, col2, col3 = st.columns(3)
        with col1:
            st.subheader(f"{gen_info['name']}")
            st.write(f"**Customer:** {gen_info['customer']}")
            st.write(f"**Model:** {gen_info['model']}")
        with col2:
            status_color = {'Running': '🟢', 'Stopped': '🟡', 'Fault': '🔴'}.get(gen_info['status'], '⚪')
            st.write(f"**Status:** {status_color} {gen_info['status']}")
            st.write(f"**Protocol:** {gen_info['controller_protocol']}")
        with col3:
            st.write(f"**Installed:** {gen_info['install_date']}")
            st.write(f"**Tier:** {gen_info['subscription_tier']}")
        
        # Tabs
        tab1, tab2, tab3 = st.tabs(["📊 Live Data", "📈 History", "🚨 Alerts"])
        
        with tab1:
            show_live_data_tab(telemetry_df)
        
        with tab2:
            show_history_tab(telemetry_df)
        
        with tab3:
            show_generator_alerts_tab(alerts_df, selected_gen)

def show_live_data_tab(telemetry_df: pd.DataFrame):
    """Live data tab for generator detail."""
    if telemetry_df.empty:
        st.info("No telemetry data available.")
        return
    
    # Latest values - ensure we have the data
    try:
        latest = telemetry_df.sort_values('ts').iloc[-1]
    except (KeyError, IndexError):
        st.info("No recent telemetry data available.")
        return
    
    # Live metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        fuel_val = latest.get('fuel_pct', 0)
        fuel_color = "🟢" if fuel_val > 50 else "🟡" if fuel_val > 20 else "🔴"
        st.metric("Fuel Level", f"{fuel_val:.1f}%" if fuel_val > 0 else "N/A", delta=fuel_color)
    
    with col2:
        load_val = latest.get('load_pct', 0)
        load_color = "🟢" if load_val < 80 else "🟡" if load_val < 90 else "🔴"
        st.metric("Load", f"{load_val:.1f}%" if load_val > 0 else "N/A", delta=load_color)
    
    with col3:
        temp_val = latest.get('temp_c', 0)
        temp_color = "🟢" if temp_val < 85 else "🟡" if temp_val < 95 else "🔴"
        st.metric("Temperature", f"{temp_val:.1f}°C" if temp_val > 0 else "N/A", delta=temp_color)
    
    with col4:
        volt_val = latest.get('voltage', 0)
        volt_color = "🟢" if volt_val > 12.0 else "🟡" if volt_val > 11.5 else "🔴"
        st.metric("Battery", f"{volt_val:.1f}V" if volt_val > 0 else "N/A", delta=volt_color)
    
    # Run hours and status
    col1, col2 = st.columns(2)
    with col1:
        run_hours_val = latest.get('run_hours', 0)
        st.metric("Run Hours", f"{run_hours_val:.1f}h" if run_hours_val > 0 else "N/A")
    with col2:
        timestamp_val = latest.get('ts', 'Unknown')
        st.metric("Last Update", str(timestamp_val))

def show_history_tab(telemetry_df: pd.DataFrame):
    """History charts tab."""
    if telemetry_df.empty:
        st.info("No historical data available.")
        return
    
    # Time range selector
    time_range = st.selectbox("Time Range:", ["Last 24 Hours", "Last 7 Days"])
    
    # Filter data
    try:
        telemetry_df = telemetry_df.copy()
        telemetry_df['ts'] = pd.to_datetime(telemetry_df['ts'], errors='coerce')
        
        now = datetime.now()
        if time_range == "Last 24 Hours":
            cutoff = now - timedelta(days=1)
        else:
            cutoff = now - timedelta(days=7)
        
        filtered_df = telemetry_df[telemetry_df['ts'] > cutoff].sort_values('ts')
        
        if filtered_df.empty:
            st.info(f"No data available for {time_range.lower()}.")
            return
    except Exception as e:
        st.error(f"Error processing telemetry data: {str(e)}")
        return
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        try:
            # Fuel and Load
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=filtered_df['ts'], y=filtered_df['fuel_pct'],
                          name='Fuel %', line=dict(color='blue')),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=filtered_df['ts'], y=filtered_df['load_pct'],
                          name='Load %', line=dict(color='green')),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="Time")
            fig.update_yaxes(title_text="Fuel %", secondary_y=False)
            fig.update_yaxes(title_text="Load %", secondary_y=True)
            fig.update_layout(title="Fuel & Load Trends", height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating fuel/load chart: {str(e)}")
    
    with col2:
        try:
            # Temperature and Voltage
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=filtered_df['ts'], y=filtered_df['temp_c'],
                          name='Temp °C', line=dict(color='red')),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=filtered_df['ts'], y=filtered_df['voltage'],
                          name='Voltage V', line=dict(color='orange')),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="Time")
            fig.update_yaxes(title_text="Temperature °C", secondary_y=False)
            fig.update_yaxes(title_text="Voltage V", secondary_y=True)
            fig.update_layout(title="Temperature & Voltage", height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.error(f"Error creating temperature/voltage chart: {str(e)}")
    
    # Export options
    st.subheader("📄 Export Reports")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export CSV"):
            try:
                csv_data = filtered_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"generator_data_{time_range.replace(' ', '_').lower()}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error creating CSV: {str(e)}")
    
    with col2:
        if st.button("Export PDF"):
            st.info("PDF export would be generated here in a real system.")
    
    with col3:
        if st.button("Email Report"):
            st.info("Report would be emailed to customer contact in a real system.")

def show_generator_alerts_tab(alerts_df: pd.DataFrame, generator_id: str):
    """Generator-specific alerts tab."""
    if alerts_df.empty:
        st.info("No alerts for this generator.")
        return
    
    try:
        # Alert timeline
        alerts_df = alerts_df.copy()
        alerts_df['ts'] = pd.to_datetime(alerts_df['ts'], errors='coerce')
        alerts_df = alerts_df.sort_values('ts', ascending=False)
        
        for _, alert in alerts_df.head(10).iterrows():
            severity_color = {
                'CRITICAL': '#dc3545',
                'WARN': '#ffc107',
                'INFO': '#17a2b8'
            }.get(alert.get('severity', 'INFO'), '#6c757d')
            
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    severity = alert.get('severity', 'INFO')
                    rule = alert.get('rule', 'Unknown')
                    message = alert.get('message', 'No message')
                    timestamp = alert.get('ts', 'Unknown time')
                    
                    st.markdown(f"**<span style='color: {severity_color}'>{severity}</span>** - {rule}")
                    st.write(message)
                    st.caption(f"Time: {timestamp}")
                
                with col2:
                    ack_by = alert.get('ack_by', '')
                    if ack_by:
                        st.success("✓ Acknowledged")
                        st.caption(f"By: {ack_by}")
                    else:
                        if st.button("Acknowledge", key=f"gen_ack_{alert.get('id', 'unknown')}"):
                            st.success("Alert acknowledged!")
                
                with col3:
                    alert_id = alert.get('id', 'unknown')
                    notes = st.text_input("Notes:", key=f"notes_{alert_id}", placeholder="Add notes...")
                    if st.button("Save", key=f"save_{alert_id}"):
                        st.success("Notes saved!")
                
                st.markdown("---")
    except Exception as e:
        st.error(f"Error displaying alerts: {str(e)}")
        st.info("There may be an issue with the alert data format.")

def show_service_portal():
    """Business/Service portal page."""
    if st.session_state.user_role != "service@demo":
        st.error("Access denied. This page is only available to Service personnel.")
        return
    
    st.title("🏢 Business/Service Portal")
    
    # Load data
    data = load_data_files()
    config = load_config()
    
    # Fleet Analytics
    st.subheader("📊 Fleet Analytics")
    
    generators_df = data['generators']
    telemetry_df = data['telemetry']
    alerts_df = data['alerts']
    
    # Revenue calculations
    pricing = config['pricing']
    subscription_counts = generators_df['subscription_tier'].value_counts()
    
    tier_pricing = {'Basic': 500, 'Pro': pricing['subscription'], 'Premium': pricing['premium']}
    total_revenue = sum(subscription_counts.get(tier, 0) * price for tier, price in tier_pricing.items())
    
    # Analytics KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        connected_units = len(generators_df[generators_df['status'] == 'Running'])
        adoption_rate = connected_units / len(generators_df) * 100
        st.metric("Adoption Rate", f"{adoption_rate:.1f}%", f"{connected_units}/{len(generators_df)}")
    
    with col2:
        active_alerts = len(alerts_df[alerts_df['status'] == 'OPEN'])
        st.metric("Active Alerts", active_alerts)
    
    with col3:
        if not telemetry_df.empty:
            avg_temp = telemetry_df.groupby('generator_id')['temp_c'].tail(1).mean()
            st.metric("Fleet Avg Temp", f"{avg_temp:.1f}°C")
        else:
            st.metric("Fleet Avg Temp", "N/A")
    
    with col4:
        st.metric("Monthly Revenue", f"${total_revenue:,}")
    
    # Revenue breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        # Subscription tier distribution
        fig = px.pie(values=subscription_counts.values, names=subscription_counts.index,
                    title="Subscription Tiers")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue by tier
        revenue_by_tier = {tier: subscription_counts.get(tier, 0) * price 
                          for tier, price in tier_pricing.items()}
        fig = px.bar(x=list(revenue_by_tier.keys()), y=list(revenue_by_tier.values()),
                    title="Revenue by Tier")
        st.plotly_chart(fig, use_container_width=True)

def show_admin_page():
    """Administration page (Service role only)."""
    if st.session_state.user_role != "service@demo":
        st.error("Access denied. This page is only available to Service personnel.")
        return
    
    st.title("⚙️ Administration")
    
    # Load data
    data = load_data_files()
    config = load_config()
    
    # Threshold Management
    st.subheader("⚠️ Alert Thresholds")
    
    # Global defaults
    with st.expander("Global Default Thresholds"):
        col1, col2 = st.columns(2)
        with col1:
            fuel_low = st.number_input("Fuel Low (%)", 
                                     value=config['thresholds_default']['fuel_low'],
                                     min_value=5, max_value=50)
            temp_high = st.number_input("Temperature High (°C)",
                                      value=config['thresholds_default']['temp_high'],
                                      min_value=70, max_value=120)
        with col2:
            overload_pct = st.number_input("Overload (%)",
                                         value=config['thresholds_default']['overload_pct'],
                                         min_value=80, max_value=100)
            battery_low = st.number_input("Battery Low (V)",
                                        value=config['thresholds_default']['battery_low'],
                                        min_value=10.0, max_value=13.0, step=0.1)
        
        if st.button("Update Global Thresholds"):
            config['thresholds_default'] = {
                'fuel_low': fuel_low,
                'temp_high': temp_high,
                'overload_pct': overload_pct,
                'battery_low': battery_low
            }
            save_config(config)
            st.success("Global thresholds updated!")
    
    # Customer-specific thresholds
    with st.expander("Customer-Specific Thresholds"):
        customer_list = data['customers']['name'].tolist()
        selected_customer = st.selectbox("Select Customer:", customer_list)
        
        current_thresholds = config['per_customer_thresholds'].get(
            selected_customer, config['thresholds_default']
        )
        
        col1, col2 = st.columns(2)
        with col1:
            cust_fuel_low = st.number_input("Fuel Low (%) - Customer",
                                          value=current_thresholds['fuel_low'],
                                          key="cust_fuel")
            cust_temp_high = st.number_input("Temperature High (°C) - Customer",
                                           value=current_thresholds['temp_high'],
                                           key="cust_temp")
        with col2:
            cust_overload = st.number_input("Overload (%) - Customer",
                                          value=current_thresholds['overload_pct'],
                                          key="cust_overload")
            cust_battery = st.number_input("Battery Low (V) - Customer",
                                         value=current_thresholds['battery_low'],
                                         key="cust_battery", step=0.1)
        
        if st.button("Update Customer Thresholds"):
            config['per_customer_thresholds'][selected_customer] = {
                'fuel_low': cust_fuel_low,
                'temp_high': cust_temp_high,
                'overload_pct': cust_overload,
                'battery_low': cust_battery
            }
            save_config(config)
            st.success(f"Thresholds updated for {selected_customer}!")
    
    # System Configuration
    st.subheader("🔧 System Configuration")
    
    new_refresh = st.number_input("Auto-refresh interval (seconds):",
                                value=config['refresh_seconds'],
                                min_value=5, max_value=60)
    
    if st.button("Update Refresh Rate"):
        config['refresh_seconds'] = new_refresh
        save_config(config)
        st.success("Refresh rate updated!")

def main():
    """Main application function."""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Initialize data - call this every time to ensure data exists
    load_seed_data()
    
    # Authentication check
    if not st.session_state.authenticated:
        show_login_page()
        return
    
    # Sidebar navigation
    st.sidebar.title(f"👤 {st.session_state.role_name}")
    st.sidebar.write(f"Logged in as: {st.session_state.user_role}")
    
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.role_name = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Navigation menu
    if st.session_state.user_role == "customer@demo":
        pages = {
            "⚡ Fleet Monitoring": show_fleet_monitoring,
            "🚨 Alerts": show_alerts_page,
            "🔧 Generator Detail": show_generator_detail
        }
    else:  # service@demo
        pages = {
            "⚡ Fleet Monitoring": show_fleet_monitoring,
            "🚨 Alerts": show_alerts_page,
            "🔧 Generator Detail": show_generator_detail,
            "🏢 Service Portal": show_service_portal,
            "⚙️ Admin": show_admin_page
        }
    
    selected_page = st.sidebar.selectbox("Navigation:", list(pages.keys()))
    
    # Display selected page
    pages[selected_page]()

if __name__ == "__main__":
    main()
