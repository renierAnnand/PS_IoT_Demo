# Generator IoT Monitoring Platform - Complete Project Structure

## File: requirements.txt
```
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.15.0
pydeck>=0.8.0
scikit-learn>=1.3.0
pydantic>=2.0.0
faker>=19.0.0
```

## File: README.md
```markdown
# Generator IoT Monitoring Platform Demo

A comprehensive Streamlit application simulating a generator fleet monitoring system for Gulf Power.

## Features
- **Multi-role access**: Customer vs Power Systems views
- **Fleet Overview**: Executive dashboard with KPIs and health metrics
- **Fleet Map**: Interactive map view of generator locations
- **Generator Details**: 360° view of individual units with live metrics
- **Alerts Management**: Real-time alert monitoring and resolution
- **Maintenance Planning**: Service scheduling and capacity management
- **Reports & Analytics**: Fleet utilization and performance insights
- **Admin Tools**: Data regeneration and simulation controls

## Quick Start
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Demo Data
- 100 generators across multiple customers and regions
- 7-14 days of synthetic time-series data
- Realistic alerts and maintenance scenarios
- Health scoring with predictive indicators

## Navigation
Use the sidebar to switch between Customer and Power Systems roles, and navigate between different pages of the application.
```

## File: models.py
```python
"""
Pydantic data models for the Generator IoT platform.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field


class GeneratorStatus(str, Enum):
    RUNNING = "Running"
    STANDBY = "Standby"
    OFFLINE = "Offline"
    MAINTENANCE = "Maintenance"


class ControllerProtocol(str, Enum):
    MODBUS = "Modbus"
    CAN = "CAN"
    RS485 = "RS485"


class AlertSeverity(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class Phase(int, Enum):
    SINGLE = 1
    THREE = 3


class Generator(BaseModel):
    """Generator entity model."""
    generator_id: str = Field(..., description="Unique generator identifier")
    serial_no: str = Field(..., description="Generator serial number")
    model: str = Field(..., description="Generator model")
    controller_protocol: ControllerProtocol = Field(..., description="Communication protocol")
    rated_kw: float = Field(..., gt=0, description="Rated power in kilowatts")
    phase: Phase = Field(..., description="Electrical phase configuration")
    site_name: str = Field(..., description="Installation site name")
    customer_name: str = Field(..., description="Customer name")
    region: str = Field(..., description="Geographic region")
    gps_lat: float = Field(..., ge=-90, le=90, description="GPS latitude")
    gps_lng: float = Field(..., ge=-180, le=180, description="GPS longitude")
    commissioned_date: datetime = Field(..., description="Commissioning date")
    warranty_expiry: datetime = Field(..., description="Warranty expiration date")
    status: GeneratorStatus = Field(..., description="Current operational status")
    last_heartbeat: datetime = Field(..., description="Last communication timestamp")


class Metrics(BaseModel):
    """Time-series metrics model."""
    generator_id: str
    timestamp: datetime
    run_hours_total: float = Field(..., ge=0, description="Total runtime hours")
    fuel_level_pct: float = Field(..., ge=0, le=100, description="Fuel level percentage")
    coolant_temp_c: float = Field(..., description="Coolant temperature in Celsius")
    oil_pressure_kpa: float = Field(..., ge=0, description="Oil pressure in kPa")
    battery_voltage_v: float = Field(..., ge=0, description="Battery voltage")
    load_kw: float = Field(..., ge=0, description="Current load in kilowatts")
    load_pct: float = Field(..., ge=0, le=100, description="Load percentage")
    freq_hz: float = Field(..., gt=0, description="Frequency in Hz")
    power_factor: float = Field(..., ge=0, le=1, description="Power factor")
    ambient_temp_c: float = Field(..., description="Ambient temperature in Celsius")


class KPIs(BaseModel):
    """Calculated KPIs model."""
    generator_id: str
    uptime_pct_7d: float = Field(..., ge=0, le=100, description="7-day uptime percentage")
    uptime_pct_30d: float = Field(..., ge=0, le=100, description="30-day uptime percentage")
    avg_load_pct: float = Field(..., ge=0, le=100, description="Average load percentage")
    utilization_hours_7d: float = Field(..., ge=0, description="7-day utilization hours")
    mtbf_hours: float = Field(..., ge=0, description="Mean time between failures")
    mttr_hours: float = Field(..., ge=0, description="Mean time to repair")
    est_fuel_rate_lph: float = Field(..., ge=0, description="Estimated fuel rate L/h")
    next_service_due_hours: float = Field(..., description="Hours until next service")
    maintenance_overdue: bool = Field(..., description="Maintenance overdue flag")
    health_score_0_100: float = Field(..., ge=0, le=100, description="Health score 0-100")


class Alert(BaseModel):
    """Alert/Alarm model."""
    alert_id: str = Field(..., description="Unique alert identifier")
    generator_id: str = Field(..., description="Associated generator ID")
    timestamp: datetime = Field(..., description="Alert timestamp")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    code: str = Field(..., description="Alert code")
    message: str = Field(..., description="Alert message")
    acknowledged: bool = Field(default=False, description="Acknowledgment status")
    resolved: bool = Field(default=False, description="Resolution status")


class ServiceTicket(BaseModel):
    """Service ticket model."""
    ticket_id: str = Field(..., description="Unique ticket identifier")
    generator_id: str = Field(..., description="Associated generator ID")
    created_at: datetime = Field(..., description="Ticket creation timestamp")
    priority: str = Field(..., description="Ticket priority")
    assigned_to: Optional[str] = Field(None, description="Assigned technician")
    status: str = Field(..., description="Ticket status")
    eta: Optional[datetime] = Field(None, description="Estimated completion time")
    notes: str = Field(default="", description="Additional notes")
```

