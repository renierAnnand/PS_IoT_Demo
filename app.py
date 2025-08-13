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
import json
import os
from datetime import datetime, timedelta
import time
import random
from typing import Dict, List, Optional, Tuple
from pathlib import Path

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
        "rate": 3.75,
        "format": "SAR {:,.0f}"
    },
    "revenue_targets": {
        "service_revenue_per_ticket": 850 * 3.75,
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
        generators_data = generate_enhanced_generator_data()
        df = pd.DataFrame(generators_data)
        df.to_csv(generators_file, index=False)
        return df
    
    df = pd.read_csv(generators_file)
    
    contact_columns = ['primary_contact_name', 'primary_contact_phone', 'primary_contact_email', 
                      'alt_contact_name', 'alt_contact_phone', 'alt_contact_email']
    
    missing_columns = [col for col in contact_columns if col not in df.columns]
    
    if missing_columns:
        contact_mapping = {
            'King Faisal Medical City': {
                'primary_contact_name': 'Ahmed Al-Rashid', 'primary_contact_phone': '+966-11-464-7272', 
                'primary_contact_email': 'ahmed.alrashid@kfmc.sa',
                'alt_contact_name': 'Fahad Al-Mahmoud', 'alt_contact_phone': '+966-11-464-7273', 
                'alt_contact_email': 'fahad.mahmoud@kfmc.sa'
            },
            'Riyadh Mall Complex': {
                'primary_contact_name': 'Mohammed Al-Saud', 'primary_contact_phone': '+966-11-234-5678', 
                'primary_contact_email': 'mohammed.saud@riyadhmall.com',
                'alt_contact_name': 'Khalid Operations', 'alt_contact_phone': '+966-11-234-5679', 
                'alt_contact_email': 'ops@riyadhmall.com'
            }
        }
        
        default_contact = {
            'primary_contact_name': 'Facility Manager', 'primary_contact_phone': '+966-11-000-0000', 
            'primary_contact_email': 'contact@customer.sa',
            'alt_contact_name': 'Operations Team', 'alt_contact_phone': '+966-11-000-0001', 
            'alt_contact_email': 'ops@customer.sa'
        }
        
        for col in contact_columns:
            if col not in df.columns:
                df[col] = df['customer_name'].apply(lambda x: contact_mapping.get(x, default_contact).get(col, default_contact[col]))
        
        df.to_csv(generators_file, index=False)
    
    if 'customer_contact' not in df.columns:
        df['customer_contact'] = df['primary_contact_email']
        df.to_csv(generators_file, index=False)
    
    if 'installation_date' not in df.columns:
        df['installation_date'] = [
            datetime.now() - timedelta(days=random.randint(365, 1825)) for _ in range(len(df))
        ]
        df.to_csv(generators_file, index=False)
    
    return df

def generate_enhanced_generator_data() -> Dict:
    """Generate enhanced generator data with comprehensive contact information."""
    
    customer_names = [
        'King Faisal Medical City', 'Riyadh Mall Complex', 'SABIC Industrial', 'ARAMCO Office Tower',
        'Al Rajhi Banking HQ', 'STC Data Center', 'NEOM Construction', 'Red Sea Project',
        'Saudi Airlines Hub', 'KAUST Research', 'PIF Headquarters', 'Vision 2030 Center',
        'Ministry Complex', 'Royal Hospital', 'Diplomatic Quarter', 'Financial District',
        'Entertainment City', 'Sports Boulevard', 'Green Riyadh', 'ROSHN Development',
        'ENOWA Energy Hub', 'THE LINE Project', 'Oxagon Port', 'Trojena Resort',
        'Al-Ula Heritage', 'Qiddiya Venue', 'SPARK Sports', 'Mukaab Tower',
        'Diriyah Gate', 'King Salman Park'
    ]
    
    # Generate contact data
    contact_data = []
    for i in range(30):
        contact_data.append({
            'primary_contact_name': f'Contact-{i+1}', 
            'primary_contact_phone': f'+966-11-{1000+i:04d}',
            'primary_contact_email': f'contact{i+1}@customer.sa',
            'alt_contact_name': f'Alt-Contact-{i+1}', 
            'alt_contact_phone': f'+966-11-{2000+i:04d}',
            'alt_contact_email': f'alt{i+1}@customer.sa'
        })
    
    return {
        'serial_number': [f'PS-{2020 + i//4}-{i+1:04d}' for i in range(30)],
        'model_series': ([
            'PS-2000 Series', 'PS-1500 Series', 'PS-1000 Series', 'PS-800 Series',
            'PS-2500 Industrial', 'PS-2000 Commercial', 'PS-1800 Healthcare', 'PS-1200 Retail'
        ] * 4)[:30],
        'customer_name': customer_names,
        'primary_contact_name': [contact['primary_contact_name'] for contact in contact_data],
        'primary_contact_phone': [contact['primary_contact_phone'] for contact in contact_data],
        'primary_contact_email': [contact['primary_contact_email'] for contact in contact_data],
        'alt_contact_name': [contact['alt_contact_name'] for contact in contact_data],
        'alt_contact_phone': [contact['alt_contact_phone'] for contact in contact_data],
        'alt_contact_email': [contact['alt_contact_email'] for contact in contact_data],
        'customer_contact': [contact['primary_contact_email'] for contact in contact_data],
        'rated_kw': [
            2000, 1500, 1000, 800, 2500, 2000, 1800, 1200,
            1000, 750, 600, 400, 2200, 1800, 1400, 900,
            650, 500, 350, 300, 2800, 2200, 1600, 1100,
            850, 700, 450, 380, 320, 280
        ],
        'service_contract': [
            'Premium Care', 'Basic Maintenance', 'Preventive Plus', 'No Contract'
        ] * 8,
        'next_service_hours': [random.randint(-200, 800) for _ in range(30)],
        'total_runtime_hours': [random.randint(2000, 12000) for _ in range(30)],
        'location_city': [
            'Riyadh', 'Riyadh', 'Dammam', 'Riyadh', 'Riyadh', 'Jeddah', 'NEOM', 'Al-Ula',
            'Riyadh', 'Thuwal', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh',
            'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'NEOM', 'NEOM', 'NEOM', 'Qiddiya',
            'Al-Ula', 'Qiddiya', 'Riyadh', 'Riyadh', 'Diriyah', 'Riyadh'
        ][:30],
        'installation_date': [
            datetime.now() - timedelta(days=random.randint(365, 1825)) for _ in range(30)
        ]
    }

@st.cache_data(ttl=60)
def generate_real_time_status(generators_df: pd.DataFrame) -> pd.DataFrame:
    """Generate real-time operational status and sensor data."""
    seed = int(time.time() // 60)
    np.random.seed(seed)
    
    status_data = []
    for _, gen in generators_df.iterrows():
        try:
            oil_pressure = np.random.uniform(20, 35)
            coolant_temp = np.random.uniform(75, 110)
            vibration = np.random.uniform(1.0, 6.0)
            fuel_level = np.random.uniform(10, 95)
            load_percent = np.random.uniform(0, 100)
            
            has_fault = (oil_pressure < 25 or coolant_temp > 105 or vibration > 5.0 or fuel_level < 15)
            is_needed = np.random.choice([True, False], p=[0.7, 0.3])
            
            if has_fault:
                operational_status = "FAULT"
                status_color = "fault"
                fault_description = []
                if oil_pressure < 25: 
                    fault_description.append("Low oil pressure")
                if coolant_temp > 105: 
                    fault_description.append("High coolant temperature")
                if vibration > 5.0: 
                    fault_description.append("High vibration")
                if fuel_level < 15: 
                    fault_description.append("Low fuel")
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
            
            service_hours = gen.get('next_service_hours', 500)
            runtime_hours = gen.get('total_runtime_hours', 5000)
            
            needs_proactive_contact = False
            service_type = "Regular Maintenance"
            
            if service_hours < 0:
                needs_proactive_contact = True
                service_type = "Overdue Maintenance"
            elif service_hours < 48:
                needs_proactive_contact = True
                service_type = "Urgent Service Due"
            elif service_hours < CONFIG["proactive_notification_hours"]:
                needs_proactive_contact = True
                service_type = "Scheduled Service Due"
            
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
        except Exception:
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
# ENHANCED CUSTOMER PORTAL
# ========================================

def show_enhanced_customer_portal():
    """Enhanced customer portal with proactive fault alerts and detailed sensor monitoring."""
    st.title("🏢 Customer Portal - Advanced Generator Monitoring")
    st.markdown("### 🚨 Real-Time Alerts • 📊 Detailed Sensor Data • 🔍 Proactive Monitoring")
    
    try:
        generators_df = load_base_generator_data()
        status_df = generate_real_time_status(generators_df)
        
        if generators_df.empty:
            st.error("No generator data available. Please contact support.")
            return
        
        customers = generators_df['customer_name'].unique()
        selected_customer = st.selectbox("Select Your Organization:", customers, key="customer_select")
        
        customer_generators = generators_df[generators_df['customer_name'] == selected_customer]
        customer_status = status_df[status_df['customer_name'] == selected_customer]
        
        if customer_generators.empty:
            st.error("No generators found for selected customer")
            return
        
        st.markdown(f"### Welcome, {selected_customer}")
        
        # PROACTIVE ALERTS SECTION
        st.subheader("🚨 Proactive Fault Alert System")
        
        fault_alerts = customer_status[customer_status['operational_status'] == 'FAULT']
        warning_alerts = customer_status[
            (customer_status['oil_pressure'] < 28) | 
            (customer_status['coolant_temp'] > 95) | 
            (customer_status['vibration'] > 4.0) | 
            (customer_status['fuel_level'] < 30)
        ]
        
        if not fault_alerts.empty:
            for _, alert in fault_alerts.iterrows():
                st.error(f"""
                🚨 **CRITICAL FAULT DETECTED - {alert['serial_number']}**
                - **Issue:** {alert['fault_description']}
                - **Status:** Requires immediate attention
                - **Auto-Response:** Emergency service has been notified
                - **ETA:** Technician will contact you within 30 minutes
                """)
        
        warning_alerts_filtered = warning_alerts[~warning_alerts['serial_number'].isin(fault_alerts['serial_number'])] if not fault_alerts.empty else warning_alerts
        if not warning_alerts_filtered.empty:
            for _, warning in warning_alerts_filtered.iterrows():
                warning_details = []
                if warning['oil_pressure'] < 28:
                    warning_details.append(f"Oil Pressure: {warning['oil_pressure']} PSI (Below normal)")
                if warning['coolant_temp'] > 95:
                    warning_details.append(f"Coolant Temp: {warning['coolant_temp']}°C (Above normal)")
                if warning['vibration'] > 4.0:
                    warning_details.append(f"Vibration: {warning['vibration']} mm/s (Above normal)")
                if warning['fuel_level'] < 30:
                    warning_details.append(f"Fuel Level: {warning['fuel_level']}% (Low)")
                
                st.warning(f"""
                ⚠️ **SENSOR WARNING - {warning['serial_number']}**
                - **Issues:** {', '.join(warning_details)}
                - **Action:** Monitor closely, consider maintenance scheduling
                - **Status:** Generator operational but requires attention
                """)
        
        if fault_alerts.empty and warning_alerts_filtered.empty:
            st.success("""
            ✅ **ALL GENERATORS OPERATING NORMALLY**
            - No critical faults detected
            - All sensors within normal operating ranges
            - Proactive monitoring system active 24/7
            """)
        
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
        
        # DETAILED SENSOR DATA SECTION
        st.subheader("📊 Live Sensor Data & Monitoring")
        
        if not customer_status.empty:
            for _, gen_status in customer_status.iterrows():
                try:
                    gen_info = customer_generators[customer_generators['serial_number'] == gen_status['serial_number']].iloc[0]
                    
                    with st.expander(f"🔍 {gen_status['serial_number']} - {gen_info['model_series']} - Detailed Sensor View", expanded=True):
                        
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
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
                            
                            st.markdown(f"""
                            **Generator Status:** {status_icon}  
                            **Model:** {gen_info['model_series']}  
                            **Capacity:** {gen_info['rated_kw']} kW  
                            **Location:** {gen_info['location_city']}  
                            **Runtime:** {gen_status.get('runtime_hours', 5000):,} hours  
                            **Status Detail:** {status_detail}
                            """)
                        
                        with col2:
                            st.markdown("**🔍 Live Sensor Readings:**")
                            
                            sensor_col1, sensor_col2, sensor_col3, sensor_col4 = st.columns(4)
                            
                            with sensor_col1:
                                oil_color = "🟢" if gen_status['oil_pressure'] >= 28 else "🟡" if gen_status['oil_pressure'] >= 25 else "🔴"
                                oil_status = "Normal" if gen_status['oil_pressure'] >= 28 else "Warning" if gen_status['oil_pressure'] >= 25 else "Critical"
                                st.metric("🛢️ Oil Pressure", f"{gen_status['oil_pressure']} PSI", delta=f"{oil_color} {oil_status}")
                                st.caption("Normal: 28-35 PSI")
                                if gen_status['oil_pressure'] < 28:
                                    st.caption("⚠️ Below normal range")
                            
                            with sensor_col2:
                                temp_color = "🟢" if gen_status['coolant_temp'] <= 95 else "🟡" if gen_status['coolant_temp'] <= 105 else "🔴"
                                temp_status = "Normal" if gen_status['coolant_temp'] <= 95 else "Warning" if gen_status['coolant_temp'] <= 105 else "Critical"
                                st.metric("🌡️ Coolant Temp", f"{gen_status['coolant_temp']}°C", delta=f"{temp_color} {temp_status}")
                                st.caption("Normal: 75-95°C")
                                if gen_status['coolant_temp'] > 95:
                                    st.caption("⚠️ Above normal range")
                            
                            with sensor_col3:
                                vib_color = "🟢" if gen_status['vibration'] <= 4.0 else "🟡" if gen_status['vibration'] <= 5.0 else "🔴"
                                vib_status = "Normal" if gen_status['vibration'] <= 4.0 else "Warning" if gen_status['vibration'] <= 5.0 else "Critical"
                                st.metric("🔧 Vibration", f"{gen_status['vibration']} mm/s", delta=f"{vib_color} {vib_status}")
                                st.caption("Normal: 1.0-4.0 mm/s")
                                if gen_status['vibration'] > 4.0:
                                    st.caption("⚠️ Above normal range")
                            
                            with sensor_col4:
                                fuel_color = "🟢" if gen_status['fuel_level'] >= 50 else "🟡" if gen_status['fuel_level'] >= 20 else "🔴"
                                fuel_status = "Normal" if gen_status['fuel_level'] >= 50 else "Low" if gen_status['fuel_level'] >= 20 else "Critical"
                                st.metric("⛽ Fuel Level", f"{gen_status['fuel_level']}%", delta=f"{fuel_color} {fuel_status}")
                                st.caption("Normal: >50%")
                                if gen_status['fuel_level'] < 50:
                                    st.caption("⚠️ Consider refueling")
                        
                        # Sensor trend visualization
                        st.markdown("**📈 24-Hour Sensor Trends:**")
                        
                        hours = list(range(24))
                        np.random.seed(hash(gen_status['serial_number']) % (2**32 - 1))
                        
                        oil_trend = [max(20, min(35, gen_status['oil_pressure'] + np.random.normal(0, 1))) for _ in hours]
                        temp_trend = [max(70, min(110, gen_status['coolant_temp'] + np.random.normal(0, 2))) for _ in hours]
                        vib_trend = [max(0.5, min(6, gen_status['vibration'] + np.random.normal(0, 0.3))) for _ in hours]
                        fuel_trend = [max(10, min(100, gen_status['fuel_level'] + np.random.normal(0, 1.5))) for _ in hours]
                        
                        trend_col1, trend_col2 = st.columns(2)
                        
                        with trend_col1:
                            fig_oil = go.Figure()
                            fig_oil.add_trace(go.Scatter(x=hours, y=oil_trend, mode='lines+markers', 
                                                       name='Oil Pressure', line_color='blue'))
                            fig_oil.add_hline(y=25, line_dash="dash", line_color="red", 
                                            annotation_text="Min Threshold")
                            fig_oil.update_layout(title="Oil Pressure (PSI)", height=200, 
                                                showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                            st.plotly_chart(fig_oil, use_container_width=True)
                            
                            fig_vib = go.Figure()
                            fig_vib.add_trace(go.Scatter(x=hours, y=vib_trend, mode='lines+markers', 
                                                       name='Vibration', line_color='purple'))
                            fig_vib.add_hline(y=4.0, line_dash="dash", line_color="orange", 
                                            annotation_text="Warning Level")
                            fig_vib.update_layout(title="Vibration (mm/s)", height=200, 
                                                showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                            st.plotly_chart(fig_vib, use_container_width=True)
                        
                        with trend_col2:
                            fig_temp = go.Figure()
                            fig_temp.add_trace(go.Scatter(x=hours, y=temp_trend, mode='lines+markers', 
                                                        name='Temperature', line_color='red'))
                            fig_temp.add_hline(y=95, line_dash="dash", line_color="orange", 
                                             annotation_text="Warning Level")
                            fig_temp.update_layout(title="Coolant Temperature (°C)", height=200, 
                                                 showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                            st.plotly_chart(fig_temp, use_container_width=True)
                            
                            fig_fuel = go.Figure()
                            fig_fuel.add_trace(go.Scatter(x=hours, y=fuel_trend, mode='lines+markers', 
                                                        name='Fuel Level', line_color='green'))
                            fig_fuel.add_hline(y=20, line_dash="dash", line_color="red", 
                                             annotation_text="Low Fuel")
                            fig_fuel.update_layout(title="Fuel Level (%)", height=200, 
                                                 showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                            st.plotly_chart(fig_fuel, use_container_width=True)
                        
                        st.markdown("**⚡ Quick Actions:**")
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if st.button(f"📅 Schedule Service", key=f"schedule_{gen_status['serial_number']}", use_container_width=True):
                                st.success(f"✅ Service scheduled for {gen_status['serial_number']}")
                        
                        with action_col2:
                            if gen_status['operational_status'] == 'FAULT':
                                if st.button(f"🚨 Emergency Service", key=f"emergency_{gen_status['serial_number']}", use_container_width=True, type="primary"):
                                    st.success(f"🚨 Emergency service dispatched for {gen_status['serial_number']}")
                            else:
                                if st.button(f"📞 Contact Support", key=f"support_{gen_status['serial_number']}", use_container_width=True):
                                    st.success(f"📞 Support contacted for {gen_status['serial_number']}")
                        
                        with action_col3:
                            if st.button(f"📊 Full Report", key=f"report_{gen_status['serial_number']}", use_container_width=True):
                                st.info(f"📊 Generating detailed report for {gen_status['serial_number']}")
                    
                    st.markdown("---")
                except Exception:
                    continue
        
        # ALERT SETTINGS & PREFERENCES
        st.subheader("⚙️ Alert Settings & Preferences")
        
        with st.expander("🔔 Customize Your Alert Preferences", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📱 Notification Methods**")
                email_alerts = st.checkbox("📧 Email Alerts", value=True)
                sms_alerts = st.checkbox("📱 SMS Alerts", value=True)
                phone_alerts = st.checkbox("📞 Emergency Phone Calls", value=True)
                
                st.markdown("**⏰ Alert Frequency**")
                immediate_critical = st.checkbox("🚨 Immediate (Critical Faults)", value=True)
                hourly_warnings = st.checkbox("⏰ Hourly (Warnings)", value=True)
                daily_reports = st.checkbox("📅 Daily Status Reports", value=True)
            
            with col2:
                st.markdown("**🎯 Custom Thresholds**")
                oil_threshold = st.slider("Oil Pressure Alert (PSI)", 20, 30, 25)
                temp_threshold = st.slider("Temperature Alert (°C)", 85, 100, 95)
                vib_threshold = st.slider("Vibration Alert (mm/s)", 3.0, 5.0, 4.0, step=0.1)
                fuel_threshold = st.slider("Fuel Level Alert (%)", 15, 40, 25)
                
                if st.button("💾 Save Alert Settings", use_container_width=True, type="primary"):
                    st.success("✅ Alert preferences saved successfully!")
        
        # Enhanced Service & Support
        st.subheader("🛠️ Service & Support Center")
        
        fault_count_service = len(customer_status[customer_status['operational_status'] == 'FAULT'])
        warning_count_service = len(warning_alerts_filtered) if 'warning_alerts_filtered' in locals() else 0
        
        if fault_count_service > 0:
            st.error(f"🚨 **{fault_count_service} Critical Issues** - Emergency service automatically notified")
        elif warning_count_service > 0:
            st.warning(f"⚠️ **{warning_count_service} Warnings** - Recommend scheduling preventive maintenance")
        else:
            st.success("✅ **All Systems Normal** - Proactive monitoring active")
        
        service_col1, service_col2, service_col3, service_col4 = st.columns(4)
        
        with service_col1:
            if st.button("📅 Schedule Maintenance", use_container_width=True):
                st.success("✅ Maintenance request submitted!")
                st.info("🔔 Our service team will contact you within 2 hours")
        
        with service_col2:
            if st.button("🚨 Report Emergency", use_container_width=True, type="primary"):
                st.success("🚨 Emergency ticket created!")
                st.info("☎️ Emergency technician will call within 15 minutes")
        
        with service_col3:
            if st.button("🛒 Request Parts Quote", use_container_width=True):
                st.success("🛒 Parts specialist notified!")
                st.info("📧 Quote will be emailed within 4 hours")
        
        with service_col4:
            if st.button("📞 Contact Support", use_container_width=True):
                st.success("📞 Support ticket created!")
                st.info("🎧 Response within 1 hour")
        
        st.markdown("#### 📞 24/7 Support Contact Information")
        
        support_col1, support_col2, support_col3 = st.columns(3)
        
        with support_col1:
            st.info("""
            **🚨 Emergency Support**
            - Phone: +966-800-POWER-1
            - Available: 24/7
            - Response: <30 minutes
            """)
        
        with support_col2:
            st.info("""
            **🔧 Technical Support**
            - Phone: +966-11-TECH-SUP
            - Email: support@powersystem.sa
            - Hours: 6 AM - 10 PM
            """)
        
        with support_col3:
            st.info("""
            **📋 Service Scheduling**
            - Phone: +966-11-SERVICE
            - Email: service@powersystem.sa
            - Hours: 7 AM - 6 PM
            """)
        
    except Exception as e:
        st.error(f"Error loading customer portal: {str(e)}")
        st.info("Please try refreshing the page.")

# ========================================
# SIMPLIFIED WORK MANAGEMENT (BASIC VERSION)
# ========================================

def show_work_management_dashboard():
    """Basic work management dashboard."""
    st.title("🎫 Work Management Dashboard")
    st.markdown("### Service Coordination & Customer Management")
    
    try:
        generators_df = load_base_generator_data()
        status_df = generate_real_time_status(generators_df)
        
        if generators_df.empty or status_df.empty:
            st.error("No data available. Please check system status.")
            return
        
        # Basic metrics
        col1, col2, col3, col4 = st.columns(4)
        
        total_generators = len(generators_df)
        running_count = len(status_df[status_df['operational_status'] == 'RUNNING'])
        fault_count = len(status_df[status_df['operational_status'] == 'FAULT'])
        opportunities = len(status_df[status_df['revenue_opportunity'] == True])
        
        with col1:
            st.metric("Total Generators", total_generators)
        with col2:
            st.metric("🟢 Running", running_count)
        with col3:
            st.metric("🔴 Faults", fault_count, delta="Critical" if fault_count > 0 else "Normal")
        with col4:
            st.metric("💰 Opportunities", opportunities)
        
        # Show fault alerts
        if fault_count > 0:
            st.subheader("🚨 Active Fault Alerts")
            fault_generators = status_df[status_df['operational_status'] == 'FAULT']
            for _, gen in fault_generators.iterrows():
                st.error(f"""
                **Generator:** {gen['serial_number']} - {gen['customer_name']}
                **Issue:** {gen['fault_description']}
                **Action:** Contact customer for emergency service
                """)
        
        # Service opportunities
        if opportunities > 0:
            st.subheader("⚡ Service Opportunities")
            opportunity_generators = status_df[status_df['revenue_opportunity'] == True]
            
            opportunities_list = []
            for _, gen in opportunity_generators.iterrows():
                revenue_estimate = CONFIG['revenue_targets']['service_revenue_per_ticket']
                
                opportunities_list.append({
                    'Generator': gen['serial_number'],
                    'Customer': gen['customer_name'][:30] + "...",
                    'Issue': gen['fault_description'] if gen['operational_status'] == 'FAULT' else gen['service_type'],
                    'Priority': 'CRITICAL' if gen['operational_status'] == 'FAULT' else 'HIGH',
                    'Est. Revenue': format_currency(revenue_estimate / 3.75),
                    'Contact': gen['customer_contact']
                })
            
            if opportunities_list:
                opportunities_df = pd.DataFrame(opportunities_list)
                st.dataframe(opportunities_df, use_container_width=True, hide_index=True)
        
        # System status
        if fault_count == 0 and opportunities == 0:
            st.success("✅ All systems operating normally. No immediate actions required.")
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Main application."""
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        authenticate_system()
        return
    
    st.sidebar.markdown(f"### {st.session_state.role_name}")
    st.sidebar.write("Power System Work Management")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    st.sidebar.markdown("---")
    
    if st.session_state.user_role in ["operations@powersystem", "service@powersystem", "sales@powersystem"]:
        pages = {
            "🎫 Work Management": show_work_management_dashboard,
            "🏢 Customer Portal": show_enhanced_customer_portal
        }
    else:
        pages = {
            "🏢 My Generators": show_enhanced_customer_portal
        }
    
    selected_page = st.sidebar.selectbox("Navigate:", list(pages.keys()))
    
    try:
        pages[selected_page]()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please try refreshing the page.")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎯 System Status")
    st.sidebar.success("✅ Real-time monitoring active")
    st.sidebar.info(f"🕒 Last update: {datetime.now().strftime('%H:%M:%S')}")
    
    st.sidebar.markdown("### ⚡ Platform Features")
    
    if st.session_state.user_role in ["operations@powersystem", "service@powersystem", "sales@powersystem"]:
        st.sidebar.markdown("✅ Proactive Service Notifications")
        st.sidebar.markdown("✅ Advanced Ticketing System")
        st.sidebar.markdown("✅ Real-time Generator Status")
        st.sidebar.markdown("✅ Customer Portal Access")
    else:
        st.sidebar.markdown("**🚨 FAULT ALERT SYSTEM**")
        st.sidebar.markdown("   • Critical fault notifications")
        st.sidebar.markdown("   • Warning alerts for sensors")
        st.sidebar.markdown("   • Automatic emergency dispatch")
        st.sidebar.markdown("**📊 SENSOR MONITORING**")
        st.sidebar.markdown("   • Live sensor readings")
        st.sidebar.markdown("   • Historical trend charts")
        st.sidebar.markdown("   • Threshold monitoring")
        st.sidebar.markdown("**⚙️ ALERT CUSTOMIZATION**")
        st.sidebar.markdown("   • Custom alert thresholds")
        st.sidebar.markdown("   • Notification preferences")
        st.sidebar.markdown("**🛠️ SERVICE INTEGRATION**")
        st.sidebar.markdown("   • Emergency service dispatch")
        st.sidebar.markdown("   • 24/7 support access")

if __name__ == "__main__":
    main()
