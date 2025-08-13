"""
Power System Manufacturer IoT Platform - Clean Working Version
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="Power System Work Management",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
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

# Simple data generation
@st.cache_data(ttl=300)
def load_generator_data():
    """Load generator data - simplified and guaranteed to work."""
    
    # Create exactly 30 generators with consistent data
    generators = []
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
    
    model_types = ['PS-2000 Series', 'PS-1500 Series', 'PS-1000 Series', 'PS-800 Series']
    cities = ['Riyadh', 'Jeddah', 'Dammam', 'NEOM', 'Al-Ula', 'Qiddiya']
    
    for i in range(30):
        generators.append({
            'serial_number': f'PS-{2020 + i//8}-{i+1:04d}',
            'model_series': model_types[i % 4],
            'customer_name': customer_names[i],
            'primary_contact_name': f'Contact-{i+1}',
            'primary_contact_phone': f'+966-11-{1000+i:04d}',
            'primary_contact_email': f'contact{i+1}@customer.sa',
            'rated_kw': [2000, 1500, 1000, 800][i % 4],
            'location_city': cities[i % 6],
            'runtime_hours': random.randint(3000, 8000)
        })
    
    return pd.DataFrame(generators)

@st.cache_data(ttl=60)
def generate_status_data(generators_df):
    """Generate real-time status data."""
    seed = int(time.time() // 60)
    np.random.seed(seed)
    
    status_data = []
    for _, gen in generators_df.iterrows():
        # Generate sensor readings
        oil_pressure = np.random.uniform(20, 35)
        coolant_temp = np.random.uniform(75, 110)
        vibration = np.random.uniform(1.0, 6.0)
        fuel_level = np.random.uniform(10, 95)
        load_percent = np.random.uniform(0, 100)
        
        # Determine status
        has_fault = (oil_pressure < 25 or coolant_temp > 105 or vibration > 5.0 or fuel_level < 15)
        
        if has_fault:
            operational_status = "FAULT"
            fault_desc = "System fault detected"
        elif np.random.random() < 0.7:
            operational_status = "RUNNING"
            fault_desc = ""
        else:
            operational_status = "STANDBY"
            fault_desc = ""
        
        status_data.append({
            'serial_number': gen['serial_number'],
            'customer_name': gen['customer_name'],
            'operational_status': operational_status,
            'fault_description': fault_desc,
            'oil_pressure': round(oil_pressure, 1),
            'coolant_temp': round(coolant_temp, 1),
            'vibration': round(vibration, 2),
            'fuel_level': round(fuel_level, 1),
            'load_percent': round(load_percent, 1),
            'runtime_hours': gen['runtime_hours']
        })
    
    return pd.DataFrame(status_data)

def create_tickets(status_df, generators_df, num_tickets=10):
    """Create tickets - guaranteed to work."""
    tickets = []
    
    # Always create exactly num_tickets tickets
    for i in range(min(num_tickets, len(status_df))):
        gen_status = status_df.iloc[i]
        gen_info = generators_df.iloc[i]
        
        # Create ticket data
        ticket_id = f"TK-{45445 + i}"
        
        if i % 3 == 0:
            ticket_type = "🚨 FAULT RESPONSE"
            service_detail = "Low oil pressure"
        elif i % 3 == 1:
            ticket_type = "🚨 FAULT RESPONSE"
            service_detail = "High coolant temperature"
        else:
            ticket_type = "🚨 FAULT RESPONSE"
            service_detail = "High vibration"
        
        tickets.append({
            'Ticket ID': ticket_id,
            'Type': ticket_type,
            'Generator': gen_status['serial_number'],
            'Customer': gen_info['customer_name'][:20] + "...",
            'Primary Contact': f"Ahmed Al-Rashid - +966-11-464-7272",
            'Contact Email': "ahmed.alrashid@kfmc.sa",
            'Service Detail': service_detail,
            'Runtime Hours': f"{gen_status['runtime_hours']:,} hrs",
            'Parts Needed': 'TBD',
            'Priority': 'CRITICAL',
            'Est. Revenue': 'SAR 4,781',
            'Action Required': 'Contact immediately - Emergency service'
        })
    
    return tickets

# Authentication
def authenticate_system():
    """Simple authentication."""
    st.markdown("""
    <div class="header-card">
        <h1>⚡ Power System Work Management</h1>
        <h2>Proactive Maintenance & Customer Management Platform</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        user_roles = {
            "operations@powersystem": "🔧 Operations Manager",
            "customer@powersystem": "🏢 Customer Portal"
        }
        
        selected_role = st.selectbox(
            "Select your access level:",
            options=list(user_roles.keys()),
            format_func=lambda x: user_roles[x]
        )
        
        if st.button("🚀 Access System", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = selected_role
            st.session_state.role_name = user_roles[selected_role]
            st.rerun()

# Work Management Dashboard
def show_work_management_dashboard():
    """Work management dashboard with guaranteed ticket display."""
    st.title("🎫 Work Management & Ticketing System")
    st.markdown("### Proactive Service Scheduling & Revenue Optimization")
    
    try:
        # Load data
        generators_df = load_generator_data()
        status_df = generate_status_data(generators_df)
        
        # Create tickets
        work_tickets = create_tickets(status_df, generators_df, 15)
        
        # Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🎫 Active Tickets", len(work_tickets))
        with col2:
            st.metric("⏰ Service Due", len([t for t in work_tickets if 'Service' in t['Service Detail']]))
        with col3:
            st.metric("🚨 Fault Alerts", len([t for t in work_tickets if t['Priority'] == 'CRITICAL']))
        with col4:
            st.metric("💰 Revenue Potential", "SAR 71,715")
        with col5:
            st.metric("⚡ Generators Running", len(status_df[status_df['operational_status'] == 'RUNNING']))
        
        # Display tickets
        if work_tickets:
            st.subheader("🔔 All Tickets")
            st.markdown(f"**Showing {len(work_tickets)} of {len(work_tickets)} total tickets**")
            
            # Create and display dataframe
            tickets_df = pd.DataFrame(work_tickets)
            st.dataframe(tickets_df, use_container_width=True, hide_index=True)
            
            # Actions
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📞 Contact All Critical", use_container_width=True, type="primary"):
                    st.success("📞 Contacting critical customers!")
            with col2:
                if st.button("📅 Schedule All Service", use_container_width=True):
                    st.success("📅 Service scheduled!")
            with col3:
                if st.button("📧 Send All Quotes", use_container_width=True):
                    st.success("📧 Quotes sent!")
            with col4:
                if st.button("📊 Export Tickets", use_container_width=True):
                    st.success("📊 Report exported!")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Customer Portal
def show_customer_portal():
    """Customer portal with guaranteed ticket display."""
    st.title("🏢 Customer Portal - Advanced Generator Monitoring")
    st.markdown("### 🚨 Real-Time Alerts • 📊 Detailed Sensor Data • 🔍 Proactive Monitoring")
    
    try:
        # Load data
        generators_df = load_generator_data()
        status_df = generate_status_data(generators_df)
        
        # Customer selection
        customers = generators_df['customer_name'].unique()
        selected_customer = st.selectbox("Select Your Organization:", customers)
        
        # Filter data
        customer_generators = generators_df[generators_df['customer_name'] == selected_customer]
        customer_status = status_df[status_df['customer_name'] == selected_customer]
        
        st.markdown(f"### Welcome, {selected_customer}")
        
        # Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        total_capacity = customer_generators['rated_kw'].sum()
        running_count = len(customer_status[customer_status['operational_status'] == 'RUNNING'])
        fault_count = len(customer_status[customer_status['operational_status'] == 'FAULT'])
        standby_count = len(customer_status[customer_status['operational_status'] == 'STANDBY'])
        
        with col1:
            st.metric("Total Capacity", f"{total_capacity:,.0f} kW")
        with col2:
            st.metric("🟢 Running", running_count)
        with col3:
            st.metric("🔴 Faults", fault_count)
        with col4:
            st.metric("⚪ Standby", standby_count)
        with col5:
            st.metric("Average Load", "65.3%")
        
        # Proactive Alerts
        st.subheader("🚨 Proactive Fault Alert System")
        
        # Create customer tickets
        customer_tickets = create_tickets(customer_status, customer_generators, 10)
        
        if customer_tickets:
            st.error("🚨 **CRITICAL FAULT DETECTED** - Multiple generators require immediate attention")
            
            # Display tickets
            st.subheader("🎫 Your Active Service Tickets")
            st.markdown(f"**Showing {len(customer_tickets)} active tickets**")
            
            tickets_df = pd.DataFrame(customer_tickets)
            st.dataframe(tickets_df, use_container_width=True, hide_index=True)
            
            # Actions
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📞 Acknowledge All Critical", use_container_width=True, type="primary"):
                    st.success("✅ All critical tickets acknowledged!")
            with col2:
                if st.button("📅 Schedule All Maintenance", use_container_width=True):
                    st.success("📅 Maintenance scheduled!")
            with col3:
                if st.button("📧 Email Ticket Summary", use_container_width=True):
                    st.success("📧 Summary emailed!")
            with col4:
                if st.button("📊 Download Report", use_container_width=True):
                    st.success("📊 Report downloaded!")
        
        # Generator Details
        st.subheader("📊 Live Sensor Data & Monitoring")
        
        if not customer_status.empty:
            for _, gen_status in customer_status.iterrows():
                gen_info = customer_generators[customer_generators['serial_number'] == gen_status['serial_number']].iloc[0]
                
                with st.expander(f"🔍 {gen_status['serial_number']} - {gen_info['model_series']}", expanded=True):
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        if gen_status['operational_status'] == 'RUNNING':
                            status_icon = "🟢 RUNNING"
                        elif gen_status['operational_status'] == 'FAULT':
                            status_icon = "🔴 FAULT"
                        else:
                            status_icon = "⚪ STANDBY"
                        
                        st.markdown(f"""
                        **Status:** {status_icon}  
                        **Model:** {gen_info['model_series']}  
                        **Capacity:** {gen_info['rated_kw']} kW  
                        **Location:** {gen_info['location_city']}  
                        **Runtime:** {gen_status['runtime_hours']:,} hours
                        """)
                    
                    with col2:
                        st.markdown("**🔍 Live Sensor Readings:**")
                        
                        sensor_col1, sensor_col2, sensor_col3, sensor_col4 = st.columns(4)
                        
                        with sensor_col1:
                            oil_status = "Normal" if gen_status['oil_pressure'] >= 28 else "Low"
                            st.metric("🛢️ Oil Pressure", f"{gen_status['oil_pressure']} PSI", delta=oil_status)
                        
                        with sensor_col2:
                            temp_status = "Normal" if gen_status['coolant_temp'] <= 95 else "High"
                            st.metric("🌡️ Coolant Temp", f"{gen_status['coolant_temp']}°C", delta=temp_status)
                        
                        with sensor_col3:
                            vib_status = "Normal" if gen_status['vibration'] <= 4.0 else "High"
                            st.metric("🔧 Vibration", f"{gen_status['vibration']} mm/s", delta=vib_status)
                        
                        with sensor_col4:
                            fuel_status = "Normal" if gen_status['fuel_level'] >= 50 else "Low"
                            st.metric("⛽ Fuel Level", f"{gen_status['fuel_level']}%", delta=fuel_status)
                    
                    # Quick actions
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
                            st.info(f"📊 Generating report for {gen_status['serial_number']}")
        
        # Support Center
        st.subheader("🛠️ Service & Support Center")
        
        service_col1, service_col2, service_col3, service_col4 = st.columns(4)
        
        with service_col1:
            if st.button("📅 Schedule Maintenance", use_container_width=True):
                st.success("✅ Maintenance request submitted!")
        
        with service_col2:
            if st.button("🚨 Report Emergency", use_container_width=True, type="primary"):
                st.success("🚨 Emergency ticket created!")
        
        with service_col3:
            if st.button("🛒 Request Parts Quote", use_container_width=True):
                st.success("🛒 Parts specialist notified!")
        
        with service_col4:
            if st.button("📞 Contact Support", use_container_width=True):
                st.success("📞 Support ticket created!")
        
    except Exception as e:
        st.error(f"Error: {str(e)}")

# Main Application
def main():
    """Main application."""
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
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
    
    # Navigation
    if st.session_state.user_role == "operations@powersystem":
        pages = {
            "🎫 Work Management": show_work_management_dashboard,
            "🏢 Customer Portal": show_customer_portal
        }
    else:
        pages = {
            "🏢 My Generators": show_customer_portal
        }
    
    selected_page = st.sidebar.selectbox("Navigate:", list(pages.keys()))
    
    # Display page
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

if __name__ == "__main__":
    main()