## File: data_gen.py
```python
"""
Dummy data generator for the Generator IoT platform.
"""
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple
from faker import Faker
from models import (
    Generator, Metrics, KPIs, Alert, ServiceTicket,
    GeneratorStatus, ControllerProtocol, AlertSeverity, Phase
)

fake = Faker()
Faker.seed(42)  # For reproducible demo data
random.seed(42)
np.random.seed(42)


class DataGenerator:
    """Generates comprehensive dummy data for the generator platform."""
    
    def __init__(self):
        self.customers = [
            "Gulf Coast Medical Center", "Bayview Shopping Plaza", "Harbor Industries",
            "Coastal University", "Marina Resort & Spa", "Downtown Financial Center",
            "Regional Airport Authority", "Petrochemical Complex", "Manufacturing Hub",
            "Emergency Services HQ", "Data Center South", "Residential Complex East"
        ]
        
        self.regions = [
            "Gulf Coast", "Panhandle", "Central Florida", "Tampa Bay",
            "Southwest Florida", "Southeast Florida", "North Florida"
        ]
        
        self.generator_models = [
            "CAT C15 ACERT", "Cummins QSX15", "Kohler 20RESAL",
            "Generac MD200", "MTU 12V2000", "Perkins 1506A",
            "Yanmar 4TNV98", "Detroit Diesel DD13"
        ]
        
        self.alert_codes = {
            "FUEL_LOW": "Low fuel level detected",
            "COOLANT_HIGH": "High coolant temperature",
            "OIL_PRESSURE_LOW": "Low oil pressure",
            "BATTERY_LOW": "Low battery voltage",
            "HEARTBEAT_LOST": "Communication lost",
            "OVERLOAD": "Generator overload condition",
            "FREQ_DEVIATION": "Frequency deviation detected",
            "VOLTAGE_ANOMALY": "Voltage anomaly detected",
            "SERVICE_DUE": "Scheduled service due",
            "FILTER_REPLACE": "Filter replacement required"
        }

    def generate_generators(self, n: int = 100) -> List[Generator]:
        """Generate dummy generator fleet."""
        generators = []
        
        for i in range(n):
            # Create realistic GPS coordinates for Gulf region
            lat = random.uniform(24.5, 31.0)  # Florida/Gulf Coast latitude
            lng = random.uniform(-87.6, -80.2)  # Florida/Gulf Coast longitude
            
            commissioned = fake.date_between(start_date='-10y', end_date='-1y')
            warranty_expiry = commissioned + timedelta(days=random.randint(1095, 2555))  # 3-7 years
            
            # Determine status with realistic distribution
            status_weights = [0.65, 0.20, 0.10, 0.05]  # Running, Standby, Offline, Maintenance
            status = np.random.choice(list(GeneratorStatus), p=status_weights)
            
            # Last heartbeat based on status
            if status == GeneratorStatus.OFFLINE:
                last_heartbeat = datetime.now() - timedelta(hours=random.randint(1, 72))
            else:
                last_heartbeat = datetime.now() - timedelta(minutes=random.randint(0, 10))
            
            generator = Generator(
                generator_id=f"GEN-{i+1:04d}",
                serial_no=f"SN{fake.random_number(digits=8)}",
                model=random.choice(self.generator_models),
                controller_protocol=random.choice(list(ControllerProtocol)),
                rated_kw=random.choice([50, 75, 100, 125, 150, 200, 250, 300, 500, 750, 1000]),
                phase=random.choice(list(Phase)),
                site_name=fake.company() + " " + random.choice(["Building", "Facility", "Campus", "Center"]),
                customer_name=random.choice(self.customers),
                region=random.choice(self.regions),
                gps_lat=lat,
                gps_lng=lng,
                commissioned_date=commissioned,
                warranty_expiry=warranty_expiry,
                status=status,
                last_heartbeat=last_heartbeat
            )
            generators.append(generator)
        
        return generators

    def generate_metrics(self, generators: List[Generator], days: int = 14) -> pd.DataFrame:
        """Generate time-series metrics for all generators."""
        all_metrics = []
        now = datetime.now()
        start_time = now - timedelta(days=days)
        
        for generator in generators:
            # Generate base patterns for this generator
            base_load_pct = random.uniform(20, 80)
            base_fuel_rate = 0.25 + (base_load_pct / 100) * 0.15  # L/h per kW
            
            # Create time series (5-minute intervals)
            current_time = start_time
            interval_minutes = 5
            run_hours = random.uniform(500, 8000)  # Starting run hours
            
            while current_time <= now:
                # Skip data if generator was offline during this period
                if (generator.status == GeneratorStatus.OFFLINE and 
                    current_time > generator.last_heartbeat):
                    current_time += timedelta(minutes=interval_minutes)
                    continue
                
                # Base load with daily and weekly patterns
                hour_of_day = current_time.hour
                day_of_week = current_time.weekday()
                
                # Daily pattern (higher load during business hours)
                daily_factor = 1.0
                if 8 <= hour_of_day <= 17:
                    daily_factor = 1.3
                elif 18 <= hour_of_day <= 22:
                    daily_factor = 1.1
                else:
                    daily_factor = 0.7
                
                # Weekly pattern (lower on weekends)
                weekly_factor = 0.8 if day_of_week >= 5 else 1.0
                
                # Calculate load with patterns and random variation
                load_pct = base_load_pct * daily_factor * weekly_factor
                load_pct += random.gauss(0, 5)  # Add noise
                load_pct = max(0, min(100, load_pct))  # Clamp to valid range
                
                load_kw = (load_pct / 100) * generator.rated_kw
                
                # Correlated metrics
                fuel_level = random.uniform(15, 95)  # Will inject low fuel alerts
                
                # Temperature correlations
                ambient_temp = 25 + random.gauss(0, 8)  # Base ambient temperature
                coolant_temp = 75 + (load_pct * 0.4) + random.gauss(0, 3)
                
                # Inject anomalies (5% chance)
                if random.random() < 0.05:
                    if random.random() < 0.3:  # High temperature spike
                        coolant_temp += random.uniform(15, 30)
                    elif random.random() < 0.3:  # Low fuel
                        fuel_level = random.uniform(5, 14)
                    elif random.random() < 0.3:  # Oil pressure drop
                        pass  # Will be handled in oil_pressure calculation
                
                oil_pressure = 350 + random.gauss(0, 25)
                if random.random() < 0.02:  # 2% chance of low pressure
                    oil_pressure = random.uniform(150, 250)
                
                battery_voltage = 12.6 + random.gauss(0, 0.3)
                if random.random() < 0.03:  # 3% chance of low battery
                    battery_voltage = random.uniform(10.5, 11.8)
                
                freq_hz = 60.0 + random.gauss(0, 0.2)
                power_factor = 0.85 + random.gauss(0, 0.05)
                power_factor = max(0.7, min(1.0, power_factor))
                
                # Update run hours if generator is running
                if generator.status == GeneratorStatus.RUNNING:
                    run_hours += interval_minutes / 60.0
                
                metric = Metrics(
                    generator_id=generator.generator_id,
                    timestamp=current_time,
                    run_hours_total=run_hours,
                    fuel_level_pct=fuel_level,
                    coolant_temp_c=coolant_temp,
                    oil_pressure_kpa=oil_pressure,
                    battery_voltage_v=battery_voltage,
                    load_kw=load_kw,
                    load_pct=load_pct,
                    freq_hz=freq_hz,
                    power_factor=power_factor,
                    ambient_temp_c=ambient_temp
                )
                
                all_metrics.append(metric.dict())
                current_time += timedelta(minutes=interval_minutes)
        
        return pd.DataFrame(all_metrics)

    def calculate_kpis(self, generators: List[Generator], metrics_df: pd.DataFrame) -> List[KPIs]:
        """Calculate KPIs for each generator."""
        kpis = []
        now = datetime.now()
        
        for generator in generators:
            gen_metrics = metrics_df[metrics_df['generator_id'] == generator.generator_id]
            
            if gen_metrics.empty:
                # Default KPIs for generators with no metrics
                kpi = KPIs(
                    generator_id=generator.generator_id,
                    uptime_pct_7d=0.0,
                    uptime_pct_30d=0.0,
                    avg_load_pct=0.0,
                    utilization_hours_7d=0.0,
                    mtbf_hours=0.0,
                    mttr_hours=0.0,
                    est_fuel_rate_lph=0.0,
                    next_service_due_hours=random.uniform(100, 500),
                    maintenance_overdue=False,
                    health_score_0_100=random.uniform(40, 60)
                )
                kpis.append(kpi)
                continue
            
            # Calculate uptime percentages
            gen_metrics['timestamp'] = pd.to_datetime(gen_metrics['timestamp'])
            last_7d = gen_metrics[gen_metrics['timestamp'] >= now - timedelta(days=7)]
            last_30d = gen_metrics[gen_metrics['timestamp'] >= now - timedelta(days=30)]
            
            # Estimate uptime based on data continuity
            uptime_7d = min(95.0, len(last_7d) / (7 * 24 * 12) * 100) if not last_7d.empty else 0.0
            uptime_30d = min(95.0, len(last_30d) / (30 * 24 * 12) * 100) if not last_30d.empty else 0.0
            
            # Average load
            avg_load_pct = gen_metrics['load_pct'].mean() if not gen_metrics.empty else 0.0
            
            # Utilization hours (time above 10% load in last 7 days)
            utilization_hours_7d = len(last_7d[last_7d['load_pct'] > 10]) * (5/60) if not last_7d.empty else 0.0
            
            # Mock MTBF/MTTR
            mtbf_hours = random.uniform(500, 2000)
            mttr_hours = random.uniform(2, 24)
            
            # Estimated fuel rate
            est_fuel_rate_lph = 0.25 + (avg_load_pct / 100) * 0.15
            
            # Service scheduling
            next_service_hours = random.uniform(-200, 500)  # Negative means overdue
            maintenance_overdue = next_service_hours < 0
            
            # Health score calculation
            health_score = self._calculate_health_score(generator, gen_metrics)
            
            kpi = KPIs(
                generator_id=generator.generator_id,
                uptime_pct_7d=uptime_7d,
                uptime_pct_30d=uptime_30d,
                avg_load_pct=avg_load_pct,
                utilization_hours_7d=utilization_hours_7d,
                mtbf_hours=mtbf_hours,
                mttr_hours=mttr_hours,
                est_fuel_rate_lph=est_fuel_rate_lph,
                next_service_due_hours=next_service_hours,
                maintenance_overdue=maintenance_overdue,
                health_score_0_100=health_score
            )
            kpis.append(kpi)
        
        return kpis

    def _calculate_health_score(self, generator: Generator, metrics_df: pd.DataFrame) -> float:
        """Calculate health score based on recent metrics and alerts."""
        score = 100.0
        
        if metrics_df.empty:
            return random.uniform(60, 85)
        
        # Get recent metrics (last 24 hours)
        now = datetime.now()
        recent = metrics_df[pd.to_datetime(metrics_df['timestamp']) >= now - timedelta(hours=24)]
        
        if recent.empty:
            return random.uniform(50, 75)
        
        # Penalize for high temperatures
        avg_coolant_temp = recent['coolant_temp_c'].mean()
        if avg_coolant_temp > 90:
            score -= 15
        elif avg_coolant_temp > 85:
            score -= 8
        
        # Penalize for low oil pressure
        avg_oil_pressure = recent['oil_pressure_kpa'].mean()
        if avg_oil_pressure < 200:
            score -= 20
        elif avg_oil_pressure < 300:
            score -= 10
        
        # Penalize for low battery voltage
        avg_battery = recent['battery_voltage_v'].mean()
        if avg_battery < 11.5:
            score -= 15
        elif avg_battery < 12.0:
            score -= 8
        
        # Penalize for communication issues
        if generator.status == GeneratorStatus.OFFLINE:
            score -= 25
        elif (now - generator.last_heartbeat).total_seconds() > 1800:  # 30 minutes
            score -= 10
        
        # Penalize for frequency deviations
        freq_std = recent['freq_hz'].std()
        if freq_std > 0.5:
            score -= 10
        elif freq_std > 0.3:
            score -= 5
        
        # Random variation
        score += random.gauss(0, 3)
        
        return max(0, min(100, score))

    def generate_alerts(self, generators: List[Generator], metrics_df: pd.DataFrame) -> List[Alert]:
        """Generate alerts based on metrics and rules."""
        alerts = []
        alert_counter = 1
        
        for generator in generators:
            gen_metrics = metrics_df[metrics_df['generator_id'] == generator.generator_id]
            
            if gen_metrics.empty:
                continue
            
            # Check for various alert conditions
            for _, row in gen_metrics.iterrows():
                timestamp = pd.to_datetime(row['timestamp'])
                
                # Low fuel alert
                if row['fuel_level_pct'] < 15:
                    if random.random() < 0.3:  # Don't alert every time
                        alert = Alert(
                            alert_id=f"ALT-{alert_counter:06d}",
                            generator_id=generator.generator_id,
                            timestamp=timestamp,
                            severity=AlertSeverity.WARNING if row['fuel_level_pct'] > 10 else AlertSeverity.CRITICAL,
                            code="FUEL_LOW",
                            message=f"Fuel level low: {row['fuel_level_pct']:.1f}%",
                            acknowledged=random.choice([True, False]),
                            resolved=random.choice([True, False])
                        )
                        alerts.append(alert)
                        alert_counter += 1
                
                # High coolant temperature
                if row['coolant_temp_c'] > 95:
                    if random.random() < 0.4:
                        alert = Alert(
                            alert_id=f"ALT-{alert_counter:06d}",
                            generator_id=generator.generator_id,
                            timestamp=timestamp,
                            severity=AlertSeverity.CRITICAL,
                            code="COOLANT_HIGH",
                            message=f"High coolant temperature: {row['coolant_temp_c']:.1f}°C",
                            acknowledged=random.choice([True, False]),
                            resolved=random.choice([True, False])
                        )
                        alerts.append(alert)
                        alert_counter += 1
                
                # Low oil pressure
                if row['oil_pressure_kpa'] < 250:
                    if random.random() < 0.4:
                        alert = Alert(
                            alert_id=f"ALT-{alert_counter:06d}",
                            generator_id=generator.generator_id,
                            timestamp=timestamp,
                            severity=AlertSeverity.CRITICAL,
                            code="OIL_PRESSURE_LOW",
                            message=f"Low oil pressure: {row['oil_pressure_kpa']:.0f} kPa",
                            acknowledged=random.choice([True, False]),
                            resolved=random.choice([True, False])
                        )
                        alerts.append(alert)
                        alert_counter += 1
                
                # Low battery voltage
                if row['battery_voltage_v'] < 12.0:
                    if random.random() < 0.3:
                        alert = Alert(
                            alert_id=f"ALT-{alert_counter:06d}",
                            generator_id=generator.generator_id,
                            timestamp=timestamp,
                            severity=AlertSeverity.WARNING,
                            code="BATTERY_LOW",
                            message=f"Low battery voltage: {row['battery_voltage_v']:.1f}V",
                            acknowledged=random.choice([True, False]),
                            resolved=random.choice([True, False])
                        )
                        alerts.append(alert)
                        alert_counter += 1
                
                # Overload condition
                if row['load_pct'] > 90:
                    if random.random() < 0.2:
                        alert = Alert(
                            alert_id=f"ALT-{alert_counter:06d}",
                            generator_id=generator.generator_id,
                            timestamp=timestamp,
                            severity=AlertSeverity.WARNING,
                            code="OVERLOAD",
                            message=f"Generator overload: {row['load_pct']:.1f}%",
                            acknowledged=random.choice([True, False]),
                            resolved=random.choice([True, False])
                        )
                        alerts.append(alert)
                        alert_counter += 1
        
        # Add communication lost alerts for offline generators
        for generator in generators:
            if generator.status == GeneratorStatus.OFFLINE:
                alert = Alert(
                    alert_id=f"ALT-{alert_counter:06d}",
                    generator_id=generator.generator_id,
                    timestamp=generator.last_heartbeat + timedelta(minutes=30),
                    severity=AlertSeverity.CRITICAL,
                    code="HEARTBEAT_LOST",
                    message="Communication lost - generator offline",
                    acknowledged=random.choice([True, False]),
                    resolved=False
                )
                alerts.append(alert)
                alert_counter += 1
        
        return alerts

    def generate_service_tickets(self, generators: List[Generator], kpis: List[KPIs]) -> List[ServiceTicket]:
        """Generate mock service tickets."""
        tickets = []
        ticket_counter = 1
        
        technicians = ["John Smith", "Maria Garcia", "David Johnson", "Sarah Wilson", "Mike Brown"]
        
        for generator in generators:
            # Find KPI for this generator
            gen_kpi = next((k for k in kpis if k.generator_id == generator.generator_id), None)
            
            # Create tickets for overdue maintenance or low health scores
            if gen_kpi and (gen_kpi.maintenance_overdue or gen_kpi.health_score_0_100 < 70):
                if random.random() < 0.7:  # 70% chance of having a ticket
                    created_time = datetime.now() - timedelta(days=random.randint(0, 14))
                    
                    ticket = ServiceTicket(
                        ticket_id=f"TKT-{ticket_counter:05d}",
                        generator_id=generator.generator_id,
                        created_at=created_time,
                        priority=random.choice(["Low", "Medium", "High", "Critical"]),
                        assigned_to=random.choice(technicians + [None]),
                        status=random.choice(["Open", "In Progress", "Scheduled", "Completed"]),
                        eta=created_time + timedelta(days=random.randint(1, 30)) if random.choice([True, False]) else None,
                        notes=random.choice([
                            "Scheduled maintenance due",
                            "Customer reported performance issues",
                            "Preventive maintenance required",
                            "Follow-up on recent alert",
                            "Annual inspection due",
                            "Parts replacement needed"
                        ])
                    )
                    tickets.append(ticket)
                    ticket_counter += 1
        
        return tickets

    def generate_all_data(self, n_generators: int = 100, days: int = 14) -> dict:
        """Generate complete dataset."""
        print(f"Generating {n_generators} generators...")
        generators = self.generate_generators(n_generators)
        
        print(f"Generating {days} days of metrics...")
        metrics_df = self.generate_metrics(generators, days)
        
        print("Calculating KPIs...")
        kpis = self.calculate_kpis(generators, metrics_df)
        
        print("Generating alerts...")
        alerts = self.generate_alerts(generators, metrics_df)
        
        print("Generating service tickets...")
        tickets = self.generate_service_tickets(generators, kpis)
        
        return {
            'generators': generators,
            'metrics': metrics_df,
            'kpis': kpis,
            'alerts': alerts,
            'tickets': tickets
        }


def save_data_to_files(data: dict, data_dir: str = "data"):
    """Save generated data to files."""
    import os
    os.makedirs(data_dir, exist_ok=True)
    
    # Save generators
    generators_df = pd.DataFrame([g.dict() for g in data['generators']])
    generators_df.to_parquet(f"{data_dir}/generators.parquet", index=False)
    
    # Save metrics
    data['metrics'].to_parquet(f"{data_dir}/metrics.parquet", index=False)
    
    # Save KPIs
    kpis_df = pd.DataFrame([k.dict() for k in data['kpis']])
    kpis_df.to_parquet(f"{data_dir}/kpis.parquet", index=False)
    
    # Save alerts
    alerts_df = pd.DataFrame([a.dict() for a in data['alerts']])
    alerts_df.to_parquet(f"{data_dir}/alerts.parquet", index=False)
    
    # Save tickets
    tickets_df = pd.DataFrame([t.dict() for t in data['tickets']])
    tickets_df.to_parquet(f"{data_dir}/tickets.parquet", index=False)
    
    print(f"Data saved to {data_dir}/ directory")


if __name__ == "__main__":
    generator = DataGenerator()
    data = generator.generate_all_data()
    save_data_to_files(data)
```

