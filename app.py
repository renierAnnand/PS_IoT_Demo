"""
Power System Manufacturer IoT Platform
Work Management & Proactive Maintenance Platform
Focus: Ticketing system, proactive customer contact, enhanced customer portal
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pydeck as pdk
import json
import os
from datetime import datetime, timedelta
import time
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import functools

# Page configuration
st.set_page_config(
    page_title="Power System Work Management",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for work management focus
st.markdown("""
<style>
    .ticket-card {
        background: linear-gradient(135deg, #d32f2f 0%, #f44336 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.3rem 0;
        border-left: 5px solid #b71c1c;
    }
    .service-due-card {
        background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        border-left: 5px solid #e65100;
    }
    .revenue-opportunity {
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        border-left: 5px solid #1b5e20;
    }
    .generator-running {
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%);
        padding: 0.8rem;
        border-radius: 6px;
        color: white;
        margin: 0.2rem 0;
    }
    .generator-fault {
        background: linear-gradient(135deg, #d32f2f 0%, #f44336 100%);
        padding: 0.8rem;
        border-radius: 6px;
        color: white;
        margin: 0.2rem 0;
    }
    .generator-standby {
        background: linear-gradient(135deg, #757575 0%, #9e9e9e 100%);
        padding: 0.8rem;
        border-radius: 6px;
        color: white;
        margin: 0.2rem 0;
    }
    .generator-maintenance {
        background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
        padding: 0.8rem;
        border-radius: 6px;
        color: white;
        margin: 0.2rem 0;
    }
    .header-card {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .proactive-alert {
        background: linear-gradient(135deg, #7b1fa2 0%, #9c27b0 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        border: 2px solid #4a148c;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { border-color: #4a148c; }
        50% { border-color: #9c27b0; }
        100% { border-color: #4a148c; }
    }
</style>
""", unsafe_allow_html=True)

# Configuration
CONFIG = {
    "company_name": "Power System Manufacturing",
    "refresh_interval": 30,
    "cache_ttl": 300,
    "proactive_notification_hours": 72,
    "currency": {
        "symbol": "SAR",
        "rate": 3.75,  # 1 USD = 3.75 SAR
        "format": "SAR {:,.0f}"
    },
    "revenue_targets": {
        "service_revenue_per_ticket": 850 * 3.75,  # Convert to SAR
        "parts_revenue_per_ticket": 450 * 3.75
    }
}

def format_currency(amount_usd):
    """Convert USD to SAR and format properly."""
    amount_sar = amount_usd * CONFIG["currency"]["rate"]
    return CONFIG["currency"]["format"].format(amount_sar)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ========================================
# DATA MODELS AND GENERATION
# ========================================

@st.cache_data(ttl=CONFIG["cache_ttl"])
def load_base_generator_data() -> pd.DataFrame:
    """Load base generator data with enhanced status tracking."""
    generators_file = DATA_DIR / "generators.csv"
    
    if not generators_file.exists():
        generators_data = _generate_enhanced_generator_data()
        df = pd.DataFrame(generators_data)
        df.to_csv(generators_file, index=False)
        return df
    
    # Load existing data
    df = pd.read_csv(generators_file)
    
    # Check if customer_contact column exists, if not add it
    if 'customer_contact' not in df.columns:
        # Generate customer contacts based on customer names
        contact_mapping = {
            'King Faisal Medical City': 'ahmed.alrashid@kfmc.sa',
            'Riyadh Mall Complex': 'ops@riyadhmall.com',
            'SABIC Industrial': 'maint@sabic.com',
            'ARAMCO Office Tower': 'facility@aramco.com',
            'Al Rajhi Banking HQ': 'tech@alrajhi.com',
            'STC Data Center': 'ops@stc.sa',
            'NEOM Construction': 'eng@neom.sa',
            'Red Sea Project': 'maint@redsea.sa',
            'Saudi Airlines Hub': 'tech@saudiairlines.com',
            'KAUST Research': 'facility@kaust.edu.sa',
            'PIF Headquarters': 'ops@pif.gov.sa',
            'Vision 2030 Center': 'tech@vision2030.sa',
            'Ministry Complex': 'maint@ministry.gov.sa',
            'Royal Hospital': 'eng@royalhospital.sa',
            'Diplomatic Quarter': 'ops@diplomatic.sa',
            'Financial District': 'tech@financial.sa',
            'Entertainment City': 'facility@entertainment.sa',
            'Sports Boulevard': 'ops@sportsboulevard.sa',
            'Green Riyadh': 'eng@greenriyadh.sa',
            'ROSHN Development': 'tech@roshn.sa',
            'ENOWA Energy Hub': 'ops@enowa.sa',
            'THE LINE Project': 'eng@theline.sa',
            'Oxagon Port': 'facility@oxagon.sa',
            'Trojena Resort': 'tech@trojena.sa',
            'Al-Ula Heritage': 'ops@alula.sa',
            'Qiddiya Venue': 'facility@qiddiya.sa',
            'SPARK Sports': 'tech@spark.sa',
            'Mukaab Tower': 'eng@mukaab.sa',
            'Diriyah Gate': 'ops@diriyah.sa',
            'King Salman Park': 'facility@kingsalmanpark.sa'
        }
        
        df['customer_contact'] = df['customer_name'].map(contact_mapping).fillna('contact@customer.sa')
        
        # Save updated data
        df.to_csv(generators_file, index=False)
    
    # Check if installation_date exists, if not add it
    if 'installation_date' not in df.columns:
        df['installation_date'] = [
            datetime.now() - timedelta(days=random.randint(365, 1825)) for _ in range(len(df))
        ]
        df.to_csv(generators_file, index=False)
    
    return df

def _generate_enhanced_generator_data() -> Dict:
    """Generate enhanced generator data with operational status."""
    return {
        'serial_number': [f'PS-{2020 + i//4}-{i:04d}' for i in range(1, 31)],
        'model_series': ([
            'PS-2000 Series', 'PS-1500 Series', 'PS-1000 Series', 'PS-800 Series',
            'PS-2500 Industrial', 'PS-2000 Commercial', 'PS-1800 Healthcare', 'PS-1200 Retail'
        ] * 4)[:30],
        'customer_name': [
            'King Faisal Medical City', 'Riyadh Mall Complex', 'SABIC Industrial', 'ARAMCO Office Tower',
            'Al Rajhi Banking HQ', 'STC Data Center', 'NEOM Construction', 'Red Sea Project',
            'Saudi Airlines Hub', 'KAUST Research', 'PIF Headquarters', 'Vision 2030 Center',
            'Ministry Complex', 'Royal Hospital', 'Diplomatic Quarter', 'Financial District',
            'Entertainment City', 'Sports Boulevard', 'Green Riyadh', 'ROSHN Development',
            'ENOWA Energy Hub', 'THE LINE Project', 'Oxagon Port', 'Trojena Resort',
            'Al-Ula Heritage', 'Qiddiya Venue', 'SPARK Sports', 'Mukaab Tower',
            'Diriyah Gate', 'King Salman Park'
        ],
        'customer_contact': [
            'ahmed.alrashid@kfmc.sa', 'ops@riyadhmall.com', 'maint@sabic.com', 'facility@aramco.com',
            'tech@alrajhi.com', 'ops@stc.sa', 'eng@neom.sa', 'maint@redsea.sa',
            'tech@saudiairlines.com', 'facility@kaust.edu.sa', 'ops@pif.gov.sa', 'tech@vision2030.sa',
            'maint@ministry.gov.sa', 'eng@royalhospital.sa', 'ops@diplomatic.sa', 'tech@financial.sa',
            'facility@entertainment.sa', 'ops@sportsboulevard.sa', 'eng@greenriyadh.sa', 'tech@roshn.sa',
            'ops@enowa.sa', 'eng@theline.sa', 'facility@oxagon.sa', 'tech@trojena.sa',
            'ops@alula.sa', 'facility@qiddiya.sa', 'tech@spark.sa', 'eng@mukaab.sa',
            'ops@diriyah.sa', 'facility@kingsalmanpark.sa'
        ],
        'rated_kw': [
            2000, 1500, 1000, 800, 2500, 2000, 1800, 1200,
            1000, 750, 600, 400, 2200, 1800, 1400, 900,
            650, 500, 350, 300, 2800, 2200, 1600, 1100,
            850, 700, 450, 380, 320, 280
        ],
        'service_contract': [
            'Premium Care', 'Basic Maintenance', 'Preventive Plus', 'No Contract',
            'Premium Care', 'No Contract', 'Preventive Plus', 'Premium Care',
            'Basic Maintenance', 'Premium Care', 'No Contract', 'Basic Maintenance',
            'Preventive Plus', 'Premium Care', 'No Contract', 'Basic Maintenance',
            'Premium Care', 'No Contract', 'Preventive Plus', 'Basic Maintenance',
            'Premium Care', 'Premium Care', 'No Contract', 'Preventive Plus',
            'Basic Maintenance', 'Premium Care', 'No Contract', 'Basic Maintenance',
            'No Contract', 'Preventive Plus'
        ],
        'next_service_hours': [random.randint(-200, 800) for _ in range(30)],
        'total_runtime_hours': [random.randint(2000, 12000) for _ in range(30)],
        'location_city': [
            'Riyadh', 'Riyadh', 'Dammam', 'Riyadh', 'Riyadh', 'Jeddah', 'NEOM', 'Al-Ula',
            'Riyadh', 'Thuwal', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh',
            'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'NEOM', 'NEOM', 'NEOM', 'Qiddiya',
            'Al-Ula', 'Qiddiya', 'Riyadh', 'Riyadh', 'Diriyah', 'Riyadh'
        ],
        'installation_date': [
            datetime.now() - timedelta(days=random.randint(365, 1825)) for _ in range(30)
        ]
    }

@st.cache_data(ttl=60)  # Update every minute for real-time feel
def generate_real_time_status(generators_df: pd.DataFrame) -> pd.DataFrame:
    """Generate real-time operational status and sensor data."""
    seed = int(time.time() // 60)  # Changes every minute
    np.random.seed(seed)
    
    status_data = []
    for _, gen in generators_df.iterrows():
        try:
            # Operational status logic
            oil_pressure = np.random.uniform(20, 35)
            coolant_temp = np.random.uniform(75, 110)
            vibration = np.random.uniform(1.0, 6.0)
            fuel_level = np.random.uniform(10, 95)
            load_percent = np.random.uniform(0, 100)
            
            # Determine operational status
            has_fault = (oil_pressure < 25 or coolant_temp > 105 or vibration > 5.0 or fuel_level < 15)
            is_needed = np.random.choice([True, False], p=[0.7, 0.3])  # 70% chance generator is needed
            
            if has_fault:
                operational_status = "FAULT"
                status_color = "fault"
                fault_description = []
                if oil_pressure < 25: fault_description.append("Low oil pressure")
                if coolant_temp > 105: fault_description.append("High coolant temperature")
                if vibration > 5.0: fault_description.append("High vibration")
                if fuel_level < 15: fault_description.append("Low fuel")
                fault_desc = ", ".join(fault_description)
            elif is_needed and fuel_level > 20:
                operational_status = "RUNNING"
                status_color = "running"
                fault_desc = ""
            elif not is_needed:
                operational_status = "STANDBY"
                status_color = "standby"
                fault_desc = "Not required - standby mode"
            else:
                operational_status = "MAINTENANCE"
                status_color = "maintenance"
                fault_desc = "Scheduled maintenance"
            
            # Calculate next service notification with more variety
            service_hours = gen.get('next_service_hours', 500)  # Default to 500 if missing
            runtime_hours = gen.get('total_runtime_hours', 5000)
            
            # Different service types based on runtime and schedule
            if runtime_hours > 10000:  # High usage generators need more frequent service
                service_hours = max(-50, service_hours - 200)  # More likely to need service
            elif runtime_hours < 3000:  # Low usage generators
                service_hours = min(1000, service_hours + 300)  # Less frequent service needed
            
            # Create varied service needs
            needs_proactive_contact = False
            service_type = "Regular Maintenance"
            
            if service_hours < 0:
                needs_proactive_contact = True
                service_type = "Overdue Maintenance"
            elif service_hours < 48:  # Due within 48 hours
                needs_proactive_contact = True
                service_type = "Urgent Service Due"
            elif service_hours < CONFIG["proactive_notification_hours"]:  # Due within 72 hours
                needs_proactive_contact = True
                service_type = "Scheduled Service Due"
            elif service_hours < 168:  # Due within 1 week
                needs_proactive_contact = np.random.choice([True, False], p=[0.3, 0.7])  # 30% chance
                service_type = "Upcoming Service"
            
            # Get customer contact with fallback
            customer_contact = gen.get('customer_contact', 'contact@customer.sa')
            
            status_data.append({
                'serial_number': gen['serial_number'],
                'customer_name': gen['customer_name'],
                'customer_contact': customer_contact,
                'operational_status': operational_status,
                'status_color': status_color,
                'fault_description': fault_desc,
                'oil_pressure': round(oil_pressure, 1),
                'coolant_temp': round(coolant_temp, 1),
                'vibration': round(vibration, 2),
                'fuel_level': round(fuel_level, 1),
                'load_percent': round(load_percent, 1),
                'next_service_hours': service_hours,
                'service_type': service_type,
                'runtime_hours': runtime_hours,
                'needs_proactive_contact': needs_proactive_contact,
                'revenue_opportunity': has_fault or needs_proactive_contact
            })
        except Exception as e:
            # Skip problematic rows and continue
            continue
    
    return pd.DataFrame(status_data)

@st.cache_data(ttl=60)  # Update every minute for real-time feel
def generate_interval_service_data(generators_df: pd.DataFrame) -> pd.DataFrame:
    """Generate realistic interval-based service scheduling data."""
    seed = int(time.time() // 60)
    np.random.seed(seed)
    
    interval_data = []
    
    # Realistic service intervals and tasks
    service_types = {
        'minor': {
            'interval': 400,  # Every 250-500 hours (using 400 as average)
            'name': 'Minor Service',
            'tasks': ['Oil change', 'Oil filter replacement', 'Fuel filter change', 'Air filter check/clean', 'Coolant check', 'Battery inspection', 'Belts inspection', 'General operational checks'],
            'parts': ['Oil Filter', 'Oil (20L)', 'Fuel Filter'],
            'cost': 450 * 3.75  # Convert to SAR
        },
        'intermediate': {
            'interval': 1000,  # Every 1,000 hours
            'name': 'Intermediate Service',
            'tasks': ['All minor service items', 'Cooling system inspection', 'Exhaust inspection', 'Electrical connections check', 'Alternator inspection', 'Turbocharger check', 'Load testing'],
            'parts': ['Oil Filter', 'Oil (20L)', 'Fuel Filter', 'Air Filter', 'Coolant'],
            'cost': 850 * 3.75  # Convert to SAR
        },
        'major': {
            'interval': 15000,  # Every 10,000-20,000 hours (using 15,000 as average)
            'name': 'Major Service / Overhaul',
            'tasks': ['Complete engine teardown', 'Engine rebuild', 'Bearings replacement', 'Piston rings replacement', 'Valves replacement', 'Alternator refurbishment', 'Radiator re-core', 'Full electrical inspection'],
            'parts': ['Complete Engine Kit', 'Alternator Parts', 'Radiator Core', 'Electrical Components', 'Oil Filter', 'Oil (40L)', 'Coolant (20L)'],
            'cost': 12500 * 3.75  # Convert to SAR
        }
    }
    
    for _, gen in generators_df.iterrows():
        try:
            runtime_hours = gen.get('total_runtime_hours', random.randint(3000, 9000))
            model = gen['model_series']
            
            # Determine which service is due next based on runtime
            services_due = []
            
            for service_key, service_info in service_types.items():
                interval = service_info['interval']
                
                # Calculate hours since last service (simulate)
                hours_since_service = runtime_hours % interval
                hours_to_next_service = interval - hours_since_service
                
                # Calculate notification threshold (5% before interval)
                notification_threshold = interval * 0.05
                
                # Force some services to be due for demonstration purposes
                # Make 30% of generators due for service
                if np.random.random() < 0.3:
                    if service_key == 'minor':
                        hours_to_next_service = random.randint(-50, 20)  # Some overdue, some due soon
                    elif service_key == 'intermediate':
                        hours_to_next_service = random.randint(-100, 50)
                    elif service_key == 'major':
                        hours_to_next_service = random.randint(-200, 100)
                
                # Additional overdue services for demonstration
                if np.random.random() < 0.15:  # 15% chance of being overdue
                    hours_to_next_service = -random.randint(10, 300)
                
                services_due.append({
                    'service_type': service_key,
                    'service_name': service_info['name'],
                    'hours_to_next': hours_to_next_service,
                    'notification_threshold': notification_threshold,
                    'tasks': service_info['tasks'],
                    'parts': service_info['parts'],
                    'cost': service_info['cost'],
                    'needs_contact': hours_to_next_service <= notification_threshold
                })
            
            # Find the most urgent service (closest to due or overdue)
            most_urgent = min(services_due, key=lambda x: x['hours_to_next'])
            
            # Only include if it needs contact or is overdue
            if most_urgent['needs_contact'] or most_urgent['hours_to_next'] <= 0:
                
                # Determine status and priority
                if most_urgent['hours_to_next'] < 0:
                    service_status = "OVERDUE"
                    priority = "CRITICAL" if most_urgent['service_type'] == 'major' else "HIGH"
                    days_overdue = abs(most_urgent['hours_to_next']) // 24
                    service_detail = f"{most_urgent['service_name']} overdue by {days_overdue} days"
                elif most_urgent['hours_to_next'] <= most_urgent['notification_threshold']:
                    service_status = "DUE SOON"
                    priority = "HIGH" if most_urgent['service_type'] == 'major' else "MEDIUM"
                    service_detail = f"{most_urgent['service_name']} due in {int(most_urgent['hours_to_next'])} hours"
                else:
                    service_status = "SCHEDULED"
                    priority = "LOW"
                    service_detail = f"Next {most_urgent['service_name']} in {int(most_urgent['hours_to_next'])} hours"
                
                # Adjust cost for overdue services
                estimated_cost = most_urgent['cost']
                if most_urgent['hours_to_next'] < 0:
                    estimated_cost = int(estimated_cost * 1.2)  # 20% surcharge for delayed service
                
                # Critical applications (Healthcare) get higher priority
                if 'Healthcare' in model:
                    if priority == "MEDIUM":
                        priority = "HIGH"
                    elif priority == "LOW":
                        priority = "MEDIUM"
                
                interval_data.append({
                    'serial_number': gen['serial_number'],
                    'customer_name': gen['customer_name'],
                    'customer_contact': gen.get('customer_contact', 'contact@customer.sa'),
                    'model_series': model,
                    'service_type': most_urgent['service_type'],
                    'service_name': most_urgent['service_name'],
                    'service_interval': service_types[most_urgent['service_type']]['interval'],
                    'runtime_hours': runtime_hours,
                    'hours_to_next_service': int(most_urgent['hours_to_next']),
                    'service_status': service_status,
                    'priority': priority,
                    'service_detail': service_detail,
                    'tasks_required': '; '.join(most_urgent['tasks'][:3]) + ('...' if len(most_urgent['tasks']) > 3 else ''),
                    'parts_needed': ", ".join(most_urgent['parts']),
                    'estimated_cost': estimated_cost,
                    'needs_contact': True,
                    'contact_status': 'PENDING',
                    'contact_notes': '',
                    'last_contact_date': None,
                    'service_booked': False
                })
                
        except Exception as e:
            continue
    
    return pd.DataFrame(interval_data)

# ========================================
# AUTHENTICATION
# ========================================

def authenticate_system():
    """Authentication for work management system."""
    st.markdown("""
    <div class="header-card">
        <h1>⚡ Power System Work Management</h1>
        <h2>Proactive Maintenance & Customer Management Platform</h2>
        <p>Advanced ticketing • Proactive notifications • Customer portal</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        user_roles = {
            "operations@powersystem": "🔧 Operations Manager - Work Orders & Tickets",
            "service@powersystem": "⚡ Service Team - Field Operations",
            "sales@powersystem": "💰 Sales Team - Revenue Opportunities",
            "customer@powersystem": "🏢 Customer Portal - Generator Status"
        }
        
        selected_role = st.selectbox(
            "Select your access level:",
            options=list(user_roles.keys()),
            format_func=lambda x: user_roles[x]
        )
        
        if st.button("🚀 Access Work Management System", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = selected_role
            st.session_state.role_name = user_roles[selected_role]
            st.rerun()

# ========================================
# WORK MANAGEMENT DASHBOARD
# ========================================

def show_work_management_dashboard():
    """Advanced work management and ticketing system."""
    st.title("🎫 Work Management & Ticketing System")
    st.markdown("### Proactive Service Scheduling & Revenue Optimization")
    
    # Initialize filter state
    if 'active_filter' not in st.session_state:
        st.session_state.active_filter = 'all'
    
    try:
        # Load data first
        generators_df = load_base_generator_data()
        if generators_df.empty:
            st.error("No generator data available. Please check data initialization.")
            return
            
        status_df = generate_real_time_status(generators_df)
        if status_df.empty:
            st.error("No status data available. Please check data generation.")
            return
            
        interval_service_df = generate_interval_service_data(generators_df)
        
        # Calculate all metrics at the beginning
        # Basic counts
        total_generators = len(generators_df)
        running_count = len(status_df[status_df['operational_status'] == 'RUNNING'])
        fault_count = len(status_df[status_df['operational_status'] == 'FAULT'])
        
        # Opportunity calculations
        fault_opportunities = len(status_df[status_df['revenue_opportunity'] == True])
        
        if interval_service_df.empty:
            interval_opportunities = 0
            service_due_count = 0
            overdue_service = 0
            interval_revenue = 0
        else:
            interval_opportunities = len(interval_service_df[interval_service_df['needs_contact'] == True])
            service_due_count = interval_opportunities
            overdue_service = len(interval_service_df[interval_service_df['service_status'] == 'OVERDUE'])
            interval_revenue = interval_service_df[interval_service_df['needs_contact'] == True]['estimated_cost'].sum()
        
        total_opportunities = fault_opportunities + interval_opportunities
        
        # Revenue calculations
        fault_revenue = fault_opportunities * CONFIG['revenue_targets']['service_revenue_per_ticket']
        potential_revenue = fault_revenue + interval_revenue
        
        # Enhanced metric cards with click functionality
        st.subheader("📊 Key Metrics - Click to Filter")
        
        # Show current filter status
        filter_labels = {
            'all': 'All Tickets',
            'active_tickets': 'Active Tickets',
            'service_due': 'Service Due',
            'fault_alerts': 'Fault Alerts',
            'revenue_potential': 'Revenue Potential',
            'generators_running': 'Generators Running'
        }
        
        current_filter = filter_labels.get(st.session_state.active_filter, 'All Tickets')
        st.info(f"🔍 **Current Filter:** {current_filter}")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            # Active filter styling
            card_class = "ticket-card" if st.session_state.active_filter != 'active_tickets' else "ticket-card"
            border_style = "border: 3px solid #fff;" if st.session_state.active_filter == 'active_tickets' else ""
            
            if st.button(f"🎫 Active Tickets\n{total_opportunities}\nRevenue opportunities", key="btn_active_tickets", use_container_width=True):
                st.session_state.active_filter = 'active_tickets'
                st.rerun()
            
            st.markdown(f"""
            <div class="{card_class}" style="{border_style}">
                <p style='font-size:12px; margin:0;'>🚨 {fault_opportunities} faults | ⏰ {interval_opportunities} intervals</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            service_color = "service-due-card"
            border_style = "border: 3px solid #fff;" if st.session_state.active_filter == 'service_due' else ""
            
            if st.button(f"⏰ Service Due\n{service_due_count}\nProactive notifications", key="btn_service_due", use_container_width=True):
                st.session_state.active_filter = 'service_due'
                st.rerun()
            
            st.markdown(f"""
            <div class="{service_color}" style="{border_style}">
                {"<p style='font-size:12px; margin:0;'>⚠️ " + str(overdue_service) + " overdue</p>" if overdue_service > 0 else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            border_style = "border: 3px solid #fff;" if st.session_state.active_filter == 'fault_alerts' else ""
            
            if st.button(f"🚨 Fault Alerts\n{fault_count}\nImmediate response needed", key="btn_fault_alerts", use_container_width=True):
                st.session_state.active_filter = 'fault_alerts'
                st.rerun()
            
            st.markdown(f"""
            <div class="ticket-card" style="{border_style}">
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            border_style = "border: 3px solid #fff;" if st.session_state.active_filter == 'revenue_potential' else ""
            
            if st.button(f"💰 Revenue Potential\n{format_currency(potential_revenue / 3.75)}\nFrom current tickets", key="btn_revenue_potential", use_container_width=True):
                st.session_state.active_filter = 'revenue_potential'
                st.rerun()
            
            st.markdown(f"""
            <div class="revenue-opportunity" style="{border_style}">
                <p style='font-size:12px; margin:0;'>🚨 {format_currency(fault_revenue / 3.75)} | ⏰ {format_currency(interval_revenue / 3.75)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            border_style = "border: 3px solid #fff;" if st.session_state.active_filter == 'generators_running' else ""
            
            if st.button(f"⚡ Generators Running\n{running_count}\nOf {total_generators} total", key="btn_generators_running", use_container_width=True):
                st.session_state.active_filter = 'generators_running'
                st.rerun()
            
            st.markdown(f"""
            <div class="revenue-opportunity" style="{border_style}">
            </div>
            """, unsafe_allow_html=True)
        
        # Show filtered content based on active filter
        if total_opportunities > 0:
            show_filtered_tickets(status_df, interval_service_df, st.session_state.active_filter)
        else:
            st.success("✅ No immediate proactive notifications required!")
            show_system_status(status_df, interval_service_df)
    
    except Exception as e:
        st.error(f"Error loading work management dashboard: {str(e)}")
        st.info("Please try refreshing the page.")
        if st.button("🔄 Retry Loading Dashboard"):
            st.rerun()

def show_filtered_tickets(status_df, interval_service_df, active_filter):
    """Display tickets filtered by the selected category."""
    st.subheader("🔔 Filtered Tickets")
    
    # Get fault opportunities
    fault_opportunities = status_df[
        (status_df['needs_proactive_contact'] == True) | 
        (status_df['operational_status'] == 'FAULT')
    ]
    
    # Get interval opportunities
    interval_opportunities = interval_service_df[interval_service_df['needs_contact'] == True] if not interval_service_df.empty else pd.DataFrame()
    
    # Combine tickets
    combined_tickets = []
    
    # Add fault tickets
    for _, opportunity in fault_opportunities.iterrows():
        try:
            if opportunity['operational_status'] == 'FAULT':
                ticket_type = "🚨 FAULT RESPONSE"
                priority = "CRITICAL"
                estimated_revenue_usd = CONFIG['revenue_targets']['service_revenue_per_ticket'] / 3.75 * 1.5  # Convert back to USD for calculation
                action = "Contact immediately - Emergency service"
                service_detail = opportunity['fault_description']
                parts_needed = "TBD"
                ticket_category = 'fault'
            else:
                ticket_type = "📅 PREVENTIVE SERVICE"
                priority = "HIGH"
                estimated_revenue_usd = CONFIG['revenue_targets']['service_revenue_per_ticket'] / 3.75  # Convert back to USD for calculation
                action = "Schedule within 72 hours"
                service_detail = f"Service due in {opportunity['next_service_hours']} hours"
                parts_needed = "Oil Filter, Oil"
                ticket_category = 'fault'
            
            combined_tickets.append({
                'Ticket ID': f"TK-{random.randint(10000, 99999)}",
                'Type': ticket_type,
                'Generator': opportunity['serial_number'],
                'Customer': opportunity['customer_name'][:20] + "...",
                'Contact': opportunity['customer_contact'],
                'Service Detail': service_detail,
                'Runtime Hours': f"{opportunity.get('runtime_hours', 5000):,} hrs",
                'Parts Needed': parts_needed,
                'Priority': priority,
                'Est. Revenue': format_currency(estimated_revenue_usd),
                'Action Required': action,
                'Category': ticket_category,
                'Revenue_USD': estimated_revenue_usd
            })
        except Exception:
            continue
    
    # Add interval service tickets
    for _, service in interval_opportunities.iterrows():
        try:
            if service['service_status'] == 'OVERDUE':
                ticket_type = f"🔴 {service['service_name'].upper()}"
                priority = "CRITICAL" if service['service_type'] == 'major' else "HIGH"
                action = "Contact immediately - Service overdue"
            elif service['priority'] == 'HIGH':
                ticket_type = f"🟡 {service['service_name'].upper()}"
                priority = "HIGH"
                action = "Schedule within 48 hours"
            else:
                ticket_type = f"🟢 {service['service_name'].upper()}"
                priority = "MEDIUM"
                action = "Schedule within 1 week"
            
            estimated_revenue_usd = service['estimated_cost'] / 3.75  # Convert SAR back to USD for consistency
            
            combined_tickets.append({
                'Ticket ID': f"SV-{random.randint(10000, 99999)}",
                'Type': ticket_type,
                'Generator': service['serial_number'],
                'Customer': service['customer_name'][:20] + "...",
                'Contact': service['customer_contact'],
                'Service Detail': service['service_detail'],
                'Runtime Hours': f"{service['runtime_hours']:,} hrs",
                'Parts Needed': service['parts_needed'],
                'Priority': priority,
                'Est. Revenue': format_currency(estimated_revenue_usd),
                'Action Required': action,
                'Category': 'service',
                'Revenue_USD': estimated_revenue_usd
            })
        except Exception:
            continue
    
    if combined_tickets:
        tickets_df = pd.DataFrame(combined_tickets)
        
        # Apply filtering based on active_filter
        if active_filter == 'fault_alerts':
            filtered_tickets = tickets_df[tickets_df['Category'] == 'fault']
            filter_title = "🚨 Fault Response Tickets"
        elif active_filter == 'service_due':
            filtered_tickets = tickets_df[tickets_df['Category'] == 'service']
            filter_title = "⏰ Service Due Tickets"
        elif active_filter == 'revenue_potential':
            # Sort by revenue - highest first
            filtered_tickets = tickets_df.sort_values('Revenue_USD', ascending=False)
            filter_title = "💰 Tickets by Revenue Potential"
        elif active_filter == 'active_tickets':
            filtered_tickets = tickets_df
            filter_title = "🎫 All Active Tickets"
        elif active_filter == 'generators_running':
            # Show operational status info instead of tickets
            st.info("Generator operational status information:")
            running_gens = status_df[status_df['operational_status'] == 'RUNNING']
            if not running_gens.empty:
                status_display = running_gens[['serial_number', 'customer_name', 'load_percent', 'fuel_level']].copy()
                status_display.columns = ['Generator', 'Customer', 'Load %', 'Fuel %']
                st.dataframe(status_display, use_container_width=True, hide_index=True)
            return
        else:
            filtered_tickets = tickets_df
            filter_title = "🎫 All Tickets"
        
        st.markdown(f"""
        <div class="proactive-alert">
            <h4>{filter_title}</h4>
            <p>Showing {len(filtered_tickets)} of {len(tickets_df)} total tickets</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sort by priority
        priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
        filtered_tickets['priority_sort'] = filtered_tickets['Priority'].map(priority_order)
        filtered_tickets = filtered_tickets.sort_values('priority_sort').drop(['priority_sort', 'Category', 'Revenue_USD'], axis=1)
        
        st.dataframe(filtered_tickets, use_container_width=True, hide_index=True)
        
        # Add filter reset button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Show All Tickets", use_container_width=True):
                st.session_state.active_filter = 'all'
                st.rerun()
        
        # Work Order Management
        show_work_order_management(filtered_tickets)

def show_work_order_management(tickets_df):
    """Work order creation and management interface."""
    st.subheader("📋 Work Order Management")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if not tickets_df.empty:
            ticket_options = [
                f"{row['Ticket ID']} - {row['Type']} - {row['Generator']} - {row['Customer']}"
                for _, row in tickets_df.iterrows()
            ]
            
            selected_ticket = st.selectbox(
                "Select ticket to create work order:",
                options=ticket_options,
                key="wo_ticket_select"
            )
            
            if selected_ticket:
                ticket_id = selected_ticket.split(' - ')[0]
                selected_row = tickets_df[tickets_df['Ticket ID'] == ticket_id].iloc[0]
                
                technician_options = [
                    "Ahmed Al-Rashid (Riyadh Region)",
                    "Mohammed Al-Saud (Jeddah Region)", 
                    "Khalid Al-Otaibi (Eastern Region)",
                    "Abdullah Al-Nasser (NEOM Region)",
                    "Auto-assign based on location"
                ]
                
                selected_technician = st.selectbox(
                    "Assign technician:",
                    options=technician_options,
                    key="technician_select"
                )
                
                schedule_options = [
                    "🚨 Emergency - Same day",
                    "⚡ Urgent - Within 24 hours", 
                    "📅 Scheduled - Within 3 days",
                    "📆 Planned - Within 1 week"
                ]
                
                selected_schedule = st.selectbox(
                    "Schedule priority:",
                    options=schedule_options,
                    key="schedule_select"
                )
                
                wo_notes = st.text_area(
                    "Work order notes:",
                    placeholder="Enter special instructions...",
                    key="wo_notes"
                )
        else:
            st.info("No tickets available for work order creation")
    
    with col2:
        st.write("**Selected Ticket Details:**")
        if 'selected_row' in locals():
            st.info(f"""
            **Generator:** {selected_row['Generator']}
            **Customer:** {selected_row['Customer']}
            **Type:** {selected_row['Type']}
            **Priority:** {selected_row['Priority']}
            **Revenue:** {selected_row['Est. Revenue']}
            """)
        
        st.write("**🔧 Action Buttons:**")
        
        if st.button("📋 Create Work Order", use_container_width=True, type="primary"):
            if 'selected_ticket' in locals() and 'selected_technician' in locals() and 'selected_schedule' in locals():
                wo_number = f"WO-{random.randint(100000, 999999)}"
                st.success(f"✅ Work Order {wo_number} created successfully!")
                if 'selected_technician' in locals():
                    st.info(f"👷 Assigned to: {selected_technician.split('(')[0].strip()}")
                if 'selected_schedule' in locals():
                    st.info(f"⏰ Schedule: {selected_schedule}")
                
                # Show work order summary with SAR currency
                with st.expander("📋 Work Order Summary"):
                    if 'selected_row' in locals():
                        st.write(f"""
                        **Work Order:** {wo_number}
                        **Ticket:** {selected_row['Ticket ID']}
                        **Generator:** {selected_row['Generator']}
                        **Customer:** {selected_row['Customer']}
                        **Service Type:** {selected_row['Type']}
                        **Technician:** {selected_technician}
                        **Schedule:** {selected_schedule}
                        **Estimated Revenue:** {selected_row['Est. Revenue']}
                        **Parts Required:** {selected_row['Parts Needed']}
                        **Notes:** {'wo_notes' if 'wo_notes' in locals() and wo_notes else 'None'}
                        """)
            else:
                st.error("Please select all required fields")
        
        if st.button("📞 Mark as Contacted", use_container_width=True):
            st.success("📞 Contact status updated!")
        
        if st.button("❌ Close Ticket", use_container_width=True):
            st.warning("❌ Ticket closed")
        
        if st.button("📧 Send Quote", use_container_width=True):
            st.success("📧 Quote sent to customer!")

def show_system_status(status_df, interval_service_df):
    """Show system status when no tickets are active."""
    st.info(f"""
    **System Status:**
    - ✅ {len(status_df)} generators checked for faults
    - ✅ {len(interval_service_df)} generators checked for service intervals  
    - ✅ All systems operating within normal parameters
    """)

# ========================================
# ENHANCED CUSTOMER PORTAL
# ========================================

def show_enhanced_customer_portal():
    """Enhanced customer portal with real-time generator status and sensor readings."""
    st.title("🏢 Customer Portal - Real-Time Generator Monitoring")
    st.markdown("### Live Status • Sensor Readings • Operational Health")
    
    try:
        # Load data
        generators_df = load_base_generator_data()
        status_df = generate_real_time_status(generators_df)
        
        if generators_df.empty:
            st.error("No generator data available. Please contact support.")
            return
        
        # Customer selection
        customers = generators_df['customer_name'].unique()
        selected_customer = st.selectbox("Select Your Organization:", customers, key="customer_select")
        
        # Filter data for selected customer
        customer_generators = generators_df[generators_df['customer_name'] == selected_customer]
        customer_status = status_df[status_df['customer_name'] == selected_customer]
        
        if customer_generators.empty:
            st.error("No generators found for selected customer")
            return
        
        st.markdown(f"### Welcome, {selected_customer}")
        
        # Customer metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_capacity = customer_generators['rated_kw'].sum()
        running_count = len(customer_status[customer_status['operational_status'] == 'RUNNING'])
        fault_count = len(customer_status[customer_status['operational_status'] == 'FAULT'])
        standby_count = len(customer_status[customer_status['operational_status'] == 'STANDBY'])
        avg_load = customer_status['load_percent'].mean() if not customer_status.empty else 0
        
        with col1:
            st.metric("Total Capacity", f"{total_capacity:,.0f} kW")
        with col2:
            st.metric("🟢 Running", running_count, delta="Active")
        with col3:
            st.metric("🔴 Faults", fault_count, delta="⚠️ Attention" if fault_count > 0 else "✅ Normal")
        with col4:
            st.metric("⚪ Standby", standby_count, delta="Ready")
        with col5:
            st.metric("Average Load", f"{avg_load:.1f}%")
        
        # Generator status details
        st.subheader("⚡ Your Generator Fleet - Live Status")
        
        if not customer_status.empty:
            for _, gen_status in customer_status.iterrows():
                try:
                    gen_info = customer_generators[customer_generators['serial_number'] == gen_status['serial_number']].iloc[0]
                    
                    status_class = f"generator-{gen_status['status_color']}"
                    
                    if gen_status['operational_status'] == 'RUNNING':
                        status_icon = "🟢 RUNNING"
                        status_detail = f"Load: {gen_status['load_percent']}% | All systems normal"
                    elif gen_status['operational_status'] == 'FAULT':
                        status_icon = "🔴 FAULT"
                        status_detail = f"⚠️ {gen_status['fault_description']}"
                    elif gen_status['operational_status'] == 'STANDBY':
                        status_icon = "⚪ STANDBY"
                        status_detail = "Generator ready - Not currently needed"
                    else:
                        status_icon = "🟡 MAINTENANCE"
                        status_detail = "Scheduled maintenance in progress"
                    
                    col1, col2 = st.columns([2, 3])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="{status_class}">
                            <h4>{gen_status['serial_number']} - {status_icon}</h4>
                            <p><strong>Model:</strong> {gen_info['model_series']}</p>
                            <p><strong>Capacity:</strong> {gen_info['rated_kw']} kW</p>
                            <p><strong>Status:</strong> {status_detail}</p>
                            <p><strong>Location:</strong> {gen_info['location_city']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        sensor_col1, sensor_col2, sensor_col3, sensor_col4 = st.columns(4)
                        
                        with sensor_col1:
                            oil_color = "🟢" if gen_status['oil_pressure'] >= 28 else "🟡" if gen_status['oil_pressure'] >= 25 else "🔴"
                            st.metric("Oil Pressure", f"{gen_status['oil_pressure']} PSI", delta=f"{oil_color}")
                        
                        with sensor_col2:
                            temp_color = "🟢" if gen_status['coolant_temp'] <= 95 else "🟡" if gen_status['coolant_temp'] <= 105 else "🔴"
                            st.metric("Coolant Temp", f"{gen_status['coolant_temp']}°C", delta=f"{temp_color}")
                        
                        with sensor_col3:
                            vib_color = "🟢" if gen_status['vibration'] <= 4.0 else "🟡" if gen_status['vibration'] <= 5.0 else "🔴"
                            st.metric("Vibration", f"{gen_status['vibration']} mm/s", delta=f"{vib_color}")
                        
                        with sensor_col4:
                            fuel_color = "🟢" if gen_status['fuel_level'] >= 50 else "🟡" if gen_status['fuel_level'] >= 20 else "🔴"
                            st.metric("Fuel Level", f"{gen_status['fuel_level']}%", delta=f"{fuel_color}")
                    
                    st.markdown("---")
                except Exception:
                    continue
        
        # Quick actions
        st.subheader("🚀 Service & Support")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📅 Schedule Maintenance", use_container_width=True):
                st.success("✅ Maintenance request submitted!")
        
        with col2:
            if st.button("🚨 Report Emergency", use_container_width=True, type="primary"):
                st.success("🚨 Emergency ticket created!")
        
        with col3:
            if st.button("🛒 Request Parts Quote", use_container_width=True):
                st.success("🛒 Parts specialist will contact you!")
        
        with col4:
            if st.button("📞 Contact Support", use_container_width=True):
                st.success("📞 Support ticket created!")
        
    except Exception as e:
        st.error(f"Error loading customer portal: {str(e)}")

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Main application with work management focus."""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Authentication check
    if not st.session_state.authenticated:
        authenticate_system()
        return
    
    # Sidebar
    st.sidebar.markdown(f"### {st.session_state.role_name}")
    st.sidebar.write("Power System Work Management")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Role-based navigation
    if st.session_state.user_role in ["operations@powersystem", "service@powersystem", "sales@powersystem"]:
        pages = {
            "🎫 Work Management": show_work_management_dashboard,
            "🏢 Customer Portal": show_enhanced_customer_portal
        }
    else:  # customer@powersystem
        pages = {
            "🏢 My Generators": show_enhanced_customer_portal
        }
    
    selected_page = st.sidebar.selectbox("Navigate:", list(pages.keys()))
    
    # Display selected page
    try:
        pages[selected_page]()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please try refreshing the page.")
    
    # Sidebar status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 System Status")
    st.sidebar.success("✅ Real-time monitoring active")
    st.sidebar.info(f"🕒 Last update: {datetime.now().strftime('%H:%M:%S')}")
    
    # Key platform features
    st.sidebar.markdown("### ⚡ Platform Features")
    st.sidebar.markdown("✅ Proactive Service Notifications")
    st.sidebar.markdown("✅ Advanced Ticketing System")
    st.sidebar.markdown("🆕 **Professional Service Intervals**")
    st.sidebar.markdown("   • Minor (250-500 hrs)")
    st.sidebar.markdown("   • Intermediate (1,000 hrs)")
    st.sidebar.markdown("   • Major (10,000-20,000 hrs)")
    st.sidebar.markdown("✅ Real-time Generator Status")
    st.sidebar.markdown("✅ Live Sensor Monitoring")
    st.sidebar.markdown("✅ Revenue Optimization")
    st.sidebar.markdown("✅ Customer Self-Service Portal")

if __name__ == "__main__":
    main()
