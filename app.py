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
import threading
from typing import Dict, List, Optional
from pathlib import Path
import random
import math

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
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
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

# Enhanced configuration for manufacturer focus
CONFIG_FILE = DATA_DIR / "config.json"
MANUFACTURER_CONFIG = {
    "company_name": "Power System Manufacturing",
    "refresh_seconds": 5,
    "demo_mode": "manufacturer",  # manufacturer, customer, technician
    "auto_scenarios": True,
    "parts_sales_ai": True,
    "service_optimization": True,
    "demo_speed": 1.0,
    "revenue_targets": {
        "parts_annual": 2500000,  # $2.5M annual parts revenue target
        "service_contracts": 1800000,  # $1.8M service revenue target
        "upsell_conversion": 0.25  # 25% upsell conversion rate
    },
    "parts_catalog": {
        "filters": {"oil": 150, "air": 85, "fuel": 120, "coolant": 200},
        "wear_parts": {"belts": 250, "hoses": 180, "gaskets": 95},
        "major_components": {"alternators": 3500, "control_panels": 2800, "cooling_systems": 4200},
        "consumables": {"oil_5l": 45, "coolant_10l": 85, "lubricants": 65}
    },
    "service_packages": {
        "basic_maintenance": {"price": 800, "margin": 0.35},
        "preventive_plus": {"price": 1500, "margin": 0.42},
        "premium_care": {"price": 2800, "margin": 0.48},
        "emergency_response": {"price": 1200, "margin": 0.55}
    },
    "customer_tiers": {
        "enterprise": {"discount": 0.15, "terms": "Net 30", "priority": "High"},
        "commercial": {"discount": 0.08, "terms": "Net 15", "priority": "Medium"},
        "small_business": {"discount": 0.05, "terms": "Net 10", "priority": "Standard"}
    }
}