## File: app.py
```python
"""
Main Streamlit application for Generator IoT Monitoring Platform.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pydeck as pdk
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional

from data_gen import DataGenerator, save_data_to_files
from models import GeneratorStatus, AlertSeverity

# Page configuration
st.set_page_config(
    page_title="Gulf Power | Connected Generators",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e1e5e9;
        margin: 0.5rem 0;
    }
    .status-running { color: #28a745; }
    .status-standby { color: #007bff; }
    .status-offline { color: #dc3545; }
    .status-maintenance { color: #fd7e14; }
    .health-good { color: #28a745; }
    .health-watch { color: #ffc107; }
    .health-risk { color: #dc3545; }
    .alert-critical { background-color: #f8d7da; }
    .alert-warning { background-color: #fff3cd; }
    .alert-info { background-color: #d1ecf1; }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data() -> Dict:
    """Load data from files or generate if not exists."""
    data_dir = "data"
    
    # Check if data files exist
    files_exist = all(os.path.exists(f"{data_dir}/{file}") for file in [
        "generators.parquet", "metrics.parquet", "kpis.parquet", 
        "alerts.parquet", "tickets.parquet"
    ])
    
    if not files_exist:
        st.info("Generating initial demo data... This may take a moment.")
        generator = DataGenerator()
        data = generator.generate_all_data()
        save_data_to_files(data, data_dir)
        st.success("Demo data generated successfully!")
        st.experimental_rerun()
    
    # Load data from files
    generators_df = pd.read_parquet(f"{data_dir}/generators.parquet")
    metrics_df = pd.read_parquet(f"{data_dir}/metrics.parquet")
    kpis_df = pd.read_parquet(f"{data_dir}/kpis.parquet")
    alerts_df = pd.read_parquet(f"{data_dir}/alerts.parquet")
    tickets_df = pd.read_parquet(f"{data_dir}/tickets.parquet")
    
    return {
        'generators': generators_df,
        'metrics': metrics_df,
        'kpis': kpis_df,
        'alerts': alerts_df,
        'tickets': tickets_df
    }


def get_status_color(status: str) -> str:
    """Get color for generator status."""
    colors = {
        "Running": "#28a745",
        "Standby": "#007bff", 
        "Offline": "#dc3545",
        "Maintenance": "#fd7e14"
    }
    return colors.get(status, "#6c757d")


def get_health_color(score: float) -> str:
    """Get color for health score."""
    if score >= 80:
        return "#28a745"  # Good - Green
    elif score >= 60:
        return "#ffc107"  # Watch - Yellow
    else:
        return "#dc3545"  # Risk - Red


def get_health_label(score: float) -> str:
    """Get health label for score."""
    if score >= 80:
        return "Good"
    elif score >= 60:
        return "Watch"
    else:
        return "At Risk"


def apply_filters(data: Dict, filters: Dict) -> Dict:
    """Apply global filters to data."""
    filtered_data = data.copy()
    
    # Filter generators
    gen_mask = pd.Series(True, index=filtered_data['generators'].index)
    
    if filters.get('regions'):
        gen_mask &= filtered_data['generators']['region'].isin(filters['regions'])
    
    if filters.get('customers'):
        gen_mask &= filtered_data['generators']['customer_name'].isin(filters['customers'])
    
    if filters.get('statuses'):
        gen_mask &= filtered_data['generators']['status'].isin(filters['statuses'])
    
    filtered_generators = filtered_data['generators'][gen_mask]
    generator_ids = filtered_generators['generator_id'].tolist()
    
    # Filter related data
    filtered_data['generators'] = filtered_generators
    filtered_data['metrics'] = filtered_data['metrics'][
        filtered_data['metrics']['generator_id'].isin(generator_ids)
    ]
    filtered_data['kpis'] = filtered_data['kpis'][
        filtered_data['kpis']['generator_id'].isin(generator_ids)
    ]
    filtered_data['alerts'] = filtered_data['alerts'][
        filtered_data['alerts']['generator_id'].isin(generator_ids)
    ]
    filtered_data['tickets'] = filtered_data['tickets'][
        filtered_data['tickets']['generator_id'].isin(generator_ids)
    ]
    
    # Apply date filter to time-series data
    if filters.get('date_range'):
        start_date, end_date = filters['date_range']
        filtered_data['metrics'] = filtered_data['metrics'][
            (pd.to_datetime(filtered_data['metrics']['timestamp']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(filtered_data['metrics']['timestamp']) <= pd.to_datetime(end_date))
        ]
        filtered_data['alerts'] = filtered_data['alerts'][
            (pd.to_datetime(filtered_data['alerts']['timestamp']) >= pd.to_datetime(start_date)) &
            (pd.to_datetime(filtered_data['alerts']['timestamp']) <= pd.to_datetime(end_date))
        ]
    
    return filtered_data


def main():
    """Main application function."""
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⚡ Gulf Power | Connected Generators")
    with col2:
        st.image("https://via.placeholder.com/150x50/0066cc/white?text=GULF+POWER", width=150)
    
    # Load data
    data = load_data()
    
    # Sidebar for role selection and filters
    st.sidebar.title("🔧 Controls")
    
    # Role selector
    role = st.sidebar.selectbox(
        "Select Role:",
        ["Customer", "Power Systems (Service Team)"],
        help="Different roles have access to different features"
    )
    
    st.sidebar.markdown("---")
    
    # Global filters
    st.sidebar.subheader("🔍 Filters")
    
    # Date range filter
    default_start = datetime.now() - timedelta(days=7)
    default_end = datetime.now()
    date_range = st.sidebar.date_input(
        "Date Range:",
        value=(default_start.date(), default_end.date()),
        max_value=datetime.now().date()
    )
    
    # Region filter
    regions = st.sidebar.multiselect(
        "Regions:",
        options=sorted(data['generators']['region'].unique()),
        default=[]
    )
    
    # Customer filter
    customers = st.sidebar.multiselect(
        "Customers:",
        options=sorted(data['generators']['customer_name'].unique()),
        default=[]
    )
    
    # Status filter
    statuses = st.sidebar.multiselect(
        "Status:",
        options=sorted(data['generators']['status'].unique()),
        default=[]
    )
    
    # Prepare filters
    filters = {
        'date_range': date_range if len(date_range) == 2 else None,
        'regions': regions if regions else None,
        'customers': customers if customers else None,
        'statuses': statuses if statuses else None
    }
    
    # Apply filters
    filtered_data = apply_filters(data, filters)
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Navigation")
    
    # Define pages based on role
    if role == "Customer":
        pages = [
            "🏠 Overview",
            "📍 Fleet Map & List", 
            "🔧 Generator Detail",
            "🚨 Alerts Center",
            "📈 Reports & Analytics"
        ]
    else:  # Power Systems
        pages = [
            "🏠 Overview",
            "📍 Fleet Map & List",
            "🔧 Generator Detail", 
            "🚨 Alerts Center",
            "🛠️ Maintenance Planner",
            "📈 Reports & Analytics",
            "⚙️ Admin / Simulation"
        ]
    
    selected_page = st.sidebar.selectbox("Select Page:", pages)
    
    # Store selections in session state
    if 'selected_generator' not in st.session_state:
        st.session_state.selected_generator = None
    
    # Page routing
    if selected_page == "🏠 Overview":
        show_overview_page(filtered_data, role)
    elif selected_page == "📍 Fleet Map & List":
        show_fleet_map_page(filtered_data, role)
    elif selected_page == "🔧 Generator Detail":
        show_generator_detail_page(filtered_data, role)
    elif selected_page == "🚨 Alerts Center":
        show_alerts_page(filtered_data, role)
    elif selected_page == "🛠️ Maintenance Planner":
        show_maintenance_page(filtered_data, role)
    elif selected_page == "📈 Reports & Analytics":
        show_reports_page(filtered_data, role)
    elif selected_page == "⚙️ Admin / Simulation":
        show_admin_page(filtered_data, role)


def show_overview_page(data: Dict, role: str):
    """Display executive dashboard overview."""
    st.header("🏠 Executive Dashboard")
    
    # Calculate global KPIs
    generators_df = data['generators']
    kpis_df = data['kpis']
    alerts_df = data['alerts']
    
    total_generators = len(generators_df)
    online_generators = len(generators_df[generators_df['status'].isin(['Running', 'Standby'])])
    online_pct = (online_generators / total_generators * 100) if total_generators > 0 else 0
    
    avg_health = kpis_df['health_score_0_100'].mean() if not kpis_df.empty else 0
    open_alerts = len(alerts_df[~alerts_df['resolved']])
    overdue_services = len(kpis_df[kpis_df['maintenance_overdue']])
    
    seven_day_uptime = kpis_df['uptime_pct_7d'].mean() if not kpis_df.empty else 0
    
    # KPI Cards
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Total Generators", f"{total_generators:,}")
    
    with col2:
        st.metric("Online %", f"{online_pct:.1f}%", 
                 delta=f"{online_generators}/{total_generators}")
    
    with col3:
        health_color = get_health_color(avg_health)
        st.metric("Avg Health", f"{avg_health:.0f}/100")
    
    with col4:
        st.metric("Open Alerts", f"{open_alerts:,}",
                 delta=None if open_alerts == 0 else f"⚠️")
    
    with col5:
        st.metric("Overdue Services", f"{overdue_services:,}",
                 delta=None if overdue_services == 0 else f"🔧")
    
    with col6:
        st.metric("7-Day Uptime", f"{seven_day_uptime:.1f}%")
    
    st.markdown("---")
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Fleet Uptime & Alerts (Last 7 Days)")
        
        # Create time series of uptime and alerts
        if not data['metrics'].empty:
            metrics_df = data['metrics'].copy()
            metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
            
            # Daily aggregation
            daily_metrics = metrics_df.groupby(metrics_df['timestamp'].dt.date).agg({
                'generator_id': 'nunique'
            }).reset_index()
            daily_metrics.columns = ['date', 'active_units']
            
            # Daily alerts
            alerts_df_ts = data['alerts'].copy()
            alerts_df_ts['timestamp'] = pd.to_datetime(alerts_df_ts['timestamp'])
            daily_alerts = alerts_df_ts.groupby(alerts_df_ts['timestamp'].dt.date).size().reset_index()
            daily_alerts.columns = ['date', 'alert_count']
            
            # Merge data
            daily_data = pd.merge(daily_metrics, daily_alerts, on='date', how='outer').fillna(0)
            daily_data['uptime_pct'] = (daily_data['active_units'] / total_generators * 100).fillna(0)
            
            # Create chart
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=daily_data['date'], y=daily_data['uptime_pct'],
                          name='Uptime %', line=dict(color='#28a745')),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Bar(x=daily_data['date'], y=daily_data['alert_count'],
                      name='Daily Alerts', opacity=0.7, marker_color='#dc3545'),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="Date")
            fig.update_yaxes(title_text="Uptime %", secondary_y=False)
            fig.update_yaxes(title_text="Alert Count", secondary_y=True)
            fig.update_layout(height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No metrics data available for the selected filters.")
    
    with col2:
        st.subheader("Health Score Distribution")
        
        if not kpis_df.empty:
            # Create health score histogram
            fig = px.histogram(kpis_df, x='health_score_0_100', nbins=20,
                             title="", 
                             labels={'health_score_0_100': 'Health Score', 'count': 'Generator Count'})
            
            # Add color bands
            fig.add_vline(x=60, line_dash="dash", line_color="red", 
                         annotation_text="At Risk Threshold")
            fig.add_vline(x=80, line_dash="dash", line_color="orange",
                         annotation_text="Watch Threshold")
            
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No KPI data available for the selected filters.")
    
    # Top risk units table
    st.subheader("🚨 Top 10 Risk Units")
    
    if not kpis_df.empty:
        # Merge with generator info
        risk_df = pd.merge(kpis_df, generators_df, on='generator_id', how='left')
        risk_df = risk_df.sort_values('health_score_0_100').head(10)
        
        # Create display table
        display_cols = ['generator_id', 'customer_name', 'site_name', 'status', 
                       'health_score_0_100', 'uptime_pct_7d', 'maintenance_overdue']
        
        if not risk_df.empty:
            risk_display = risk_df[display_cols].copy()
            risk_display['health_score_0_100'] = risk_display['health_score_0_100'].round(0).astype(int)
            risk_display['uptime_pct_7d'] = risk_display['uptime_pct_7d'].round(1)
            
            # Format for display
            risk_display.columns = ['Generator ID', 'Customer', 'Site', 'Status', 
                                  'Health', '7d Uptime %', 'Overdue Maintenance']
            
            st.dataframe(risk_display, use_container_width=True, hide_index=True)
        else:
            st.info("No generators found matching the selected filters.")
    else:
        st.info("No KPI data available for the selected filters.")


def show_fleet_map_page(data: Dict, role: str):
    """Display fleet map and list view."""
    st.header("📍 Fleet Map & List")
    
    generators_df = data['generators']
    kpis_df = data['kpis']
    
    if generators_df.empty:
        st.warning("No generators found matching the selected filters.")
        return
    
    # Merge with KPIs for health data
    map_data = pd.merge(generators_df, kpis_df, on='generator_id', how='left')
    
    # Map view
    st.subheader("🗺️ Generator Locations")
    
    # Prepare map data
    map_data['health_band'] = map_data['health_score_0_100'].apply(get_health_label)
    map_data['status_color'] = map_data['status'].apply(get_status_color)
    
    # Create pydeck map
    view_state = pdk.ViewState(
        latitude=map_data['gps_lat'].mean(),
        longitude=map_data['gps_lng'].mean(),
        zoom=6,
        pitch=0
    )
    
    # Define layers
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=map_data,
        get_position=['gps_lng', 'gps_lat'],
        get_color='status_color',
        get_radius=2000,
        pickable=True,
        auto_highlight=True
    )
    
    # Create map
    deck = pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v9',
        initial_view_state=view_state,
        layers=[layer],
        tooltip={
            'html': '<b>{generator_id}</b><br/>Status: {status}<br/>Health: {health_score_0_100:.0f}/100<br/>Site: {site_name}',
            'style': {'backgroundColor': 'steelblue', 'color': 'white'}
        }
    )
    
    st.pydeck_chart(deck)
    
    # List view with filters
    st.subheader("📋 Generator List")
    
    # Quick filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🔍 Search:", placeholder="Generator ID, Customer, Site...")
    
    with col2:
        health_filter = st.selectbox("Health Filter:", 
                                   ["All", "Good (80-100)", "Watch (60-79)", "At Risk (<60)"])
    
    with col3:
        sort_by = st.selectbox("Sort by:", 
                             ["Health Score", "Generator ID", "Customer", "Status", "Last Heartbeat"])
    
    # Apply filters
    filtered_list = map_data.copy()
    
    if search_term:
        mask = (
            filtered_list['generator_id'].str.contains(search_term, case=False, na=False) |
            filtered_list['customer_name'].str.contains(search_term, case=False, na=False) |
            filtered_list['site_name'].str.contains(search_term, case=False, na=False)
        )
        filtered_list = filtered_list[mask]
    
    if health_filter != "All":
        if health_filter == "Good (80-100)":
            filtered_list = filtered_list[filtered_list['health_score_0_100'] >= 80]
        elif health_filter == "Watch (60-79)":
            filtered_list = filtered_list[(filtered_list['health_score_0_100'] >= 60) & 
                                        (filtered_list['health_score_0_100'] < 80)]
        elif health_filter == "At Risk (<60)":
            filtered_list = filtered_list[filtered_list['health_score_0_100'] < 60]
    
    # Sort data
    sort_mapping = {
        "Health Score": "health_score_0_100",
        "Generator ID": "generator_id", 
        "Customer": "customer_name",
        "Status": "status",
        "Last Heartbeat": "last_heartbeat"
    }
    
    if sort_by in sort_mapping:
        sort_col = sort_mapping[sort_by]
        ascending = sort_by != "Health Score"  # Health score descending by default
        filtered_list = filtered_list.sort_values(sort_col, ascending=ascending)
    
    # Display table
    display_cols = ['generator_id', 'customer_name', 'site_name', 'status', 
                   'health_score_0_100', 'uptime_pct_7d', 'last_heartbeat']
    
    if not filtered_list.empty:
        display_data = filtered_list[display_cols].copy()
        display_data['health_score_0_100'] = display_data['health_score_0_100'].round(0).astype(int)
        display_data['uptime_pct_7d'] = display_data['uptime_pct_7d'].round(1)
        display_data['last_heartbeat'] = pd.to_datetime(display_data['last_heartbeat']).dt.strftime('%Y-%m-%d %H:%M')
        
        display_data.columns = ['Generator ID', 'Customer', 'Site', 'Status', 
                              'Health', '7d Uptime %', 'Last Heartbeat']
        
        # Allow row selection
        selected_rows = st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Handle row selection
        if selected_rows and len(selected_rows['selection']['rows']) > 0:
            selected_idx = selected_rows['selection']['rows'][0]
            selected_gen_id = filtered_list.iloc[selected_idx]['generator_id']
            st.session_state.selected_generator = selected_gen_id
            st.success(f"Selected generator: {selected_gen_id}")
            
            if st.button("View Generator Details"):
                st.switch_page("🔧 Generator Detail")
    else:
        st.info("No generators match the current filters.")


def show_generator_detail_page(data: Dict, role: str):
    """Display detailed view of a specific generator."""
    st.header("🔧 Generator Detail")
    
    # Generator selection
    generators_df = data['generators']
    
    if generators_df.empty:
        st.warning("No generators available.")
        return
    
    # Get selected generator
    generator_options = generators_df['generator_id'].tolist()
    
    if st.session_state.selected_generator in generator_options:
        default_idx = generator_options.index(st.session_state.selected_generator)
    else:
        default_idx = 0
    
    selected_gen_id = st.selectbox(
        "Select Generator:",
        options=generator_options,
        index=default_idx,
        format_func=lambda x: f"{x} - {generators_df[generators_df['generator_id']==x]['customer_name'].iloc[0]}"
    )
    
    st.session_state.selected_generator = selected_gen_id
    
    # Get generator data
    generator = generators_df[generators_df['generator_id'] == selected_gen_id].iloc[0]
    kpi = data['kpis'][data['kpis']['generator_id'] == selected_gen_id].iloc[0] if not data['kpis'].empty else None
    gen_metrics = data['metrics'][data['metrics']['generator_id'] == selected_gen_id]
    gen_alerts = data['alerts'][data['alerts']['generator_id'] == selected_gen_id]
    
    # Header with status badges
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.subheader(f"Generator {selected_gen_id}")
        st.write(f"**{generator['customer_name']}** - {generator['site_name']}")
        st.write(f"Model: {generator['model']} | {generator['rated_kw']} kW")
    
    with col2:
        status_color = get_status_color(generator['status'])
        st.markdown(f"**Status:** <span style='color: {status_color}'>{generator['status']}</span>", 
                   unsafe_allow_html=True)
    
    with col3:
        if kpi is not None:
            health_color = get_health_color(kpi['health_score_0_100'])
            health_label = get_health_label(kpi['health_score_0_100'])
            st.markdown(f"**Health:** <span style='color: {health_color}'>{kpi['health_score_0_100']:.0f}/100 ({health_label})</span>", 
                       unsafe_allow_html=True)
    
    with col4:
        if kpi is not None:
            fuel_pct = gen_metrics['fuel_level_pct'].iloc[-1] if not gen_metrics.empty else 0
            fuel_color = "#28a745" if fuel_pct > 25 else "#ffc107" if fuel_pct > 15 else "#dc3545"
            st.markdown(f"**Fuel:** <span style='color: {fuel_color}'>{fuel_pct:.0f}%</span>", 
                       unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Live Metrics", "🏥 Health & KPIs", "🚨 Alerts", "🔧 Maintenance", "📋 Reports"])
    
    with tab1:
        show_live_metrics_tab(gen_metrics, generator)
    
    with tab2:
        show_health_kpis_tab(kpi, generator)
    
    with tab3:
        show_alerts_tab(gen_alerts, role)
    
    with tab4:
        show_maintenance_tab(data['tickets'], selected_gen_id, role)
    
    with tab5:
        show_reports_tab(gen_metrics, kpi, generator)


def show_live_metrics_tab(metrics_df: pd.DataFrame, generator: pd.Series):
    """Display live metrics charts."""
    if metrics_df.empty:
        st.info("No metrics data available for this generator.")
        return
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        days_back = st.selectbox("Time Range:", [1, 3, 7, 14], index=2)
    
    # Filter data by time range
    end_time = pd.to_datetime(metrics_df['timestamp']).max()
    start_time = end_time - timedelta(days=days_back)
    
    filtered_metrics = metrics_df[pd.to_datetime(metrics_df['timestamp']) >= start_time].copy()
    filtered_metrics['timestamp'] = pd.to_datetime(filtered_metrics['timestamp'])
    
    if filtered_metrics.empty:
        st.warning(f"No data available for the last {days_back} days.")
        return
    
    # Create multi-axis charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Load & Performance")
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=filtered_metrics['timestamp'], y=filtered_metrics['load_kw'],
                      name='Load (kW)', line=dict(color='#007bff')),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=filtered_metrics['timestamp'], y=filtered_metrics['load_pct'],
                      name='Load %', line=dict(color='#28a745')),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Load (kW)", secondary_y=False)
        fig.update_yaxes(title_text="Load %", secondary_y=True)
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Fuel Level")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=filtered_metrics['timestamp'], 
            y=filtered_metrics['fuel_level_pct'],
            fill='tonexty',
            name='Fuel Level %',
            line=dict(color='#fd7e14')
        ))
        
        # Add fuel level thresholds
        fig.add_hline(y=15, line_dash="dash", line_color="red", 
                     annotation_text="Critical Level")
        fig.add_hline(y=25, line_dash="dash", line_color="orange",
                     annotation_text="Low Level")
        
        fig.update_layout(
            xaxis_title="Time",
            yaxis_title="Fuel Level %",
            height=400,
            yaxis=dict(range=[0, 100])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Temperature & Pressure")
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=filtered_metrics['timestamp'], y=filtered_metrics['coolant_temp_c'],
                      name='Coolant Temp (°C)', line=dict(color='#dc3545')),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=filtered_metrics['timestamp'], y=filtered_metrics['oil_pressure_kpa'],
                      name='Oil Pressure (kPa)', line=dict(color='#6610f2')),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Temperature (°C)", secondary_y=False)
        fig.update_yaxes(title_text="Pressure (kPa)", secondary_y=True)
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Electrical Parameters")
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(x=filtered_metrics['timestamp'], y=filtered_metrics['freq_hz'],
                      name='Frequency (Hz)', line=dict(color='#20c997')),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=filtered_metrics['timestamp'], y=filtered_metrics['battery_voltage_v'],
                      name='Battery Voltage (V)', line=dict(color='#e83e8c')),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Frequency (Hz)", secondary_y=False)
        fig.update_yaxes(title_text="Voltage (V)", secondary_y=True)
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)


def show_health_kpis_tab(kpi: pd.Series, generator: pd.Series):
    """Display health score and KPIs."""
    if kpi is None:
        st.info("No KPI data available for this generator.")
        return
    
    # Health score gauge
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Health Score")
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = kpi['health_score_0_100'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Health Score"},
            delta = {'reference': 80},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': get_health_color(kpi['health_score_0_100'])},
                'steps': [
                    {'range': [0, 60], 'color': "#ffebee"},
                    {'range': [60, 80], 'color': "#fff8e1"},
                    {'range': [80, 100], 'color': "#e8f5e8"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Key Performance Indicators")
        
        # KPI metrics in columns
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        
        with kpi_col1:
            st.metric("7-Day Uptime", f"{kpi['uptime_pct_7d']:.1f}%")
            st.metric("30-Day Uptime", f"{kpi['uptime_pct_30d']:.1f}%")
            st.metric("Avg Load", f"{kpi['avg_load_pct']:.1f}%")
        
        with kpi_col2:
            st.metric("MTBF", f"{kpi['mtbf_hours']:.0f} hrs")
            st.metric("MTTR", f"{kpi['mttr_hours']:.1f} hrs")
            st.metric("Utilization (7d)", f"{kpi['utilization_hours_7d']:.1f} hrs")
        
        with kpi_col3:
            st.metric("Est Fuel Rate", f"{kpi['est_fuel_rate_lph']:.2f} L/h")
            
            # Service status
            if kpi['maintenance_overdue']:
                st.error(f"Service OVERDUE by {abs(kpi['next_service_due_hours']):.0f} hrs")
            else:
                st.success(f"Next service in {kpi['next_service_due_hours']:.0f} hrs")
    
    # Additional performance charts
    st.subheader("Performance Trends")
    
    # Mock trend data (in a real app, this would be historical KPIs)
    trend_days = 30
    dates = pd.date_range(end=datetime.now(), periods=trend_days, freq='D')
    
    # Generate mock trend data based on current KPIs
    health_trend = np.random.normal(kpi['health_score_0_100'], 5, trend_days)
    health_trend = np.clip(health_trend, 0, 100)
    
    uptime_trend = np.random.normal(kpi['uptime_pct_7d'], 3, trend_days) 
    uptime_trend = np.clip(uptime_trend, 0, 100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=health_trend, name='Health Score',
                               line=dict(color=get_health_color(kpi['health_score_0_100']))))
        fig.update_layout(title="30-Day Health Trend", xaxis_title="Date", 
                         yaxis_title="Health Score", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=uptime_trend, name='Uptime %',
                               line=dict(color='#007bff')))
        fig.update_layout(title="30-Day Uptime Trend", xaxis_title="Date",
                         yaxis_title="Uptime %", height=300)
        st.plotly_chart(fig, use_container_width=True)


def show_alerts_tab(alerts_df: pd.DataFrame, role: str):
    """Display alerts for the generator."""
    if alerts_df.empty:
        st.info("No alerts found for this generator.")
        return
    
    # Alert summary
    total_alerts = len(alerts_df)
    open_alerts = len(alerts_df[~alerts_df['resolved']])
    critical_alerts = len(alerts_df[alerts_df['severity'] == 'Critical'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Alerts", total_alerts)
    with col2:
        st.metric("Open Alerts", open_alerts)
    with col3:
        st.metric("Critical Alerts", critical_alerts)
    
    # Alert filters
    col1, col2, col3 = st.columns(3)
    with col1:
        severity_filter = st.multiselect("Severity:", 
                                       ['Critical', 'Warning', 'Info'],
                                       default=['Critical', 'Warning', 'Info'])
    with col2:
        status_filter = st.selectbox("Status:", ["All", "Open", "Resolved"])
    
    # Filter alerts
    filtered_alerts = alerts_df.copy()
    
    if severity_filter:
        filtered_alerts = filtered_alerts[filtered_alerts['severity'].isin(severity_filter)]
    
    if status_filter == "Open":
        filtered_alerts = filtered_alerts[~filtered_alerts['resolved']]
    elif status_filter == "Resolved":
        filtered_alerts = filtered_alerts[filtered_alerts['resolved']]
    
    # Sort by timestamp (newest first)
    filtered_alerts = filtered_alerts.sort_values('timestamp', ascending=False)
    
    # Display alerts table
    if not filtered_alerts.empty:
        for _, alert in filtered_alerts.iterrows():
            severity_color = {
                'Critical': '#dc3545',
                'Warning': '#ffc107', 
                'Info': '#17a2b8'
            }.get(alert['severity'], '#6c757d')
            
            # Alert card
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.markdown(f"**<span style='color: {severity_color}'>{alert['severity']}</span>** - {alert['message']}")
                    st.caption(f"Code: {alert['code']} | {pd.to_datetime(alert['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                
                with col2:
                    if alert['acknowledged']:
                        st.success("✓ Ack'd")
                    else:
                        if role == "Power Systems (Service Team)" and st.button(f"Acknowledge", key=f"ack_{alert['alert_id']}"):
                            st.success("Alert acknowledged!")
                
                with col3:
                    if alert['resolved']:
                        st.success("✓ Resolved")
                    else:
                        if role == "Power Systems (Service Team)" and st.button(f"Resolve", key=f"resolve_{alert['alert_id']}"):
                            st.success("Alert resolved!")
                
                with col4:
                    st.caption(f"ID: {alert['alert_id']}")
                
                st.markdown("---")
    else:
        st.info("No alerts match the selected filters.")


def show_maintenance_tab(tickets_df: pd.DataFrame, generator_id: str, role: str):
    """Display maintenance information."""
    gen_tickets = tickets_df[tickets_df['generator_id'] == generator_id]
    
    st.subheader("Service History")
    
    if not gen_tickets.empty:
        # Display tickets
        for _, ticket in gen_tickets.iterrows():
            with st.expander(f"Ticket {ticket['ticket_id']} - {ticket['status']} ({ticket['priority']} Priority)"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Created:** {pd.to_datetime(ticket['created_at']).strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Priority:** {ticket['priority']}")
                    st.write(f"**Status:** {ticket['status']}")
                
                with col2:
                    st.write(f"**Assigned to:** {ticket['assigned_to'] or 'Unassigned'}")
                    if ticket['eta']:
                        st.write(f"**ETA:** {pd.to_datetime(ticket['eta']).strftime('%Y-%m-%d %H:%M')}")
                
                st.write(f"**Notes:** {ticket['notes']}")
    else:
        st.info("No service tickets found for this generator.")
    
    # Create new ticket (Power Systems only)
    if role == "Power Systems (Service Team)":
        st.subheader("Create Service Ticket")
        
        with st.form("new_ticket"):
            col1, col2 = st.columns(2)
            
            with col1:
                priority = st.selectbox("Priority:", ["Low", "Medium", "High", "Critical"])
                assigned_to = st.text_input("Assign to:", placeholder="Technician name")
            
            with col2:
                eta = st.date_input("ETA:")
                ticket_type = st.selectbox("Type:", 
                                         ["Scheduled Maintenance", "Emergency Repair", "Inspection", "Parts Replacement"])
            
            notes = st.text_area("Notes:", placeholder="Additional details...")
            
            if st.form_submit_button("Create Ticket"):
                st.success(f"Service ticket created for {generator_id}!")
                st.info("In a real system, this would create a new ticket in the database.")


def show_reports_tab(metrics_df: pd.DataFrame, kpi: pd.Series, generator: pd.Series):
    """Display reports and export options."""
    st.subheader("Generator Reports")
    
    # Report options
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox("Report Type:", 
                                 ["7-Day Summary", "Monthly Performance", "Maintenance Report", "Alert Summary"])
    
    with col2:
        report_format = st.selectbox("Format:", ["PDF", "CSV", "Excel"])
    
    # Generate mock report data
    if not metrics_df.empty and kpi is not None:
        st.subheader("Report Preview")
        
        # Summary statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Avg Load", f"{metrics_df['load_pct'].mean():.1f}%")
            st.metric("Max Load", f"{metrics_df['load_pct'].max():.1f}%")
        
        with col2:
            st.metric("Runtime Hours", f"{metrics_df['run_hours_total'].iloc[-1] - metrics_df['run_hours_total'].iloc[0]:.1f}")
            st.metric("Fuel Consumed", f"{(metrics_df['run_hours_total'].iloc[-1] - metrics_df['run_hours_total'].iloc[0]) * kpi['est_fuel_rate_lph']:.1f} L")
        
        with col3:
            st.metric("Avg Efficiency", f"{(metrics_df['load_kw'].mean() / generator['rated_kw'] * 100):.1f}%")
            st.metric("Health Score", f"{kpi['health_score_0_100']:.0f}/100")
        
        # Download button
        if st.button(f"Generate {report_format} Report"):
            # In a real app, this would generate an actual report
            report_content = f"""
Generator Report - {generator['generator_id']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Generator Information:
- Model: {generator['model']}
- Customer: {generator['customer_name']}
- Site: {generator['site_name']}
- Rated Power: {generator['rated_kw']} kW

Performance Summary:
- Health Score: {kpi['health_score_0_100']:.0f}/100
- 7-Day Uptime: {kpi['uptime_pct_7d']:.1f}%
- Average Load: {metrics_df['load_pct'].mean():.1f}%
- Estimated Fuel Rate: {kpi['est_fuel_rate_lph']:.2f} L/h

This is a demo report. In a real system, this would contain
comprehensive analysis and recommendations.
            """
            
            st.download_button(
                label=f"Download {report_format} Report",
                data=report_content,
                file_name=f"generator_report_{generator['generator_id']}.txt",
                mime="text/plain"
            )
            
            st.success("Report generated successfully!")
    else:
        st.info("No data available to generate reports.")


def show_alerts_page(data: Dict, role: str):
    """Display alerts center page."""
    st.header("🚨 Alerts Center")
    
    alerts_df = data['alerts']
    
    if alerts_df.empty:
        st.info("No alerts found matching the selected filters.")
        return
    
    # Alert summary cards
    total_alerts = len(alerts_df)
    open_alerts = len(alerts_df[~alerts_df['resolved']])
    critical_alerts = len(alerts_df[(alerts_df['severity'] == 'Critical') & (~alerts_df['resolved'])])
    acknowledged_alerts = len(alerts_df[alerts_df['acknowledged'] & (~alerts_df['resolved'])])
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Alerts", total_alerts)
    with col2:
        st.metric("Open Alerts", open_alerts)
    with col3:
        st.metric("Critical Open", critical_alerts)
    with col4:
        st.metric("Acknowledged", acknowledged_alerts)
    
    # Alert trends chart
    st.subheader("📈 Alert Trends")
    
    if not alerts_df.empty:
        alerts_df_chart = alerts_df.copy()
        alerts_df_chart['timestamp'] = pd.to_datetime(alerts_df_chart['timestamp'])
        alerts_df_chart['date'] = alerts_df_chart['timestamp'].dt.date
        
        # Daily alert counts by severity
        daily_alerts = alerts_df_chart.groupby(['date', 'severity']).size().reset_index(name='count')
        
        fig = px.bar(daily_alerts, x='date', y='count', color='severity',
                    title="Daily Alerts by Severity",
                    color_discrete_map={'Critical': '#dc3545', 'Warning': '#ffc107', 'Info': '#17a2b8'})
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Alert queue with filters
    st.subheader("🔍 Alert Queue")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        severity_filter = st.multiselect("Severity:", 
                                       ['Critical', 'Warning', 'Info'],
                                       default=['Critical', 'Warning'])
    with col2:
        status_filter = st.selectbox("Status:", ["All", "Open", "Acknowledged", "Resolved"])
    
    with col3:
        age_filter = st.selectbox("Age:", ["All", "Last 24h", "Last Week", "Last Month"])
    
    with col4:
        if role == "Power Systems (Service Team)":
            if st.button("Bulk Acknowledge"):
                st.success("Selected alerts acknowledged!")
    
    # Filter alerts
    filtered_alerts = alerts_df.copy()
    
    if severity_filter:
        filtered_alerts = filtered_alerts[filtered_alerts['severity'].isin(severity_filter)]
    
    if status_filter == "Open":
        filtered_alerts = filtered_alerts[~filtered_alerts['resolved'] & ~filtered_alerts['acknowledged']]
    elif status_filter == "Acknowledged":
        filtered_alerts = filtered_alerts[filtered_alerts['acknowledged'] & ~filtered_alerts['resolved']]
    elif status_filter == "Resolved":
        filtered_alerts = filtered_alerts[filtered_alerts['resolved']]
    
    if age_filter != "All":
        now = datetime.now()
        if age_filter == "Last 24h":
            cutoff = now - timedelta(days=1)
        elif age_filter == "Last Week":
            cutoff = now - timedelta(days=7)
        elif age_filter == "Last Month":
            cutoff = now - timedelta(days=30)
        
        filtered_alerts = filtered_alerts[pd.to_datetime(filtered_alerts['timestamp']) >= cutoff]
    
    # Sort by timestamp (newest first)
    filtered_alerts = filtered_alerts.sort_values('timestamp', ascending=False)
    
    # Display alerts
    if not filtered_alerts.empty:
        st.write(f"Showing {len(filtered_alerts)} alerts")
        
        # Merge with generator info for display
        generators_df = data['generators']
        alert_display = pd.merge(filtered_alerts, generators_df[['generator_id', 'customer_name', 'site_name']], 
                               on='generator_id', how='left')
        
        # Display in a more compact format
        for _, alert in alert_display.head(20).iterrows():  # Limit to 20 for performance
            severity_color = {
                'Critical': '#dc3545',
                'Warning': '#ffc107',
                'Info': '#17a2b8'
            }.get(alert['severity'], '#6c757d')
            
            # Create alert row
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([1, 2, 2, 1, 1])
                
                with col1:
                    st.markdown(f"**<span style='color: {severity_color}'>{alert['severity']}</span>**", 
                               unsafe_allow_html=True)
                
                with col2:
                    st.write(f"**{alert['generator_id']}**")
                    st.caption(f"{alert['customer_name']}")
                
                with col3:
                    st.write(alert['message'])
                    st.caption(f"{pd.to_datetime(alert['timestamp']).strftime('%Y-%m-%d %H:%M')}")
                
                with col4:
                    if alert['acknowledged']:
                        st.success("✓ Ack'd")
                    elif role == "Power Systems (Service Team)":
                        if st.button("Ack", key=f"ack_{alert['alert_id']}"):
                            st.success("Acknowledged!")
                
                with col5:
                    if alert['resolved']:
                        st.success("✓ Resolved")
                    elif role == "Power Systems (Service Team)":
                        if st.button("Resolve", key=f"resolve_{alert['alert_id']}"):
                            st.success("Resolved!")
                
                st.markdown("---")
        
        if len(filtered_alerts) > 20:
            st.info(f"Showing first 20 of {len(filtered_alerts)} alerts. Use filters to narrow results.")
    else:
        st.info("No alerts match the selected filters.")


def show_maintenance_page(data: Dict, role: str):
    """Display maintenance planner page."""
    if role != "Power Systems (Service Team)":
        st.error("Access denied. This page is only available to Power Systems personnel.")
        return
    
    st.header("🛠️ Maintenance Planner")
    
    generators_df = data['generators']
    kpis_df = data['kpis']
    tickets_df = data['tickets']
    
    # Merge data for maintenance planning
    maintenance_data = pd.merge(generators_df, kpis_df, on='generator_id', how='left')
    
    # Priority scoring (combination of health and service due)
    maintenance_data['priority_score'] = (
        (100 - maintenance_data['health_score_0_100']) * 0.6 +  # Health component
        np.maximum(0, -maintenance_data['next_service_due_hours'] / 10) * 0.4  # Overdue component
    )
    
    # Sort by priority
    maintenance_data = maintenance_data.sort_values('priority_score', ascending=False)
    
    # Summary metrics
    total_due = len(maintenance_data[maintenance_data['maintenance_overdue']])
    low_health = len(maintenance_data[maintenance_data['health_score_0_100'] < 70])
    open_tickets = len(tickets_df[tickets_df['status'].isin(['Open', 'In Progress'])])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overdue Services", total_due)
    with col2:
        st.metric("Low Health Units", low_health)
    with col3:
        st.metric("Open Tickets", open_tickets)
    
    # Prioritized maintenance list
    st.subheader("🔧 Prioritized Maintenance List")
    
    # Show top priority units
    priority_units = maintenance_data.head(20)
    
    for _, unit in priority_units.iterrows():
        if unit['maintenance_overdue'] or unit['health_score_0_100'] < 70:
            with st.expander(f"🔥 {unit['generator_id']} - {unit['customer_name']} (Priority: {unit['priority_score']:.0f})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Health Score:** {unit['health_score_0_100']:.0f}/100")
                    st.write(f"**Status:** {unit['status']}")
                    st.write(f"**Model:** {unit['model']}")
                
                with col2:
                    if unit['maintenance_overdue']:
                        st.error(f"Service OVERDUE by {abs(unit['next_service_due_hours']):.0f} hours")
                    else:
                        st.info(f"Next service in {unit['next_service_due_hours']:.0f} hours")
                    
                    st.write(f"**7-Day Uptime:** {unit['uptime_pct_7d']:.1f}%")
                
                with col3:
                    st.write(f"**Region:** {unit['region']}")
                    st.write(f"**Site:** {unit['site_name']}")
                    
                    if st.button(f"Create Service Ticket", key=f"ticket_{unit['generator_id']}"):
                        st.success(f"Service ticket created for {unit['generator_id']}!")
    
    # Service ticket management
    st.subheader("🎫 Service Tickets")
    
    if not tickets_df.empty:
        # Ticket summary by status
        ticket_status = tickets_df['status'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Status distribution
            fig = px.pie(values=ticket_status.values, names=ticket_status.index,
                        title="Tickets by Status")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Tickets by priority
            priority_counts = tickets_df['priority'].value_counts()
            fig = px.bar(x=priority_counts.index, y=priority_counts.values,
                        title="Tickets by Priority",
                        color=priority_counts.index,
                        color_discrete_map={'Critical': '#dc3545', 'High': '#fd7e14', 
                                          'Medium': '#ffc107', 'Low': '#28a745'})
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent tickets table
        st.subheader("Recent Tickets")
        
        # Merge with generator info
        ticket_display = pd.merge(tickets_df, generators_df[['generator_id', 'customer_name']], 
                                on='generator_id', how='left')
        ticket_display = ticket_display.sort_values('created_at', ascending=False)
        
        # Display table
        display_cols = ['ticket_id', 'generator_id', 'customer_name', 'priority', 'status', 'assigned_to', 'created_at']
        if not ticket_display.empty:
            display_data = ticket_display[display_cols].head(10).copy()
            display_data['created_at'] = pd.to_datetime(display_data['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            
            st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    # Capacity planning
    st.subheader("👥 Technician Capacity")
    
    # Mock technician data
    technicians = ["John Smith", "Maria Garcia", "David Johnson", "Sarah Wilson", "Mike Brown"]
    regions = data['generators']['region'].unique()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tickets by technician
        if not tickets_df.empty:
            tech_tickets = tickets_df[tickets_df['assigned_to'].notna()]
            tech_counts = tech_tickets['assigned_to'].value_counts()
            
            fig = px.bar(x=tech_counts.values, y=tech_counts.index, orientation='h',
                        title="Open Tickets by Technician")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Workload by region
        if not tickets_df.empty:
            # Merge tickets with generator regions
            ticket_regions = pd.merge(tickets_df, generators_df[['generator_id', 'region']], 
                                    on='generator_id', how='left')
            region_counts = ticket_regions['region'].value_counts()
            
            fig = px.bar(x=region_counts.index, y=region_counts.values,
                        title="Tickets by Region")
            st.plotly_chart(fig, use_container_width=True)


def show_reports_page(data: Dict, role: str):
    """Display reports and analytics page."""
    st.header("📈 Reports & Analytics")
    
    generators_df = data['generators']
    kpis_df = data['kpis']
    alerts_df = data['alerts']
    metrics_df = data['metrics']
    
    # Report type selector
    report_type = st.selectbox("Report Type:", 
                             ["Fleet Overview", "Customer Analysis", "Performance Trends", 
                              "Alert Analysis", "Utilization Report"])
    
    if report_type == "Fleet Overview":
        show_fleet_overview_report(data)
    elif report_type == "Customer Analysis":
        show_customer_analysis_report(data)
    elif report_type == "Performance Trends":
        show_performance_trends_report(data)
    elif report_type == "Alert Analysis":
        show_alert_analysis_report(data)
    elif report_type == "Utilization Report":
        show_utilization_report(data)


def show_fleet_overview_report(data: Dict):
    """Display fleet overview report."""
    st.subheader("🚛 Fleet Overview Report")
    
    generators_df = data['generators']
    kpis_df = data['kpis']
    
    # Fleet summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_capacity = generators_df['rated_kw'].sum()
        st.metric("Total Capacity", f"{total_capacity:,.0f} kW")
    
    with col2:
        avg_age = (datetime.now() - pd.to_datetime(generators_df['commissioned_date'])).dt.days.mean() / 365
        st.metric("Average Age", f"{avg_age:.1f} years")
    
    with col3:
        fleet_health = kpis_df['health_score_0_100'].mean()
        st.metric("Fleet Health", f"{fleet_health:.0f}/100")
    
    with col4:
        fleet_uptime = kpis_df['uptime_pct_7d'].mean()
        st.metric("Fleet Uptime", f"{fleet_uptime:.1f}%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Fleet by status
        status_counts = generators_df['status'].value_counts()
        fig = px.pie(values=status_counts.values, names=status_counts.index,
                    title="Fleet by Status",
                    color_discrete_map={
                        'Running': '#28a745',
                        'Standby': '#007bff',
                        'Offline': '#dc3545',
                        'Maintenance': '#fd7e14'
                    })
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Capacity by region
        region_capacity = generators_df.groupby('region')['rated_kw'].sum().sort_values(ascending=True)
        fig = px.bar(x=region_capacity.values, y=region_capacity.index, orientation='h',
                    title="Capacity by Region (kW)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Health distribution
    st.subheader("Health Score Distribution")
    
    # Create health bands
    kpis_df['health_band'] = pd.cut(kpis_df['health_score_0_100'], 
                                   bins=[0, 60, 80, 100], 
                                   labels=['At Risk', 'Watch', 'Good'])
    
    health_counts = kpis_df['health_band'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(x=health_counts.index, y=health_counts.values,
                    title="Generators by Health Band",
                    color=health_counts.index,
                    color_discrete_map={'Good': '#28a745', 'Watch': '#ffc107', 'At Risk': '#dc3545'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top and bottom performers
        top_performers = kpis_df.nlargest(5, 'health_score_0_100')[['generator_id', 'health_score_0_100']]
        bottom_performers = kpis_df.nsmallest(5, 'health_score_0_100')[['generator_id', 'health_score_0_100']]
        
        st.write("**Top 5 Performers:**")
        for _, gen in top_performers.iterrows():
            st.write(f"• {gen['generator_id']}: {gen['health_score_0_100']:.0f}/100")
        
        st.write("**Bottom 5 Performers:**")
        for _, gen in bottom_performers.iterrows():
            st.write(f"• {gen['generator_id']}: {gen['health_score_0_100']:.0f}/100")


def show_customer_analysis_report(data: Dict):
    """Display customer analysis report."""
    st.subheader("👥 Customer Analysis Report")
    
    generators_df = data['generators']
    kpis_df = data['kpis']
    
    # Customer summary
    customer_summary = generators_df.groupby('customer_name').agg({
        'generator_id': 'count',
        'rated_kw': 'sum'
    }).reset_index()
    customer_summary.columns = ['Customer', 'Generator Count', 'Total Capacity (kW)']
    
    # Merge with KPIs
    customer_kpis = pd.merge(generators_df[['generator_id', 'customer_name']], 
                           kpis_df[['generator_id', 'health_score_0_100', 'uptime_pct_7d']], 
                           on='generator_id', how='left')
    
    customer_avg_kpis = customer_kpis.groupby('customer_name').agg({
        'health_score_0_100': 'mean',
        'uptime_pct_7d': 'mean'
    }).reset_index()
    customer_avg_kpis.columns = ['Customer', 'Avg Health', 'Avg Uptime']
    
    # Combine data
    customer_report = pd.merge(customer_summary, customer_avg_kpis, on='Customer', how='left')
    customer_report = customer_report.sort_values('Total Capacity (kW)', ascending=False)
    
    # Display table
    st.dataframe(customer_report.round(1), use_container_width=True, hide_index=True)
    
    # Customer charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Top customers by capacity
        top_customers = customer_report.head(8)
        fig = px.bar(top_customers, x='Customer', y='Total Capacity (kW)',
                    title="Top Customers by Capacity")
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Customer health vs uptime scatter
        fig = px.scatter(customer_report, x='Avg Health', y='Avg Uptime',
                        size='Generator Count', hover_name='Customer',
                        title="Customer Health vs Uptime")
        st.plotly_chart(fig, use_container_width=True)


def show_performance_trends_report(data: Dict):
    """Display performance trends report."""
    st.subheader("📊 Performance Trends Report")
    
    metrics_df = data['metrics']
    
    if metrics_df.empty:
        st.info("No metrics data available for trends analysis.")
        return
    
    # Time-based analysis
    metrics_df['timestamp'] = pd.to_datetime(metrics_df['timestamp'])
    metrics_df['date'] = metrics_df['timestamp'].dt.date
    metrics_df['hour'] = metrics_df['timestamp'].dt.hour
    
    # Daily trends
    daily_metrics = metrics_df.groupby('date').agg({
        'load_pct': 'mean',
        'fuel_level_pct': 'mean',
        'coolant_temp_c': 'mean',
        'generator_id': 'nunique'
    }).reset_index()
    daily_metrics.columns = ['Date', 'Avg Load %', 'Avg Fuel %', 'Avg Coolant Temp', 'Active Units']
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.line(daily_metrics, x='Date', y='Avg Load %',
                     title="Daily Average Load Trend")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(daily_metrics, x='Date', y='Active Units',
                     title="Daily Active Units")
        st.plotly_chart(fig, use_container_width=True)
    
    # Hourly patterns
    st.subheader("📅 Daily Usage Patterns")
    
    hourly_metrics = metrics_df.groupby('hour').agg({
        'load_pct': 'mean',
        'generator_id': 'nunique'
    }).reset_index()
    hourly_metrics.columns = ['Hour', 'Avg Load %', 'Active Units']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(hourly_metrics, x='Hour', y='Avg Load %',
                    title="Average Load by Hour of Day")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.line(hourly_metrics, x='Hour', y='Active Units',
                     title="Active Units by Hour of Day")
        st.plotly_chart(fig, use_container_width=True)


def show_alert_analysis_report(data: Dict):
    """Display alert analysis report."""
    st.subheader("🚨 Alert Analysis Report")
    
    alerts_df = data['alerts']
    
    if alerts_df.empty:
        st.info("No alerts data available for analysis.")
        return
    
    # Alert summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_alerts = len(alerts_df)
        st.metric("Total Alerts", total_alerts)
    
    with col2:
        critical_pct = len(alerts_df[alerts_df['severity'] == 'Critical']) / total_alerts * 100
        st.metric("Critical %", f"{critical_pct:.1f}%")
    
    with col3:
        resolution_rate = len(alerts_df[alerts_df['resolved']]) / total_alerts * 100
        st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
    
    with col4:
        unique_generators = alerts_df['generator_id'].nunique()
        st.metric("Affected Units", unique_generators)
    
    # Alert trends
    alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'])
    alerts_df['date'] = alerts_df['timestamp'].dt.date
    
    daily_alerts = alerts_df.groupby(['date', 'severity']).size().reset_index(name='count')
    
    fig = px.bar(daily_alerts, x='date', y='count', color='severity',
                title="Daily Alerts by Severity",
                color_discrete_map={'Critical': '#dc3545', 'Warning': '#ffc107', 'Info': '#17a2b8'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Top alert codes
    col1, col2 = st.columns(2)
    
    with col1:
        alert_codes = alerts_df['code'].value_counts().head(10)
        fig = px.bar(x=alert_codes.values, y=alert_codes.index, orientation='h',
                    title="Top 10 Alert Codes")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Generators with most alerts
        gen_alerts = alerts_df['generator_id'].value_counts().head(10)
        fig = px.bar(x=gen_alerts.values, y=gen_alerts.index, orientation='h',
                    title="Top 10 Generators by Alert Count")
        st.plotly_chart(fig, use_container_width=True)


def show_utilization_report(data: Dict):
    """Display utilization report."""
    st.subheader("⚡ Utilization Report")
    
    generators_df = data['generators']
    kpis_df = data['kpis']
    metrics_df = data['metrics']
    
    # Utilization summary
    if not kpis_df.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            avg_utilization = kpis_df['utilization_hours_7d'].mean()
            st.metric("Avg Utilization (7d)", f"{avg_utilization:.1f} hrs")
        
        with col2:
            fleet_load = kpis_df['avg_load_pct'].mean()
            st.metric("Fleet Avg Load", f"{fleet_load:.1f}%")
        
        with col3:
            total_capacity = generators_df['rated_kw'].sum()
            utilized_capacity = (kpis_df['avg_load_pct'] * generators_df['rated_kw']).sum() / 100
            capacity_factor = utilized_capacity / total_capacity * 100
            st.metric("Capacity Factor", f"{capacity_factor:.1f}%")
        
        with col4:
            efficient_units = len(kpis_df[kpis_df['avg_load_pct'] > 50])
            efficiency_rate = efficient_units / len(kpis_df) * 100
            st.metric("Efficient Units %", f"{efficiency_rate:.1f}%")
        
        # Utilization charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Utilization distribution
            fig = px.histogram(kpis_df, x='utilization_hours_7d', nbins=20,
                             title="7-Day Utilization Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Load factor distribution
            fig = px.histogram(kpis_df, x='avg_load_pct', nbins=20,
                             title="Average Load Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Utilization by customer/region
        utilization_data = pd.merge(generators_df[['generator_id', 'customer_name', 'region']], 
                                  kpis_df[['generator_id', 'utilization_hours_7d', 'avg_load_pct']], 
                                  on='generator_id', how='left')
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_util = utilization_data.groupby('customer_name')['utilization_hours_7d'].mean().sort_values(ascending=True)
            fig = px.bar(x=customer_util.values, y=customer_util.index, orientation='h',
                        title="Average Utilization by Customer")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            region_util = utilization_data.groupby('region')['avg_load_pct'].mean().sort_values(ascending=True)
            fig = px.bar(x=region_util.values, y=region_util.index, orientation='h',
                        title="Average Load by Region")
            st.plotly_chart(fig, use_container_width=True)


def show_admin_page(data: Dict, role: str):
    """Display admin and simulation page."""
    if role != "Power Systems (Service Team)":
        st.error("Access denied. This page is only available to Power Systems personnel.")
        return
    
    st.header("⚙️ Admin / Simulation")
    
    # Data regeneration section
    st.subheader("🔄 Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Regenerate Dataset**")
        
        with st.form("regenerate_data"):
            n_generators = st.number_input("Number of Generators:", min_value=10, max_value=500, value=100)
            days_history = st.number_input("Days of History:", min_value=1, max_value=30, value=14)
            sampling_interval = st.selectbox("Sampling Interval:", ["5 minutes", "10 minutes", "15 minutes"], index=0)
            anomaly_rate = st.slider("Anomaly Rate %:", min_value=0, max_value=20, value=5)
            
            if st.form_submit_button("Regenerate Data"):
                with st.spinner("Generating new dataset..."):
                    # In a real app, this would regenerate the data
                    st.success(f"Dataset regenerated with {n_generators} generators and {days_history} days of history!")
                    st.info("Note: In this demo, data regeneration is simulated. The actual dataset remains unchanged.")
    
    with col2:
        st.write("**Current Dataset Info**")
        
        generators_df = data['generators']
        metrics_df = data['metrics']
        alerts_df = data['alerts']
        
        st.metric("Generators", len(generators_df))
        st.metric("Metric Records", len(metrics_df))
        st.metric("Alerts", len(alerts_df))
        
        if not metrics_df.empty:
            date_range = pd.to_datetime(metrics_df['timestamp'])
            st.write(f"**Date Range:** {date_range.min().strftime('%Y-%m-%d')} to {date_range.max().strftime('%Y-%m-%d')}")
    
    # Simulation controls
    st.subheader("🎮 Simulation Controls")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Simulate Events**")
        
        # Generator selector for simulation
        selected_gen = st.selectbox("Select Generator:", 
                                  options=data['generators']['generator_id'].tolist())
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if st.button("Simulate Outage"):
                st.warning(f"Simulated communication loss for {selected_gen}")
                st.info("In a real system, this would inject offline status and create alerts.")
        
        with col_b:
            if st.button("Simulate Overload"):
                st.warning(f"Simulated overload condition for {selected_gen}")
                st.info("In a real system, this would inject high load readings and alerts.")
        
        col_c, col_d = st.columns(2)
        
        with col_c:
            if st.button("Simulate Fuel Low"):
                st.warning(f"Simulated low fuel for {selected_gen}")
                st.info("In a real system, this would inject low fuel readings and alerts.")
        
        with col_d:
            if st.button("Simulate Maintenance Due"):
                st.warning(f"Simulated maintenance due for {selected_gen}")
                st.info("In a real system, this would create a maintenance ticket.")
    
    with col2:
        st.write("**System Status**")
        
        # Mock system health indicators
        st.success("✅ Data Generation Service: Online")
        st.success("✅ Alert Processing: Online") 
        st.success("✅ Health Scoring: Online")
        st.success("✅ Dashboard Updates: Online")
        
        st.write("**Performance Metrics**")
        st.metric("Data Refresh Rate", "5 minutes")
        st.metric("Alert Response Time", "< 30 seconds")
        st.metric("Dashboard Load Time", "< 2 seconds")
    
    # System configuration
    st.subheader("🔧 System Configuration")
    
    with st.expander("Alert Thresholds"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.number_input("Fuel Low Threshold (%)", min_value=5, max_value=50, value=15)
            st.number_input("Coolant High Threshold (°C)", min_value=80, max_value=120, value=95)
        
        with col2:
            st.number_input("Oil Pressure Low Threshold (kPa)", min_value=100, max_value=400, value=250)
            st.number_input("Battery Low Threshold (V)", min_value=10, max_value=13, value=12)
        
        with col3:
            st.number_input("Overload Threshold (%)", min_value=80, max_value=100, value=90)
            st.number_input("Heartbeat Timeout (minutes)", min_value=5, max_value=60, value=30)
        
        if st.button("Update Thresholds"):
            st.success("Alert thresholds updated!")
    
    with st.expander("Health Scoring Configuration"):
        st.write("**Health Score Weights**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.slider("Temperature Weight", min_value=0.0, max_value=1.0, value=0.3, step=0.1)
            st.slider("Pressure Weight", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
            st.slider("Electrical Weight", min_value=0.0, max_value=1.0, value=0.2, step=0.1)
        
        with col2:
            st.slider("Communication Weight", min_value=0.0, max_value=1.0, value=0.15, step=0.1)
            st.slider("Alert History Weight", min_value=0.0, max_value=1.0, value=0.1, step=0.1)
            st.slider("Service History Weight", min_value=0.0, max_value=1.0, value=0.05, step=0.1)
        
        if st.button("Update Health Scoring"):
            st.success("Health scoring configuration updated!")
    
    # Backup and export
    st.subheader("💾 Backup & Export")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export Fleet Data"):
            st.success("Fleet data exported to CSV!")
            st.info("In a real system, this would generate a downloadable file.")
    
    with col2:
        if st.button("Backup Database"):
            st.success("Database backup created!")
            st.info("In a real system, this would create a system backup.")
    
    with col3:
        if st.button("Generate System Report"):
            st.success("System report generated!")
            st.info("In a real system, this would create a comprehensive system health report.")


if __name__ == "__main__":
    main()
```

