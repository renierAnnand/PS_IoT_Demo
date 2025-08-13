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
    """Real-time fleet monitoring with comprehensive sensor data."""
    st.title("🗺️ Real-Time Fleet Monitoring Dashboard")
    st.markdown("### Live GPS Tracking & Advanced Sensor Analytics")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except:
        st.error("Please initialize data first")
        return
    
    # Fleet overview metrics
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
    
    # Enhanced Interactive Map
    st.subheader("🗺️ Live Fleet Map - GPS Tracking & Status")
    
    # Create comprehensive map data
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
        oil_pressure = random.uniform(25, 35)
        oil_temp = random.uniform(85, 105)
        coolant_temp = random.uniform(80, 100)
        vibration = random.uniform(1.5, 5.0)
        fuel_level = random.uniform(15, 90)
        
        # Health score calculation
        health_score = 100
        if oil_pressure < 28: health_score -= 15
        if oil_temp > 100: health_score -= 20
        if coolant_temp > 95: health_score -= 25
        if vibration > 4.0: health_score -= 30
        health_score = max(20, min(100, health_score))
        
        # Status determination
        if oil_pressure < 25 or coolant_temp > 100:
            color = [255, 0, 0, 180]
            status = "CRITICAL"
        elif oil_pressure < 28 or coolant_temp > 95 or vibration > 4.0:
            color = [255, 165, 0, 180]
            status = "WARNING"
        elif health_score > 85:
            color = [0, 255, 0, 160]
            status = "HEALTHY"
        else:
            color = [255, 255, 0, 160]
            status = "MONITOR"
        
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
    
    # Create PyDeck map
    map_df = pd.DataFrame(map_data)
    
    view_state = pdk.ViewState(latitude=24.7136, longitude=46.6753, zoom=6, pitch=45)
    
    layer = pdk.Layer(
        'ScatterplotLayer', data=map_df,
        get_position='[lon, lat]', get_color='color',
        get_radius='size', radius_scale=200, pickable=True
    )
    
    deck_map = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state, layers=[layer],
        tooltip={
            'text': '''{generator_id} - {status}
Customer: {customer}
Health Score: {health_score}%
Oil Pressure: {oil_pressure} PSI
Coolant Temp: {coolant_temp}°C
Vibration: {vibration} mm/s
Fuel Level: {fuel_level}%'''
        }
    )
    
    st.pydeck_chart(deck_map)
    
    # Smart Alerts Section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚨 Smart Alerts & Escalations")
        
        alerts = []
        for _, gen_data in map_df.iterrows():
            gen_id = gen_data['generator_id']
            
            if gen_data['oil_pressure'] < 25:
                alerts.append({
                    'Level': '🔴 CRITICAL',
                    'Generator': gen_id,
                    'Alert': f'Oil pressure critical: {gen_data["oil_pressure"]} PSI',
                    'Action': 'AUTO-SHUTDOWN',
                    'Time': f'{random.randint(1, 10)} min ago'
                })
            
            elif gen_data['oil_pressure'] < 28:
                alerts.append({
                    'Level': '🟠 WARNING',
                    'Generator': gen_id,
                    'Alert': f'Oil pressure low: {gen_data["oil_pressure"]} PSI',
                    'Action': 'MONITOR',
                    'Time': f'{random.randint(15, 60)} min ago'
                })
        
        if alerts:
            alerts_df = pd.DataFrame(alerts[:8])
            st.dataframe(alerts_df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No active alerts - All systems normal!")
        
        if st.button("🚨 Emergency Protocol"):
            st.success("Emergency protocols activated!")
    
    with col2:
        st.subheader("📊 Fleet Health Analytics")
        
        # Fleet averages
        avg_oil_pressure = map_df['oil_pressure'].mean()
        avg_coolant_temp = map_df['coolant_temp'].mean()
        avg_vibration = map_df['vibration'].mean()
        
        col_a, col_b = st.columns(2)
        with col_a:
            oil_status = "🟢" if avg_oil_pressure > 30 else "🟡" if avg_oil_pressure > 28 else "🔴"
            st.metric(f"Oil Pressure {oil_status}", f"{avg_oil_pressure:.1f} PSI")
            
            temp_status = "🟢" if avg_coolant_temp < 90 else "🟡" if avg_coolant_temp < 95 else "🔴"
            st.metric(f"Coolant Temp {temp_status}", f"{avg_coolant_temp:.1f}°C")
        
        with col_b:
            vib_status = "🟢" if avg_vibration < 3.5 else "🟡" if avg_vibration < 4.0 else "🔴"
            st.metric(f"Vibration {vib_status}", f"{avg_vibration:.2f} mm/s")
            
            health_status = "🟢" if avg_health_score > 90 else "🟡" if avg_health_score > 80 else "🔴"
            st.metric(f"Fleet Health {health_status}", f"{avg_health_score:.1f}%")
        
        # ML Predictions
        st.write("**🔮 ML Predictions (Next 30 Days):**")
        predictions = [
            {"Type": "Bearing Failure", "Units": 3, "Confidence": "87%"},
            {"Type": "Oil Degradation", "Units": 7, "Confidence": "92%"},
            {"Type": "Cooling Issues", "Units": 2, "Confidence": "78%"}
        ]
        pred_df = pd.DataFrame(predictions)
        st.dataframe(pred_df, use_container_width=True, hide_index=True)

def show_customer_portal():
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
    
    # Proactive notification
    if random.random() > 0.5:
        notification_types = [
            ("🟡", "Service Reminder", "Generator PS-2021-0003 is due for maintenance in 3 days"),
            ("🔴", "Critical Alert", "Low fuel detected on Generator PS-2020-0008 - 15% remaining"),
            ("🟢", "Success", "Preventive maintenance completed on Generator PS-2021-0001")
        ]
        icon, alert_type, message = random.choice(notification_types)
        
        if "Critical" in alert_type:
            st.error(f"{icon} **{alert_type}:** {message}")
        elif "Success" in alert_type:
            st.success(f"{icon} **{alert_type}:** {message}")
        else:
            st.info(f"{icon} **{alert_type}:** {message}")
    
    # Customer metrics with traffic light system
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_capacity = customer_generators['rated_kw'].sum()
    active_generators = len(customer_generators)
    avg_runtime = customer_generators['total_runtime_hours'].mean()
    
    # Calculate health indicators
    health_scores = [random.uniform(75, 98) for _ in customer_generators.iterrows()]
    avg_health = sum(health_scores) / len(health_scores)
    
    if avg_health > 90:
        health_color = "🟢"
        health_status = "Excellent"
    elif avg_health > 80:
        health_color = "🟡"
        health_status = "Good"
    else:
        health_color = "🔴"
        health_status = "Needs Attention"
    
    with col1:
        st.metric("Fleet Health", f"{health_color} {health_status}", delta=f"{avg_health:.1f}%")
    with col2:
        st.metric("Total Capacity", f"{total_capacity:,.0f} kW")
    with col3:
        st.metric("Active Units", active_generators)
    with col4:
        fuel_avg = random.uniform(30, 80)
        fuel_color = "🟢" if fuel_avg > 50 else "🟡" if fuel_avg > 30 else "🔴"
        st.metric("Fleet Fuel", f"{fuel_color} {fuel_avg:.0f}%")
    with col5:
        uptime = random.uniform(97.5, 99.8)
        uptime_color = "🟢" if uptime > 99 else "🟡"
        st.metric("Uptime", f"{uptime_color} {uptime:.1f}%")
    
    # Enhanced fleet status
    st.subheader("🔋 Your Generator Fleet - Live Status")
    
    fleet_data = []
    for _, gen in customer_generators.iterrows():
        fuel_level = random.uniform(15, 90)
        efficiency = random.uniform(82, 96)
        
        # Service status
        hours_to_service = gen['next_service_hours']
        if hours_to_service < 0:
            service_status = "🔴 Overdue"
        elif hours_to_service < 50:
            service_status = "🟠 Due Soon"
        else:
            service_status = "🟢 Current"
        
        # Health indicator
        health_score = random.uniform(75, 98)
        if health_score > 90:
            health_indicator = "🟢 Healthy"
        elif health_score > 80:
            health_indicator = "🟡 Monitor"
        else:
            health_indicator = "🔴 Critical"
        
        fleet_data.append({
            'Serial Number': gen['serial_number'],
            'Model': gen['model_series'],
            'Location': gen['location_city'],
            'Health': health_indicator,
            'Fuel Level': f"{fuel_level:.0f}%",
            'Efficiency': f"{efficiency:.1f}%",
            'Service Status': service_status,
            'Runtime': f"{gen['total_runtime_hours']:,} hrs"
        })
    
    fleet_df = pd.DataFrame(fleet_data)
    st.dataframe(fleet_df, use_container_width=True, hide_index=True)
    
    # One-click service requests
    st.subheader("🚀 One-Click Service Requests")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="service-upsell">
            <h4>🔧 Smart Schedule</h4>
            <p>AI-optimized maintenance</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📅 Schedule Service", use_container_width=True):
            st.success("✅ Service scheduled! Technician Ahmed available tomorrow.")
    
    with col2:
        st.markdown("""
        <div class="parts-opportunity">
            <h4>🚨 Emergency</h4>
            <p>24/7 rapid response</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 Emergency Call", use_container_width=True, type="primary"):
            st.success("🚨 Emergency dispatch! ETA: 35 minutes")
    
    with col3:
        st.markdown("""
        <div class="customer-value">
            <h4>📦 Smart Parts</h4>
            <p>AI recommendations</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🛒 Order Parts", use_container_width=True):
            st.success("🛒 AI analyzed your needs - Oil filters recommended!")
    
    with col4:
        st.markdown("""
        <div class="manufacturer-insights">
            <h4>🔍 Diagnostics</h4>
            <p>Self-help tools</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Run Check", use_container_width=True):
            st.success("🔍 Fleet check complete - All systems normal!")

def show_parts_planning():
    """Parts & Technician Planning dashboard."""
    st.title("🔧 Parts & Technician Planning")
    st.markdown("### Auto-Generated Work Orders & Resource Management")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except:
        st.error("Please initialize data first")
        return
    
    # Planning metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pending Work Orders", random.randint(15, 25))
    with col2:
        st.metric("Available Technicians", 8)
    with col3:
        st.metric("Parts Availability", f"{random.randint(85, 95)}%")
    with col4:
        st.metric("Avg Response Time", f"{random.uniform(2.5, 4.2):.1f} hrs")
    
    # Work orders
    st.subheader("🤖 Auto-Generated Work Orders")
    
    work_orders = []
    for i, (_, gen) in enumerate(generators_df.head(10).iterrows()):
        service_hours = gen['next_service_hours']
        
        if service_hours < 0:
            issue = "Scheduled Maintenance"
            priority = "High"
            parts = "Oil Filter, Air Filter, Oil"
            cost = 850
        elif service_hours < 50:
            issue = "Preventive Service"
            priority = "Medium"
            parts = "Oil Filter, Oil"
            cost = 450
        else:
            issue = "Diagnostic Check"
            priority = "Low"
            parts = "N/A"
            cost = 200
        
        technicians = ['Ahmed Al-Rashid', 'Mohammed Al-Saud', 'Khalid Al-Otaibi']
        assigned_tech = random.choice(technicians)
        
        work_orders.append({
            'WO #': f'WO-{2024120 + i}',
            'Generator': gen['serial_number'],
            'Customer': gen['customer_name'][:20] + "...",
            'Issue': issue,
            'Priority': priority,
            'Parts Needed': parts,
            'Est. Cost': f"${cost}",
            'Technician': assigned_tech,
            'Status': random.choice(['Pending', 'Scheduled', 'In Progress'])
        })
    
    work_orders_df = pd.DataFrame(work_orders)
    st.dataframe(work_orders_df, use_container_width=True, hide_index=True)
    
    # Parts and technician planning
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📦 Parts Requirements")
        
        parts_data = [
            {'Part': 'Oil Filter', 'Needed': 8, 'In Stock': 45, 'Status': '✅ Available'},
            {'Part': 'Air Filter', 'Needed': 5, 'In Stock': 32, 'Status': '✅ Available'},
            {'Part': 'Oil (20L)', 'Needed': 12, 'In Stock': 28, 'Status': '✅ Available'},
            {'Part': 'Belt Kit', 'Needed': 3, 'In Stock': 8, 'Status': '⚠️ Low Stock'},
            {'Part': 'Coolant', 'Needed': 4, 'In Stock': 15, 'Status': '✅ Available'}
        ]
        
        parts_df = pd.DataFrame(parts_data)
        st.dataframe(parts_df, use_container_width=True, hide_index=True)
        
        if st.button("📋 Generate Purchase Order"):
            st.success("Purchase order generated for low-stock items!")
    
    with col2:
        st.subheader("👷 Technician Assignment")
        
        tech_data = [
            {'Name': 'Ahmed Al-Rashid', 'Location': 'Riyadh', 'Status': '✅ Available', 'Jobs': 2},
            {'Name': 'Mohammed Al-Saud', 'Location': 'Jeddah', 'Status': '🟡 On Call', 'Jobs': 3},
            {'Name': 'Khalid Al-Otaibi', 'Location': 'Dammam', 'Status': '✅ Available', 'Jobs': 1},
            {'Name': 'Abdullah Al-Nasser', 'Location': 'NEOM', 'Status': '🔴 Travel', 'Jobs': 2}
        ]
        
        tech_df = pd.DataFrame(tech_data)
        st.dataframe(tech_df, use_container_width=True, hide_index=True)
        
        if st.button("🔄 Optimize Routes"):
            st.success("Routes optimized - 23% efficiency improvement!")

def show_generator_specs():
    """Generator specifications analysis."""
    st.title("📊 Generator Specifications Analysis")
    st.markdown("### GULFPOWER Baudouin Gensets Integration")
    
    # Baudouin specifications
    baudouin_models = {
        'Model': ['6M11G65/5', '6M16G115/5', '6M21G165/5', '6M26G220/5', '6M33G275/5'],
        'Power_kW': [65, 115, 165, 220, 275],
        'Fuel_Consumption_L_h': [19.5, 32.2, 45.8, 60.5, 75.2],
        'Service_Interval_Hours': [250, 250, 250, 500, 500],
        'Annual_Maintenance_Cost': [3200, 4800, 6500, 8500, 11000]
    }
    
    baudouin_df = pd.DataFrame(baudouin_models)
    
    st.subheader("🔧 Baudouin Generator Specifications")
    st.dataframe(baudouin_df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Power Range Analysis")
        fig = px.bar(baudouin_df, x='Model', y='Power_kW', title="Power Output by Model")
        fig.update_layout(height=300, xaxis_tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💰 Revenue Potential")
        
        revenue_data = []
        for _, model in baudouin_df.iterrows():
            annual_revenue = model['Annual_Maintenance_Cost'] * 1.5  # Include parts
            revenue_data.append({
                'Model': model['Model'],
                'Annual Revenue': f"${annual_revenue:,.0f}"
            })
        
        revenue_df = pd.DataFrame(revenue_data)
        st.dataframe(revenue_df, use_container_width=True, hide_index=True)

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
            "🔧 Parts Planning": show_parts_planning,
            "📊 Generator Specs": show_generator_specs,
            "🏢 Customer Portal": show_customer_portal
        }
    elif st.session_state.user_role == "sales@powersystem":
        pages = {
            "💰 Sales Dashboard": show_ceo_revenue_dashboard,
            "🗺️ Fleet Overview": show_fleet_monitoring_dashboard,
            "🔧 Parts Planning": show_parts_planning,
            "📊 Generator Analysis": show_generator_specs,
            "🏢 Customer Insights": show_customer_portal
        }
    elif st.session_state.user_role == "service@powersystem":
        pages = {
            "🔧 Service Operations": show_fleet_monitoring_dashboard,
            "🛠️ Parts Planning": show_parts_planning,
            "📊 Specs & Maintenance": show_generator_specs,
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
    st.sidebar.markdown("✅ Real-time Fleet Monitoring with GPS")
    st.sidebar.markdown("✅ Smart Alerts & Escalations")
    st.sidebar.markdown("✅ Auto Parts & Technician Planning")
    st.sidebar.markdown("✅ Predictive Maintenance AI")
    st.sidebar.markdown("✅ Enhanced Customer Portal")
    st.sidebar.markdown("✅ Proactive Notifications")
    
    # Revenue targets
    targets = MANUFACTURER_CONFIG['revenue_targets']
    st.sidebar.markdown("### 🎯 Annual Targets")
    st.sidebar.write(f"Parts: ${targets['parts_annual']:,.0f}")
    st.sidebar.write(f"Service: ${targets['service_contracts']:,.0f}")

if __name__ == "__main__":
    main()