def load_manufacturer_config() -> Dict:
    """Load manufacturer-specific configuration."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Merge with manufacturer defaults
            for key, value in MANUFACTURER_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    else:
        save_manufacturer_config(MANUFACTURER_CONFIG)
        return MANUFACTURER_CONFIG

def save_manufacturer_config(config: Dict):
    """Save manufacturer configuration."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def analyze_generator_specs():
    """Analyze uploaded generator specifications and integrate with platform."""
    st.title("📊 Generator Specifications Analysis")
    st.markdown("### GULFPOWER Baudouin Gensets Integration")
    
        try:
            # First check if file exists in the environment
            excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
            if excel_files:
                st.success(f"Found Excel file: {excel_files[0]}")
        except Exception as e:
            st.info("Excel file analysis not available in this environment.")
        
        # For demo purposes, create sample Baudouin generator data
            baudouin_models = {
                'Model': ['6M11G65/5', '6M16G115/5', '6M21G165/5', '6M26G220/5', '6M33G275/5', 
                         '12V26G440/5', '12V33G550/5', '16V26G605/5', '16V33G715/5'],
                'Power_kW': [65, 115, 165, 220, 275, 440, 550, 605, 715],
                'Engine_Type': ['6M11', '6M16', '6M21', '6M26', '6M33', '12V26', '12V33', '16V26', '16V33'],
                'Fuel_Consumption_L_h': [19.5, 32.2, 45.8, 60.5, 75.2, 118.8, 148.5, 163.4, 193.0],
                'Alternator_Type': ['Stamford', 'Stamford', 'Stamford', 'Leroy Somer', 'Leroy Somer', 
                                   'Leroy Somer', 'Leroy Somer', 'Mecc Alte', 'Mecc Alte'],
                'Control_Panel': ['DSE8610', 'DSE8610', 'DSE8610', 'DSE8620', 'DSE8620', 
                                 'DSE8620', 'DSE8620', 'DSE8660', 'DSE8660'],
                'ATS_Required': ['Manual', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto'],
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
                
                # Fuel efficiency comparison
                baudouin_df['Fuel_Efficiency'] = baudouin_df['Power_kW'] / baudouin_df['Fuel_Consumption_L_h']
                
                st.write("**Most Fuel Efficient Models:**")
                top_efficient = baudouin_df.nlargest(3, 'Fuel_Efficiency')[['Model', 'Fuel_Efficiency']]
                top_efficient['Fuel_Efficiency'] = top_efficient['Fuel_Efficiency'].round(2)
                st.dataframe(top_efficient, hide_index=True, use_container_width=True)
            
            with col2:
                st.subheader("💰 Maintenance Cost Analysis")
                fig2 = px.scatter(baudouin_df, x='Power_kW', y='Maintenance_Cost_Annual',
                                size='Parts_Cost_Per_Service', title="Maintenance Cost vs Power",
                                labels={'Power_kW': 'Power (kW)', 'Maintenance_Cost_Annual': 'Annual Cost ($)'})
                fig2.update_layout(height=300)
                st.plotly_chart(fig2, use_container_width=True)
                
                # Revenue potential calculation
                st.write("**Annual Revenue Potential per Model:**")
                
                revenue_potential = []
                for _, model in baudouin_df.iterrows():
                    # Calculate based on service frequency and parts
                    services_per_year = 8760 / model['Service_Interval_Hours']  # 8760 hours in a year
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
            
            # Integration opportunities
            st.subheader("🎯 Integration Opportunities")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="parts-opportunity">
                    <h4>🔧 Parts Optimization</h4>
                    <ul>
                        <li><strong>Predictive Stocking:</strong> Based on service intervals</li>
                        <li><strong>Bulk Discounts:</strong> Volume pricing for customers</li>
                        <li><strong>Emergency Kits:</strong> Critical parts packages</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="service-upsell">
                    <h4>📅 Service Scheduling</h4>
                    <ul>
                        <li><strong>Auto-scheduling:</strong> Based on hour meter readings</li>
                        <li><strong>Route optimization:</strong> Efficient technician deployment</li>
                        <li><strong>Preventive alerts:</strong> 50 hours before due</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="customer-value">
                    <h4>💡 Upsell Opportunities</h4>
                    <ul>
                        <li><strong>Extended warranties:</strong> Beyond standard coverage</li>
                        <li><strong>Performance packages:</strong> Efficiency monitoring</li>
                        <li><strong>Training programs:</strong> Customer education</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            # Maintenance schedule integration
            st.subheader("📋 Integrated Maintenance Schedule")
            
            # Create comprehensive maintenance matrix
            maintenance_matrix = []
            
            for _, model in baudouin_df.iterrows():
                interval = model['Service_Interval_Hours']
                
                # Calculate maintenance schedule
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
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("📊 Generate Fleet Analysis Report"):
                    st.success("Fleet analysis report generated and saved!")
            
            with col2:
                if st.button("📅 Auto-Schedule All Services"):
                    st.success("All services automatically scheduled based on specifications!")
            
            with col3:
                if st.button("💰 Calculate Revenue Projections"):
                    st.success("Revenue projections calculated for next 12 months!")
                    
        else:
            st.info("No Excel files found. Using sample Baudouin generator data for demonstration.")
            
    except Exception as e:
def load_manufacturer_data():
    """Load manufacturer-specific seed data."""
    
    # Enhanced Generators with manufacturer focus
    generators_file = DATA_DIR / "generators.csv"
    if not generators_file.exists():
        generators_data = {
            'serial_number': [f'PS-{2020 + i//4}-{i:04d}' for i in range(1, 31)],  # Power System serial numbers
            'model_series': ([
                'PS-2000 Series', 'PS-1500 Series', 'PS-1000 Series', 'PS-800 Series',
                'PS-2500 Industrial', 'PS-2000 Commercial', 'PS-1800 Healthcare', 'PS-1200 Retail'
            ] * 4)[:30],  # Ensure exactly 30 items
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
            'installation_date': [
                '2020-01-15', '2020-03-20', '2019-08-10', '2021-02-14',
                '2020-06-18', '2021-09-25', '2019-12-05', '2022-01-30',
                '2020-04-12', '2021-07-08', '2019-10-22', '2020-11-15',
                '2021-03-30', '2022-05-18', '2020-09-12', '2021-06-25',
                '2019-07-14', '2020-12-08', '2021-08-20', '2022-02-10',
                '2020-05-25', '2021-04-12', '2019-11-30', '2020-10-18',
                '2021-01-22', '2022-03-15', '2020-08-05', '2021-12-12',
                '2019-09-28', '2020-07-20'
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
            ],
            'industry_segment': [
                'Healthcare', 'Retail', 'Industrial', 'Corporate', 'Banking', 'Technology',
                'Construction', 'Tourism', 'Aviation', 'Education', 'Government', 'Government',
                'Government', 'Healthcare', 'Government', 'Finance', 'Entertainment', 'Infrastructure',
                'Environment', 'Real Estate', 'Energy', 'Urban Development', 'Industrial', 'Entertainment',
                'Tourism', 'Entertainment', 'Sports', 'Mixed Use', 'Tourism', 'Entertainment'
            ],
            'annual_fuel_cost': [random.randint(25000, 180000) for _ in range(30)],
            'maintenance_spend_ytd': [random.randint(8000, 65000) for _ in range(30)]
        }
        pd.DataFrame(generators_data).to_csv(generators_file, index=False)
    
    # Parts inventory and sales data
    parts_sales_file = DATA_DIR / "parts_sales.csv"
    if not parts_sales_file.exists():
        parts_data = []
        config = load_manufacturer_config()
        
        # Generate realistic parts sales history
        for i in range(200):  # 200 parts sales records
            sale_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            # Select random part category and item
            categories = list(config['parts_catalog'].keys())
            category = random.choice(categories)
            parts_in_category = list(config['parts_catalog'][category].keys())
            part_name = random.choice(parts_in_category)
            unit_price = config['parts_catalog'][category][part_name]
            
            # Realistic quantity based on part type
            if category == 'major_components':
                quantity = random.randint(1, 2)
            elif category == 'consumables':
                quantity = random.randint(2, 10)
            else:
                quantity = random.randint(1, 4)
            
            parts_data.append({
                'sale_id': f'PS-{sale_date.strftime("%Y%m")}-{i:04d}',
                'sale_date': sale_date.strftime('%Y-%m-%d'),
                'generator_serial': f'PS-{random.randint(2019, 2022)}-{random.randint(1, 30):04d}',
                'part_category': category,
                'part_name': part_name,
                'part_number': f'PN-{random.randint(10000, 99999)}',
                'quantity': quantity,
                'unit_price': unit_price,
                'total_amount': unit_price * quantity,
                'margin_pct': random.uniform(0.25, 0.55),
                'customer_tier': random.choice(['Enterprise', 'Commercial', 'Small Business']),
                'sales_channel': random.choice(['Direct', 'Distributor', 'Online Portal', 'Field Service']),
                'urgency': random.choice(['Routine', 'Urgent', 'Emergency']),
                'warranty_claim': random.choice([True, False]) if random.random() < 0.15 else False
            })
        
        pd.DataFrame(parts_data).to_csv(parts_sales_file, index=False)
    
    # Service revenue tracking
    service_revenue_file = DATA_DIR / "service_revenue.csv"
    if not service_revenue_file.exists():
        service_data = []
        
        for i in range(150):  # 150 service records
            service_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            service_types = ['Basic Maintenance', 'Preventive Plus', 'Premium Care', 'Emergency Response', 'Diagnostic', 'Repair']
            service_type = random.choice(service_types)
            
            # Base pricing
            base_prices = {
                'Basic Maintenance': 800, 'Preventive Plus': 1500, 'Premium Care': 2800,
                'Emergency Response': 1200, 'Diagnostic': 400, 'Repair': 950
            }
            
            base_price = base_prices.get(service_type, 800)
            # Add complexity factor
            complexity_multiplier = random.uniform(0.8, 2.2)
            total_amount = base_price * complexity_multiplier
            
            service_data.append({
                'service_id': f'SRV-{service_date.strftime("%Y%m")}-{i:04d}',
                'service_date': service_date.strftime('%Y-%m-%d'),
                'generator_serial': f'PS-{random.randint(2019, 2022)}-{random.randint(1, 30):04d}',
                'service_type': service_type,
                'technician_id': f'TECH-{random.randint(100, 999)}',
                'labor_hours': random.uniform(2, 16),
                'parts_used_value': random.randint(0, 1500) if random.random() < 0.7 else 0,
                'total_amount': total_amount,
                'margin_pct': random.uniform(0.30, 0.60),
                'customer_satisfaction': random.randint(7, 10),
                'contract_type': random.choice(['Warranty', 'Service Contract', 'Pay-per-service', 'Emergency']),
                'response_time_hours': random.uniform(0.5, 48),
                'upsell_opportunity': random.choice([True, False]) if random.random() < 0.3 else False,
                'follow_up_needed': random.choice([True, False]) if random.random() < 0.2 else False
            })
        
        pd.DataFrame(service_data).to_csv(service_revenue_file, index=False)

def analyze_generator_specs():
    """Analyze uploaded generator specifications and integrate with platform."""
    st.title("📊 Generator Specifications Analysis")
    st.markdown("### GULFPOWER Baudouin Gensets Integration")
    
    # Try to read the uploaded file
    try:
        # First check if file exists in the environment
        excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx')]
        if excel_files:
            st.success(f"Found Excel file: {excel_files[0]}")
            
            # For demo purposes, create sample Baudouin generator data
        baudouin_models = {
            'Model': ['6M11G65/5', '6M16G115/5', '6M21G165/5', '6M26G220/5', '6M33G275/5', 
                     '12V26G440/5', '12V33G550/5', '16V26G605/5', '16V33G715/5'],
            'Power_kW': [65, 115, 165, 220, 275, 440, 550, 605, 715],
            'Engine_Type': ['6M11', '6M16', '6M21', '6M26', '6M33', '12V26', '12V33', '16V26', '16V33'],
            'Fuel_Consumption_L_h': [19.5, 32.2, 45.8, 60.5, 75.2, 118.8, 148.5, 163.4, 193.0],
            'Alternator_Type': ['Stamford', 'Stamford', 'Stamford', 'Leroy Somer', 'Leroy Somer', 
                               'Leroy Somer', 'Leroy Somer', 'Mecc Alte', 'Mecc Alte'],
            'Control_Panel': ['DSE8610', 'DSE8610', 'DSE8610', 'DSE8620', 'DSE8620', 
                             'DSE8620', 'DSE8620', 'DSE8660', 'DSE8660'],
            'ATS_Required': ['Manual', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto', 'Auto'],
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
            
            # Fuel efficiency comparison
            baudouin_df['Fuel_Efficiency'] = baudouin_df['Power_kW'] / baudouin_df['Fuel_Consumption_L_h']
            
            st.write("**Most Fuel Efficient Models:**")
            top_efficient = baudouin_df.nlargest(3, 'Fuel_Efficiency')[['Model', 'Fuel_Efficiency']]
            top_efficient['Fuel_Efficiency'] = top_efficient['Fuel_Efficiency'].round(2)
            st.dataframe(top_efficient, hide_index=True, use_container_width=True)
        
        with col2:
            st.subheader("💰 Maintenance Cost Analysis")
            fig2 = px.scatter(baudouin_df, x='Power_kW', y='Maintenance_Cost_Annual',
                            size='Parts_Cost_Per_Service', title="Maintenance Cost vs Power",
                            labels={'Power_kW': 'Power (kW)', 'Maintenance_Cost_Annual': 'Annual Cost ($)'})
            fig2.update_layout(height=300)
            st.plotly_chart(fig2, use_container_width=True)
            
            # Revenue potential calculation
            st.write("**Annual Revenue Potential per Model:**")
            
            revenue_potential = []
            for _, model in baudouin_df.iterrows():
                # Calculate based on service frequency and parts
                services_per_year = 8760 / model['Service_Interval_Hours']  # 8760 hours in a year
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
        
        # Integration opportunities
        st.subheader("🎯 Integration Opportunities")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="parts-opportunity">
                <h4>🔧 Parts Optimization</h4>
                <ul>
                    <li><strong>Predictive Stocking:</strong> Based on service intervals</li>
                    <li><strong>Bulk Discounts:</strong> Volume pricing for customers</li>
                    <li><strong>Emergency Kits:</strong> Critical parts packages</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="service-upsell">
                <h4>📅 Service Scheduling</h4>
                <ul>
                    <li><strong>Auto-scheduling:</strong> Based on hour meter readings</li>
                    <li><strong>Route optimization:</strong> Efficient technician deployment</li>
                    <li><strong>Preventive alerts:</strong> 50 hours before due</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="customer-value">
                <h4>💡 Upsell Opportunities</h4>
                <ul>
                    <li><strong>Extended warranties:</strong> Beyond standard coverage</li>
                    <li><strong>Performance packages:</strong> Efficiency monitoring</li>
                    <li><strong>Training programs:</strong> Customer education</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Maintenance schedule integration
        st.subheader("📋 Integrated Maintenance Schedule")
        
        # Create comprehensive maintenance matrix
        maintenance_matrix = []
        
        for _, model in baudouin_df.iterrows():
            interval = model['Service_Interval_Hours']
            
            # Calculate maintenance schedule
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
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generate Fleet Analysis Report"):
                st.success("Fleet analysis report generated and saved!")
        
        with col2:
            if st.button("📅 Auto-Schedule All Services"):
                st.success("All services automatically scheduled based on specifications!")
        
        with col3:
            if st.button("💰 Calculate Revenue Projections"):
                st.success("Revenue projections calculated for next 12 months!")
    """Load manufacturer-specific seed data."""
    
    # Enhanced Generators with manufacturer focus
    generators_file = DATA_DIR / "generators.csv"
    if not generators_file.exists():
        generators_data = {
            'serial_number': [f'PS-{2020 + i//4}-{i:04d}' for i in range(1, 31)],  # Power System serial numbers
            'model_series': ([
                'PS-2000 Series', 'PS-1500 Series', 'PS-1000 Series', 'PS-800 Series',
                'PS-2500 Industrial', 'PS-2000 Commercial', 'PS-1800 Healthcare', 'PS-1200 Retail'
            ] * 4)[:30],  # Ensure exactly 30 items
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
            'installation_date': [
                '2020-01-15', '2020-03-20', '2019-08-10', '2021-02-14',
                '2020-06-18', '2021-09-25', '2019-12-05', '2022-01-30',
                '2020-04-12', '2021-07-08', '2019-10-22', '2020-11-15',
                '2021-03-30', '2022-05-18', '2020-09-12', '2021-06-25',
                '2019-07-14', '2020-12-08', '2021-08-20', '2022-02-10',
                '2020-05-25', '2021-04-12', '2019-11-30', '2020-10-18',
                '2021-01-22', '2022-03-15', '2020-08-05', '2021-12-12',
                '2019-09-28', '2020-07-20'
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
            ],
            'industry_segment': [
                'Healthcare', 'Retail', 'Industrial', 'Corporate', 'Banking', 'Technology',
                'Construction', 'Tourism', 'Aviation', 'Education', 'Government', 'Government',
                'Government', 'Healthcare', 'Government', 'Finance', 'Entertainment', 'Infrastructure',
                'Environment', 'Real Estate', 'Energy', 'Urban Development', 'Industrial', 'Entertainment',
                'Tourism', 'Entertainment', 'Sports', 'Mixed Use', 'Tourism', 'Entertainment'
            ],
            'annual_fuel_cost': [random.randint(25000, 180000) for _ in range(30)],
            'maintenance_spend_ytd': [random.randint(8000, 65000) for _ in range(30)]
        }
        pd.DataFrame(generators_data).to_csv(generators_file, index=False)
    
    # Parts inventory and sales data
    parts_sales_file = DATA_DIR / "parts_sales.csv"
    if not parts_sales_file.exists():
        parts_data = []
        config = load_manufacturer_config()
        
        # Generate realistic parts sales history
        for i in range(200):  # 200 parts sales records
            sale_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            # Select random part category and item
            categories = list(config['parts_catalog'].keys())
            category = random.choice(categories)
            parts_in_category = list(config['parts_catalog'][category].keys())
            part_name = random.choice(parts_in_category)
            unit_price = config['parts_catalog'][category][part_name]
            
            # Realistic quantity based on part type
            if category == 'major_components':
                quantity = random.randint(1, 2)
            elif category == 'consumables':
                quantity = random.randint(2, 10)
            else:
                quantity = random.randint(1, 4)
            
            parts_data.append({
                'sale_id': f'PS-{sale_date.strftime("%Y%m")}-{i:04d}',
                'sale_date': sale_date.strftime('%Y-%m-%d'),
                'generator_serial': f'PS-{random.randint(2019, 2022)}-{random.randint(1, 30):04d}',
                'part_category': category,
                'part_name': part_name,
                'part_number': f'PN-{random.randint(10000, 99999)}',
                'quantity': quantity,
                'unit_price': unit_price,
                'total_amount': unit_price * quantity,
                'margin_pct': random.uniform(0.25, 0.55),
                'customer_tier': random.choice(['Enterprise', 'Commercial', 'Small Business']),
                'sales_channel': random.choice(['Direct', 'Distributor', 'Online Portal', 'Field Service']),
                'urgency': random.choice(['Routine', 'Urgent', 'Emergency']),
                'warranty_claim': random.choice([True, False]) if random.random() < 0.15 else False
            })
        
        pd.DataFrame(parts_data).to_csv(parts_sales_file, index=False)
    
    # Service revenue tracking
    service_revenue_file = DATA_DIR / "service_revenue.csv"
    if not service_revenue_file.exists():
        service_data = []
        
        for i in range(150):  # 150 service records
            service_date = datetime.now() - timedelta(days=random.randint(1, 365))
            
            service_types = ['Basic Maintenance', 'Preventive Plus', 'Premium Care', 'Emergency Response', 'Diagnostic', 'Repair']
            service_type = random.choice(service_types)
            
            # Base pricing
            base_prices = {
                'Basic Maintenance': 800, 'Preventive Plus': 1500, 'Premium Care': 2800,
                'Emergency Response': 1200, 'Diagnostic': 400, 'Repair': 950
            }
            
            base_price = base_prices.get(service_type, 800)
            # Add complexity factor
            complexity_multiplier = random.uniform(0.8, 2.2)
            total_amount = base_price * complexity_multiplier
            
            service_data.append({
                'service_id': f'SRV-{service_date.strftime("%Y%m")}-{i:04d}',
                'service_date': service_date.strftime('%Y-%m-%d'),
                'generator_serial': f'PS-{random.randint(2019, 2022)}-{random.randint(1, 30):04d}',
                'service_type': service_type,
                'technician_id': f'TECH-{random.randint(100, 999)}',
                'labor_hours': random.uniform(2, 16),
                'parts_used_value': random.randint(0, 1500) if random.random() < 0.7 else 0,
                'total_amount': total_amount,
                'margin_pct': random.uniform(0.30, 0.60),
                'customer_satisfaction': random.randint(7, 10),
                'contract_type': random.choice(['Warranty', 'Service Contract', 'Pay-per-service', 'Emergency']),
                'response_time_hours': random.uniform(0.5, 48),
                'upsell_opportunity': random.choice([True, False]) if random.random() < 0.3 else False,
                'follow_up_needed': random.choice([True, False]) if random.random() < 0.2 else False
            })
        
        pd.DataFrame(service_data).to_csv(service_revenue_file, index=False)

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

def show_fleet_monitoring_dashboard():
    """Real-time fleet monitoring with GPS tracking and sensor data."""
    st.title("🗺️ Real-Time Fleet Monitoring")
    st.markdown("### Live GPS Tracking & Health Monitoring")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except Exception:
        st.error("Loading sample data...")
        return
    
    # Fleet overview metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    online_count = len(generators_df[generators_df['warranty_status'] == 'Active'])
    critical_alerts = random.randint(2, 8)
    service_due = len(generators_df[generators_df['next_service_hours'] < 100])
    
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
    
    # Interactive map with generator locations
    st.subheader("🗺️ Live Fleet Map")
    
    # Create map data with random coordinates around Saudi Arabia
    map_data = []
    cities = {
        'Riyadh': (24.7136, 46.6753),
        'Jeddah': (21.4858, 39.1925),
        'Dammam': (26.4207, 50.0888),
        'NEOM': (28.2654, 35.3254),
        'Al-Ula': (26.6084, 37.9218),
        'Qiddiya': (24.6500, 46.1667)
    }
    
    for _, gen in generators_df.iterrows():
        city = gen['location_city']
        base_lat, base_lon = cities.get(city, cities['Riyadh'])
        
        # Add some random offset for realistic distribution
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
        
        # Health status based on various factors
        health_score = random.randint(75, 98)
        if health_score > 90:
            color = [0, 255, 0, 160]  # Green
            status = "Healthy"
        elif health_score > 80:
            color = [255, 255, 0, 160]  # Yellow
            status = "Monitor"
        else:
            color = [255, 0, 0, 160]  # Red
            status = "Critical"
        
        map_data.append({
            'lat': lat,
            'lon': lon,
            'generator_id': gen['serial_number'],
            'customer': gen['customer_name'],
            'health_score': health_score,
            'status': status,
            'color': color,
            'size': gen['rated_kw'] / 100  # Size based on capacity
        })
    
    # Create PyDeck map
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
        tooltip={'text': '{generator_id}\n{customer}\nHealth: {health_score}%\nStatus: {status}'}
    )
    
    st.pydeck_chart(deck_map)
    
    # Real-time sensor data
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Critical Sensor Alerts")
        
        # Generate realistic sensor alerts
        sensor_alerts = [
            {
                'Generator': 'PS-2021-0001',
                'Alert': 'Oil Pressure Low',
                'Current': '28 PSI',
                'Threshold': '30 PSI',
                'Severity': '🟡 Warning',
                'Time': '2 mins ago'
            },
            {
                'Generator': 'PS-2020-0005',
                'Alert': 'Coolant Temp High',
                'Current': '98°C',
                'Threshold': '95°C',
                'Severity': '🔴 Critical',
                'Time': '5 mins ago'
            },
            {
                'Generator': 'PS-2021-0012',
                'Alert': 'Vibration Elevated',
                'Current': '4.2 mm/s',
                'Threshold': '4.0 mm/s',
                'Severity': '🟡 Warning',
                'Time': '8 mins ago'
            },
            {
                'Generator': 'PS-2020-0008',
                'Alert': 'Fuel Level Low',
                'Current': '15%',
                'Threshold': '20%',
                'Severity': '🟠 Urgent',
                'Time': '12 mins ago'
            }
        ]
        
        alerts_df = pd.DataFrame(sensor_alerts)
        st.dataframe(alerts_df, use_container_width=True, hide_index=True)
        
        # Quick action buttons
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚨 Dispatch Emergency Team"):
                st.success("Emergency technician dispatched to PS-2020-0005!")
        with col_b:
            if st.button("📧 Notify All Customers"):
                st.success("Proactive notifications sent!")
    
    with col2:
        st.subheader("📊 Fleet Health Overview")
        
        # Health distribution
        health_data = {
            'Status': ['Healthy', 'Monitor', 'Critical', 'Offline'],
            'Count': [
                len([g for g in map_data if g['health_score'] > 90]),
                len([g for g in map_data if 80 < g['health_score'] <= 90]),
                len([g for g in map_data if g['health_score'] <= 80]),
                random.randint(0, 3)
            ]
        }
        
        fig = px.pie(health_data, values='Count', names='Status',
                    title="Fleet Health Distribution",
                    color_discrete_map={
                        'Healthy': '#2ed573',
                        'Monitor': '#ffa726', 
                        'Critical': '#ff6b6b',
                        'Offline': '#6c757d'
                    })
        st.plotly_chart(fig, use_container_width=True)

def show_predictive_maintenance_engine():
    """Advanced predictive maintenance with ML insights."""
    st.title("🔮 Predictive Maintenance Engine")
    st.markdown("### AI-Powered Failure Prediction & Prevention")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
    except Exception:
        st.error("Loading sample data...")
        return
    
    # ML Model performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="service-upsell">
            <h3>Bearing Failure Model</h3>
            <h1>94.2%</h1>
            <p>Prediction Accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="parts-opportunity">
            <h3>Oil Analysis Model</h3>
            <h1>91.8%</h1>
            <p>Prediction Accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="customer-value">
            <h3>Coolant System Model</h3>
            <h1>89.5%</h1>
            <p>Prediction Accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        prevented_failures = random.randint(15, 25)
        st.metric("Failures Prevented", prevented_failures, delta="This quarter")
    
    # Maintenance schedule based on the checklist
    st.subheader("📅 Smart Maintenance Scheduling")
    
    maintenance_schedule = {
        'Daily': ['Check fuel levels', 'Inspect for leaks', 'Check warning indicators', 'Listen for unusual noises'],
        'Weekly': ['Run generator 10-15 minutes', 'Inspect oil levels', 'Check coolant levels', 'Clean air filters', 'Test battery voltage'],
        'Monthly': ['Check battery terminals', 'Inspect belts and hoses', 'Check exhaust system', 'Test load bank'],
        'Quarterly': ['Change oil and oil filter', 'Flush and replace coolant', 'Inspect electrical connections', 'Lubricate moving parts'],
        'Annual': ['Full system inspection', 'Replace fuel filters', 'Test automatic transfer switch', 'Professional servicing']
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🎯 High-Priority Predictions**")
        
        predictions = [
            {
                'Generator': 'PS-2020-0003',
                'Prediction': 'Bearing Failure',
                'Confidence': '87%',
                'Time to Failure': '18 days',
                'Action': 'Schedule bearing replacement',
                'Cost Savings': '$15,000'
            },
            {
                'Generator': 'PS-2021-0007',
                'Prediction': 'Oil Degradation',
                'Confidence': '92%',
                'Time to Failure': '12 days',
                'Action': 'Oil change and analysis',
                'Cost Savings': '$8,500'
            },
            {
                'Generator': 'PS-2020-0011',
                'Prediction': 'Coolant System Issue',
                'Confidence': '85%',
                'Time to Failure': '25 days',
                'Action': 'Coolant flush and inspection',
                'Cost Savings': '$12,000'
            }
        ]
        
        pred_df = pd.DataFrame(predictions)
        st.dataframe(pred_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**📊 Sensor Trend Analysis**")
        
        # Simulate sensor trend data
        days = list(range(1, 31))
        oil_pressure = [30 + random.uniform(-2, 2) + (i * -0.1) for i in days]  # Declining trend
        coolant_temp = [85 + random.uniform(-3, 3) + (i * 0.05) for i in days]  # Rising trend
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=days, y=oil_pressure, mode='lines', name='Oil Pressure (PSI)', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=days, y=coolant_temp, mode='lines', name='Coolant Temp (°C)', line=dict(color='red')))
        
        # Add threshold lines
        fig.add_hline(y=25, line_dash="dash", line_color="blue", annotation_text="Oil Pressure Min")
        fig.add_hline(y=95, line_dash="dash", line_color="red", annotation_text="Coolant Temp Max")
        
        fig.update_layout(title="30-Day Sensor Trends", height=300)
        st.plotly_chart(fig, use_container_width=True)

def show_smart_alerts_system():
    """Smart alerts and escalation management."""
    st.title("🚨 Smart Alerts & Escalation System")
    st.markdown("### Tiered Notifications & Automated Responses")
    
    # Alert categories and counts
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="alert-revenue">
            <h3>Critical Alerts</h3>
            <h1>3</h1>
            <p>Immediate shutdown required</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="parts-opportunity">
            <h3>Warning Alerts</h3>
            <h1>8</h1>
            <p>Trending toward danger</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="service-upsell">
            <h3>Routine Alerts</h3>
            <h1>15</h1>
            <p>Scheduled maintenance</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.metric("Response Time", "4.2 min", delta="Target: <5 min")
    
    # Live alert feed
    st.subheader("⚡ Live Alert Feed")
    
    # Generate realistic alert stream
    current_time = datetime.now()
    alerts = []
    
    alert_types = [
        ('🔴 CRITICAL', 'Engine shutdown - Oil pressure lost', 'PS-2020-0005', '30 seconds ago'),
        ('🟠 WARNING', 'Coolant temperature rising', 'PS-2021-0008', '2 minutes ago'),
        ('🟡 ROUTINE', 'Service due in 50 hours', 'PS-2020-0012', '5 minutes ago'),
        ('🔴 CRITICAL', 'Fuel leak detected', 'PS-2021-0003', '8 minutes ago'),
        ('🟠 WARNING', 'Vibration levels elevated', 'PS-2020-0009', '12 minutes ago'),
        ('🟡 ROUTINE', 'Battery voltage low', 'PS-2021-0015', '15 minutes ago'),
        ('🟠 WARNING', 'Air filter restriction high', 'PS-2020-0007', '18 minutes ago'),
        ('🟡 ROUTINE', 'Load bank test due', 'PS-2021-0011', '22 minutes ago')
    ]
    
    for severity, message, generator, time_ago in alert_types:
        alerts.append({
            'Severity': severity,
            'Message': message,
            'Generator': generator,
            'Time': time_ago,
            'Status': 'NEW' if 'CRITICAL' in severity else 'OPEN',
            'Action': 'Auto-dispatch' if 'CRITICAL' in severity else 'Monitor'
        })
    
    alerts_df = pd.DataFrame(alerts)
    st.dataframe(alerts_df, use_container_width=True, hide_index=True)
    
    # Alert automation settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚙️ Automation Rules")
        
        st.write("**Critical Alert Actions:**")
        st.checkbox("✅ Auto-dispatch emergency technician", value=True)
        st.checkbox("✅ Notify customer immediately", value=True)
        st.checkbox("✅ Create high-priority work order", value=True)
        st.checkbox("✅ Escalate to on-call manager", value=True)
        
        st.write("**Warning Alert Actions:**")
        st.checkbox("📧 Send email notification", value=True)
        st.checkbox("📱 SMS to service coordinator", value=True)
        st.checkbox("📅 Schedule preventive maintenance", value=True)
        
        if st.button("💾 Save Automation Rules"):
            st.success("Automation rules updated!")
    
    with col2:
        st.subheader("📊 Alert Response Analytics")
        
        # Response time trends
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        response_times = [random.uniform(2, 8) for _ in days]
        
        fig = px.bar(x=days, y=response_times, title="Average Response Time by Day")
        fig.add_hline(y=5, line_dash="dash", line_color="red", annotation_text="Target: 5 min")
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        # Alert resolution stats
        resolution_data = {
            'Resolution Type': ['Auto-Resolved', 'Tech Dispatch', 'Customer Action', 'Escalated'],
            'Count': [12, 8, 5, 2]
        }
        
        fig2 = px.pie(resolution_data, values='Count', names='Resolution Type',
                     title="Alert Resolution Methods")
        st.plotly_chart(fig2, use_container_width=True)

def show_ceo_revenue_dashboard():
    """CEO-focused revenue and growth analytics dashboard."""
    st.title("👔 CEO Revenue Dashboard")
    st.markdown("### Strategic Overview: After-Sales Revenue Performance")
    
    # Load manufacturer data
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
        parts_sales_df = pd.read_csv(DATA_DIR / "parts_sales.csv")
        service_revenue_df = pd.read_csv(DATA_DIR / "service_revenue.csv")
    except Exception:
        st.error("Loading sample data...")
        return
    
    config = load_manufacturer_config()
    
    # Executive KPIs
    st.subheader("💰 Revenue Performance")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Calculate key metrics
    parts_revenue_ytd = parts_sales_df['total_amount'].sum()
    service_revenue_ytd = service_revenue_df['total_amount'].sum()
    total_after_sales = parts_revenue_ytd + service_revenue_ytd
    
    # Targets
    parts_target = config['revenue_targets']['parts_annual']
    service_target = config['revenue_targets']['service_contracts']
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
    
    # Calculate average margins
    parts_margin = parts_sales_df['margin_pct'].mean() * 100
    service_margin = service_revenue_df['margin_pct'].mean() * 100
    
    with col4:
        st.markdown(f"""
        <div class="customer-value">
            <h3>Avg Parts Margin</h3>
            <h1>{parts_margin:.1f}%</h1>
            <p>Industry target: 40%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="manufacturer-insights">
            <h3>Avg Service Margin</h3>
            <h1>{service_margin:.1f}%</h1>
            <p>Industry target: 45%</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Revenue trends and insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Monthly Revenue Trends")
        
        # Create monthly revenue data
        parts_sales_df['sale_date'] = pd.to_datetime(parts_sales_df['sale_date'])
        service_revenue_df['service_date'] = pd.to_datetime(service_revenue_df['service_date'])
        
        monthly_parts = parts_sales_df.groupby(parts_sales_df['sale_date'].dt.to_period('M'))['total_amount'].sum()
        monthly_service = service_revenue_df.groupby(service_revenue_df['service_date'].dt.to_period('M'))['total_amount'].sum()
        
        # Combine data
        monthly_data = pd.DataFrame({
            'Month': monthly_parts.index.astype(str),
            'Parts Revenue': monthly_parts.values,
            'Service Revenue': monthly_service.values
        }).fillna(0)
        
        fig = px.line(monthly_data, x='Month', y=['Parts Revenue', 'Service Revenue'],
                     title="Monthly After-Sales Revenue Trends")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Customer Tier Performance")
        
        # Revenue by customer tier
        tier_parts = parts_sales_df.groupby('customer_tier')['total_amount'].sum()
        tier_service = service_revenue_df.groupby('customer_tier')['total_amount'].sum()
        
        tier_data = pd.DataFrame({
            'Customer Tier': tier_parts.index,
            'Parts Revenue': tier_parts.values,
            'Service Revenue': tier_service.values
        })
        
        fig = px.bar(tier_data, x='Customer Tier', y=['Parts Revenue', 'Service Revenue'],
                    title="Revenue by Customer Tier")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Strategic insights
    st.subheader("🧠 Strategic Insights & Opportunities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="parts-opportunity">
            <h4>🔧 Parts Opportunities</h4>
            <ul>
                <li><strong>High-wear generators:</strong> 12 units due for major service</li>
                <li><strong>Filter sales:</strong> $45K opportunity this month</li>
                <li><strong>Consumables upsell:</strong> 68% conversion potential</li>
                <li><strong>Emergency parts:</strong> 24hr delivery premium available</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="service-upsell">
            <h4>💼 Service Upselling</h4>
            <ul>
                <li><strong>Contract upgrades:</strong> 8 customers eligible</li>
                <li><strong>Preventive maintenance:</strong> $180K annual value</li>
                <li><strong>Emergency response:</strong> 3x premium pricing</li>
                <li><strong>Training services:</strong> Untapped $95K opportunity</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="customer-value">
            <h4>📊 Customer Intelligence</h4>
            <ul>
                <li><strong>High-value accounts:</strong> 6 customers >$50K annual</li>
                <li><strong>Churn risk:</strong> 2 accounts need attention</li>
                <li><strong>Expansion ready:</strong> 4 multi-site opportunities</li>
                <li><strong>Satisfaction:</strong> 92% average (target: 95%)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_sales_manager_dashboard():
    """Sales manager dashboard focused on parts and service revenue optimization."""
    st.title("💰 Sales Manager Dashboard")
    st.markdown("### Parts Sales & Service Revenue Optimization")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
        parts_sales_df = pd.read_csv(DATA_DIR / "parts_sales.csv")
        service_revenue_df = pd.read_csv(DATA_DIR / "service_revenue.csv")
    except Exception:
        st.error("Loading sample data...")
        return
    
    # Sales performance metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate this month's performance
    current_month = datetime.now().replace(day=1)
    parts_sales_df['sale_date'] = pd.to_datetime(parts_sales_df['sale_date'])
    
    monthly_parts = parts_sales_df[parts_sales_df['sale_date'] >= current_month]['total_amount'].sum()
    monthly_target = 280000  # Monthly target
    
    with col1:
        st.metric("Monthly Parts Sales", f"${monthly_parts:,.0f}",
                 delta=f"Target: ${monthly_target:,.0f}")
    
    with col2:
        urgent_orders = len(parts_sales_df[parts_sales_df['urgency'] == 'Emergency'])
        st.metric("Emergency Orders", urgent_orders, delta="High margin opportunity")
    
    with col3:
        avg_order_value = parts_sales_df['total_amount'].mean()
        st.metric("Avg Order Value", f"${avg_order_value:,.0f}", delta="+12% vs last month")
    
    with col4:
        # Service contract conversion rate
        total_generators = len(generators_df)
        contracted_generators = len(generators_df[generators_df['service_contract'] != 'No Contract'])
        conversion_rate = (contracted_generators / total_generators) * 100
        st.metric("Service Contract Rate", f"{conversion_rate:.1f}%", delta="Target: 85%")
    
    # Parts sales analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Parts Sales by Category")
        
        category_sales = parts_sales_df.groupby('part_category')['total_amount'].sum().sort_values(ascending=False)
        
        fig = px.pie(values=category_sales.values, names=category_sales.index,
                    title="Parts Revenue Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Top selling parts
        st.write("**Top Selling Parts This Month:**")
        top_parts = parts_sales_df.groupby('part_name').agg({
            'total_amount': 'sum',
            'quantity': 'sum'
        }).sort_values('total_amount', ascending=False).head(5)
        st.dataframe(top_parts, use_container_width=True)
    
    with col2:
        st.subheader("💡 Upselling Opportunities")
        
        # Identify generators needing service
        high_runtime = generators_df[generators_df['total_runtime_hours'] > 8000]
        near_service = generators_df[generators_df['next_service_hours'] < 100]
        no_contract = generators_df[generators_df['service_contract'] == 'No Contract']
        
        opportunities = []
        
        # High runtime generators (parts opportunity)
        for _, gen in high_runtime.head(5).iterrows():
            opportunities.append({
                'Type': 'Parts Upsell',
                'Generator': gen['serial_number'],
                'Customer': gen['customer_name'],
                'Opportunity': 'High wear parts replacement',
                'Est. Value': f"${random.randint(2000, 8000):,}",
                'Priority': 'High'
            })
        
        # Service contract opportunities
        for _, gen in no_contract.head(3).iterrows():
            opportunities.append({
                'Type': 'Service Contract',
                'Generator': gen['serial_number'],
                'Customer': gen['customer_name'],
                'Opportunity': 'Upgrade to Premium Care',
                'Est. Value': f"${random.randint(15000, 35000):,}",
                'Priority': 'Medium'
            })
        
        opportunities_df = pd.DataFrame(opportunities)
        
        if not opportunities_df.empty:
            st.dataframe(opportunities_df, use_container_width=True, hide_index=True)
            
            # Quick action buttons
            st.write("**Quick Actions:**")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("📧 Send Proactive Quote"):
                    st.success("Quote templates sent to top 5 opportunities!")
            with col_b:
                if st.button("📞 Schedule Sales Calls"):
                    st.success("Sales calls scheduled for high-value prospects!")
            with col_c:
                if st.button("📊 Generate Proposals"):
                    st.success("Service upgrade proposals generated!")
    
    # Service revenue analysis
    st.subheader("🛠️ Service Revenue Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Service type performance
        service_performance = service_revenue_df.groupby('service_type').agg({
            'total_amount': 'sum',
            'margin_pct': 'mean',
            'customer_satisfaction': 'mean'
        }).round(2)
        service_performance.columns = ['Revenue', 'Avg Margin %', 'Satisfaction']
        
        st.write("**Service Type Performance:**")
        st.dataframe(service_performance, use_container_width=True)
    
    with col2:
        # Monthly service trends
        service_revenue_df['service_date'] = pd.to_datetime(service_revenue_df['service_date'])
        monthly_service = service_revenue_df.groupby(
            service_revenue_df['service_date'].dt.to_period('M')
        )['total_amount'].sum()
        
        fig = px.line(x=monthly_service.index.astype(str), y=monthly_service.values,
                     title="Monthly Service Revenue Trend")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Customer analysis
    st.subheader("👥 Customer Revenue Analysis")
    
    # Top customers by revenue
    customer_revenue = parts_sales_df.groupby('customer_tier')['total_amount'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    for i, (tier, revenue) in enumerate(customer_revenue.items()):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            <div class="customer-value">
                <h4>{tier} Customers</h4>
                <h2>${revenue:,.0f}</h2>
                <p>Parts revenue YTD</p>
            </div>
            """, unsafe_allow_html=True)

def show_service_operations_dashboard():
    """Service operations dashboard for field and customer management."""
    st.title("🔧 Service Operations Dashboard")
    st.markdown("### Field Service & Customer Management")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
        service_revenue_df = pd.read_csv(DATA_DIR / "service_revenue.csv")
    except Exception:
        st.error("Loading sample data...")
        return
    
    # Service metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Generators needing service
        service_due = len(generators_df[generators_df['next_service_hours'] < 100])
        st.metric("Service Due", service_due, delta="Next 30 days")
    
    with col2:
        # Active service contracts
        active_contracts = len(generators_df[generators_df['service_contract'] != 'No Contract'])
        st.metric("Active Contracts", active_contracts, delta=f"of {len(generators_df)} total")
    
    with col3:
        # Average response time
        avg_response = service_revenue_df['response_time_hours'].mean()
        st.metric("Avg Response Time", f"{avg_response:.1f} hrs", delta="Target: <4 hrs")
    
    with col4:
        # Customer satisfaction
        avg_satisfaction = service_revenue_df['customer_satisfaction'].mean()
        st.metric("Customer Satisfaction", f"{avg_satisfaction:.1f}/10", delta="Target: 9.0")
    
    # Service scheduling
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Upcoming Service Schedule")
        
        # Generate upcoming service list
        upcoming_service = generators_df[generators_df['next_service_hours'] < 500].copy()
        upcoming_service = upcoming_service.sort_values('next_service_hours')
        
        service_list = []
        for _, gen in upcoming_service.head(8).iterrows():
            days_until = max(1, gen['next_service_hours'] / 24)  # Convert to days
            priority = "🔴 Urgent" if days_until < 7 else "🟡 Soon" if days_until < 30 else "🟢 Planned"
            
            service_list.append({
                'Generator': gen['serial_number'],
                'Customer': gen['customer_name'][:25] + "..." if len(gen['customer_name']) > 25 else gen['customer_name'],
                'Service Type': gen['service_contract'] if gen['service_contract'] != 'No Contract' else 'Pay-per-service',
                'Days Until': f"{int(days_until)}",
                'Priority': priority
            })
        
        service_df = pd.DataFrame(service_list)
        st.dataframe(service_df, use_container_width=True, hide_index=True)
        
        # Quick scheduling actions
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("📅 Auto-Schedule Services"):
                st.success("✅ Services auto-scheduled based on priority!")
        with col_b:
            if st.button("📧 Send Customer Notifications"):
                st.success("✅ Service reminder emails sent!")
    
    with col2:
        st.subheader("🗺️ Technician Deployment")
        
        # Mock technician data
        technicians = [
            {'Name': 'Ahmed Al-Rashid', 'Location': 'Riyadh', 'Status': 'Available', 'Jobs Today': 2},
            {'Name': 'Mohammed Al-Saud', 'Location': 'Jeddah', 'Status': 'On Service Call', 'Jobs Today': 3},
            {'Name': 'Khalid Al-Otaibi', 'Location': 'Dammam', 'Status': 'Available', 'Jobs Today': 1},
            {'Name': 'Abdullah Al-Nasser', 'Location': 'NEOM', 'Status': 'Travel to Site', 'Jobs Today': 2},
            {'Name': 'Omar Al-Harbi', 'Location': 'Riyadh', 'Status': 'Available', 'Jobs Today': 1},
        ]
        
        tech_df = pd.DataFrame(technicians)
        
        # Style the dataframe
        def highlight_status(row):
            colors = []
            for i, val in enumerate(row):
                if i == 2:  # Status column
                    if val == 'Available':
                        colors.append('background-color: #d4edda')
                    elif val == 'On Service Call':
                        colors.append('background-color: #fff3cd')
                    else:
                        colors.append('background-color: #f8d7da')
                else:
                    colors.append('')
            return colors
        
        styled_tech = tech_df.style.apply(highlight_status, axis=1)
        st.dataframe(styled_tech, use_container_width=True, hide_index=True)
        
        # Dispatch controls
        st.write("**Quick Dispatch:**")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚨 Emergency Dispatch"):
                st.success("Emergency team dispatched to critical site!")
        with col_b:
            if st.button("📍 Optimize Routes"):
                st.success("Routes optimized for efficiency!")
    
    # Service revenue and contract management
    st.subheader("💼 Contract & Revenue Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Contract type distribution
        contract_dist = generators_df['service_contract'].value_counts()
        
        fig = px.pie(values=contract_dist.values, names=contract_dist.index,
                    title="Service Contract Distribution")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue by service type
        service_revenue = service_revenue_df.groupby('service_type')['total_amount'].sum()
        
        fig = px.bar(x=service_revenue.index, y=service_revenue.values,
                    title="Revenue by Service Type")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Contract upgrade opportunities
    st.subheader("🎯 Contract Upgrade Opportunities")
    
    # Identify upgrade candidates
    upgrade_candidates = generators_df[
        (generators_df['service_contract'] == 'No Contract') |
        (generators_df['service_contract'] == 'Basic Maintenance')
    ].copy()
    
    if not upgrade_candidates.empty:
        upgrade_opportunities = []
        
        for _, gen in upgrade_candidates.head(6).iterrows():
            current_contract = gen['service_contract']
            recommended = 'Premium Care' if gen['customer_tier'] == 'Enterprise' else 'Preventive Plus'
            
            # Calculate potential annual value
            if recommended == 'Premium Care':
                annual_value = random.randint(25000, 45000)
            else:
                annual_value = random.randint(12000, 25000)
            
            upgrade_opportunities.append({
                'Generator': gen['serial_number'],
                'Customer': gen['customer_name'][:30] + "..." if len(gen['customer_name']) > 30 else gen['customer_name'],
                'Current': current_contract,
                'Recommended': recommended,
                'Annual Value': f"${annual_value:,}",
                'Customer Tier': gen['customer_tier']
            })
        
        upgrade_df = pd.DataFrame(upgrade_opportunities)
        st.dataframe(upgrade_df, use_container_width=True, hide_index=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📞 Schedule Sales Meetings"):
                st.success("Sales meetings scheduled with upgrade candidates!")
        with col2:
            if st.button("📊 Generate Proposals"):
                st.success("Custom upgrade proposals generated!")
        with col3:
            if st.button("📧 Send Value Presentations"):
                st.success("Value proposition emails sent!")
    else:
        st.info("All customers have optimal service contracts! 🎉")

def show_customer_portal():
    """Enhanced customer portal with mobile features and self-help insights."""
    st.title("🏢 Customer Portal")
    st.markdown("### Your Generator Performance & Support Dashboard")
    
    try:
        generators_df = pd.read_csv(DATA_DIR / "generators.csv")
        parts_sales_df = pd.read_csv(DATA_DIR / "parts_sales.csv")
        service_revenue_df = pd.read_csv(DATA_DIR / "service_revenue.csv")
    except Exception:
        st.error("Loading sample data...")
        return
    
    # Customer selection
    customers = generators_df['customer_name'].unique()
    selected_customer = st.selectbox("Select Your Organization:", customers)
    
    # Filter data for selected customer
    customer_generators = generators_df[generators_df['customer_name'] == selected_customer]
    
    if customer_generators.empty:
        st.error("No generators found for selected customer")
        return
    
    st.markdown(f"### Welcome, {selected_customer}")
    
    # Real-time notification banner
    if random.random() > 0.7:  # 30% chance of showing alert
        alert_types = [
            ("🟡", "Service reminder: Generator PS-2021-0003 is due for maintenance in 5 days"),
            ("🔴", "Critical alert: Low fuel detected on Generator PS-2020-0008 - 12% remaining"),
            ("🟢", "Success: Preventive maintenance completed on Generator PS-2021-0001"),
            ("🔵", "Info: Load bank test scheduled for next week - Generator PS-2020-0012")
        ]
        
        icon, message = random.choice(alert_types)
        st.info(f"{icon} **Live Update:** {message}")
    
    # Customer overview metrics with traffic light system
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_capacity = customer_generators['rated_kw'].sum()
    active_generators = len(customer_generators)
    avg_runtime = customer_generators['total_runtime_hours'].mean()
    estimated_annual_spend = len(customer_generators) * random.randint(8000, 25000)
    
    # Calculate overall health status
    health_scores = []
    for _, gen in customer_generators.iterrows():
        score = random.randint(75, 98)
        health_scores.append(score)
    
    avg_health = sum(health_scores) / len(health_scores)
    
    # Traffic light health indicator
    if avg_health > 90:
        health_color = "🟢"
        health_status = "Healthy"
    elif avg_health > 80:
        health_color = "🟡"
        health_status = "Monitor"
    else:
        health_color = "🔴"
        health_status = "Attention Needed"
    
    with col1:
        st.metric("Fleet Health", f"{health_color} {health_status}", delta=f"{avg_health:.1f}% avg score")
    
    with col2:
        st.metric("Total Capacity", f"{total_capacity:,.0f} kW")
    
    with col3:
        st.metric("Active Units", active_generators)
    
    with col4:
        # Fuel status across fleet
        fuel_levels = [random.randint(15, 95) for _ in customer_generators.iterrows()]
        avg_fuel = sum(fuel_levels) / len(fuel_levels)
        fuel_status = "🟢" if avg_fuel > 50 else "🟡" if avg_fuel > 30 else "🔴"
        st.metric("Fuel Status", f"{fuel_status} {avg_fuel:.0f}% avg")
    
    with col5:
        # Service status
        service_due_count = len(customer_generators[customer_generators['next_service_hours'] < 100])
        service_status = "🔴" if service_due_count > 2 else "🟡" if service_due_count > 0 else "🟢"
        st.metric("Service Status", f"{service_status} {service_due_count} due soon")
    
    # Enhanced generator fleet status with maintenance tracking
    st.subheader("🔋 Your Generator Fleet - Live Status")
    
    # Create enhanced fleet view with maintenance schedule
    fleet_data = []
    maintenance_schedule = {
        'Daily': ['Fuel check', 'Visual inspection', 'Control panel check'],
        'Weekly': ['15-min run test', 'Oil level check', 'Battery test'],
        'Monthly': ['Battery terminals', 'Belt inspection', 'Load bank test'],
        'Quarterly': ['Oil change', 'Coolant flush', 'Full inspection'],
        'Annual': ['Major service', 'ATS test', 'Professional certification']
    }
    
    for _, gen in customer_generators.iterrows():
        # Calculate next maintenance type needed
        hours_to_service = gen['next_service_hours']
        
        if hours_to_service < 0:
            next_maintenance = "🔴 Overdue - Quarterly Service"
            priority = "Critical"
        elif hours_to_service < 50:
            next_maintenance = "🟠 Due Soon - Oil Change"
            priority = "High"
        elif hours_to_service < 200:
            next_maintenance = "🟡 Scheduled - Monthly Check"
            priority = "Medium"
        else:
            next_maintenance = "🟢 Current - Weekly Test"
            priority = "Low"
        
        # Calculate estimated cost
        if "Quarterly" in next_maintenance:
            est_cost = random.randint(800, 1500)
        elif "Oil Change" in next_maintenance:
            est_cost = random.randint(200, 400)
        else:
            est_cost = random.randint(50, 150)
        
        fleet_data.append({
            'Serial Number': gen['serial_number'],
            'Model': gen['model_series'],
            'Location': gen['location_city'],
            'Capacity': f"{gen['rated_kw']} kW",
            'Runtime': f"{gen['total_runtime_hours']:,} hrs",
            'Next Maintenance': next_maintenance,
            'Est. Cost': f"${est_cost}",
            'Fuel Level': f"{random.randint(20, 90)}%",
            'Last Service': f"{random.randint(30, 180)} days ago"
        })
    
    fleet_df = pd.DataFrame(fleet_data)
    st.dataframe(fleet_df, use_container_width=True, hide_index=True)
    
    # One-click service request section
    st.subheader("🚀 One-Click Service Requests")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="service-upsell">
            <h4>🔧 Routine Maintenance</h4>
            <p>Schedule your next service</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📅 Book Maintenance", key="book_maint", use_container_width=True):
            st.success("✅ Maintenance booked! Technician will contact you within 4 hours.")
            st.info("📍 Nearest technician: Ahmed Al-Rashid (18 km away)")
    
    with col2:
        st.markdown("""
        <div class="parts-opportunity">
            <h4>🚨 Emergency Service</h4>
            <p>24/7 emergency response</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚨 Emergency Call", key="emergency", use_container_width=True, type="primary"):
            st.success("🚨 Emergency dispatch activated! ETA: 45 minutes")
            st.info("📞 Emergency hotline: +966-11-XXX-XXXX")
    
    with col3:
        st.markdown("""
        <div class="customer-value">
            <h4>📦 Order Parts</h4>
            <p>Genuine parts delivery</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🛒 Order Parts", key="order_parts", use_container_width=True):
            st.success("🛒 Parts catalog opened! Free delivery on orders >$200")
    
    # Self-help insights and diagnostics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💡 Self-Help Insights")
        
        # Fuel consumption insights
        st.write("**⛽ Fuel Efficiency Analysis**")
        
        # Mock fuel consumption data
        monthly_consumption = [random.randint(800, 1500) for _ in range(6)]
        months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        fig = px.line(x=months, y=monthly_consumption, 
                     title="Monthly Fuel Consumption (Liters)")
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        # Efficiency tips
        st.markdown("""
        **🎯 Efficiency Tips:**
        - Your fleet is **8% more efficient** than industry average
        - Consider load balancing during peak hours
        - Regular filter changes improve efficiency by 3-5%
        """)
        
        # Quick diagnostics
        st.write("**🔍 Quick Health Check**")
        if st.button("Run Fleet Diagnostic", key="diagnostic"):
            st.success("✅ Diagnostic complete!")
            st.write("**Results:**")
            st.write("• Oil pressure: Normal (all units)")
            st.write("• Coolant levels: Low on PS-2021-0003 (⚠️)")
            st.write("• Battery voltage: Normal (all units)")
            st.write("• Air filters: Replace on 2 units (🔧)")
    
    with col2:
        st.subheader("📊 Performance Analytics")
        
        # Uptime analysis
        uptime_data = {
            'Generator': [gen['serial_number'] for _, gen in customer_generators.head(5).iterrows()],
            'Uptime %': [random.uniform(96, 99.8) for _ in range(5)]
        }
        
        fig = px.bar(uptime_data, x='Generator', y='Uptime %',
                    title="Generator Uptime (Last 30 Days)")
        fig.add_hline(y=99, line_dash="dash", line_color="green", annotation_text="SLA Target")
        fig.update_layout(height=250)
        st.plotly_chart(fig, use_container_width=True)
        
        # Cost breakdown
        st.write("**💰 Monthly Cost Breakdown**")
        cost_data = {
            'Category': ['Fuel', 'Maintenance', 'Parts', 'Emergency'],
            'Amount': [12500, 3200, 1800, 850]
        }
        
        fig2 = px.pie(cost_data, values='Amount', names='Category',
                     title="Cost Distribution ($)")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Maintenance history and compliance
    st.subheader("📋 Maintenance History & Compliance")
    
    # Generate maintenance history
    maintenance_history = []
    service_types = ['Oil Change', 'Filter Replacement', 'Full Service', 'Emergency Repair', 'Load Bank Test']
    
    for i in range(8):
        service_date = datetime.now() - timedelta(days=random.randint(10, 180))
        
        maintenance_history.append({
            'Date': service_date.strftime('%Y-%m-%d'),
            'Generator': random.choice([gen['serial_number'] for _, gen in customer_generators.iterrows()]),
            'Service Type': random.choice(service_types),
            'Technician': random.choice(['Ahmed Al-Rashid', 'Mohammed Al-Saud', 'Khalid Al-Otaibi']),
            'Duration': f"{random.randint(2, 8)} hours",
            'Cost': f"${random.randint(200, 1500)}",
            'Status': 'Completed',
            'Certificate': '📄 Download'
        })
    
    history_df = pd.DataFrame(maintenance_history)
    st.dataframe(history_df, use_container_width=True, hide_index=True)
    
    # Compliance and reporting
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Generate Compliance Report", use_container_width=True):
            st.success("📊 Compliance report generated and emailed!")
    
    with col2:
        if st.button("📄 Download Service Certificates", use_container_width=True):
            st.success("📄 All certificates downloaded as PDF!")
    
    with col3:
        if st.button("📈 Export Performance Data", use_container_width=True):
            st.success("📈 Performance data exported to Excel!")
    
    # Proactive notifications preferences
    with st.expander("🔔 Notification Preferences"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Alert Notifications:**")
            st.checkbox("📧 Email alerts", value=True)
            st.checkbox("📱 SMS notifications", value=True)
            st.checkbox("🔔 Push notifications", value=False)
            st.checkbox("📞 Phone calls for critical alerts", value=True)
        
        with col2:
            st.write("**Maintenance Reminders:**")
            st.checkbox("📅 Service due reminders", value=True)
            st.checkbox("⛽ Low fuel alerts", value=True)
            st.checkbox("🔋 Battery status updates", value=True)
            st.checkbox("📊 Monthly performance reports", value=True)
        
        if st.button("💾 Save Preferences"):
            st.success("Notification preferences updated!")

def main():
    """Main application with manufacturer focus."""
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Initialize data
    load_manufacturer_data()
    
    # Authentication check
    if not st.session_state.authenticated:
        authenticate_manufacturer()
        return
    
    # Role-based navigation
    config = load_manufacturer_config()
    
    # Sidebar with role info
    st.sidebar.markdown(f"### {st.session_state.role_name}")
    st.sidebar.write(f"Power System Manufacturing Platform")
    
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
            "🔮 Predictive Maintenance": show_predictive_maintenance_engine,
            "🚨 Smart Alerts": show_smart_alerts_system,
            "📊 Generator Specs": analyze_generator_specs,
            "💰 Sales Analytics": show_sales_manager_dashboard,
            "🔧 Service Operations": show_service_operations_dashboard
        }
    elif st.session_state.user_role == "sales@powersystem":
        pages = {
            "💰 Sales Dashboard": show_sales_manager_dashboard,
            "🔮 Predictive Opportunities": show_predictive_maintenance_engine,
            "📊 Generator Analysis": analyze_generator_specs,
            "👔 Executive Summary": show_ceo_revenue_dashboard,
            "🗺️ Fleet Overview": show_fleet_monitoring_dashboard,
            "🔧 Service Opportunities": show_service_operations_dashboard
        }
    elif st.session_state.user_role == "service@powersystem":
        pages = {
            "🔧 Service Operations": show_service_operations_dashboard,
            "🗺️ Fleet Monitoring": show_fleet_monitoring_dashboard,
            "🚨 Alert Center": show_smart_alerts_system,
            "🔮 Predictive Maintenance": show_predictive_maintenance_engine,
            "📊 Specs & Maintenance": analyze_generator_specs,
            "💰 Revenue Opportunities": show_sales_manager_dashboard,
            "🏢 Customer Management": show_customer_portal
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
    
    # Sidebar footer with company info
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚡ Power System Manufacturing")
    st.sidebar.markdown("**Advanced IoT Platform**")
    st.sidebar.markdown("✅ Real-time Fleet Monitoring")
    st.sidebar.markdown("✅ Predictive Maintenance AI")
    st.sidebar.markdown("✅ Smart Alert System")
    st.sidebar.markdown("✅ Parts Sales Optimization")
    st.sidebar.markdown("✅ Service Revenue Growth")
    st.sidebar.markdown("✅ Customer Self-Service Portal")
    st.sidebar.markdown("✅ Mobile Field Management")
    st.sidebar.markdown("✅ Compliance & Reporting")
    
    # Advanced features indicator
    st.sidebar.markdown("### 🚀 Advanced Features")
    st.sidebar.markdown("🗺️ **GPS Fleet Tracking**")
    st.sidebar.markdown("🔮 **94% ML Accuracy**")
    st.sidebar.markdown("📱 **One-Click Service**")
    st.sidebar.markdown("🎯 **Proactive Notifications**")
    st.sidebar.markdown("📊 **Generator Spec Integration**")
    
    # Revenue targets display
    targets = config['revenue_targets']
    st.sidebar.markdown("### 🎯 Annual Targets")
    st.sidebar.write(f"Parts: ${targets['parts_annual']:,.0f}")
    st.sidebar.write(f"Service: ${targets['service_contracts']:,.0f}")
    st.sidebar.write(f"Total: ${(targets['parts_annual'] + targets['service_contracts']):,.0f}")

if __name__ == "__main__":
    main()
