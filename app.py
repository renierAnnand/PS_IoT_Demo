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
    "proactive_notification_hours": 72,  # Hours in advance to notify
    "revenue_targets": {
        "service_revenue_per_ticket": 850,
        "parts_revenue_per_ticket": 450
    }
}

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
            'cost': 450
        },
        'intermediate': {
            'interval': 1000,  # Every 1,000 hours
            'name': 'Intermediate Service',
            'tasks': ['All minor service items', 'Cooling system inspection', 'Exhaust inspection', 'Electrical connections check', 'Alternator inspection', 'Turbocharger check', 'Load testing'],
            'parts': ['Oil Filter', 'Oil (20L)', 'Fuel Filter', 'Air Filter', 'Coolant'],
            'cost': 850
        },
        'major': {
            'interval': 15000,  # Every 10,000-20,000 hours (using 15,000 as average)
            'name': 'Major Service / Overhaul',
            'tasks': ['Complete engine teardown', 'Engine rebuild', 'Bearings replacement', 'Piston rings replacement', 'Valves replacement', 'Alternator refurbishment', 'Radiator re-core', 'Full electrical inspection'],
            'parts': ['Complete Engine Kit', 'Alternator Parts', 'Radiator Core', 'Electrical Components', 'Oil Filter', 'Oil (40L)', 'Coolant (20L)'],
            'cost': 12500
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
                hours_since_service = runtime_hours % interval
                hours_to_next_service = interval - hours_since_service
                
                # Calculate notification threshold (5% before interval)
                notification_threshold = interval * 0.05
                
                # Add some variation - some might be overdue
                if np.random.random() < 0.1:  # 10% chance of being overdue
                    hours_to_next_service = -random.randint(10, 200)
                
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
            
            # Calculate next service notification
            service_hours = gen.get('next_service_hours', 500)  # Default to 500 if missing
            needs_proactive_contact = service_hours < CONFIG["proactive_notification_hours"] and service_hours > 0
            
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
                'needs_proactive_contact': needs_proactive_contact,
                'revenue_opportunity': has_fault or needs_proactive_contact
            })
        except Exception as e:
            # Skip problematic rows and continue
            st.error(f"Error processing generator {gen.get('serial_number', 'Unknown')}: {str(e)}")
            continue
    
    return pd.DataFrame(status_data)

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
    
    try:
        # Load data
        generators_df = load_base_generator_data()
        status_df = generate_real_time_status(generators_df)
        interval_service_df = generate_interval_service_data(generators_df)
        
        if generators_df.empty or status_df.empty:
            st.error("No generator data available. Please check data initialization.")
            return
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Calculate metrics with enhanced service tracking
        total_opportunities = len(status_df[status_df['revenue_opportunity'] == True])
        fault_count = len(status_df[status_df['operational_status'] == 'FAULT'])
        service_due = len(status_df[status_df['needs_proactive_contact'] == True])
        overdue_service = len(status_df[status_df['next_service_hours'] < 0])
        potential_revenue = total_opportunities * CONFIG['revenue_targets']['service_revenue_per_ticket']
        
        with col1:
            st.markdown(f"""
            <div class="ticket-card">
                <h4>🎫 Active Tickets</h4>
                <h2>{total_opportunities}</h2>
                <p>Revenue opportunities</p>
                <p style='font-size:12px;'>🚨 {fault_opportunities} faults | ⏰ {interval_opportunities} intervals</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            service_color = "service-due-card" if service_due_count > 0 else "revenue-opportunity"
            st.markdown(f"""
            <div class="{service_color}">
                <h4>⏰ Service Due</h4>
                <h2>{service_due_count}</h2>
                <p>Proactive notifications</p>
                {"<p style='font-size:12px;'>⚠️ " + str(overdue_service) + " overdue</p>" if overdue_service > 0 else ""}
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="ticket-card">
                <h4>🚨 Fault Alerts</h4>
                <h2>{fault_count}</h2>
                <p>Immediate response needed</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="revenue-opportunity">
                <h4>💰 Revenue Potential</h4>
                <h2>${potential_revenue:,.0f}</h2>
                <p>From current tickets</p>
                <p style='font-size:12px;'>🚨 ${fault_revenue:,.0f} | ⏰ ${interval_revenue:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            running_count = len(status_df[status_df['operational_status'] == 'RUNNING'])
            st.markdown(f"""
            <div class="revenue-opportunity">
                <h4>⚡ Generators Running</h4>
                <h2>{running_count}</h2>
                <p>Of {len(status_df)} total</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Proactive notifications section - COMBINED fault and service tickets
        st.subheader("🔔 Proactive Customer Notifications")
        
        # Combine fault-based and interval service opportunities
        fault_opportunities = status_df[
            (status_df['needs_proactive_contact'] == True) | 
            (status_df['operational_status'] == 'FAULT')
        ].copy()
        
        # Get interval service opportunities
        interval_opportunities = interval_service_df[interval_service_df['needs_contact'] == True].copy()
        
        # Combine both types of tickets
        combined_tickets = []
        
        # Add fault-based tickets
        for _, opportunity in fault_opportunities.iterrows():
            if opportunity['operational_status'] == 'FAULT':
                ticket_type = "🚨 FAULT RESPONSE"
                priority = "CRITICAL"
                estimated_revenue = CONFIG['revenue_targets']['service_revenue_per_ticket'] * 1.5
                action = "Contact immediately - Emergency service"
                service_detail = opportunity['fault_description']
                parts_needed = "TBD"
                runtime_hours = opportunity.get('runtime_hours', 5000)
            else:
                ticket_type = "📅 PREVENTIVE SERVICE"
                priority = "HIGH"
                estimated_revenue = CONFIG['revenue_targets']['service_revenue_per_ticket']
                action = "Schedule within 72 hours"
                service_detail = f"Service due in {opportunity['next_service_hours']} hours"
                parts_needed = "Oil Filter, Oil"
                runtime_hours = opportunity.get('runtime_hours', 5000)
            
            combined_tickets.append({
                'Ticket ID': f"TK-{random.randint(10000, 99999)}",
                'Type': ticket_type,
                'Generator': opportunity['serial_number'],
                'Customer': opportunity['customer_name'][:20] + "...",
                'Contact': opportunity['customer_contact'],
                'Service Detail': service_detail,
                'Runtime Hours': f"{runtime_hours:,} hrs",
                'Parts Needed': parts_needed,
                'Priority': priority,
                'Est. Revenue': f"${estimated_revenue:,.0f}",
                'Action Required': action,
                'Ticket Source': 'fault'
            })
        
        # Add interval service tickets
        for _, service in interval_opportunities.iterrows():
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
                'Est. Revenue': f"${service['estimated_cost']:,.0f}",
                'Action Required': action,
                'Ticket Source': 'service'
            })
        
        if combined_tickets:
            st.markdown("""
            <div class="proactive-alert">
                <h4>🚨 Immediate Action Required</h4>
                <p>The following customers should be contacted proactively to arrange service and maximize revenue:</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Display combined tickets table
            tickets_df = pd.DataFrame(combined_tickets)
            
            # Sort by priority (Critical first, then High, then Medium)
            priority_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2}
            tickets_df['priority_sort'] = tickets_df['Priority'].map(priority_order)
            tickets_df = tickets_df.sort_values('priority_sort').drop('priority_sort', axis=1)
            
            # Display the table without the Ticket Source column (internal use only)
            display_df = tickets_df.drop(['Ticket Source'], axis=1)
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Work Order Creation Section
            st.subheader("📋 Work Order Management")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Select ticket for work order creation
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
                    # Get selected ticket details
                    ticket_id = selected_ticket.split(' - ')[0]
                    selected_row = tickets_df[tickets_df['Ticket ID'] == ticket_id].iloc[0]
                    
                    # Technician assignment
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
                    
                    # Schedule options
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
                    
                    # Additional work order notes
                    wo_notes = st.text_area(
                        "Work order notes:",
                        placeholder="Enter special instructions, customer requirements, site access details...",
                        key="wo_notes"
                    )
            
            with col2:
                st.write("**Selected Ticket Details:**")
                if selected_ticket:
                    st.info(f"""
                    **Generator:** {selected_row['Generator']}
                    **Customer:** {selected_row['Customer']}
                    **Type:** {selected_row['Type']}
                    **Priority:** {selected_row['Priority']}
                    **Revenue:** {selected_row['Est. Revenue']}
                    **Parts:** {selected_row['Parts Needed'][:30]}...
                    """)
                
                st.write("**🔧 Action Buttons:**")
                
                if st.button("📋 Create Work Order", use_container_width=True, type="primary"):
                    if selected_ticket and selected_technician and selected_schedule:
                        wo_number = f"WO-{random.randint(100000, 999999)}"
                        st.success(f"✅ Work Order {wo_number} created successfully!")
                        st.info(f"👷 Assigned to: {selected_technician.split('(')[0].strip()}")
                        st.info(f"⏰ Schedule: {selected_schedule}")
                        st.info(f"📧 Customer notification sent to {selected_row['Contact']}")
                        
                        # Show work order summary
                        with st.expander("📋 Work Order Summary"):
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
                            **Notes:** {wo_notes if wo_notes else 'None'}
                            """)
                    else:
                        st.error("Please select all required fields")
                
                if st.button("📞 Mark as Contacted", use_container_width=True):
                    st.success(f"📞 Ticket {ticket_id} marked as contacted")
                    st.info("⏰ Follow-up reminder set for 24 hours")
                
                if st.button("❌ Close Ticket", use_container_width=True):
                    st.warning(f"❌ Ticket {ticket_id} closed")
                    st.info("📝 Reason required for closure")
                
                if st.button("📧 Send Quote", use_container_width=True):
                    st.success("📧 Service quote sent to customer!")
                    st.info("💰 Quote includes labor and parts estimate")
            
            # Quick contact actions
            st.subheader("📞 Quick Customer Contact")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📧 Send Email Notifications", use_container_width=True, type="primary"):
                    st.success(f"✅ Email notifications sent to {len(tickets)} customers!")
                    st.info("📋 Auto-generated service proposals attached")
            
            with col2:
                if st.button("📱 Generate Call List", use_container_width=True):
                    st.success("📞 Call list generated and assigned to service team")
                    st.download_button(
                        "📄 Download Call List",
                        data=tickets_df.to_csv(index=False),
                        file_name=f"service_calls_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("🎫 Create Work Orders", use_container_width=True):
                    st.success(f"✅ {len(tickets)} work orders created in system")
                    st.info("💰 Estimated total revenue: ${:,.0f}".format(sum([CONFIG['revenue_targets']['service_revenue_per_ticket'] for _ in tickets])))
        
        else:
            st.success("✅ No immediate proactive notifications required!")
            
            # Show summary of what we checked
            st.info(f"""
            **System Status:**
            - ✅ {len(status_df)} generators checked for faults
            - ✅ {len(interval_service_df)} generators checked for service intervals  
            - ✅ All systems operating within normal parameters
            """)
            
            # Show next upcoming services
            upcoming_services = interval_service_df[
                (interval_service_df['hours_to_next_service'] > 0) & 
                (interval_service_df['hours_to_next_service'] <= 500)
            ].sort_values('hours_to_next_service').head(5)
            
            if not upcoming_services.empty:
                st.info("📅 **Next Upcoming Services:**")
                upcoming_display = upcoming_services[['serial_number', 'customer_name', 'service_name', 'hours_to_next_service', 'estimated_cost']].copy()
                upcoming_display.columns = ['Generator', 'Customer', 'Service Type', 'Hours Until Due', 'Est. Revenue']
                st.dataframe(upcoming_display, use_container_width=True, hide_index=True)
        
        # INTERVAL SERVICE MANAGEMENT SECTION
        st.subheader("⏰ Interval Service Management")
        st.markdown("### Professional Generator Maintenance Scheduling")
        
        # Service type explanation
        st.markdown("""
        **🔧 Service Types:**
        - **Minor Service** (250-500 hrs): Oil change, filters, basic checks
        - **Intermediate Service** (1,000 hrs): Comprehensive inspection, load testing  
        - **Major Service** (10,000-20,000 hrs): Complete overhaul, engine rebuild
        """)
        
        # Filter generators that need interval service contact
        interval_contact_needed = interval_service_df[interval_service_df['needs_contact'] == True].copy()
        
        # Interval service metrics with service type breakdown
        col1, col2, col3, col4 = st.columns(4)
        
        total_interval_services = len(interval_contact_needed)
        
        # Count by service type
        minor_services = len(interval_service_df[interval_service_df['service_type'] == 'minor'])
        intermediate_services = len(interval_service_df[interval_service_df['service_type'] == 'intermediate']) 
        major_services = len(interval_service_df[interval_service_df['service_type'] == 'major'])
        
        total_interval_revenue = interval_service_df[interval_service_df['needs_contact'] == True]['estimated_cost'].sum()
        
        with col1:
            st.markdown(f"""
            <div class="service-due-card">
                <h4>📞 Total Services Due</h4>
                <h2>{total_interval_services}</h2>
                <p>Require customer contact</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="revenue-opportunity">
                <h4>🔧 Service Breakdown</h4>
                <h2>{minor_services + intermediate_services + major_services}</h2>
                <p style='font-size:12px;'>🟢 {minor_services} Minor | 🟡 {intermediate_services} Inter | 🔴 {major_services} Major</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            critical_services = len(interval_service_df[interval_service_df['priority'] == 'CRITICAL'])
            high_services = len(interval_service_df[interval_service_df['priority'] == 'HIGH'])
            
            st.markdown(f"""
            <div class="ticket-card">
                <h4>⚠️ High Priority</h4>
                <h2>{critical_services + high_services}</h2>
                <p style='font-size:12px;'>🔴 {critical_services} Critical | 🟠 {high_services} High</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="revenue-opportunity">
                <h4>💰 Service Revenue</h4>
                <h2>${total_interval_revenue:,.0f}</h2>
                <p>From scheduled services</p>
            </div>
            """, unsafe_allow_html=True)
        
        if not interval_contact_needed.empty:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #1976d2 0%, #2196f3 100%); padding: 1rem; border-radius: 8px; color: white; margin: 1rem 0;">
                <h4>📞 Interval Service Contact List</h4>
                <p>Generators approaching service intervals - Contact customers to schedule maintenance</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create enhanced interval service table with professional service details
            interval_display_data = []
            for idx, service in interval_contact_needed.iterrows():
                
                # Service type icon
                service_icon = {
                    'minor': '🟢',
                    'intermediate': '🟡', 
                    'major': '🔴'
                }.get(service['service_type'], '⚪')
                
                interval_display_data.append({
                    'Service ID': f"SV-{service['serial_number'][-4:]}",
                    'Generator': service['serial_number'],
                    'Customer': service['customer_name'][:20] + "...",
                    'Contact': service['customer_contact'],
                    'Service Type': f"{service_icon} {service['service_name']}",
                    'Runtime': f"{service['runtime_hours']:,} hrs",
                    'Interval': f"{service['service_interval']} hrs",
                    'Status': service['service_status'],
                    'Priority': service['priority'],
                    'Service Detail': service['service_detail'],
                    'Tasks Required': service['tasks_required'],
                    'Parts Needed': service['parts_needed'][:50] + "..." if len(service['parts_needed']) > 50 else service['parts_needed'],
                    'Est. Cost': f"${service['estimated_cost']:,.0f}"
                })
            
            interval_df_display = pd.DataFrame(interval_display_data)
            st.dataframe(interval_df_display, use_container_width=True, hide_index=True)
            
            # Customer contact management section
            st.subheader("📞 Customer Contact Management")
            
            # Contact action interface
            col1, col2 = st.columns([2, 1])
            
            with col1:
                selected_service = st.selectbox(
                    "Select service to update:",
                    options=[f"{row['Service ID']} - {row['Generator']} - {row['Customer']}" for row in interval_display_data],
                    key="interval_service_select"
                )
                
                contact_action = st.radio(
                    "Contact Action:",
                    ["📞 Called Customer", "📧 Sent Email", "📅 Service Booked", "❌ Close (No Service)"],
                    key="contact_action"
                )
                
                contact_notes = st.text_area(
                    "Contact Notes:",
                    placeholder="Enter details about customer contact, service agreement, or reason for closure...",
                    key="contact_notes"
                )
            
            with col2:
                st.write("**Action Buttons:**")
                
                if st.button("💾 Update Contact Status", use_container_width=True, type="primary"):
                    if contact_notes.strip():
                        if "Service Booked" in contact_action:
                            st.success(f"✅ Service booked for {selected_service.split(' - ')[1]}!")
                            st.info("📋 Work order automatically created")
                            st.info("📧 Confirmation email sent to customer")
                        elif "Close" in contact_action:
                            st.warning(f"❌ Service closed for {selected_service.split(' - ')[1]}")
                            st.info("📝 Notes saved for future reference")
                        else:
                            st.success(f"📞 Contact status updated for {selected_service.split(' - ')[1]}")
                            st.info("⏰ Follow-up reminder set for 24 hours")
                    else:
                        st.error("Please enter contact notes before updating")
                
                if st.button("📋 Create Work Order", use_container_width=True):
                    st.success("📋 Work order created!")
                    st.info("👷 Technician will be assigned automatically")
                
                if st.button("📧 Send Service Quote", use_container_width=True):
                    st.success("📧 Service quote sent to customer!")
                    st.info("💰 Includes parts and labor estimates")
                
                if st.button("📞 Add to Call Queue", use_container_width=True):
                    st.success("📞 Added to priority call queue!")
                    st.info("🔔 Sales team will be notified")
            
            # Quick bulk actions
            st.subheader("⚡ Bulk Actions")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📧 Email All Customers", use_container_width=True):
                    st.success(f"📧 Service reminder emails sent to {len(interval_contact_needed)} customers!")
                    st.info("📋 Automated service quotes included")
            
            with col2:
                if st.button("📞 Generate Call List", use_container_width=True):
                    st.success("📞 Priority call list generated!")
                    st.download_button(
                        "📄 Download Call List",
                        data=interval_df_display.to_csv(index=False),
                        file_name=f"interval_services_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with col3:
                if st.button("📋 Create All Work Orders", use_container_width=True):
                    st.success(f"📋 {len(interval_contact_needed)} work orders created!")
                    st.info(f"💰 Total revenue potential: ${total_interval_revenue:,.0f}")
            
            with col4:
                if st.button("📊 Export Report", use_container_width=True):
                    st.success("📊 Interval service report generated!")
                    st.download_button(
                        "📄 Download Report",
                        data=interval_df_display.to_csv(index=False),
                        file_name=f"interval_service_report_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        else:
            st.success("✅ No interval services requiring immediate contact - All generators on schedule!")
            
            # Show next upcoming services
            upcoming_services = interval_service_df[
                (interval_service_df['hours_to_next_service'] > 0) & 
                (interval_service_df['hours_to_next_service'] <= 200)
            ].sort_values('hours_to_next_service').head(5)
            
            if not upcoming_services.empty:
                st.info("📅 **Upcoming Services (Next 200 hours):**")
                upcoming_display = upcoming_services[['serial_number', 'customer_name', 'service_name', 'hours_to_next_service', 'estimated_cost']].copy()
                upcoming_display.columns = ['Generator', 'Customer', 'Service Type', 'Hours Until Service', 'Est. Cost']
                st.dataframe(upcoming_display, use_container_width=True, hide_index=True)
        
        # Service Portfolio Analysis
        st.subheader("📊 Service Portfolio Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**🔧 Service Type Revenue Breakdown:**")
            
            # Calculate revenue by service type
            service_revenue = []
            for service_type in ['minor', 'intermediate', 'major']:
                type_services = interval_service_df[interval_service_df['service_type'] == service_type]
                if not type_services.empty:
                    count = len(type_services)
                    revenue = type_services['estimated_cost'].sum()
                    avg_cost = revenue / count if count > 0 else 0
                    
                    service_names = {
                        'minor': '🟢 Minor Service',
                        'intermediate': '🟡 Intermediate Service',
                        'major': '🔴 Major Service'
                    }
                    
                    service_revenue.append({
                        'Service Type': service_names[service_type],
                        'Count': count,
                        'Total Revenue': f"${revenue:,.0f}",
                        'Avg Cost': f"${avg_cost:,.0f}"
                    })
            
            if service_revenue:
                revenue_df = pd.DataFrame(service_revenue)
                st.dataframe(revenue_df, use_container_width=True, hide_index=True)
            else:
                st.info("No service data available")
        
        with col2:
            st.write("**⏰ Service Urgency Distribution:**")
            
            urgency_data = []
            for status in ['OVERDUE', 'DUE SOON', 'SCHEDULED']:
                status_services = interval_service_df[interval_service_df['service_status'] == status]
                if not status_services.empty:
                    count = len(status_services)
                    revenue = status_services['estimated_cost'].sum()
                    
                    status_icons = {
                        'OVERDUE': '🔴',
                        'DUE SOON': '🟡',
                        'SCHEDULED': '🟢'
                    }
                    
                    urgency_data.append({
                        'Status': f"{status_icons.get(status, '⚪')} {status}",
                        'Count': count,
                        'Revenue': f"${revenue:,.0f}"
                    })
            
            if urgency_data:
                urgency_df = pd.DataFrame(urgency_data)
                st.dataframe(urgency_df, use_container_width=True, hide_index=True)
            else:
                st.info("No urgency data available")
        
        with col3:
            st.write("**🏥 Critical Applications Priority:**")
            
            # Healthcare and critical applications get special attention
            critical_apps = interval_service_df[interval_service_df['model_series'].str.contains('Healthcare|Industrial', na=False)]
            
            if not critical_apps.empty:
                critical_summary = []
                healthcare_count = len(critical_apps[critical_apps['model_series'].str.contains('Healthcare', na=False)])
                industrial_count = len(critical_apps[critical_apps['model_series'].str.contains('Industrial', na=False)])
                
                if healthcare_count > 0:
                    critical_summary.append({
                        'Application': '🏥 Healthcare',
                        'Count': healthcare_count,
                        'Avg Interval': '600 hrs'
                    })
                
                if industrial_count > 0:
                    critical_summary.append({
                        'Application': '🏭 Industrial',
                        'Count': industrial_count,
                        'Avg Interval': '800 hrs'
                    })
                
                if critical_summary:
                    critical_df = pd.DataFrame(critical_summary)
                    st.dataframe(critical_df, use_container_width=True, hide_index=True)
                    st.info("⚠️ Critical applications receive priority scheduling")
            else:
                st.info("No critical applications requiring service")
        
        # Service Schedule Overview
        st.subheader("📅 Professional Service Schedule Overview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🔧 Service Categories & Costs:**")
            
            # Professional service breakdown with realistic costs
            service_breakdown = [
                {
                    "Service Type": "🟢 Minor Service",
                    "Interval": "250-500 hrs",
                    "Typical Tasks": "Oil change, filters, basic inspection",
                    "Avg Cost": "$450",
                    "Duration": "2-3 hrs"
                },
                {
                    "Service Type": "🟡 Intermediate Service", 
                    "Interval": "1,000 hrs",
                    "Typical Tasks": "Comprehensive inspection, load testing",
                    "Avg Cost": "$850",
                    "Duration": "4-6 hrs"
                },
                {
                    "Service Type": "🔴 Major Service",
                    "Interval": "10,000-20,000 hrs", 
                    "Typical Tasks": "Complete overhaul, engine rebuild",
                    "Avg Cost": "$12,500",
                    "Duration": "3-5 days"
                }
            ]
            
            service_df = pd.DataFrame(service_breakdown)
            st.dataframe(service_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.write("**💰 Revenue Opportunity Analysis:**")
            
            # Calculate actual revenue potential from current data
            if not interval_service_df.empty:
                revenue_analysis = []
                
                for service_type in ['minor', 'intermediate', 'major']:
                    type_data = interval_service_df[interval_service_df['service_type'] == service_type]
                    if not type_data.empty:
                        due_count = len(type_data[type_data['needs_contact'] == True])
                        total_revenue = type_data[type_data['needs_contact'] == True]['estimated_cost'].sum()
                        
                        service_names = {
                            'minor': '🟢 Minor',
                            'intermediate': '🟡 Intermediate', 
                            'major': '🔴 Major'
                        }
                        
                        revenue_analysis.append({
                            "Type": service_names[service_type],
                            "Due Now": due_count,
                            "Revenue": f"${total_revenue:,.0f}",
                            "Avg Value": f"${total_revenue/due_count:,.0f}" if due_count > 0 else "$0"
                        })
                
                if revenue_analysis:
                    revenue_df = pd.DataFrame(revenue_analysis)
                    st.dataframe(revenue_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No current revenue opportunities")
            else:
                st.info("No service data available")
        
        # Fleet status overview
        st.subheader("🗺️ Fleet Status Overview")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Status summary
            status_summary = status_df['operational_status'].value_counts()
            
            fig = px.pie(
                values=status_summary.values, 
                names=status_summary.index,
                title="Generator Operational Status",
                color_discrete_map={
                    'RUNNING': '#4CAF50',
                    'FAULT': '#F44336', 
                    'STANDBY': '#9E9E9E',
                    'MAINTENANCE': '#FF9800'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Revenue opportunities by customer
            revenue_by_customer = status_df[status_df['revenue_opportunity'] == True].groupby('customer_name').size().reset_index()
            revenue_by_customer.columns = ['Customer', 'Opportunities']
            revenue_by_customer = revenue_by_customer.sort_values('Opportunities', ascending=False).head(8)
            
            if not revenue_by_customer.empty:
                fig2 = px.bar(
                    revenue_by_customer, 
                    x='Opportunities', 
                    y='Customer',
                    title="Revenue Opportunities by Customer",
                    orientation='h'
                )
                fig2.update_layout(height=400)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No current revenue opportunities identified")
        
        with col3:
            # Technician assignment and parts status
            st.write("**👷 Technician Assignment:**")
            
            # Mock technician data
            total_tickets = len(proactive_opportunities) if 'proactive_opportunities' in locals() else 0
            technicians = [
                {"Name": "Ahmed Al-Rashid", "Region": "Riyadh", "Assigned": min(6, total_tickets//3), "Available": "✅"},
                {"Name": "Mohammed Al-Saud", "Region": "Jeddah", "Assigned": min(4, total_tickets//4), "Available": "✅"},
                {"Name": "Khalid Al-Otaibi", "Region": "Eastern", "Assigned": min(5, total_tickets//3), "Available": "🟡"},
                {"Name": "Abdullah Al-Nasser", "Region": "NEOM", "Assigned": min(2, total_tickets//5), "Available": "✅"}
            ]
            
            tech_df = pd.DataFrame(technicians)
            st.dataframe(tech_df, use_container_width=True, hide_index=True)
            
            st.write("**📦 Critical Parts Status:**")
            
            parts_status = [
                {"Part": "Oil Filters", "Stock": 45, "Status": "✅"},
                {"Part": "Air Filters", "Stock": 12, "Status": "🟡"},
                {"Part": "Belt Kits", "Stock": 8, "Status": "🔴"},
                {"Part": "Oil (20L)", "Stock": 28, "Status": "✅"}
            ]
            
            parts_df = pd.DataFrame(parts_status)
            st.dataframe(parts_df, use_container_width=True, hide_index=True)
            
            if st.button("📋 Generate Purchase Order", use_container_width=True):
                st.success("PO generated for low-stock items!")
        
        # Weekly Service Metrics
        st.subheader("📊 Weekly Service Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("This Week's Revenue", "$12,750", delta="+15% vs last week")
        with col2:
            st.metric("Tickets Closed", "23", delta="+8 this week")
        with col3:
            st.metric("Avg Response Time", "2.3 hrs", delta="-0.5 hrs improved")
        with col4:
            st.metric("Customer Satisfaction", "94%", delta="+2% this month")
    
    except Exception as e:
        st.error(f"Error loading work management dashboard: {str(e)}")
        st.info("Please try refreshing the page. If the problem persists, contact system administrator.")
        
        # Show basic fallback interface
        st.subheader("🔧 System Status")
        st.warning("Dashboard temporarily unavailable - showing basic status")
        
        if st.button("🔄 Retry Loading Dashboard"):
            st.rerun()

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
        
        # Real-time notifications for customer
        fault_generators = customer_status[customer_status['operational_status'] == 'FAULT']
        service_due_generators = customer_status[customer_status['needs_proactive_contact'] == True]
        
        if not fault_generators.empty:
            st.markdown("""
            <div class="proactive-alert">
                <h4>🚨 URGENT: Generator Fault Detected</h4>
                <p>One or more of your generators has detected a fault. Our service team will contact you shortly.</p>
            </div>
            """, unsafe_allow_html=True)
        
        if not service_due_generators.empty:
            st.info(f"📅 **Service Reminder:** {len(service_due_generators)} generator(s) due for scheduled maintenance within 72 hours")
        
        # Customer fleet overview
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
        
        # Detailed generator status with live sensor readings
        st.subheader("⚡ Your Generator Fleet - Live Status & Sensor Readings")
        
        if customer_status.empty:
            st.warning("No real-time data available for your generators. Please contact support.")
            return
        
        # Create detailed status display
        for _, gen_status in customer_status.iterrows():
            try:
                gen_info = customer_generators[customer_generators['serial_number'] == gen_status['serial_number']].iloc[0]
                
                # Choose appropriate styling based on status
                status_class = f"generator-{gen_status['status_color']}"
                
                # Status indicators
                if gen_status['operational_status'] == 'RUNNING':
                    status_icon = "🟢 RUNNING"
                    status_detail = f"Load: {gen_status['load_percent']}% | All systems normal"
                elif gen_status['operational_status'] == 'FAULT':
                    status_icon = "🔴 FAULT"
                    status_detail = f"⚠️ {gen_status['fault_description']}"
                elif gen_status['operational_status'] == 'STANDBY':
                    status_icon = "⚪ STANDBY"
                    status_detail = "Generator ready - Not currently needed"
                else:  # MAINTENANCE
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
                    # Live sensor readings
                    sensor_col1, sensor_col2, sensor_col3, sensor_col4 = st.columns(4)
                    
                    with sensor_col1:
                        oil_color = "🟢" if gen_status['oil_pressure'] >= 28 else "🟡" if gen_status['oil_pressure'] >= 25 else "🔴"
                        st.metric(
                            "Oil Pressure", 
                            f"{gen_status['oil_pressure']} PSI",
                            delta=f"{oil_color} Normal" if gen_status['oil_pressure'] >= 28 else f"{oil_color} Alert"
                        )
                    
                    with sensor_col2:
                        temp_color = "🟢" if gen_status['coolant_temp'] <= 95 else "🟡" if gen_status['coolant_temp'] <= 105 else "🔴"
                        st.metric(
                            "Coolant Temp", 
                            f"{gen_status['coolant_temp']}°C",
                            delta=f"{temp_color} Normal" if gen_status['coolant_temp'] <= 95 else f"{temp_color} Alert"
                        )
                    
                    with sensor_col3:
                        vib_color = "🟢" if gen_status['vibration'] <= 4.0 else "🟡" if gen_status['vibration'] <= 5.0 else "🔴"
                        st.metric(
                            "Vibration", 
                            f"{gen_status['vibration']} mm/s",
                            delta=f"{vib_color} Normal" if gen_status['vibration'] <= 4.0 else f"{vib_color} Alert"
                        )
                    
                    with sensor_col4:
                        fuel_color = "🟢" if gen_status['fuel_level'] >= 50 else "🟡" if gen_status['fuel_level'] >= 20 else "🔴"
                        st.metric(
                            "Fuel Level", 
                            f"{gen_status['fuel_level']}%",
                            delta=f"{fuel_color} Good" if gen_status['fuel_level'] >= 50 else f"{fuel_color} Low"
                        )
                
                st.markdown("---")
                
            except Exception as e:
                st.warning(f"Error displaying generator {gen_status.get('serial_number', 'Unknown')}: {str(e)}")
                continue
        
        # Quick service requests
        st.subheader("🚀 Service & Support")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📅 Schedule Maintenance", use_container_width=True):
                st.success("✅ Maintenance request submitted! Our team will contact you within 2 hours.")
        
        with col2:
            if st.button("🚨 Report Emergency", use_container_width=True, type="primary"):
                st.success("🚨 Emergency ticket created! Technician dispatched - ETA: 45 minutes")
        
        with col3:
            if st.button("🛒 Request Parts Quote", use_container_width=True):
                st.success("🛒 Parts specialist will contact you with a quote within 4 hours")
        
        with col4:
            if st.button("📞 Contact Support", use_container_width=True):
                st.success("📞 Support ticket created. Response time: 1 hour")
        
        # Fleet performance summary
        st.subheader("📊 Fleet Performance Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution pie chart
            status_counts = customer_status['operational_status'].value_counts()
            if not status_counts.empty:
                fig = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Current Fleet Status",
                    color_discrete_map={
                        'RUNNING': '#4CAF50',
                        'FAULT': '#F44336',
                        'STANDBY': '#9E9E9E', 
                        'MAINTENANCE': '#FF9800'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No status data available for charts")
        
        with col2:
            # Load distribution
            if not customer_status.empty:
                fig2 = px.bar(
                    x=customer_status['serial_number'],
                    y=customer_status['load_percent'],
                    title="Generator Load Distribution",
                    labels={'x': 'Generator', 'y': 'Load %'}
                )
                fig2.update_xaxis(tickangle=45)
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No load data available for charts")
    
    except Exception as e:
        st.error(f"Error loading customer portal: {str(e)}")
        st.info("Please try refreshing the page. If the problem persists, contact support.")
        
        # Show basic fallback interface
        st.subheader("🔧 System Status")
        st.warning("Customer portal temporarily unavailable")
        
        if st.button("🔄 Retry Loading Portal"):
            st.rerun()

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
    
    # Role-based navigation (CEO Dashboard removed)
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
