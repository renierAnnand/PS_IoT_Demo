"""
Power System Manufacturer IoT Platform
Advanced after-sales revenue optimization and customer value platform
Focus: Parts sales, service revenue, customer retention, and fleet insights
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
import random
from typing import Dict, List, Optional
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="Power System Manufacturer Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for manufacturer branding
st.markdown("""
<style>
    .revenue-card {
        background: linear-gradient(135deg, #2e7d32 0%, #43a047 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.3);
    }
    .parts-opportunity {
        background: linear-gradient(135deg, #f57c00 0%, #ff9800 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        border-left: 5px solid #e65100;
    }
    .service-upsell {
        background: linear-gradient(135deg, #1976d2 0%, #2196f3 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        border-left: 5px solid #0d47a1;
    }
    .customer-value {
        background: linear-gradient(135deg, #7b1fa2 0%, #9c27b0 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        border-left: 5px solid #4a148c;
    }
    .manufacturer-insights {
        background: linear-gradient(135deg, #d32f2f 0%, #f44336 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        border-left: 5px solid #b71c1c;
    }
    .alert-revenue {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        border: 2px solid #ff4757;
        animation: pulse 2s infinite;
    }
    .manufacturer-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize data directory
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

# Configuration
MANUFACTURER_CONFIG = {
    "company_name": "Power System Manufacturing",
    "refresh_seconds": 5,
    "demo_mode": "manufacturer",
    "revenue_targets": {
        "parts_annual": 2500000,
        "service_contracts": 1800000,
        "upsell_conversion": 0.25
    },
    "parts_catalog": {
        "filters": {"oil": 150, "air": 85, "fuel": 120, "coolant": 200},
        "wear_parts": {"belts": 250, "hoses": 180, "gaskets": 95},
        "major_components": {"alternators": 3500, "control_panels": 2800, "cooling_systems": 4200},
        "consumables": {"oil_5l": 45, "coolant_10l": 85, "lubricants": 65}
    }
}

def load_manufacturer_data():
    """Load manufacturer-specific seed data."""
    generators_file = DATA_DIR / "generators.csv"
    if not generators_file.exists():
        generators_data = {
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
        pd.DataFrame(generators_data).to_csv(generators_file, index=False)

def authenticate_manufacturer():
    """Manufacturer-focused authentication."""
    st.markdown("""
    <div class="manufacturer-header">
        <h1>⚡ Power System Manufacturing</h1>
        <h2>After-Sales Revenue Optimization Platform</h2>
        <p>Maximize parts sales • Optimize service revenue • Enhance customer value</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Select Your Dashboard")
        
        user_roles = {
            "ceo@powersystem": "👔 CEO Dashboard - Revenue & Growth Analytics",
            "sales@powersystem": "💰 Sales Manager - Parts & Service Revenue",
            "service@powersystem": "🔧 Service Operations - Field & Customer Management",
            "customer@powersystem": "🏢 Customer Portal - Performance & Support"
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
        
        st.markdown("---")
        
        # Platform capabilities
        st.markdown("### 🎯 Platform Capabilities")
        capabilities = [
            "💰 **Revenue Optimization** - AI-driven parts sales opportunities",
            "🔧 **Service Upselling** - Predictive maintenance monetization",
            "📊 **Customer Analytics** - Lifetime value optimization",
            "🚀 **Growth Intelligence** - Market expansion insights",
            "⚡ **Real-time Monitoring** - Fleet performance tracking",
            "🎭 **Scenario Planning** - Revenue impact modeling"
        ]
        for cap in capabilities:
            st.markdown(cap)

def show_ceo_revenue_dashboard():
    """CEO-focused revenue and growth analytics dashboard."""
    st.title("👔 CEO Revenue Dashboard")
    st.markdown("### Strategic Overview: After-Sales Revenue Performance")
    
    # Load data
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except:
        st.error("Please initialize data first")
        return
    
    # Executive KPIs
    st.subheader("💰 Revenue Performance")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Mock revenue data
    parts_revenue_ytd = 1850000
    service_revenue_ytd = 1420000
    total_after_sales = parts_revenue_ytd + service_revenue_ytd
    
    # Targets
    parts_target = MANUFACTURER_CONFIG['revenue_targets']['parts_annual']
    service_target = MANUFACTURER_CONFIG['revenue_targets']['service_contracts']
    total_target = parts_target + service_target
    
    with col1:
        st.markdown(f"""
        <div class="revenue-card">
            <h3>Total After-Sales Revenue</h3>
            <h1>${total_after_sales:,.0f}</h1>
            <p>Target: ${total_target:,.0f}</p>
            <p>{(total_after_sales/total_target*100):.1f}% of annual target</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="parts-opportunity">
            <h3>Parts Revenue</h3>
            <h1>${parts_revenue_ytd:,.0f}</h1>
            <p>Target: ${parts_target:,.0f}</p>
            <p>{(parts_revenue_ytd/parts_target*100):.1f}% achieved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="service-upsell">
            <h3>Service Revenue</h3>
            <h1>${service_revenue_ytd:,.0f}</h1>
            <p>Target: ${service_target:,.0f}</p>
            <p>{(service_revenue_ytd/service_target*100):.1f}% achieved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="customer-value">
            <h3>Avg Parts Margin</h3>
            <h1>42.3%</h1>
            <p>Industry target: 40%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="manufacturer-insights">
            <h3>Avg Service Margin</h3>
            <h1>48.7%</h1>
            <p>Industry target: 45%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Fleet overview
    st.subheader("🏭 Fleet Overview")
    
    # Display generator fleet summary
    total_capacity = generators_df['rated_kw'].sum()
    active_contracts = len(generators_df[generators_df['service_contract'] != 'No Contract'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Fleet Capacity", f"{total_capacity:,.0f} kW")
        st.metric("Active Service Contracts", f"{active_contracts} of {len(generators_df)}")
        
        # Contract distribution
        contract_dist = generators_df['service_contract'].value_counts()
        fig = px.pie(values=contract_dist.values, names=contract_dist.index,
                    title="Service Contract Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer tier analysis
        tier_counts = generators_df['customer_tier'].value_counts()
        fig2 = px.bar(x=tier_counts.index, y=tier_counts.values,
                     title="Generators by Customer Tier")
        st.plotly_chart(fig2, use_container_width=True)
        
        # Revenue opportunities
        st.write("**💡 Revenue Opportunities:**")
        opportunities = [
            "🔧 12 units due for major service ($180K)",
            "📦 Filter replacement opportunities ($45K)",
            "📋 8 contract upgrade candidates ($320K)",
            "⚡ Emergency service premium potential ($95K)"
        ]
        for opp in opportunities:
            st.write(opp)

def show_fleet_monitoring_dashboard():
    """Real-time fleet monitoring with GPS tracking and comprehensive sensor data."""
    st.title("🗺️ Real-Time Fleet Monitoring Dashboard")
    st.markdown("### Live GPS Tracking & Health Monitoring with Advanced Sensor Analytics")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except:
        st.error("Please initialize data first")
        return
    
    # Fleet overview metrics with enhanced KPIs
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    online_count = len(generators_df[generators_df['warranty_status'] == 'Active'])
    critical_alerts = random.randint(2, 8)
    service_due = len(generators_df[generators_df['next_service_hours'] < 100])
    avg_health_score = random.uniform(85, 95)
    
    with col1:
        st.metric("Total Fleet", len(generators_df))
    with col2:
        st.metric("Online", online_count, delta="✅")
    with col3:
        st.metric("Critical Alerts", critical_alerts, delta="🚨" if critical_alerts > 5 else "⚠️")
    with col4:
        st.metric("Service Due", service_due, delta="📅")
    with col5:
        total_capacity = generators_df['rated_kw'].sum()
        st.metric("Total Capacity", f"{total_capacity:,.0f} kW")
    with col6:
        st.metric("Avg Health Score", f"{avg_health_score:.1f}%", delta="🎯 Target: 95%")
    
    # Enhanced Interactive Map with detailed status
    st.subheader("🗺️ Live Fleet Map - GPS Tracking & Status")
    
    # Create comprehensive map data with sensor information
    cities = {
        'Riyadh': (24.7136, 46.6753),
        'Jeddah': (21.4858, 39.1925),
        'Dammam': (26.4207, 50.0888),
        'NEOM': (28.2654, 35.3254),
        'Al-Ula': (26.6084, 37.9218),
        'Qiddiya': (24.6500, 46.1667)
    }
    
    map_data = []
    for _, gen in generators_df.iterrows():
        city = gen['location_city']
        base_lat, base_lon = cities.get(city, cities['Riyadh'])
        
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
        
        # Enhanced sensor data simulation
        oil_pressure = random.uniform(25, 35)  # PSI
        oil_temp = random.uniform(85, 105)     # °C
        coolant_temp = random.uniform(80, 100) # °C
        vibration = random.uniform(1.5, 5.0)   # mm/s
        fuel_level = random.uniform(15, 90)    # %
        last_service = random.randint(10, 180) # days ago
        
        # Calculate health score based on sensor readings
        health_score = 100
        if oil_pressure < 28: health_score -= 15
        if oil_temp > 100: health_score -= 20
        if coolant_temp > 95: health_score -= 25
        if vibration > 4.0: health_score -= 30
        if fuel_level < 20: health_score -= 10
        
        health_score = max(20, min(100, health_score + random.uniform(-5, 5)))
        
        # Color coding based on health and critical thresholds
        if oil_pressure < 25 or coolant_temp > 100 or vibration > 4.5:
            color = [255, 0, 0, 180]  # Critical Red
            status = "CRITICAL"
        elif oil_pressure < 28 or coolant_temp > 95 or vibration > 4.0 or fuel_level < 20:
            color = [255, 165, 0, 180]  # Warning Orange
            status = "WARNING"
        elif health_score > 85:
            color = [0, 255, 0, 160]  # Healthy Green
            status = "HEALTHY"
        else:
            color = [255, 255, 0, 160]  # Monitor Yellow
            status = "MONITOR"
        
        map_data.append({
            'lat': lat,
            'lon': lon,
            'generator_id': gen['serial_number'],
            'customer': gen['customer_name'][:30] + "..." if len(gen['customer_name']) > 30 else gen['customer_name'],
            'health_score': round(health_score, 1),
            'status': status,
            'color': color,
            'size': gen['rated_kw'] / 80,
            'oil_pressure': round(oil_pressure, 1),
            'oil_temp': round(oil_temp, 1),
            'coolant_temp': round(coolant_temp, 1),
            'vibration': round(vibration, 2),
            'fuel_level': round(fuel_level, 1),
            'last_service': last_service,
            'next_service_hours': gen['next_service_hours']
        })
    
    # Create PyDeck map with enhanced tooltip
    map_df = pd.DataFrame(map_data)
    
    view_state = pdk.ViewState(
        latitude=24.7136,
        longitude=46.6753,
        zoom=6,
        pitch=45
    )
    
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=map_df,
        get_position='[lon, lat]',
        get_color='color',
        get_radius='size',
        radius_scale=200,
        pickable=True
    )
    
    deck_map = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={
            'text': '''{generator_id} - {status}
Customer: {customer}
Health Score: {health_score}%
Oil Pressure: {oil_pressure} PSI
Oil Temp: {oil_temp}°C
Coolant Temp: {coolant_temp}°C
Vibration: {vibration} mm/s
Fuel Level: {fuel_level}%
Last Service: {last_service} days ago
Next Service: {next_service_hours} hours'''
        }
    )
    
    st.pydeck_chart(deck_map)
    
    # Enhanced Smart Alerts & Escalations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚨 Smart Alerts & Escalations")
        
        # Generate tiered alerts based on sensor data
        alerts = []
        
        for _, gen_data in map_df.iterrows():
            gen_id = gen_data['generator_id']
            
            # CRITICAL: Immediate shutdown required
            if gen_data['oil_pressure'] < 25:
                alerts.append({
                    'Level': '🔴 CRITICAL',
                    'Generator': gen_id,
                    'Alert': f'Oil pressure critical: {gen_data["oil_pressure"]} PSI',
                    'Action': 'AUTO-SHUTDOWN',
                    'Time': f'{random.randint(1, 10)} min ago',
                    'Escalation': 'Emergency team dispatched'
                })
            
            if gen_data['coolant_temp'] > 100:
                alerts.append({
                    'Level': '🔴 CRITICAL',
                    'Generator': gen_id,
                    'Alert': f'Coolant overheating: {gen_data["coolant_temp"]}°C',
                    'Action': 'AUTO-SHUTDOWN',
                    'Time': f'{random.randint(1, 15)} min ago',
                    'Escalation': 'Cooling system failure - Tech en route'
                })
            
            # WARNING: Trending toward danger zone
            elif gen_data['oil_pressure'] < 28:
                alerts.append({
                    'Level': '🟠 WARNING',
                    'Generator': gen_id,
                    'Alert': f'Oil pressure trending low: {gen_data["oil_pressure"]} PSI',
                    'Action': 'MONITOR',
                    'Time': f'{random.randint(15, 60)} min ago',
                    'Escalation': 'Service scheduled within 24hrs'
                })
            
            elif gen_data['vibration'] > 4.0:
                alerts.append({
                    'Level': '🟠 WARNING',
                    'Generator': gen_id,
                    'Alert': f'Vibration elevated: {gen_data["vibration"]} mm/s',
                    'Action': 'SCHEDULE SERVICE',
                    'Time': f'{random.randint(30, 120)} min ago',
                    'Escalation': 'Bearing inspection required'
                })
            
            # ROUTINE: Scheduled maintenance
            elif gen_data['next_service_hours'] < 50:
                alerts.append({
                    'Level': '🟡 ROUTINE',
                    'Generator': gen_id,
                    'Alert': f'Service due in {gen_data["next_service_hours"]} hours',
                    'Action': 'SCHEDULE',
                    'Time': f'{random.randint(60, 240)} min ago',
                    'Escalation': 'Customer notification sent'
                })
        
        # Display alerts sorted by severity
        severity_order = {'🔴 CRITICAL': 0, '🟠 WARNING': 1, '🟡 ROUTINE': 2}
        alerts_sorted = sorted(alerts[:8], key=lambda x: severity_order.get(x['Level'], 3))
        
        alerts_df = pd.DataFrame(alerts_sorted)
        if not alerts_df.empty:
            st.dataframe(alerts_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No active alerts - All systems operating normally!")
        
        # Alert automation controls
        st.write("**🤖 Automated Actions:**")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚨 Emergency Protocol"):
                st.success("All critical units auto-shutdown initiated!")
        with col_b:
            if st.button("📧 Notify All Customers"):
                st.success("Proactive notifications sent to affected customers!")
    
    with col2:
        st.subheader("📊 Sensor Trends & Predictive Analytics")
        
        # Real-time sensor dashboard
        st.write("**Live Sensor Readings (Fleet Average):**")
        
        # Calculate fleet averages
        avg_oil_pressure = map_df['oil_pressure'].mean()
        avg_oil_temp = map_df['oil_temp'].mean()
        avg_coolant_temp = map_df['coolant_temp'].mean()
        avg_vibration = map_df['vibration'].mean()
        avg_fuel = map_df['fuel_level'].mean()
        
        # Sensor metrics with thresholds
        sensor_col1, sensor_col2 = st.columns(2)
        
        with sensor_col1:
            oil_status = "🟢" if avg_oil_pressure > 30 else "🟡" if avg_oil_pressure > 28 else "🔴"
            st.metric(f"Oil Pressure {oil_status}", f"{avg_oil_pressure:.1f} PSI", delta="Min: 25 PSI")
            
            temp_status = "🟢" if avg_oil_temp < 95 else "🟡" if avg_oil_temp < 100 else "🔴"
            st.metric(f"Oil Temperature {temp_status}", f"{avg_oil_temp:.1f}°C", delta="Max: 100°C")
            
            fuel_status = "🟢" if avg_fuel > 30 else "🟡" if avg_fuel > 20 else "🔴"
            st.metric(f"Fuel Level {fuel_status}", f"{avg_fuel:.1f}%", delta="Min: 20%")
        
        with sensor_col2:
            coolant_status = "🟢" if avg_coolant_temp < 90 else "🟡" if avg_coolant_temp < 95 else "🔴"
            st.metric(f"Coolant Temp {coolant_status}", f"{avg_coolant_temp:.1f}°C", delta="Max: 95°C")
            
            vib_status = "🟢" if avg_vibration < 3.5 else "🟡" if avg_vibration < 4.0 else "🔴"
            st.metric(f"Vibration {vib_status}", f"{avg_vibration:.2f} mm/s", delta="Max: 4.0 mm/s")
            
            health_status = "🟢" if avg_health_score > 90 else "🟡" if avg_health_score > 80 else "🔴"
            st.metric(f"Fleet Health {health_status}", f"{avg_health_score:.1f}%", delta="Target: 95%")
        
        # Predictive maintenance insights
        st.write("**🔮 ML Predictions (Next 30 Days):**")
        
        predictions = [
            {"Type": "Bearing Failure", "Units": 3, "Confidence": "87%", "Days": "12-18"},
            {"Type": "Oil Degradation", "Units": 7, "Confidence": "92%", "Days": "5-25"},
            {"Type": "Cooling Issues", "Units": 2, "Confidence": "78%", "Days": "20-28"},
            {"Type": "Filter Clogging", "Units": 12, "Confidence": "94%", "Days": "10-30"}
        ]
        
        pred_df = pd.DataFrame(predictions)
        st.dataframe(pred_df, use_container_width=True, hide_index=True)
        
        if st.button("🔮 Generate Detailed Predictions"):
            st.success("Advanced ML analysis completed - Detailed report generated!")

def show_generator_specs_analysis():
    """Analyze generator specifications and integration."""
    st.title("📊 Generator Specifications Analysis")
    st.markdown("### GULFPOWER Baudouin Gensets Integration")
    
    # Sample Baudouin generator data
    baudouin_models = {
        'Model': ['6M11G65/5', '6M16G115/5', '6M21G165/5', '6M26G220/5', '6M33G275/5', 
                 '12V26G440/5', '12V33G550/5', '16V26G605/5', '16V33G715/5'],
        'Power_kW': [65, 115, 165, 220, 275, 440, 550, 605, 715],
        'Engine_Type': ['6M11', '6M16', '6M21', '6M26', '6M33', '12V26', '12V33', '16V26', '16V33'],
        'Fuel_Consumption_L_h': [19.5, 32.2, 45.8, 60.5, 75.2, 118.8, 148.5, 163.4, 193.0],
        'Service_Interval_Hours': [250, 250, 250, 500, 500, 500, 500, 500, 500],
        'Maintenance_Cost_Annual': [3200, 4800, 6500, 8500, 11000, 15500, 18000, 20000, 24000],
        'Parts_Cost_Per_Service': [450, 680, 920, 1200, 1450, 2100, 2400, 2650, 3100]
    }
    
    baudouin_df = pd.DataFrame(baudouin_models)
    
    # Display specifications
    st.subheader("🔧 Baudouin Generator Specifications")
    st.dataframe(baudouin_df, use_container_width=True, hide_index=True)
    
    # Analysis insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Power Range Analysis")
        fig = px.bar(baudouin_df, x='Model', y='Power_kW',
                   title="Power Output by Model")
        fig.update_layout(height=300, xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Fuel efficiency
        baudouin_df['Fuel_Efficiency'] = baudouin_df['Power_kW'] / baudouin_df['Fuel_Consumption_L_h']
        
        st.write("**Most Fuel Efficient Models:**")
        top_efficient = baudouin_df.nlargest(3, 'Fuel_Efficiency')[['Model', 'Fuel_Efficiency']]
        top_efficient['Fuel_Efficiency'] = top_efficient['Fuel_Efficiency'].round(2)
        st.dataframe(top_efficient, hide_index=True, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue Potential Analysis")
        
        # Calculate revenue potential
        revenue_potential = []
        for _, model in baudouin_df.iterrows():
            services_per_year = 8760 / model['Service_Interval_Hours']
            annual_parts_revenue = services_per_year * model['Parts_Cost_Per_Service']
            annual_service_revenue = model['Maintenance_Cost_Annual']
            total_revenue = annual_parts_revenue + annual_service_revenue
            
            revenue_potential.append({
                'Model': model['Model'],
                'Parts Revenue': f"${annual_parts_revenue:,.0f}",
                'Service Revenue': f"${annual_service_revenue:,.0f}",
                'Total Revenue': f"${total_revenue:,.0f}"
            })
        
        revenue_df = pd.DataFrame(revenue_potential)
        st.dataframe(revenue_df, hide_index=True, use_container_width=True)
        
        if st.button("💰 Calculate Revenue Projections"):
            st.success("Revenue projections calculated for next 12 months!")
    
    # Maintenance schedule integration
    st.subheader("📋 Integrated Maintenance Schedule")
    
    maintenance_matrix = []
    for _, model in baudouin_df.iterrows():
        interval = model['Service_Interval_Hours']
        
        maintenance_matrix.append({
            'Model': model['Model'],
            'Power': f"{model['Power_kW']} kW",
            'Service Interval': f"{interval} hrs",
            'Daily Check': 'Fuel, Visual, Alarms',
            'Weekly (10hrs)': 'Run test, Oil check, Battery',
            'Monthly (40hrs)': 'Load test, Belt inspection',
            f'Service ({interval}hrs)': 'Oil change, Filters, Full inspection',
            'Annual Cost': f"${model['Maintenance_Cost_Annual']:,}"
        })
    
    maintenance_df = pd.DataFrame(maintenance_matrix)
    st.dataframe(maintenance_df, use_container_width=True, hide_index=True)

def show_event_replay_analysis():
    """Event Replay & Root Cause Analysis dashboard."""
    st.title("🔍 Event Replay & Root Cause Analysis")
    st.markdown("### Detailed Event Investigation & Warranty Analysis")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except:
        st.error("Please initialize data first")
        return
    
    # Event selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Mock recent events
        recent_events = [
            'PS-2021-0001 - Oil Pressure Drop (Critical)',
            'PS-2020-0005 - Coolant Overheat (Critical)', 
            'PS-2021-0012 - Vibration Spike (Warning)',
            'PS-2020-0008 - Fuel System Issue (Warning)',
            'PS-2021-0015 - Load Bank Failure (Critical)'
        ]
        
        selected_event = st.selectbox("Select Event to Analyze:", recent_events)
        event_id = selected_event.split(' - ')[0]
        
    with col2:
        analysis_period = st.selectbox("Analysis Period:", 
                                     ["Last 24 hours", "Last 7 days", "Last 30 days", "Custom Range"])
        
    with col3:
        if st.button("🔍 Generate Analysis Report"):
            st.success("Detailed analysis report generated!")
    
    # Event timeline and sensor data
    st.subheader(f"📈 Sensor Data Timeline - {selected_event}")
    
    # Generate mock historical sensor data leading to event
    hours_before = list(range(-24, 1))  # 24 hours before to event time
    
    # Simulate realistic sensor degradation patterns
    base_oil_pressure = 32
    base_coolant_temp = 85
    base_vibration = 2.5
    
    oil_pressure_data = []
    coolant_temp_data = []
    vibration_data = []
    
    for hour in hours_before:
        # Oil pressure drops gradually then sharply
        if hour > -6:  # Last 6 hours - rapid decline
            oil_pressure = base_oil_pressure + (hour + 6) * 1.5 + random.uniform(-0.5, 0.5)
        else:  # Gradual decline
            oil_pressure = base_oil_pressure + hour * 0.1 + random.uniform(-1, 1)
        
        # Coolant temperature rises as oil pressure drops
        coolant_temp = base_coolant_temp + (-hour * 0.3) + random.uniform(-2, 2)
        if hour > -6:  # Rapid rise in last 6 hours
            coolant_temp += (hour + 6) * 2
        
        # Vibration increases with mechanical stress
        vibration = base_vibration + (-hour * 0.05) + random.uniform(-0.2, 0.2)
        if hour > -4:  # Sharp increase in last 4 hours
            vibration += (hour + 4) * 0.3
        
        oil_pressure_data.append(max(15, oil_pressure))
        coolant_temp_data.append(min(110, coolant_temp))
        vibration_data.append(max(1.0, vibration))
    
    # Create timeline chart
    timeline_df = pd.DataFrame({
        'Hours_Before_Event': hours_before,
        'Oil_Pressure_PSI': oil_pressure_data,
        'Coolant_Temp_C': coolant_temp_data,
        'Vibration_mm_s': vibration_data
    })
    
    fig = go.Figure()
    
    # Add sensor traces
    fig.add_trace(go.Scatter(x=timeline_df['Hours_Before_Event'], y=timeline_df['Oil_Pressure_PSI'],
                            mode='lines', name='Oil Pressure (PSI)', line=dict(color='blue', width=3)))
    
    fig.add_trace(go.Scatter(x=timeline_df['Hours_Before_Event'], y=timeline_df['Coolant_Temp_C'],
                            mode='lines', name='Coolant Temp (°C)', line=dict(color='red', width=3), yaxis='y2'))
    
    fig.add_trace(go.Scatter(x=timeline_df['Hours_Before_Event'], y=timeline_df['Vibration_mm_s'],
                            mode='lines', name='Vibration (mm/s)', line=dict(color='orange', width=3), yaxis='y3'))
    
    # Add threshold lines
    fig.add_hline(y=25, line_dash="dash", line_color="blue", annotation_text="Oil Pressure Critical (25 PSI)")
    fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Coolant Temp Critical (95°C)", yaxis='y2')
    fig.add_hline(y=4.0, line_dash="dash", line_color="orange", annotation_text="Vibration Warning (4.0 mm/s)", yaxis='y3')
    
    # Add event marker
    fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=4, 
                  annotation_text="EVENT OCCURRED", annotation_position="top")
    
    # Multi-axis layout
    fig.update_layout(
        title="Sensor Data Leading to Event (24-Hour Timeline)",
        xaxis=dict(title="Hours Before Event"),
        yaxis=dict(title="Oil Pressure (PSI)", side="left"),
        yaxis2=dict(title="Coolant Temperature (°C)", side="right", overlaying="y", range=[80, 110]),
        yaxis3=dict(title="Vibration (mm/s)", side="right", overlaying="y", position=0.95, range=[1, 6]),
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Root cause analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧠 AI Root Cause Analysis")
        
        # Automated analysis results
        st.markdown("""
        <div class="manufacturer-insights">
            <h4>🎯 Primary Root Cause Identified</h4>
            <p><strong>Oil Filter Blockage</strong> - 89% Confidence</p>
            <ul>
                <li><strong>Evidence:</strong> Gradual oil pressure decline over 18 hours</li>
                <li><strong>Pattern:</strong> Consistent with filter restriction buildup</li>
                <li><strong>Trigger:</strong> Extended high-load operation (156 hours continuous)</li>
                <li><strong>Secondary:</strong> Inadequate oil quality (contamination detected)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="parts-opportunity">
            <h4>⚙️ Contributing Factors</h4>
            <ul>
                <li><strong>Maintenance:</strong> Oil change overdue by 45 hours</li>
                <li><strong>Operating:</strong> Above-normal ambient temperature (+8°C)</li>
                <li><strong>Load:</strong> Running at 95% capacity for extended period</li>
                <li><strong>History:</strong> Similar pattern observed 6 months ago</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="service-upsell">
            <h4>📋 Warranty Assessment</h4>
            <ul>
                <li><strong>Warranty Status:</strong> Active (18 months remaining)</li>
                <li><strong>Claim Validity:</strong> ❌ Not covered - Maintenance neglect</li>
                <li><strong>Customer Responsibility:</strong> Overdue maintenance contributed</li>
                <li><strong>Recommendation:</strong> Enhanced maintenance contract</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🔧 Preventive Actions & Recommendations")
        
        # Actionable recommendations
        recommendations = [
            {
                'Priority': '🔴 High',
                'Action': 'Immediate oil filter replacement',
                'Timeline': '< 4 hours',
                'Cost': '$450',
                'Technician': 'Ahmed Al-Rashid (12km away)'
            },
            {
                'Priority': '🟠 Medium', 
                'Action': 'Complete oil system flush',
                'Timeline': '1-2 days',
                'Cost': '$850',
                'Technician': 'Mohammed Al-Saud'
            },
            {
                'Priority': '🟡 Low',
                'Action': 'Upgrade to Premium Care contract',
                'Timeline': '2 weeks',
                'Cost': '$2,400/year',
                'Technician': 'Sales team follow-up'
            },
            {
                'Priority': '🟢 Future',
                'Action': 'Install oil quality sensors',
                'Timeline': '1 month',
                'Cost': '$1,200',
                'Technician': 'Upgrade specialist'
            }
        ]
        
        recommendations_df = pd.DataFrame(recommendations)
        st.dataframe(recommendations_df, use_container_width=True, hide_index=True)
        
        # Quick actions
        st.write("**⚡ Quick Actions:**")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📞 Dispatch Technician"):
                st.success("Ahmed Al-Rashid dispatched - ETA: 45 minutes")
        with col_b:
            if st.button("📧 Send Report to Customer"):
                st.success("Root cause analysis report sent to customer")
        
        # Similar events
        st.write("**🔄 Similar Historical Events:**")
        similar_events = [
            "PS-2020-0012 - Oil pressure drop (6 months ago)",
            "PS-2021-0007 - Filter blockage (8 months ago)", 
            "PS-2020-0003 - Maintenance overdue (4 months ago)"
        ]
        
        for event in similar_events:
            st.write(f"• {event}")
        
        if st.button("📊 Generate Trend Analysis"):
            st.success("Fleet-wide maintenance pattern analysis generated!")

def show_parts_technician_planning():
    """Parts & Technician Planning dashboard."""
    st.title("🔧 Parts & Technician Planning")
    st.markdown("### Auto-Generated Parts Lists & Technician Assignment")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except:
        st.error("Please initialize data first")
        return
    
    # Planning overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pending_work_orders = random.randint(15, 25)
        st.metric("Pending Work Orders", pending_work_orders)
    
    with col2:
        available_techs = 8
        st.metric("Available Technicians", available_techs)
    
    with col3:
        parts_in_stock = random.randint(85, 95)
        st.metric("Parts Availability", f"{parts_in_stock}%")
    
    with col4:
        avg_response_time = random.uniform(2.5, 4.2)
        st.metric("Avg Response Time", f"{avg_response_time:.1f} hrs")
    
    # Auto-generated work orders
    st.subheader("🤖 Auto-Generated Work Orders")
    
    # Generate realistic work orders based on sensor data and maintenance schedules
    work_orders = []
    
    for i, (_, gen) in enumerate(generators_df.head(12).iterrows()):
        # Determine issue type based on runtime and service hours
        runtime = gen['total_runtime_hours']
        service_hours = gen['next_service_hours']
        
        if service_hours < 0:  # Overdue
            issue_type = "Scheduled Maintenance"
            priority = "High"
            parts_needed = ["Oil Filter", "Air Filter", "Oil (20L)", "Coolant (10L)"]
            estimated_cost = 850
            labor_hours = 4
        elif service_hours < 50:  # Due soon
            issue_type = "Preventive Service"
            priority = "Medium"
            parts_needed = ["Oil Filter", "Oil (20L)"]
            estimated_cost = 450
            labor_hours = 2
        elif runtime > 8000:  # High wear
            issue_type = "Wear Parts Replacement"
            priority = "Medium"
            parts_needed = ["Belt Kit", "Hoses", "Gasket Set"]
            estimated_cost = 650
            labor_hours = 3
        else:  # Random issues
            issues = ["Diagnostic Check", "Battery Replacement", "Minor Repair"]
            issue_type = random.choice(issues)
            priority = "Low"
            parts_needed = ["Battery"] if "Battery" in issue_type else ["Misc Parts"]
            estimated_cost = random.randint(200, 500)
            labor_hours = random.randint(1, 3)
        
        # Auto-assign technician based on location and skills
        tech_assignments = {
            'Riyadh': 'Ahmed Al-Rashid',
            'Jeddah': 'Mohammed Al-Saud', 
            'Dammam': 'Khalid Al-Otaibi',
            'NEOM': 'Abdullah Al-Nasser',
            'Al-Ula': 'Omar Al-Harbi',
            'Qiddiya': 'Fahad Al-Qahtani'
        }
        
        assigned_tech = tech_assignments.get(gen['location_city'], 'Ahmed Al-Rashid')
        
        # Calculate distance (mock)
        distances = {'Ahmed Al-Rashid': '12km', 'Mohammed Al-Saud': '8km', 'Khalid Al-Otaibi': '15km',
                    'Abdullah Al-Nasser': '25km', 'Omar Al-Harbi': '18km', 'Fahad Al-Qahtani': '10km'}
        
        work_orders.append({
            'WO #': f'WO-{2024120 + i:d}',
            'Generator': gen['serial_number'],
            'Customer': gen['customer_name'][:25] + "..." if len(gen['customer_name']) > 25 else gen['customer_name'],
            'Issue Type': issue_type,
            'Priority': priority,
            'Parts Required': ', '.join(parts_needed[:2]) + "..." if len(parts_needed) > 2 else ', '.join(parts_needed),
            'Est. Cost': f"${estimated_cost}",
            'Labor Hours': f"{labor_hours}h",
            'Assigned Technician': assigned_tech,
            'Distance': distances.get(assigned_tech, '12km'),
            'Status': random.choice(['Pending', 'Scheduled', 'In Progress', 'Parts Ordered'])
        })
    
    work_orders_df = pd.DataFrame(work_orders)
    st.dataframe(work_orders_df, use_container_width=True, hide_index=True)
    
    # Parts planning
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Auto-Generated Parts Lists")
        
        # Aggregate parts requirements
        all_parts_needed = {}
        
        # Mock parts requirements based on work orders
        parts_catalog = {
            'Oil Filter': {'stock': 45, 'cost': 150, 'supplier': 'OEM Direct'},
            'Air Filter': {'stock': 32, 'cost': 85, 'supplier': 'Filter Express'},
            'Oil (20L)': {'stock': 28, 'cost': 200, 'supplier': 'Shell Commercial'},
            'Coolant (10L)': {'stock': 15, 'cost': 85, 'supplier': 'Total Energies'},
            'Belt Kit': {'stock': 8, 'cost': 250, 'supplier': 'OEM Direct'},
            'Hoses': {'stock': 12, 'cost': 180, 'supplier': 'Hydraulic Supply'},
            'Gasket Set': {'stock': 6, 'cost': 95, 'supplier': 'OEM Direct'},
            'Battery': {'stock': 20, 'cost': 320, 'supplier': 'Battery World'}
        }
        
        # Calculate demand
        for wo in work_orders:
            parts = wo['Parts Required'].split(', ')
            for part in parts:
                part = part.replace('...', '').strip()
                if part in parts_catalog:
                    if part not in all_parts_needed:
                        all_parts_needed[part] = 0
                    all_parts_needed[part] += 1
        
        # Create parts planning table
        parts_planning = []
        for part, needed in all_parts_needed.items():
            if part in parts_catalog:
                info = parts_catalog[part]
                stock_status = "✅ In Stock" if info['stock'] >= needed else "⚠️ Low Stock" if info['stock'] > 0 else "🔴 Out of Stock"
                
                parts_planning.append({
                    'Part': part,
                    'Needed': needed,
                    'In Stock': info['stock'],
                    'Status': stock_status,
                    'Unit Cost': f"${info['cost']}",
                    'Total Cost': f"${info['cost'] * needed:,}",
                    'Supplier': info['supplier']
                })
        
        parts_df = pd.DataFrame(parts_planning)
        st.dataframe(parts_df, use_container_width=True, hide_index=True)
        
        # Parts actions
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📋 Generate Purchase Order"):
                st.success("Purchase order for low-stock items generated!")
        with col_b:
            if st.button("🚚 Expedite Critical Parts"):
                st.success("Critical parts expedited - Delivery tomorrow!")
    
    with col2:
        st.subheader("👷 Technician Assignment & Skills")
        
        # Technician profiles with skills and current status
        technicians = [
            {
                'Name': 'Ahmed Al-Rashid',
                'Location': 'Riyadh Central',
                'Status': '✅ Available',
                'Skills': 'Engine, Electrical, Diagnostics',
                'Current Jobs': 2,
                'Efficiency': '94%',
                'Distance from Jobs': '8-15km'
            },
            {
                'Name': 'Mohammed Al-Saud',
                'Location': 'Jeddah',
                'Status': '🟡 On Service Call',
                'Skills': 'Cooling, Fuel Systems, PM',
                'Current Jobs': 3,
                'Efficiency': '91%',
                'Distance from Jobs': '5-20km'
            },
            {
                'Name': 'Khalid Al-Otaibi',
                'Location': 'Dammam',
                'Status': '✅ Available',
                'Skills': 'Mechanical, Bearings, Vibration',
                'Current Jobs': 1,
                'Efficiency': '96%',
                'Distance from Jobs': '10-25km'
            },
            {
                'Name': 'Abdullah Al-Nasser',
                'Location': 'NEOM',
                'Status': '🔴 Travel to Site',
                'Skills': 'Advanced Diagnostics, Controls',
                'Current Jobs': 2,
                'Efficiency': '88%',
                'Distance from Jobs': '15-45km'
            },
            {
                'Name': 'Omar Al-Harbi',
                'Location': 'Al-Ula',
                'Status': '✅ Available',
                'Skills': 'Emergency Repair, Welding',
                'Current Jobs': 1,
                'Efficiency': '92%',
                'Distance from Jobs': '12-30km'
            }
        ]
        
        techs_df = pd.DataFrame(technicians)
        st.dataframe(techs_df, use_container_width=True, hide_index=True)
        
        # Technician optimization
        st.write("**🎯 Optimization Recommendations:**")
        optimizations = [
            "• Reassign WO-2024123 to Ahmed (closer by 8km)",
            "• Schedule PM cluster in Riyadh for efficiency", 
            "• Omar available for emergency calls (Al-Ula region)",
            "• Mohammed returning from service call at 14:30"
        ]
        
        for opt in optimizations:
            st.write(opt)
        
        # Quick actions
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔄 Auto-Optimize Routes"):
                st.success("Routes optimized - 23% efficiency improvement!")
        with col_b:
            if st.button("📞 Notify Technicians"):
                st.success("Work assignments sent to all technicians!")
        
        # Skills matrix
        if st.button("🎓 View Skills Matrix"):
            st.info("Skills matrix shows technician capabilities for advanced assignment logic")

def show_enhanced_customer_portal():
    """Enhanced customer portal with advanced features."""
    st.title("🏢 Enhanced Customer Portal")
    st.markdown("### Your Generator Performance & Support Dashboard")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except:
        st.error("Please initialize data first")
        return
    
    # Customer selection
    customers = generators_df['customer_name'].unique()
    selected_customer = st.selectbox("Select Your Organization:", customers)
    
    customer_generators = generators_df[generators_df['customer_name'] == selected_customer]
    
    if customer_generators.empty:
        st.error("No generators found for selected customer")
        return
    
    st.markdown(f"### Welcome, {selected_customer}")
    
    # Proactive notifications banner
    notification_types = [
        ("🟡", "Service Reminder", "Generator PS-2021-0003 is due for maintenance in 3 days"),
        ("🔴", "Critical Alert", "Low fuel detected on Generator PS-2020-0008 - 15% remaining"),
        ("🟠", "Performance Alert", "Efficiency drop detected on PS-2021-0001 - Trending downward"),
        ("🔵", "Scheduled Maintenance", "Load bank test scheduled for Generator PS-2020-0012 next week"),
        ("🟢", "Success", "Preventive maintenance completed on Generator PS-2021-0001 - Performance restored")
    ]
    
    # Show random notification
    if random.random() > 0.3:  # 70% chance of showing notification
        icon, alert_type, message = random.choice(notification_types)
        
        if "Critical" in alert_type:
            st.error(f"{icon} **{alert_type}:** {message}")
        elif "Performance" in alert_type:
            st.warning(f"{icon} **{alert_type}:** {message}")
        elif "Success" in alert_type:
            st.success(f"{icon} **{alert_type}:** {message}")
        else:
            st.info(f"{icon} **{alert_type}:** {message}")
    
    # Enhanced customer metrics with traffic light system
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_capacity = customer_generators['rated_kw'].sum()
    active_generators = len(customer_generators)
    avg_runtime = customer_generators['total_runtime_hours'].mean()
    estimated_annual_spend = len(customer_generators) * random.randint(8000, 25000)
    
    # Calculate overall health with realistic sensor simulation
    health_scores = []
    fuel_levels = []
    service_statuses = []
    
    for _, gen in customer_generators.iterrows():
        # Health scoring based on multiple factors
        health = random.uniform(75, 98)
        fuel = random.uniform(15, 90)
        service_hours = gen['next_service_hours']
        
        health_scores.append(health)
        fuel_levels.append(fuel)
        
        if service_hours < 0:
            service_statuses.append("overdue")
        elif service_hours < 100:
            service_statuses.append("due_soon")
        else:
            service_statuses.append("current")
    
    avg_health = sum(health_scores) / len(health_scores)
    avg_fuel = sum(fuel_levels) / len(fuel_levels)
    overdue_count = service_statuses.count("overdue")
    due_soon_count = service_statuses.count("due_soon")
    
    # Traffic light indicators
    if avg_health > 90:
        health_color = "🟢"
        health_status = "Excellent"
    elif avg_health > 80:
        health_color = "🟡"
        health_status = "Good"
    else:
        health_color = "🔴"
        health_status = "Needs Attention"
    
    if avg_fuel > 50:
        fuel_color = "🟢"
    elif avg_fuel > 30:
        fuel_color = "🟡"
    else:
        fuel_color = "🔴"
    
    if overdue_count > 0:
        service_color = "🔴"
        service_status = f"{overdue_count} Overdue"
    elif due_soon_count > 0:
        service_color = "🟡"
        service_status = f"{due_soon_count} Due Soon"
    else:
        service_color = "🟢"
        service_status = "All Current"
    
    with col1:
        st.metric("Fleet Health", f"{health_color} {health_status}", delta=f"{avg_health:.1f}% avg score")
    
    with col2:
        st.metric("Total Capacity", f"{total_capacity:,.0f} kW", delta=f"{active_generators} units")
    
    with col3:
        st.metric("Fleet Fuel Status", f"{fuel_color} {avg_fuel:.0f}% avg", delta="Auto-monitored")
    
    with col4:
        st.metric("Service Status", f"{service_color} {service_status}", delta="AI-scheduled")
    
    with col5:
        uptime_pct = random.uniform(97.5, 99.8)
        uptime_color = "🟢" if uptime_pct > 99 else "🟡" if uptime_pct > 98 else "🔴"
        st.metric("Fleet Uptime", f"{uptime_color} {uptime_pct:.1f}%", delta="SLA: 99%")
    
    # Enhanced fleet status with GPS and real-time data
    st.subheader("🔋 Your Generator Fleet - Live Status & GPS Tracking")
    
    # Create enhanced fleet view with all requested features
    fleet_data = []
    
    for _, gen in customer_generators.iterrows():
        # Simulate realistic operational data
        current_fuel = random.uniform(15, 90)
        efficiency = random.uniform(82, 96)
        vibration = random.uniform(1.8, 4.5)
        oil_pressure = random.uniform(24, 35)
        coolant_temp = random.uniform(78, 98)
        
        # Calculate remaining runtime based on fuel and consumption
        fuel_consumption_rate = 8.5  # L/hour average
        tank_capacity = 200  # Liters
        remaining_runtime = (current_fuel / 100 * tank_capacity) / fuel_consumption_rate
        
        # Maintenance status
        hours_to_service = gen['next_service_hours']
        if hours_to_service < 0:
            maintenance_status = "🔴 Overdue"
            maintenance_priority = "Critical"
        elif hours_to_service < 50:
            maintenance_status = "🟠 Due Soon"
            maintenance_priority = "High"
        elif hours_to_service < 200:
            maintenance_status = "🟡 Scheduled"
            maintenance_priority = "Medium"
        else:
            maintenance_status = "🟢 Current"
            maintenance_priority = "Low"
        
        # Health indicator based on sensor readings
        health_issues = []
        if oil_pressure < 26:
            health_issues.append("Low Oil Pressure")
        if coolant_temp > 95:
            health_issues.append("High Coolant Temp")
        if vibration > 4.0:
            health_issues.append("High Vibration")
        if efficiency < 85:
            health_issues.append("Low Efficiency")
        
        if len(health_issues) >= 2:
            health_indicator = "🔴 Critical"
        elif len(health_issues) == 1:
            health_indicator = "🟡 Warning"
        else:
            health_indicator = "🟢 Healthy"
        
        fleet_data.append({
            'Serial Number': gen['serial_number'],
            'Model': gen['model_series'],
            'Location': gen['location_city'],
            'Health': health_indicator,
            'Fuel Level': f"{current_fuel:.0f}% ({remaining_runtime:.1f}h runtime)",
            'Efficiency': f"{efficiency:.1f}%",
            'Maintenance': maintenance_status,
            'Priority': maintenance_priority,
            'Oil Pressure': f"{oil_pressure:.1f} PSI",
            'Coolant Temp': f"{coolant_temp:.0f}°C",
            'Vibration': f"{vibration:.1f} mm/s",
            'Last Service': f"{random.randint(15, 120)} days ago"
        })
    
    fleet_df = pd.DataFrame(fleet_data)
    st.dataframe(fleet_df, use_container_width=True, hide_index=True)
    
    # One-click service requests with enhanced features
    st.subheader("🚀 One-Click Service Requests & Self-Help")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="service-upsell">
            <h4>🔧 Schedule Maintenance</h4>
            <p>AI-optimized scheduling</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📅 Smart Schedule", key="smart_schedule", use_container_width=True):
            st.success("✅ AI analyzed your fleet - Optimal maintenance slots identified!")
            st.info("📍 Technician Ahmed Al-Rashid available tomorrow 10:00 AM (15km away)")
            st.info("🎯 Bundled service for 3 units saves $320 in travel costs")
    
    with col2:
        st.markdown("""
        <div class="parts-opportunity">
            <h4>🚨 Emergency Service</h4>
            <p>24/7 rapid response</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 Emergency Call", key="emergency_new", use_container_width=True, type="primary"):
            st.success("🚨 Emergency dispatch activated!")
            st.info("📞 Technician Omar Al-Harbi dispatched - ETA: 35 minutes")
            st.info("📍 GPS tracking: Vehicle #TK-205 en route")
    
    with col3:
        st.markdown("""
        <div class="customer-value">
            <h4>📦 Smart Parts Ordering</h4>
            <p>AI-recommended parts</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🛒 AI Parts Advisor", key="ai_parts", use_container_width=True):
            st.success("🛒 AI analyzed your fleet needs!")
            st.info("🎯 Recommended: Oil filters for 3 units due next month")
            st.info("💰 Bundle discount: Save 15% on preventive parts kit")
    
    with col4:
        st.markdown("""
        <div class="manufacturer-insights">
            <h4>🎓 Self-Help Diagnostics</h4>
            <p>Instant troubleshooting</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Run Diagnostics", key="self_diagnostics", use_container_width=True):
            st.success("🔍 Fleet diagnostics completed!")
            st.info("✅ All critical systems normal")
            st.info("⚠️ Generator PS-2021-0003: Check coolant level")
            st.info("💡 Tip: Monthly load bank tests improve reliability by 12%")
    
    # Enhanced self-help insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Intelligent Insights & Recommendations")
        
        # Fuel consumption analysis with predictions
        st.write("**⛽ Fuel Analytics & Optimization**")
        
        months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb']
        consumption = [1250, 1180, 1320, 1410, 1380, 1290]  # Liters
        predicted = [1320, 1280, 1240]  # Next 3 months prediction
        
        fuel_df = pd.DataFrame({
            'Month': months + ['Mar', 'Apr', 'May'],
            'Actual': consumption + [None, None, None],
            'Predicted': [None] * 6 + predicted
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=fuel_df['Month'][:6], y=fuel_df['Actual'][:6],
                                mode='lines+markers', name='Actual Consumption', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=fuel_df['Month'][5:], y=fuel_df['Predicted'][5:],
                                mode='lines+markers', name='AI Prediction', line=dict(color='orange', dash='dash')))
        
        fig.update_layout(title="Fuel Consumption Trends & AI Forecasting", height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # AI insights
        st.markdown("""
        **🎯 AI-Generated Insights:**
        - Your fleet is **8.3% more efficient** than industry average
        - Optimal refuel timing detected: Every 12 days for best pricing
        - Load balancing opportunity: Redistribute 15% load for 3% savings
        - Weather-adjusted consumption: +12% during summer months
        """)
        
        # Proactive maintenance suggestions
        st.write("**🔧 Proactive Maintenance Alerts:**")
        maintenance_alerts = [
            "🟡 **Generator PS-2021-0003:** Vibration trending up - Bearing inspection recommended",
            "🟠 **Generator PS-2020-0008:** Fuel quality alert - Consider premium fuel",
            "🟢 **Generator PS-2021-0001:** Performance optimized after recent service",
            "🔵 **Fleet-wide:** Load bank test due for 4 units next month"
        ]
        
        for alert in maintenance_alerts:
            st.markdown(alert)
    
    with col2:
        st.subheader("📊 Performance Analytics & Benchmarking")
        
        # Fleet performance comparison
        performance_metrics = {
            'Metric': ['Uptime %', 'Efficiency %', 'Response Time', 'Fuel Economy', 'Maintenance Cost'],
            'Your Fleet': [99.2, 93.1, '18 min', '8.2 L/hr', '$18,200'],
            'Industry Avg': [98.8, 91.4, '24 min', '8.9 L/hr', '$21,500'],
            'Performance': ['🟢 +0.4%', '🟢 +1.7%', '🟢 -25%', '🟢 +8%', '🟢 -15%']
        }
        
        perf_df = pd.DataFrame(performance_metrics)
        st.dataframe(perf_df, use_container_width=True, hide_index=True)
        
        # Cost breakdown with optimization opportunities
        st.write("**💰 Cost Analysis & Optimization:**")
        
        cost_categories = ['Fuel', 'Maintenance', 'Parts', 'Labor', 'Emergency']
        monthly_costs = [8500, 2200, 1400, 800, 300]
        
        fig2 = px.pie(values=monthly_costs, names=cost_categories,
                     title="Monthly Cost Breakdown")
        st.plotly_chart(fig2, use_container_width=True)
        
        # Optimization recommendations
        st.markdown("""
        **🎯 Cost Optimization Opportunities:**
        - **Fuel:** Switch to bulk purchasing - Save $340/month
        - **Maintenance:** Upgrade to Premium Care - Lock in rates, save $180/month  
        - **Parts:** Predictive replacement - Reduce emergency costs by 65%
        - **Efficiency:** Load optimization - Reduce fuel costs by 8-12%
        """)
    
    # Enhanced maintenance history with certificates
    st.subheader("📋 Maintenance History & Compliance")
    
    # Generate comprehensive maintenance history
    maintenance_history = []
    service_types = ['Oil Change', 'Filter Replacement', 'Full Service', 'Emergency Repair', 
                    'Load Bank Test', 'ATS Test', 'Diagnostic Check', 'PM Service']
    
    for i in range(12):
        service_date = datetime.now() - timedelta(days=random.randint(10, 300))
        
        maintenance_history.append({
            'Date': service_date.strftime('%Y-%m-%d'),
            'Generator': random.choice([gen['serial_number'] for _, gen in customer_generators.iterrows()]),
            'Service Type': random.choice(service_types),
            'Technician': random.choice(['Ahmed Al-Rashid', 'Mohammed Al-Saud', 'Khalid Al-Otaibi']),
            'Duration': f"{random.randint(2, 8)} hours",
            'Parts Used': random.choice(['Oil Filter, Oil', 'Air Filter', 'Belt Kit', 'Battery', 'Coolant', 'N/A']),
            'Cost': f"${random.randint(200, 1500)}",
            'Status': 'Completed',
            'Satisfaction': f"{random.randint(8, 10)}/10",
            'Certificate': '📄 Download',
            'Warranty': random.choice(['✅ Valid', '⚠️ Expires Soon', 'N/A'])
        })
    
    history_df = pd.DataFrame(maintenance_history)
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    # Compliance and reporting tools
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Generate Compliance Report", use_container_width=True):
            st.success("📊 Annual compliance report generated!")
            st.info("📧 Report emailed to: maintenance@{}.com".format(selected_customer.lower().replace(' ', '')))
    
    with col2:
        if st.button("📄 Download All Certificates", use_container_width=True):
            st.success("📄 Service certificates package ready!")
            st.info("🗃️ 24 certificates compiled in PDF format")
    
    with col3:
        if st.button("📈 Export Performance Data", use_container_width=True):
            st.success("📈 Performance data exported!")
            st.info("💾 Excel file with 12 months of operational data")
    
    with col4:
        if st.button("🔔 Configure Alerts", use_container_width=True):
            st.success("🔔 Alert preferences updated!")
            st.info("⚙️ Notifications customized for your fleet")
    
    # Proactive notification preferences
    with st.expander("🔔 Advanced Notification Preferences"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("**Critical Alerts:**")
            st.checkbox("📧 Email notifications", value=True, key="email_critical")
            st.checkbox("📱 SMS alerts", value=True, key="sms_critical")
            st.checkbox("📞 Phone calls", value=True, key="phone_critical")
            st.checkbox("🔔 Push notifications", value=False, key="push_critical")
        
        with col2:
            st.write("**Maintenance Reminders:**")
            st.checkbox("📅 Service due alerts (7 days)", value=True, key="service_alerts")
            st.checkbox("⛽ Fuel level warnings", value=True, key="fuel_alerts")
            st.checkbox("🔋 Battery status updates", value=True, key="battery_alerts")
            st.checkbox("📊 Weekly performance reports", value=True, key="weekly_reports")
        
        with col3:
            st.write("**Operational Updates:**")
            st.checkbox("🌡️ Temperature trend alerts", value=True, key="temp_alerts")
            st.checkbox("⚡ Efficiency drop notifications", value=True, key="efficiency_alerts")
            st.checkbox("🎯 Load bank test reminders", value=True, key="loadbank_alerts")
            st.checkbox("📈 Monthly analytics summary", value=True, key="monthly_analytics")
        
        if st.button("💾 Save All Preferences"):
            st.success("🔔 All notification preferences saved successfully!")
            st.info("📧 Confirmation email sent with your updated settings")

def main():
    """Main application."""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Initialize data
    load_manufacturer_data()
    
    # Authentication check
    if not st.session_state.authenticated:
        authenticate_manufacturer()
        return
    
    # Sidebar with role info
    st.sidebar.markdown(f"### {st.session_state.role_name}")
    st.sidebar.write("Power System Manufacturing Platform")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.role_name = None
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Role-based pages
    if st.session_state.user_role == "ceo@powersystem":
        pages = {
            "👔 CEO Dashboard": show_ceo_revenue_dashboard,
            "🗺️ Fleet Monitoring": show_fleet_monitoring_dashboard,
            "📊 Generator Specs": show_generator_specs_analysis,
            "🏢 Customer Portal": show_customer_portal
        }
    elif st.session_state.user_role == "sales@powersystem":
        pages = {
            "💰 Sales Dashboard": show_ceo_revenue_dashboard,
            "🗺️ Fleet Overview": show_fleet_monitoring_dashboard,
            "📊 Generator Analysis": show_generator_specs_analysis,
            "🏢 Customer Insights": show_customer_portal
        }
    elif st.session_state.user_role == "service@powersystem":
        pages = {
            "🔧 Service Operations": show_fleet_monitoring_dashboard,
            "📊 Specs & Maintenance": show_generator_specs_analysis,
            "🏢 Customer Management": show_customer_portal,
            "👔 Executive View": show_ceo_revenue_dashboard
        }
    else:  # customer@powersystem
        pages = {
            "🏢 My Dashboard": show_customer_portal,
            "📊 Performance Analytics": show_customer_portal,
            "🔧 Service & Support": show_customer_portal
        }
    
    selected_page = st.sidebar.selectbox("🧭 Navigate to:", list(pages.keys()))
    
    # Display selected page
    pages[selected_page]()
    
    # Sidebar footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Power System Manufacturing")
    st.sidebar.markdown("**Advanced IoT Platform**")
    st.sidebar.markdown("✅ Real-time Fleet Monitoring")
    st.sidebar.markdown("✅ Predictive Maintenance AI")
    st.sidebar.markdown("✅ Parts Sales Optimization")
    st.sidebar.markdown("✅ Service Revenue Growth")
    st.sidebar.markdown("✅ Customer Self-Service Portal")
    
    # Revenue targets
    targets = MANUFACTURER_CONFIG['revenue_targets']
    st.sidebar.markdown("### 🎯 Annual Targets")
    st.sidebar.write(f"Parts: ${targets['parts_annual']:,.0f}")
    st.sidebar.write(f"Service: ${targets['service_contracts']:,.0f}")
    st.sidebar.write(f"Total: ${(targets['parts_annual'] + targets['service_contracts']):,.0f}")

if __name__ == "__main__":
    main()
