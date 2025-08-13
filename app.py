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
        
        if generators_df.empty or status_df.empty:
            st.error("No generator data available. Please check data initialization.")
            return
        
        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Calculate metrics
        total_opportunities = len(status_df[status_df['revenue_opportunity'] == True])
        fault_count = len(status_df[status_df['operational_status'] == 'FAULT'])
        service_due = len(status_df[status_df['needs_proactive_contact'] == True])
        potential_revenue = total_opportunities * CONFIG['revenue_targets']['service_revenue_per_ticket']
        
        with col1:
            st.markdown(f"""
            <div class="ticket-card">
                <h4>🎫 Active Tickets</h4>
                <h2>{total_opportunities}</h2>
                <p>Revenue opportunities</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="service-due-card">
                <h4>⏰ Service Due</h4>
                <h2>{service_due}</h2>
                <p>Proactive notifications</p>
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
        
        # Proactive notifications section
        st.subheader("🔔 Proactive Customer Notifications")
        
        proactive_opportunities = status_df[
            (status_df['needs_proactive_contact'] == True) | 
            (status_df['operational_status'] == 'FAULT')
        ].copy()
        
        if not proactive_opportunities.empty:
            st.markdown("""
            <div class="proactive-alert">
                <h4>🚨 Immediate Action Required</h4>
                <p>The following customers should be contacted proactively to arrange service and maximize revenue:</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Create ticket data
            tickets = []
            for _, opportunity in proactive_opportunities.iterrows():
                if opportunity['operational_status'] == 'FAULT':
                    ticket_type = "🚨 FAULT RESPONSE"
                    priority = "CRITICAL"
                    estimated_revenue = CONFIG['revenue_targets']['service_revenue_per_ticket'] * 1.5  # Premium for emergency
                    action = "Contact immediately - Emergency service"
                else:
                    ticket_type = "📅 PREVENTIVE SERVICE"
                    priority = "HIGH"
                    estimated_revenue = CONFIG['revenue_targets']['service_revenue_per_ticket']
                    action = "Schedule within 72 hours"
                
                tickets.append({
                    'Ticket ID': f"TK-{random.randint(10000, 99999)}",
                    'Type': ticket_type,
                    'Generator': opportunity['serial_number'],
                    'Customer': opportunity['customer_name'][:25] + "...",
                    'Contact': opportunity['customer_contact'],
                    'Issue': opportunity['fault_description'] if opportunity['fault_description'] else f"Service due in {opportunity['next_service_hours']} hours",
                    'Priority': priority,
                    'Est. Revenue': f"${estimated_revenue:,.0f}",
                    'Action Required': action
                })
            
            tickets_df = pd.DataFrame(tickets)
            st.dataframe(tickets_df, use_container_width=True, hide_index=True)
            
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
            st.success("✅ No immediate proactive notifications required - All generators operating normally!")
        
        # Fleet status overview
        st.subheader("🗺️ Fleet Status Overview")
        
        # Status summary
        status_summary = status_df['operational_status'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
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
            revenue_by_customer = revenue_by_customer.sort_values('Opportunities', ascending=False).head(10)
            
            if not revenue_by_customer.empty:
                fig2 = px.bar(
                    revenue_by_customer, 
                    x='Opportunities', 
                    y='Customer',
                    title="Top Revenue Opportunities by Customer",
                    orientation='h'
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No current revenue opportunities identified")
    
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
    st.sidebar.markdown("✅ Real-time Generator Status")
    st.sidebar.markdown("✅ Live Sensor Monitoring")
    st.sidebar.markdown("✅ Revenue Optimization")
    st.sidebar.markdown("✅ Customer Self-Service Portal")

if __name__ == "__main__":
    main()
