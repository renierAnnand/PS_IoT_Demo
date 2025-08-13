"""
Optimized Power System Manufacturer IoT Platform
Performance-optimized version with caching, lazy loading, and streamlined data processing
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
    page_title="Power System Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Optimized CSS - Reduced complexity
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%);
        padding: 1rem;
        border-radius: 8px;
        color: white;
        margin: 0.3rem 0;
    }
    .alert-card {
        background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
        padding: 0.8rem;
        border-radius: 8px;
        color: white;
    }
    .header-card {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
CONFIG = {
    "company_name": "Power System Manufacturing",
    "refresh_interval": 30,  # Increased from 5 to reduce updates
    "cache_ttl": 300,  # 5 minute cache
    "revenue_targets": {
        "parts_annual": 2500000,
        "service_contracts": 1800000,
        "upsell_conversion": 0.25
    }
}

# Data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# ========================================
# PERFORMANCE OPTIMIZATION FUNCTIONS
# ========================================

@st.cache_data(ttl=CONFIG["cache_ttl"])
def load_base_generator_data() -> pd.DataFrame:
    """Cached function to load base generator data."""
    generators_file = DATA_DIR / "generators.csv"
    
    if not generators_file.exists():
        # Generate seed data once and cache it
        generators_data = _generate_seed_data()
        df = pd.DataFrame(generators_data)
        df.to_csv(generators_file, index=False)
        return df
    
    return pd.read_csv(generators_file)

def _generate_seed_data() -> Dict:
    """Generate seed data for generators - called only once."""
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
        'rated_kw': [
            2000, 1500, 1000, 800, 2500, 2000, 1800, 1200,
            1000, 750, 600, 400, 2200, 1800, 1400, 900,
            650, 500, 350, 300, 2800, 2200, 1600, 1100,
            850, 700, 450, 380, 320, 280
        ],
        'warranty_status': [
            'Active', 'Active', 'Expired', 'Active', 'Active', 'Expired', 'Active', 'Active',
            'Expired', 'Active', 'Active', 'Expired', 'Active', 'Active', 'Expired', 'Active',
            'Active', 'Expired', 'Active', 'Active', 'Active', 'Active', 'Expired', 'Active',
            'Active', 'Active', 'Expired', 'Active', 'Expired', 'Active'
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
        'customer_tier': [
            'Enterprise', 'Commercial', 'Enterprise', 'Enterprise',
            'Enterprise', 'Enterprise', 'Enterprise', 'Commercial',
            'Commercial', 'Enterprise', 'Enterprise', 'Commercial',
            'Enterprise', 'Enterprise', 'Small Business', 'Commercial',
            'Enterprise', 'Small Business', 'Enterprise', 'Commercial',
            'Enterprise', 'Enterprise', 'Small Business', 'Commercial',
            'Commercial', 'Enterprise', 'Small Business', 'Commercial',
            'Small Business', 'Commercial'
        ],
        'next_service_hours': [random.randint(-100, 800) for _ in range(30)],
        'total_runtime_hours': [random.randint(2000, 12000) for _ in range(30)],
        'location_city': [
            'Riyadh', 'Riyadh', 'Dammam', 'Riyadh', 'Riyadh', 'Jeddah', 'NEOM', 'Al-Ula',
            'Riyadh', 'Thuwal', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh',
            'Riyadh', 'Riyadh', 'Riyadh', 'Riyadh', 'NEOM', 'NEOM', 'NEOM', 'Qiddiya',
            'Al-Ula', 'Qiddiya', 'Riyadh', 'Riyadh', 'Diriyah', 'Riyadh'
        ]
    }

@st.cache_data(ttl=CONFIG["cache_ttl"])
def calculate_revenue_metrics() -> Dict:
    """Cached revenue calculations."""
    # Simulate revenue calculations
    base_parts = 1850000
    base_service = 1420000
    
    # Add some variance but keep it cached
    seed = int(time.time() // CONFIG["cache_ttl"])  # Changes every 5 minutes
    np.random.seed(seed)
    
    parts_variance = np.random.uniform(-0.05, 0.05)
    service_variance = np.random.uniform(-0.05, 0.05)
    
    return {
        'parts_revenue_ytd': int(base_parts * (1 + parts_variance)),
        'service_revenue_ytd': int(base_service * (1 + service_variance)),
        'parts_margin': 42.3,
        'service_margin': 48.7
    }

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_city_coordinates() -> Dict[str, Tuple[float, float]]:
    """Cached city coordinates."""
    return {
        'Riyadh': (24.7136, 46.6753),
        'Jeddah': (21.4858, 39.1925),
        'Dammam': (26.4207, 50.0888),
        'NEOM': (28.2654, 35.3254),
        'Al-Ula': (26.6084, 37.9218),
        'Qiddiya': (24.6500, 46.1667)
    }

@st.cache_data(ttl=CONFIG["cache_ttl"])
def generate_sensor_data(generators_df: pd.DataFrame) -> pd.DataFrame:
    """Generate optimized sensor data with caching."""
    cities = get_city_coordinates()
    
    # Use deterministic seed based on time for consistent but changing data
    seed = int(time.time() // CONFIG["cache_ttl"])
    np.random.seed(seed)
    
    map_data = []
    for _, gen in generators_df.iterrows():
        city = gen['location_city']
        base_lat, base_lon = cities.get(city, cities['Riyadh'])
        
        # Optimized data generation
        lat = base_lat + np.random.uniform(-0.1, 0.1)
        lon = base_lon + np.random.uniform(-0.1, 0.1)
        
        # Vectorized sensor simulation
        oil_pressure = np.random.uniform(25, 35)
        coolant_temp = np.random.uniform(80, 100)
        vibration = np.random.uniform(1.5, 5.0)
        fuel_level = np.random.uniform(15, 90)
        
        # Simplified health calculation
        health_score = 100
        if oil_pressure < 28: health_score -= 15
        if coolant_temp > 95: health_score -= 25
        if vibration > 4.0: health_score -= 30
        health_score = max(20, health_score)
        
        # Optimized status determination
        if oil_pressure < 25 or coolant_temp > 100:
            color, status = [255, 0, 0, 180], "CRITICAL"
        elif oil_pressure < 28 or coolant_temp > 95 or vibration > 4.0:
            color, status = [255, 165, 0, 180], "WARNING"
        elif health_score > 85:
            color, status = [0, 255, 0, 160], "HEALTHY"
        else:
            color, status = [255, 255, 0, 160], "MONITOR"
        
        map_data.append({
            'lat': lat, 'lon': lon,
            'generator_id': gen['serial_number'],
            'customer': gen['customer_name'][:30],
            'health_score': round(health_score, 1),
            'status': status, 'color': color,
            'size': gen['rated_kw'] / 80,
            'oil_pressure': round(oil_pressure, 1),
            'coolant_temp': round(coolant_temp, 1),
            'vibration': round(vibration, 2),
            'fuel_level': round(fuel_level, 1)
        })
    
    return pd.DataFrame(map_data)

# ========================================
# STREAMLINED AUTHENTICATION
# ========================================

def authenticate_manufacturer():
    """Optimized authentication with minimal UI."""
    st.markdown("""
    <div class="header-card">
        <h1>⚡ Power System Manufacturing</h1>
        <h3>After-Sales Revenue Optimization Platform</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        user_roles = {
            "ceo@powersystem": "👔 CEO Dashboard",
            "sales@powersystem": "💰 Sales Manager",
            "service@powersystem": "🔧 Service Operations",
            "customer@powersystem": "🏢 Customer Portal"
        }
        
        selected_role = st.selectbox(
            "Choose your role:",
            options=list(user_roles.keys()),
            format_func=lambda x: user_roles[x]
        )
        
        if st.button("🚀 Access Platform", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_role = selected_role
            st.session_state.role_name = user_roles[selected_role]
            st.rerun()

# ========================================
# OPTIMIZED DASHBOARD FUNCTIONS
# ========================================

def show_optimized_ceo_dashboard():
    """Optimized CEO dashboard with cached data."""
    st.title("👔 CEO Revenue Dashboard")
    
    # Load cached data
    generators_df = load_base_generator_data()
    revenue_metrics = calculate_revenue_metrics()
    
    # Revenue KPIs
    st.subheader("💰 Revenue Performance")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    parts_revenue = revenue_metrics['parts_revenue_ytd']
    service_revenue = revenue_metrics['service_revenue_ytd']
    total_revenue = parts_revenue + service_revenue
    
    targets = CONFIG['revenue_targets']
    total_target = targets['parts_annual'] + targets['service_contracts']
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Total Revenue</h4>
            <h2>${total_revenue:,.0f}</h2>
            <p>{(total_revenue/total_target*100):.1f}% of target</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Parts Revenue</h4>
            <h2>${parts_revenue:,.0f}</h2>
            <p>{(parts_revenue/targets['parts_annual']*100):.1f}% achieved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Service Revenue</h4>
            <h2>${service_revenue:,.0f}</h2>
            <p>{(service_revenue/targets['service_contracts']*100):.1f}% achieved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Parts Margin</h4>
            <h2>{revenue_metrics['parts_margin']:.1f}%</h2>
            <p>Target: 40%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Service Margin</h4>
            <h2>{revenue_metrics['service_margin']:.1f}%</h2>
            <p>Target: 45%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Optimized fleet overview
    st.subheader("🏭 Fleet Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Use cached calculations
        total_capacity = generators_df['rated_kw'].sum()
        active_contracts = len(generators_df[generators_df['service_contract'] != 'No Contract'])
        
        st.metric("Total Fleet Capacity", f"{total_capacity:,.0f} kW")
        st.metric("Active Service Contracts", f"{active_contracts} of {len(generators_df)}")
        
        # Simple pie chart
        contract_dist = generators_df['service_contract'].value_counts()
        fig = px.pie(values=contract_dist.values, names=contract_dist.index,
                    title="Service Contract Distribution", height=300)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer tier analysis
        tier_counts = generators_df['customer_tier'].value_counts()
        fig2 = px.bar(x=tier_counts.index, y=tier_counts.values,
                     title="Generators by Customer Tier", height=300)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Simplified opportunities
        st.markdown("**💡 Revenue Opportunities:**")
        st.write("🔧 12 units due for service ($180K)")
        st.write("📦 Filter replacements ($45K)")
        st.write("📋 8 contract upgrades ($320K)")

def show_optimized_fleet_monitoring():
    """Optimized fleet monitoring with lazy loading."""
    st.title("🗺️ Fleet Monitoring Dashboard")
    
    # Load base data
    generators_df = load_base_generator_data()
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    online_count = len(generators_df[generators_df['warranty_status'] == 'Active'])
    service_due = len(generators_df[generators_df['next_service_hours'] < 100])
    
    with col1:
        st.metric("Total Fleet", len(generators_df))
    with col2:
        st.metric("Online", online_count)
    with col3:
        st.metric("Service Due", service_due)
    with col4:
        st.metric("Avg Health", "87.5%")
    
    # Option to load detailed map
    if st.button("🗺️ Load Detailed Map View"):
        with st.spinner("Loading real-time sensor data..."):
            sensor_data = generate_sensor_data(generators_df)
            
            # Simplified map
            view_state = pdk.ViewState(latitude=24.7136, longitude=46.6753, zoom=6)
            
            layer = pdk.Layer(
                'ScatterplotLayer', data=sensor_data,
                get_position='[lon, lat]', get_color='color',
                get_radius='size', radius_scale=200, pickable=True
            )
            
            deck_map = pdk.Deck(
                map_style='mapbox://styles/mapbox/light-v9',
                initial_view_state=view_state, layers=[layer],
                tooltip={'text': '{generator_id} - {status}\nHealth: {health_score}%'}
            )
            
            st.pydeck_chart(deck_map)
    
    # Simplified alerts
    st.subheader("🚨 Current Alerts")
    alerts_data = [
        {'Generator': 'PS-2021-0003', 'Alert': 'Low oil pressure', 'Priority': 'High'},
        {'Generator': 'PS-2020-0008', 'Alert': 'Coolant temperature high', 'Priority': 'Medium'},
        {'Generator': 'PS-2021-0015', 'Alert': 'Service due', 'Priority': 'Low'}
    ]
    st.dataframe(pd.DataFrame(alerts_data), use_container_width=True, hide_index=True)

def show_optimized_customer_portal():
    """Optimized customer portal."""
    st.title("🏢 Customer Portal")
    
    generators_df = load_base_generator_data()
    
    # Customer selection
    customers = generators_df['customer_name'].unique()
    selected_customer = st.selectbox("Select Organization:", customers)
    
    customer_gens = generators_df[generators_df['customer_name'] == selected_customer]
    
    if customer_gens.empty:
        st.error("No generators found")
        return
    
    # Customer metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_capacity = customer_gens['rated_kw'].sum()
    active_count = len(customer_gens)
    
    with col1:
        st.metric("Fleet Health", "🟢 Excellent")
    with col2:
        st.metric("Total Capacity", f"{total_capacity:,.0f} kW")
    with col3:
        st.metric("Active Units", active_count)
    with col4:
        st.metric("Uptime", "🟢 99.2%")
    
    # Simplified fleet status
    st.subheader("🔋 Your Generator Fleet")
    
    fleet_display = customer_gens[['serial_number', 'model_series', 'location_city', 'warranty_status']].copy()
    fleet_display.columns = ['Serial Number', 'Model', 'Location', 'Status']
    
    st.dataframe(fleet_display, use_container_width=True, hide_index=True)
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📅 Schedule Service", use_container_width=True):
            st.success("✅ Service scheduled!")
    
    with col2:
        if st.button("🚨 Emergency Call", use_container_width=True, type="primary"):
            st.success("🚨 Emergency dispatch!")
    
    with col3:
        if st.button("🛒 Order Parts", use_container_width=True):
            st.success("🛒 Parts ordered!")
    
    with col4:
        if st.button("🔍 Run Diagnostics", use_container_width=True):
            st.success("🔍 Diagnostics complete!")

# ========================================
# MAIN APPLICATION
# ========================================

def main():
    """Optimized main application."""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Authentication check
    if not st.session_state.authenticated:
        authenticate_manufacturer()
        return
    
    # Simplified sidebar
    st.sidebar.markdown(f"### {st.session_state.role_name}")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    # Optimized navigation
    if st.session_state.user_role == "ceo@powersystem":
        pages = {
            "👔 CEO Dashboard": show_optimized_ceo_dashboard,
            "🗺️ Fleet Monitoring": show_optimized_fleet_monitoring,
            "🏢 Customer Portal": show_optimized_customer_portal
        }
    elif st.session_state.user_role == "customer@powersystem":
        pages = {
            "🏢 My Dashboard": show_optimized_customer_portal
        }
    else:
        pages = {
            "💰 Dashboard": show_optimized_ceo_dashboard,
            "🗺️ Fleet View": show_optimized_fleet_monitoring,
            "🏢 Customers": show_optimized_customer_portal
        }
    
    selected_page = st.sidebar.selectbox("Navigate:", list(pages.keys()))
    
    # Display selected page
    try:
        pages[selected_page]()
    except Exception as e:
        st.error(f"Error loading page: {str(e)}")
        st.info("Please try refreshing the page or selecting a different view.")
    
    # Simplified sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Platform Status")
    st.sidebar.success("✅ All systems operational")
    st.sidebar.info(f"🕒 Last update: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