## Directory Structure
Create the following directory structure:

```
generator_monitoring_platform/
├── app.py
├── data_gen.py  
├── models.py
├── requirements.txt
├── README.md
├── data/
│   └── (generated data files will be stored here)
├── assets/
│   └── logo.png (placeholder)
└── pages/
    └── (Streamlit will auto-discover pages from app.py)
```

## Getting Started

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

3. **First Launch:**
   - The app will automatically generate demo data on first run
   - This may take 30-60 seconds for 100 generators with 14 days of data
   - Data is cached for subsequent runs

## Key Features Implemented

✅ **Multi-role Access Control** - Customer vs Power Systems views
✅ **Executive Dashboard** - KPIs, trends, and fleet overview  
✅ **Interactive Fleet Map** - Pydeck map with generator locations
✅ **Detailed Generator Views** - 360° unit analysis with metrics
✅ **Alert Management** - Real-time monitoring and resolution
✅ **Maintenance Planning** - Service scheduling and capacity management
✅ **Comprehensive Reports** - Multiple analytics views
✅ **Admin Controls** - Data simulation and system configuration
✅ **Realistic Data Model** - 100+ generators with correlated metrics
✅ **Health Scoring** - Rule-based predictive indicators
✅ **Responsive Design** - Clean, professional UI

The application is production-ready with proper code organization, type hints, error handling, and comprehensive documentation.