import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import calendar

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Driver Performance Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - Dark Mode Professional Theme
st.markdown("""
<style>
    /* Main dark background */
    .stApp {
        background-color: #0e1117;
    }

    /* Main header */
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin-bottom: 0.5rem;
        padding: 20px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Section headers */
    .section-header {
        background: linear-gradient(90deg, #00b4d8 0%, #0077b6 100%);
        color: white;
        padding: 12px 20px;
        font-weight: bold;
        font-size: 1rem;
        border-radius: 10px;
        margin-top: 15px;
        box-shadow: 0 4px 15px rgba(0,180,216,0.3);
    }

    /* Performance title box */
    .performance-title {
        background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%);
        color: white;
        text-align: center;
        padding: 20px;
        font-size: 1.4rem;
        font-weight: bold;
        border-radius: 15px;
        margin-bottom: 15px;
        box-shadow: 0 8px 32px rgba(67,97,238,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }

    /* Behaviour box */
    .behaviour-box {
        background: linear-gradient(135deg, #06d6a0 0%, #118ab2 100%);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 10px;
        box-shadow: 0 8px 32px rgba(6,214,160,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .behaviour-box h4 {
        color: white !important;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Safety box */
    .safety-box {
        background: linear-gradient(135deg, #f72585 0%, #7209b7 100%);
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 10px;
        box-shadow: 0 8px 32px rgba(247,37,133,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .safety-box h4 {
        color: white !important;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Dark card style */
    .dark-card {
        background: linear-gradient(145deg, #1a1a2e, #16213e);
        border-radius: 12px;
        padding: 15px;
        border: 1px solid rgba(255,255,255,0.1);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }

    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: bold;
        color: #00d4ff;
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #a0aec0;
    }

    /* DataFrames styling for dark mode */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    /* Table header styling */
    .stDataFrame thead tr th {
        background-color: #1a1a2e !important;
        color: #00d4ff !important;
        border: 1px solid #3a3a5a !important;
        padding: 12px 8px !important;
        font-weight: 600 !important;
    }

    /* Table cell borders */
    .stDataFrame tbody tr td {
        border: 1px solid #3a3a5a !important;
        padding: 10px 8px !important;
        background-color: #0e1117 !important;
    }

    /* Table row hover effect */
    .stDataFrame tbody tr:hover td {
        background-color: #1a1a2e !important;
    }

    /* Alternating row colors */
    .stDataFrame tbody tr:nth-child(even) td {
        background-color: #141821 !important;
    }

    /* Selectbox styling dark */
    .stSelectbox > div > div {
        background-color: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
        color: white;
        font-size: 1.1rem !important;
    }

    .stSelectbox label {
        font-size: 1.1rem !important;
        text-align: center !important;
        width: 100% !important;
        display: block !important;
    }

    /* Table styling - no scroll */
    .stDataFrame {
        width: 100% !important;
    }

    .stDataFrame > div {
        width: 100% !important;
        overflow: visible !important;
    }

    .stDataFrame iframe {
        width: 100% !important;
        min-width: 100% !important;
    }

    [data-testid="stDataFrame"] > div {
        overflow-x: hidden !important;
        width: 100% !important;
    }

    /* Date input styling dark */
    .stDateInput > div > div {
        background-color: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 10px;
    }

    /* Divider dark */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        margin: 25px 0;
    }

    /* Text colors */
    .stMarkdown, p, span, label {
        color: #e0e0e0 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
    }

    /* Info message dark */
    .stAlert {
        background-color: #1a1a2e;
        border: 1px solid rgba(255,255,255,0.1);
        color: #e0e0e0;
    }

    /* Remove ALL borders from containers */
    .stColumns, [data-testid="stHorizontalBlock"], [data-testid="column"],
    .element-container, [data-testid="stVerticalBlock"],
    [data-testid="stVerticalBlock"] > div,
    div[data-testid="metric-container"],
    section[data-testid="stSidebar"],
    .block-container, .main .block-container,
    div.row-widget, div.stBlock {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        border-color: transparent !important;
    }

    /* Remove border from all divs inside main */
    .main > div, .main > div > div, .main > div > div > div {
        border: none !important;
        outline: none !important;
    }

    /* Target specific streamlit elements */
    [data-testid="stAppViewContainer"] > div,
    [data-testid="stHeader"],
    section > div {
        border: none !important;
        outline: none !important;
    }

    /* Remove borders but keep backgrounds */
    [data-testid="stVerticalBlock"] > div,
    [data-testid="column"],
    .element-container {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_database_connection():
    try:
        host = os.getenv('Host', 'swift.cj8i0e86a294.ap-south-1.rds.amazonaws.com')
        username = os.getenv('UserName', 'pradeep')
        password = os.getenv('Password', 'Amit__0411')
        port = os.getenv('Port', '5432')
        database = os.getenv('database_name', 'postgres')
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(
            connection_string,
            connect_args={
                'connect_timeout': 60,
                'options': '-c statement_timeout=120000'
            },
            pool_pre_ping=True,
            pool_recycle=300
        )
        return engine
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

@st.cache_data(ttl=3600, show_spinner=False)
def get_all_drivers(_engine):
    # Only get drivers who have trip data in the last 4 months (including current month)
    query = """
    SELECT DISTINCT driver_name, driver_code, guarantor
    FROM swift_trip_log
    WHERE driver_name IS NOT NULL
    AND driver_code IS NOT NULL
    AND loading_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '3 months'
    ORDER BY driver_name
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error fetching drivers: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_driver_info(_engine, driver_code):
    query = f"""
    SELECT code, name, guarantor, closing_balance, current_vehicle_number, app_date, unsettled_advance
    FROM swift_drivers
    WHERE code = '{driver_code}'
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_all_driver_data(_engine, driver_code, start_date, end_date):
    """Fetch all driver data in a single database connection for better performance."""
    try:
        with _engine.connect() as conn:
            # Query 1: Trip data
            trip_query = f"""
            SELECT * FROM swift_trip_log
            WHERE driver_code = '{driver_code}'
            AND loading_date >= '{start_date}'
            AND loading_date <= '{end_date}'
            ORDER BY loading_date DESC
            """
            trip_result = conn.execute(text(trip_query))
            trip_rows = trip_result.fetchall()
            trip_df = pd.DataFrame(trip_rows, columns=trip_result.keys()) if trip_rows else pd.DataFrame()

            # Query 2: Driver info
            info_query = f"""
            SELECT code, name, guarantor, closing_balance, current_vehicle_number, app_date, unsettled_advance
            FROM swift_drivers
            WHERE code = '{driver_code}'
            """
            info_result = conn.execute(text(info_query))
            info_rows = info_result.fetchall()
            driver_info = pd.DataFrame(info_rows, columns=info_result.keys()) if info_rows else pd.DataFrame()

            # Query 3: Challan data
            challan_query = f"""
            SELECT * FROM challan_data
            WHERE driver_code = '{driver_code}'
            AND challan_date >= '{start_date}'
            AND challan_date <= '{end_date}'
            ORDER BY challan_date DESC
            """
            challan_result = conn.execute(text(challan_query))
            challan_rows = challan_result.fetchall()
            challan_df = pd.DataFrame(challan_rows, columns=challan_result.keys()) if challan_rows else pd.DataFrame()

            # Query 4: Repair data
            repair_query = f"""
            SELECT * FROM deduction_data
            WHERE driver_code = '{driver_code}'
            AND transaction_date >= '{start_date}'
            AND transaction_date <= '{end_date}'
            AND type = 'Repair'
            ORDER BY transaction_date DESC
            """
            repair_result = conn.execute(text(repair_query))
            repair_rows = repair_result.fetchall()
            repair_df = pd.DataFrame(repair_rows, columns=repair_result.keys()) if repair_rows else pd.DataFrame()

            # Query 5: POD damage data
            pod_query = f"""
            SELECT cn.*, stl.loading_date, stl.driver_code
            FROM cn_data cn
            INNER JOIN swift_trip_log stl ON cn.tl_no = stl.tlhs_no
            WHERE stl.driver_code = '{driver_code}'
            AND stl.loading_date >= '{start_date}'
            AND stl.loading_date <= '{end_date}'
            AND (
                cn.pod_status ILIKE '%Delay%'
                OR cn.pod_status ILIKE '%NOT OK%'
                OR cn.pod_status ILIKE '%NOT OKAY%'
            )
            ORDER BY stl.loading_date DESC
            """
            pod_result = conn.execute(text(pod_query))
            pod_rows = pod_result.fetchall()
            pod_damage_df = pd.DataFrame(pod_rows, columns=pod_result.keys()) if pod_rows else pd.DataFrame()

            # Query 6: Safety data (day_wise_gps_km)
            safety_query = f"""
            SELECT * FROM day_wise_gps_km
            WHERE driver_code = '{driver_code}'
            AND date >= '{start_date}'
            AND date <= '{end_date}'
            ORDER BY date DESC
            """
            safety_result = conn.execute(text(safety_query))
            safety_rows = safety_result.fetchall()
            safety_data = pd.DataFrame(safety_rows, columns=safety_result.keys()) if safety_rows else pd.DataFrame()

            # Query 7: Intangles safety data
            intangles_query = f"""
            SELECT * FROM intangles_alert_data
            WHERE driver_code = '{driver_code}'
            AND event_date >= '{start_date}'
            AND event_date <= '{end_date}'
            ORDER BY event_date DESC
            """
            intangles_result = conn.execute(text(intangles_query))
            intangles_rows = intangles_result.fetchall()
            intangles_safety = pd.DataFrame(intangles_rows, columns=intangles_result.keys()) if intangles_rows else pd.DataFrame()

            return {
                'trip_df': trip_df,
                'driver_info': driver_info,
                'challan_df': challan_df,
                'repair_df': repair_df,
                'pod_damage_df': pod_damage_df,
                'safety_data': safety_data,
                'intangles_safety': intangles_safety
            }
    except Exception as e:
        return {
            'trip_df': pd.DataFrame(),
            'driver_info': pd.DataFrame(),
            'challan_df': pd.DataFrame(),
            'repair_df': pd.DataFrame(),
            'pod_damage_df': pd.DataFrame(),
            'safety_data': pd.DataFrame(),
            'intangles_safety': pd.DataFrame()
        }

@st.cache_data(ttl=3600, show_spinner=False)
def get_security_from_excel(driver_code):
    """Get security submitted from Excel file based on driver code."""
    try:
        excel_path = os.path.join(os.path.dirname(__file__), 'Driver Security Receipt:Refund.xlsx')
        df = pd.read_excel(excel_path)
        driver_row = df[df['Driver Code'] == driver_code]
        if not driver_row.empty:
            return driver_row['Driver Security Receipt/Refund'].values[0]
        return 0
    except Exception as e:
        return 0

@st.cache_data(ttl=3600, show_spinner=False)
def get_trip_data(_engine, driver_code, start_date, end_date):
    query = f"""
    SELECT * FROM swift_trip_log
    WHERE driver_code = '{driver_code}'
    AND loading_date >= '{start_date}'
    AND loading_date <= '{end_date}'
    ORDER BY loading_date DESC
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_challan_data(_engine, driver_code, start_date, end_date):
    """Get challan data for a driver using driver_code from challan_data table."""
    query = f"""
    SELECT * FROM challan_data
    WHERE driver_code = '{driver_code}'
    AND challan_date >= '{start_date}'
    AND challan_date <= '{end_date}'
    ORDER BY challan_date DESC
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_pod_damage_data(_engine, driver_code, start_date, end_date):
    """
    Get POD damage data from cn_data table.
    - Filter pod_status containing: 'Delay', 'NOT OK', 'not ok', 'NOT OKAY', 'not okay'
    - Map driver via cn_data.tl_no -> swift_trip_log.trip_log_id -> driver_code
    - Return qty as the damage count
    """
    query = f"""
    SELECT cn.*, stl.loading_date, stl.driver_code
    FROM cn_data cn
    INNER JOIN swift_trip_log stl ON cn.tl_no = stl.tlhs_no
    WHERE stl.driver_code = '{driver_code}'
    AND stl.loading_date >= '{start_date}'
    AND stl.loading_date <= '{end_date}'
    AND (
        cn.pod_status ILIKE '%Delay%'
        OR cn.pod_status ILIKE '%NOT OK%'
        OR cn.pod_status ILIKE '%NOT OKAY%'
    )
    ORDER BY stl.loading_date DESC
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

@st.cache_data(ttl=3600, show_spinner=False)
def get_repair_data(_engine, driver_code, start_date, end_date):
    query = f"""
    SELECT *, COALESCE(voucher_date, doe) as effective_date FROM repair_data
    WHERE driver_code = '{driver_code}'
    AND COALESCE(voucher_date, doe) >= '{start_date}'
    AND COALESCE(voucher_date, doe) <= '{end_date}'
    AND (dr_party NOT ILIKE '%DEF%' OR dr_party IS NULL)
    ORDER BY COALESCE(voucher_date, doe) DESC
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def convert_vehicle_no_to_gps_format(vehicle_no):
    """Convert vehicle number from swift_trip_log format to fvts_vehicles format.
    Example: '9104 HR55AR' -> 'HR55AR9104', '5822NL01AJ' -> 'NL01AJ5822'
    """
    if not vehicle_no:
        return None
    # Remove spaces
    v = vehicle_no.replace(' ', '')
    # Find where letters start (state code like HR, NL, GJ etc)
    for i, c in enumerate(v):
        if c.isalpha():
            # Split into number part and letter part
            num_part = v[:i]
            letter_part = v[i:]
            return letter_part + num_part
    return v

@st.cache_data(ttl=3600, show_spinner=False)
def get_gps_km_for_driver(_engine, driver_code, start_date, end_date):
    """Calculate GPS KM for a driver based on fvts_vehicles odometer data.
    Maps driver to vehicle using swift_trip_log periods.
    """
    try:
        # First, get all trips for this driver with vehicle assignments
        trip_query = f"""
        SELECT vehicle_no, loading_date,
               COALESCE(unloading_date, loading_date + INTERVAL '2 days') as end_date
        FROM swift_trip_log
        WHERE driver_code = '{driver_code}'
        AND loading_date >= '{start_date}'
        AND loading_date <= '{end_date}'
        ORDER BY vehicle_no, loading_date
        """
        with _engine.connect() as conn:
            result = conn.execute(text(trip_query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                trips_df = pd.DataFrame(rows, columns=columns)
            else:
                trips_df = pd.DataFrame()

        if trips_df.empty:
            return {}

        # Convert vehicle numbers to GPS format
        trips_df['gps_vehicle_no'] = trips_df['vehicle_no'].apply(convert_vehicle_no_to_gps_format)
        gps_vehicles = trips_df['gps_vehicle_no'].dropna().unique().tolist()

        if not gps_vehicles:
            return {}

        # Get odometer readings for these vehicles
        vehicles_str = "','".join(gps_vehicles)
        gps_query = f"""
        SELECT vehicle_no, date_time, odometer
        FROM fvts_vehicles
        WHERE vehicle_no IN ('{vehicles_str}')
        AND date_time >= '{start_date}'
        AND date_time <= '{end_date}'
        ORDER BY vehicle_no, date_time
        """
        with _engine.connect() as conn:
            result = conn.execute(text(gps_query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                gps_df = pd.DataFrame(rows, columns=columns)
            else:
                gps_df = pd.DataFrame()

        if gps_df.empty:
            return {}

        # Calculate GPS KM for each trip period
        total_gps_km = 0
        monthly_gps_km = {}

        for _, trip in trips_df.iterrows():
            gps_vehicle = trip['gps_vehicle_no']
            if gps_vehicle is None:
                continue

            trip_gps = gps_df[
                (gps_df['vehicle_no'] == gps_vehicle) &
                (gps_df['date_time'] >= trip['loading_date']) &
                (gps_df['date_time'] <= trip['end_date'])
            ]

            if not trip_gps.empty and len(trip_gps) > 1:
                km_diff = trip_gps['odometer'].max() - trip_gps['odometer'].min()
                if km_diff > 0:
                    total_gps_km += km_diff
                    # Add to monthly total
                    month = pd.to_datetime(trip['loading_date']).strftime('%Y-%m')
                    monthly_gps_km[month] = monthly_gps_km.get(month, 0) + km_diff

        monthly_gps_km['total'] = total_gps_km
        return monthly_gps_km

    except Exception as e:
        return {}

@st.cache_data(ttl=3600, show_spinner=False)
def get_safety_data(_engine, driver_code, start_date, end_date):
    """
    Get safety data (Night Drives and Overspeeding) from day_wise_gps_km table.
    Columns: overspeed, night_drive (need to be added to table)
    Returns dict with monthly counts for night_drives and overspeeding.
    """
    query = f"""
    SELECT TO_CHAR(date, 'YYYY-MM') as month,
           COUNT(CASE WHEN overspeed > 0 THEN 1 END) as overspeed_count,
           COUNT(CASE WHEN night_drive > 0 THEN 1 END) as night_drive_count
    FROM day_wise_gps_km
    WHERE driver_code = '{driver_code}'
    AND date >= '{start_date}'
    AND date <= '{end_date}'
    GROUP BY TO_CHAR(date, 'YYYY-MM')
    ORDER BY month
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()

            monthly_night_drives = {}
            monthly_overspeeding = {}
            total_night_drives = 0
            total_overspeeding = 0

            for row in rows:
                if row[0]:
                    month = row[0]
                    overspeed = int(row[1]) if row[1] else 0
                    night_drive = int(row[2]) if row[2] else 0

                    monthly_overspeeding[month] = overspeed
                    monthly_night_drives[month] = night_drive

                    total_overspeeding += overspeed
                    total_night_drives += night_drive

            monthly_night_drives['total'] = total_night_drives
            monthly_overspeeding['total'] = total_overspeeding

            return {
                'night_drives': monthly_night_drives,
                'overspeeding': monthly_overspeeding
            }
    except Exception as e:
        return {'night_drives': {}, 'overspeeding': {}}

@st.cache_data(ttl=3600, show_spinner=False)
def get_intangles_safety_data(_engine, driver_code, start_date, end_date):
    """
    Get safety data from intangles_alert_logs table.
    Returns:
    - Hard Braking: count of days with hard_brake alerts
    - Freerunning: count of days with freerun alerts
    - Harsh Acceleration: count of over_acc alerts
    - Total Idling Time: sum of (end_time - start_time) for idling alerts in minutes
    - Fuel Consumed while Idling: sum of fuel_consumed for idling alerts
    """
    query = f"""
    SELECT
        TO_CHAR(event_time, 'YYYY-MM') as month,
        COUNT(DISTINCT CASE WHEN alert_type = 'hard_brake' THEN DATE(event_time) END) as hard_brake_days,
        COUNT(DISTINCT CASE WHEN alert_type = 'freerun' THEN DATE(event_time) END) as freerun_days,
        COUNT(CASE WHEN alert_type = 'over_acc' THEN 1 END) as harsh_acc_count,
        COALESCE(SUM(CASE WHEN alert_type = 'idling' AND start_time IS NOT NULL AND end_time IS NOT NULL
                      THEN (end_time - start_time) / 60.0 ELSE 0 END), 0) as idling_time_mins,
        COALESCE(SUM(CASE WHEN alert_type = 'idling' THEN fuel_consumed ELSE 0 END), 0) as idling_fuel
    FROM intangles_alert_logs
    WHERE driver_code = '{driver_code}'
    AND event_time >= '{start_date}'
    AND event_time <= '{end_date}'
    GROUP BY TO_CHAR(event_time, 'YYYY-MM')
    ORDER BY month
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()

            monthly_hard_brake = {}
            monthly_freerun = {}
            monthly_harsh_acc = {}
            monthly_idling_time = {}
            monthly_idling_fuel = {}

            total_hard_brake = 0
            total_freerun = 0
            total_harsh_acc = 0
            total_idling_time = 0
            total_idling_fuel = 0

            for row in rows:
                if row[0]:
                    month = row[0]
                    hard_brake = int(row[1]) if row[1] else 0
                    freerun = int(row[2]) if row[2] else 0
                    harsh_acc = int(row[3]) if row[3] else 0
                    idling_time = float(row[4]) if row[4] else 0
                    idling_fuel = float(row[5]) if row[5] else 0

                    monthly_hard_brake[month] = hard_brake
                    monthly_freerun[month] = freerun
                    monthly_harsh_acc[month] = harsh_acc
                    monthly_idling_time[month] = idling_time
                    monthly_idling_fuel[month] = idling_fuel

                    total_hard_brake += hard_brake
                    total_freerun += freerun
                    total_harsh_acc += harsh_acc
                    total_idling_time += idling_time
                    total_idling_fuel += idling_fuel

            monthly_hard_brake['total'] = total_hard_brake
            monthly_freerun['total'] = total_freerun
            monthly_harsh_acc['total'] = total_harsh_acc
            monthly_idling_time['total'] = total_idling_time
            monthly_idling_fuel['total'] = total_idling_fuel

            return {
                'hard_brake': monthly_hard_brake,
                'freerun': monthly_freerun,
                'harsh_acc': monthly_harsh_acc,
                'idling_time': monthly_idling_time,
                'idling_fuel': monthly_idling_fuel
            }
    except Exception as e:
        return {'hard_brake': {}, 'freerun': {}, 'harsh_acc': {}, 'idling_time': {}, 'idling_fuel': {}}

@st.cache_data(ttl=3600, show_spinner=False)
def get_gps_km_from_daily(_engine, driver_code, start_date, end_date):
    """Get GPS KM data from day_wise_gps_km table grouped by month."""
    query = f"""
    SELECT TO_CHAR(date, 'YYYY-MM') as month, SUM(total_km) as gps_km
    FROM day_wise_gps_km
    WHERE driver_code = '{driver_code}'
    AND date >= '{start_date}'
    AND date <= '{end_date}'
    GROUP BY TO_CHAR(date, 'YYYY-MM')
    ORDER BY month
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            monthly_gps_km = {}
            total_km = 0
            for row in rows:
                if row[0] and row[1]:
                    monthly_gps_km[row[0]] = float(row[1])
                    total_km += float(row[1])
            monthly_gps_km['total'] = total_km
            return monthly_gps_km
    except Exception as e:
        return {}

def calculate_monthly_metrics(df, date_col='loading_date'):
    """Calculate metrics grouped by month."""
    if df.empty:
        return pd.DataFrame()

    df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    df['month'] = df[date_col].dt.to_period('M')

    monthly = df.groupby('month').agg({
        'freight': 'sum',
        'car_qty': 'sum',
        'id': 'count',
        'distance': 'sum',
        'fuel_qty': 'sum',
        'trip_exp_budget': 'sum',
        'tl_cash_advance': 'sum',
        'tl_diesel_advance': 'sum',
        'e_toll': 'sum'
    }).reset_index()

    monthly.columns = ['Month', 'Total Revenue', 'Total Qty', 'Trip Count',
                       'Total KMS', 'Fuel Qty', 'Trip Budget', 'Cash Advance',
                       'Diesel Advance', 'E-Toll']

    return monthly

def calculate_delay(row):
    """
    Calculate if a trip is delayed based on:
    - TT (Transit Time) = distance / 350 (number of days expected)
    - Actual days = unloading_date - loading_date (excluding loading day)
    - If unloading date is Sunday, add 1 day to TT
    - Delay = Actual days > TT
    Returns: 1 if delayed, 0 if on time, None if cannot calculate
    """
    try:
        # Only calculate for loaded trips with valid dates
        if pd.isna(row.get('loading_date')) or pd.isna(row.get('unloading_date')):
            return None
        if pd.isna(row.get('distance')) or row.get('distance', 0) <= 0:
            return None

        loading_date = pd.to_datetime(row['loading_date'])
        unloading_date = pd.to_datetime(row['unloading_date'])
        distance = float(row['distance'])

        # Calculate TT (Transit Time) = distance / 350
        tt = distance / 350

        # If unloading date is Sunday (weekday() == 6), add 1 day to TT
        if unloading_date.weekday() == 6:  # Sunday
            tt += 1

        # Calculate actual days (excluding loading day)
        # This means counting days from day after loading until unloading
        actual_days = (unloading_date - loading_date).days

        # Delay if actual days > TT
        if actual_days > tt:
            return 1  # Delayed
        else:
            return 0  # On time
    except Exception:
        return None

def count_delays_for_trips(df):
    """
    Count total delays for loaded trips in a dataframe.
    Returns count of delayed trips.
    """
    if df.empty:
        return 0

    # Filter only loaded trips
    loaded_df = df[df['trip_status'] == 'Loaded'].copy()

    if loaded_df.empty:
        return 0

    # Apply delay calculation to each row
    loaded_df['is_delayed'] = loaded_df.apply(calculate_delay, axis=1)

    # Count delays (where is_delayed == 1)
    delay_count = loaded_df['is_delayed'].sum()

    return int(delay_count) if pd.notna(delay_count) else 0

def format_month_header(col):
    """Format month column header (2025-12 -> Dec'25)."""
    if isinstance(col, str) and len(col) == 7 and col[4] == '-':
        try:
            year = col[2:4]  # Get last 2 digits of year
            month_num = int(col[5:7])
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            return f"{month_names[month_num-1]}'{year}"
        except:
            return col
    return col

def create_styled_table(df):
    """Create an HTML table with borders and styling."""
    html = """
    <style>
        .perf-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
            margin: 10px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .perf-table th {
            background: linear-gradient(135deg, #0077b6 0%, #00b4d8 100%);
            color: #ffffff;
            padding: 14px 12px;
            text-align: center;
            border: 1px solid #005f8a;
            font-weight: 700;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .perf-table th:first-child {
            text-align: left;
            min-width: 200px;
        }
        .perf-table th:nth-child(2) {
            text-align: left;
            min-width: 120px;
        }
        .perf-table td {
            padding: 12px;
            border: 1px solid #3a3a5a;
            background-color: #0e1117;
            color: #e0e0e0;
            text-align: right;
            font-size: 13px;
        }
        .perf-table td:first-child {
            text-align: left;
            font-weight: 600;
            color: #ffffff;
            background-color: #1a1a2e;
        }
        .perf-table td:nth-child(2) {
            text-align: left;
            color: #a0aec0;
            font-style: italic;
        }
        .perf-table td:last-child {
            background-color: #1a2d3d;
            color: #00d4ff;
            font-weight: 700;
        }
        .perf-table tr:nth-child(even) td {
            background-color: #141821;
        }
        .perf-table tr:nth-child(even) td:first-child {
            background-color: #1e1e32;
        }
        .perf-table tr:nth-child(even) td:last-child {
            background-color: #1e3040;
        }
        .perf-table tr:hover td {
            background-color: #1f2937 !important;
        }
        .perf-table tr:last-child td {
            border-bottom: 2px solid #00b4d8;
        }
    </style>
    <table class="perf-table">
        <thead>
            <tr>
    """
    for col in df.columns:
        formatted_col = format_month_header(col)
        html += f"<th>{formatted_col}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for val in row:
            html += f"<td>{val}</td>"
        html += "</tr>"

    html += "</tbody></table>"
    return html

def create_detail_table(df, title="Details"):
    """Create a styled HTML table for detail views."""
    if df.empty:
        return f"<p style='color: #a0aec0; text-align: center;'>No {title.lower()} data available</p>"

    html = f"""
    <style>
        .detail-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            margin: 10px 0;
            border-radius: 8px;
            overflow: hidden;
        }}
        .detail-table th {{
            background: linear-gradient(135deg, #3a0ca3 0%, #7209b7 100%);
            color: white;
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #5a189a;
            font-weight: 600;
            font-size: 12px;
        }}
        .detail-table td {{
            padding: 8px;
            border: 1px solid #3a3a5a;
            background-color: #1a1a2e;
            color: #e0e0e0;
            text-align: center;
            font-size: 12px;
        }}
        .detail-table tr:nth-child(even) td {{
            background-color: #141821;
        }}
        .detail-table tr:hover td {{
            background-color: #2d2d44;
        }}
    </style>
    <table class="detail-table">
        <thead><tr>
    """
    for col in df.columns:
        html += f"<th>{col}</th>"
    html += "</tr></thead><tbody>"

    for _, row in df.iterrows():
        html += "<tr>"
        for val in row:
            html += f"<td>{val}</td>"
        html += "</tr>"

    html += "</tbody></table>"
    return html

def get_trip_details(trip_df, month=None, loaded_only=True):
    """Get trip details for display. By default shows only Loaded trips."""
    if trip_df.empty:
        return pd.DataFrame()

    df = trip_df.copy()

    # Filter only Loaded trips (matching Loaded Trip Count in performance table)
    if loaded_only:
        df = df[df['trip_status'] == 'Loaded']

    if month and month != 'Total':
        df = df[df['month'] == month]

    if df.empty:
        return pd.DataFrame()

    # Select and rename columns for display (using tlhs_no as Trip ID)
    cols_to_show = ['tlhs_no', 'loading_date', 'route', 'vehicle_no', 'car_qty', 'freight', 'distance']
    available_cols = [c for c in cols_to_show if c in df.columns]
    display_df = df[available_cols].copy()

    if 'loading_date' in display_df.columns:
        display_df['loading_date'] = pd.to_datetime(display_df['loading_date']).dt.strftime('%d-%b-%Y')

    # Rename columns
    col_names = {
        'tlhs_no': 'TL No',
        'loading_date': 'Loading Date',
        'route': 'Route',
        'vehicle_no': 'Vehicle',
        'car_qty': 'Qty',
        'freight': 'Freight (₹)',
        'distance': 'KMs'
    }
    display_df.columns = [col_names.get(c, c) for c in display_df.columns]
    return display_df

def get_repair_details(repair_df, month=None):
    """Get repair details for display."""
    if repair_df.empty:
        return pd.DataFrame()

    df = repair_df.copy()
    df['effective_date'] = pd.to_datetime(df['effective_date'], errors='coerce')
    df['month'] = df['effective_date'].dt.to_period('M').astype(str)

    if month and month != 'Total':
        df = df[df['month'] == month]

    if df.empty:
        return pd.DataFrame()

    # Select columns for display
    cols_to_show = ['voucher_no', 'effective_date', 'vehicle_no', 'dr_party', 'amount', 'narration']
    available_cols = [c for c in cols_to_show if c in df.columns]
    display_df = df[available_cols].copy()

    if 'effective_date' in display_df.columns:
        display_df['effective_date'] = pd.to_datetime(display_df['effective_date']).dt.strftime('%d-%b-%Y')

    display_df.columns = ['Voucher No', 'Date', 'Vehicle', 'Party', 'Amount (₹)', 'Narration'][:len(available_cols)]
    return display_df

def get_delay_details(trip_df, month=None):
    """Get delayed trip details."""
    if trip_df.empty:
        return pd.DataFrame()

    df = trip_df[trip_df['trip_status'] == 'Loaded'].copy()
    if month and month != 'Total':
        df = df[df['month'] == month]

    if df.empty:
        return pd.DataFrame()

    # Calculate delay for each row
    df['is_delayed'] = df.apply(calculate_delay, axis=1)
    delayed_df = df[df['is_delayed'] == 1]

    if delayed_df.empty:
        return pd.DataFrame()

    # Select available columns (using tlhs_no as TL No)
    cols_to_show = ['tlhs_no', 'loading_date', 'unloading_date', 'route', 'vehicle_no', 'distance']
    available_cols = [c for c in cols_to_show if c in delayed_df.columns]
    display_df = delayed_df[available_cols].copy()

    if 'loading_date' in display_df.columns:
        display_df['loading_date'] = pd.to_datetime(display_df['loading_date']).dt.strftime('%d-%b-%Y')
    if 'unloading_date' in display_df.columns:
        display_df['unloading_date'] = pd.to_datetime(display_df['unloading_date']).dt.strftime('%d-%b-%Y')

    # Rename columns
    col_names = {
        'tlhs_no': 'TL No',
        'loading_date': 'Loading Date',
        'unloading_date': 'Unloading Date',
        'route': 'Route',
        'vehicle_no': 'Vehicle',
        'distance': 'Distance'
    }
    display_df.columns = [col_names.get(c, c) for c in display_df.columns]
    return display_df

def get_pod_damage_details(pod_damage_df, month=None):
    """Get POD damage details."""
    if pod_damage_df.empty:
        return pd.DataFrame()

    df = pod_damage_df.copy()
    df['loading_date'] = pd.to_datetime(df['loading_date'], errors='coerce')
    df['month'] = df['loading_date'].dt.to_period('M').astype(str)

    if month and month != 'Total':
        df = df[df['month'] == month]

    if df.empty:
        return pd.DataFrame()

    cols_to_show = ['cn_no', 'loading_date', 'pod_status', 'qty', 'tl_no']
    available_cols = [c for c in cols_to_show if c in df.columns]
    display_df = df[available_cols].copy()

    if 'loading_date' in display_df.columns:
        display_df['loading_date'] = pd.to_datetime(display_df['loading_date']).dt.strftime('%d-%b-%Y')

    display_df.columns = ['CN No', 'Date', 'POD Status', 'Qty', 'TL No'][:len(available_cols)]
    return display_df

def get_challan_details(challan_df, month=None):
    """Get challan details."""
    if challan_df.empty:
        return pd.DataFrame()

    df = challan_df.copy()
    df['challan_date'] = pd.to_datetime(df['challan_date'], errors='coerce')
    df['month'] = df['challan_date'].dt.to_period('M').astype(str)

    if month and month != 'Total':
        df = df[df['month'] == month]

    if df.empty:
        return pd.DataFrame()

    cols_to_show = ['challan_no', 'challan_date', 'vehicle_no', 'amount', 'status']
    available_cols = [c for c in cols_to_show if c in df.columns]
    display_df = df[available_cols].copy()

    if 'challan_date' in display_df.columns:
        display_df['challan_date'] = pd.to_datetime(display_df['challan_date']).dt.strftime('%d-%b-%Y %H:%M')

    display_df.columns = ['Challan No', 'Date', 'Vehicle', 'Amount (₹)', 'Status'][:len(available_cols)]
    return display_df

@st.cache_data(ttl=3600, show_spinner=False)
def get_safety_details(_engine, driver_code, start_date, end_date, safety_type='overspeed'):
    """Get detailed safety data (overspeeding or night drives) from day_wise_gps_km table."""
    column = 'overspeed' if safety_type == 'overspeed' else 'night_drive'
    query = f"""
    SELECT date, vehicle_no, total_km, {column} as count
    FROM day_wise_gps_km
    WHERE driver_code = '{driver_code}'
    AND date >= '{start_date}'
    AND date <= '{end_date}'
    AND {column} > 0
    ORDER BY date DESC
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def format_safety_details(safety_df, month=None):
    """Format safety details for display."""
    if safety_df.empty:
        return pd.DataFrame()

    df = safety_df.copy()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['month'] = df['date'].dt.to_period('M').astype(str)

    if month and month != 'Total':
        df = df[df['month'] == month]

    if df.empty:
        return pd.DataFrame()

    display_df = df[['date', 'vehicle_no', 'total_km', 'count']].copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%d-%b-%Y')
    display_df.columns = ['Date', 'Vehicle', 'Total KM', 'Count']
    return display_df

@st.cache_data(ttl=3600, show_spinner=False)
def get_intangles_details(_engine, driver_code, start_date, end_date, alert_type):
    """Get detailed intangles alert data for a specific alert type."""
    if alert_type == 'idling':
        query = f"""
        SELECT event_time, vehicle_plate, address,
               COALESCE((end_time - start_time) / 60.0, 0) as duration_mins,
               COALESCE(fuel_consumed, 0) as fuel_consumed
        FROM intangles_alert_logs
        WHERE driver_code = '{driver_code}'
        AND alert_type = '{alert_type}'
        AND event_time >= '{start_date}'
        AND event_time <= '{end_date}'
        ORDER BY event_time DESC
        """
    else:
        query = f"""
        SELECT event_time, vehicle_plate, address,
               COALESCE(max_speed, 0) as max_speed,
               COALESCE(distance, 0) as distance
        FROM intangles_alert_logs
        WHERE driver_code = '{driver_code}'
        AND alert_type = '{alert_type}'
        AND event_time >= '{start_date}'
        AND event_time <= '{end_date}'
        ORDER BY event_time DESC
        """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def format_intangles_details(intangles_df, month=None, alert_type='hard_brake'):
    """Format intangles alert details for display."""
    if intangles_df.empty:
        return pd.DataFrame()

    df = intangles_df.copy()
    df['event_time'] = pd.to_datetime(df['event_time'], errors='coerce')
    df['month'] = df['event_time'].dt.to_period('M').astype(str)

    if month and month != 'Total':
        df = df[df['month'] == month]

    if df.empty:
        return pd.DataFrame()

    if alert_type == 'idling':
        display_df = df[['event_time', 'vehicle_plate', 'address', 'duration_mins', 'fuel_consumed']].copy()
        display_df['event_time'] = pd.to_datetime(display_df['event_time']).dt.strftime('%d-%b-%Y %H:%M')
        display_df['duration_mins'] = display_df['duration_mins'].apply(lambda x: f"{x:.1f}")
        display_df['fuel_consumed'] = display_df['fuel_consumed'].apply(lambda x: f"{x:.2f}")
        display_df.columns = ['Date/Time', 'Vehicle', 'Location', 'Duration (mins)', 'Fuel (L)']
    else:
        display_df = df[['event_time', 'vehicle_plate', 'address', 'max_speed', 'distance']].copy()
        display_df['event_time'] = pd.to_datetime(display_df['event_time']).dt.strftime('%d-%b-%Y %H:%M')
        display_df['max_speed'] = display_df['max_speed'].apply(lambda x: f"{x:.1f}")
        display_df['distance'] = display_df['distance'].apply(lambda x: f"{x:.1f}")
        display_df.columns = ['Date/Time', 'Vehicle', 'Location', 'Max Speed', 'Distance (km)']

    return display_df

@st.cache_data(ttl=3600, show_spinner=False)
def get_low_performance_drivers(_engine, start_date, end_date):
    """
    Get all drivers with comprehensive performance metrics matching Overall Performance tab.
    Includes: Revenue, Trips, KMs, Delays, POD Damage, Repair, Advance, Contribution,
    Challans, and Safety metrics.
    """
    query = f"""
    WITH driver_trips AS (
        SELECT
            driver_code,
            driver_name,
            COUNT(CASE WHEN trip_status = 'Loaded' THEN 1 END) as loaded_trip_count,
            COUNT(CASE WHEN trip_status = 'Empty' THEN 1 END) as empty_trip_count,
            SUM(CASE WHEN trip_status = 'Loaded' THEN car_qty ELSE 0 END) as total_qty,
            SUM(CASE WHEN trip_status = 'Loaded' THEN freight ELSE 0 END) as total_revenue,
            SUM(CASE WHEN trip_status = 'Loaded' THEN distance ELSE 0 END) as loaded_kms,
            SUM(CASE WHEN trip_status = 'Empty' THEN distance ELSE 0 END) as empty_kms,
            SUM(distance) as total_running_kms,
            SUM(COALESCE(tl_cash_advance, 0) + COALESCE(tl_diesel_advance, 0) + COALESCE(e_toll, 0)) as total_advance
        FROM swift_trip_log
        WHERE driver_code IS NOT NULL
        AND loading_date >= '{start_date}'
        AND loading_date <= '{end_date}'
        GROUP BY driver_code, driver_name
    ),
    driver_delays AS (
        SELECT
            driver_code,
            COUNT(*) as delay_count
        FROM swift_trip_log
        WHERE driver_code IS NOT NULL
        AND trip_status = 'Loaded'
        AND loading_date >= '{start_date}'
        AND loading_date <= '{end_date}'
        AND unloading_date IS NOT NULL
        AND (
            (distance <= 400 AND unloading_date > loading_date + INTERVAL '2 days') OR
            (distance > 400 AND distance <= 800 AND unloading_date > loading_date + INTERVAL '3 days') OR
            (distance > 800 AND distance <= 1400 AND unloading_date > loading_date + INTERVAL '4 days') OR
            (distance > 1400 AND unloading_date > loading_date + INTERVAL '5 days')
        )
        GROUP BY driver_code
    ),
    driver_pod AS (
        SELECT
            stl.driver_code,
            COUNT(*) as pod_damage_count
        FROM cn_data cn
        JOIN swift_trip_log stl ON cn.tl_no = stl.tlhs_no
        WHERE stl.driver_code IS NOT NULL
        AND stl.loading_date >= '{start_date}'
        AND stl.loading_date <= '{end_date}'
        AND (cn.pod_status ILIKE '%Delay%' OR cn.pod_status ILIKE '%NOT OK%' OR cn.pod_status ILIKE '%NOT OKAY%')
        GROUP BY stl.driver_code
    ),
    driver_challans AS (
        SELECT
            driver_code,
            COUNT(*) as challan_count,
            COALESCE(SUM(amount), 0) as challan_amount
        FROM challan_data
        WHERE driver_code IS NOT NULL
        AND challan_date >= '{start_date}'
        AND challan_date <= '{end_date}'
        GROUP BY driver_code
    ),
    driver_repairs AS (
        SELECT
            stl.driver_code,
            COALESCE(SUM(r.amount), 0) as repair_amount
        FROM repair_data r
        JOIN swift_trip_log stl ON r.vehicle_no = stl.vehicle_no
            AND COALESCE(r.voucher_date, r.doe) >= stl.loading_date
            AND COALESCE(r.voucher_date, r.doe) <= COALESCE(stl.unloading_date, stl.loading_date + INTERVAL '5 days')
        WHERE stl.driver_code IS NOT NULL
        AND COALESCE(r.voucher_date, r.doe) >= '{start_date}'
        AND COALESCE(r.voucher_date, r.doe) <= '{end_date}'
        GROUP BY stl.driver_code
    ),
    driver_gps AS (
        SELECT
            driver_code,
            SUM(total_km) as gps_kms,
            SUM(CASE WHEN overspeed > 0 THEN 1 ELSE 0 END) as overspeed_days,
            SUM(CASE WHEN night_drive > 0 THEN 1 ELSE 0 END) as night_drive_days
        FROM day_wise_gps_km
        WHERE driver_code IS NOT NULL
        AND date >= '{start_date}'
        AND date <= '{end_date}'
        GROUP BY driver_code
    ),
    driver_intangles AS (
        SELECT
            driver_code,
            COUNT(DISTINCT CASE WHEN alert_type = 'hard_brake' THEN DATE(event_time) END) as hard_brake_days,
            COUNT(CASE WHEN alert_type = 'over_acc' THEN 1 END) as harsh_acc_count,
            COUNT(DISTINCT CASE WHEN alert_type = 'freerun' THEN DATE(event_time) END) as freerun_days,
            COALESCE(SUM(CASE WHEN alert_type = 'idling' THEN (end_time - start_time) / 60.0 ELSE 0 END), 0) as idling_time,
            COALESCE(SUM(CASE WHEN alert_type = 'idling' THEN fuel_consumed ELSE 0 END), 0) as idling_fuel
        FROM intangles_alert_logs
        WHERE driver_code IS NOT NULL
        AND event_time >= '{start_date}'
        AND event_time <= '{end_date}'
        GROUP BY driver_code
    )
    SELECT
        dt.driver_code,
        dt.driver_name,
        dt.total_revenue,
        dt.total_qty,
        dt.loaded_trip_count,
        dt.loaded_kms,
        dt.empty_kms,
        dt.total_running_kms,
        COALESCE(dg.gps_kms, 0) as gps_kms,
        COALESCE(dd.delay_count, 0) as delay_count,
        COALESCE(dp.pod_damage_count, 0) as pod_damage_count,
        COALESCE(dr.repair_amount, 0) as repair_amount,
        dt.total_advance,
        (dt.total_revenue - dt.total_advance - COALESCE(dr.repair_amount, 0)) as contribution,
        CASE WHEN dt.total_revenue > 0
            THEN ((dt.total_revenue - dt.total_advance - COALESCE(dr.repair_amount, 0)) * 100.0 / dt.total_revenue)
            ELSE 0 END as contribution_pct,
        COALESCE(dc.challan_count, 0) as challan_count,
        COALESCE(dc.challan_amount, 0) as challan_amount,
        COALESCE(dg.overspeed_days, 0) as overspeed_days,
        COALESCE(dg.night_drive_days, 0) as night_drive_days,
        COALESCE(di.hard_brake_days, 0) as hard_brake_days,
        COALESCE(di.harsh_acc_count, 0) as harsh_acc_count,
        COALESCE(di.freerun_days, 0) as freerun_days,
        COALESCE(di.idling_time, 0) as idling_time,
        COALESCE(di.idling_fuel, 0) as idling_fuel
    FROM driver_trips dt
    LEFT JOIN driver_delays dd ON dt.driver_code = dd.driver_code
    LEFT JOIN driver_pod dp ON dt.driver_code = dp.driver_code
    LEFT JOIN driver_challans dc ON dt.driver_code = dc.driver_code
    LEFT JOIN driver_repairs dr ON dt.driver_code = dr.driver_code
    LEFT JOIN driver_gps dg ON dt.driver_code = dg.driver_code
    LEFT JOIN driver_intangles di ON dt.driver_code = di.driver_code
    WHERE dt.loaded_trip_count > 0
    ORDER BY dt.driver_code
    """
    try:
        with _engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading low performance data: {e}")
        return pd.DataFrame()

def main():
    # Header
    st.markdown('<h1 class="main-header">🚗 Driver Performance Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666;'>Note * These Figures are Based on Loading Data</p>", unsafe_allow_html=True)

    # Connect to database
    engine = get_database_connection()
    if engine is None:
        st.error("Unable to connect to the database.")
        st.stop()

    # Create tabs
    tab1, tab2 = st.tabs(["📊 Overall Performance", "⚠️ Low Performance Driver"])

    with tab1:
        show_overall_performance(engine)

    with tab2:
        show_low_performance_drivers(engine)

def show_low_performance_drivers(engine):
    """Show low performance drivers tab with all metrics from Overall Performance."""
    st.markdown("### ⚠️ Low Performance Drivers")
    st.markdown("*Comprehensive driver performance analysis based on all parameters*")

    # Date range - Last 3 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    st.markdown(f"**Data Period:** {start_date.strftime('%d-%b-%Y')} to {end_date.strftime('%d-%b-%Y')}")

    # Get all drivers performance data
    low_perf_df = get_low_performance_drivers(engine, start_date, end_date)

    if low_perf_df.empty:
        st.info("No performance data available.")
        return

    # Calculate total safety violations
    low_perf_df['total_safety_violations'] = (
        low_perf_df['overspeed_days'] +
        low_perf_df['night_drive_days'] +
        low_perf_df['hard_brake_days'] +
        low_perf_df['harsh_acc_count'] +
        low_perf_df['freerun_days']
    )

    # Summary metrics row 1
    st.markdown("#### 📊 Summary Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Drivers", len(low_perf_df))
    with col2:
        st.metric("Total Trips", int(low_perf_df['loaded_trip_count'].sum()))
    with col3:
        st.metric("Total Revenue", f"₹{low_perf_df['total_revenue'].sum():,.0f}")
    with col4:
        st.metric("Total Challans", int(low_perf_df['challan_count'].sum()))
    with col5:
        st.metric("Safety Violations", int(low_perf_df['total_safety_violations'].sum()))

    # Summary metrics row 2
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Delays", int(low_perf_df['delay_count'].sum()))
    with col2:
        st.metric("POD Damages", int(low_perf_df['pod_damage_count'].sum()))
    with col3:
        st.metric("Repair Cost", f"₹{low_perf_df['repair_amount'].sum():,.0f}")
    with col4:
        st.metric("Challan Amount", f"₹{low_perf_df['challan_amount'].sum():,.0f}")
    with col5:
        avg_contribution = low_perf_df['contribution_pct'].mean()
        st.metric("Avg Contribution %", f"{avg_contribution:.1f}%")

    st.markdown("---")

    # Filter and Sort options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_option = st.selectbox(
            "🔍 Filter By",
            ["All Drivers",
             "Low Contribution (<30%)",
             "High Challans (>3)",
             "High Safety Violations (>20)",
             "High Repair Cost (>₹5,000)",
             "High Delays (>2)",
             "POD Damage Issues"]
        )
    with col2:
        sort_option = st.selectbox(
            "📋 Sort By",
            ["Contribution % (Low to High)",
             "Safety Violations (High to Low)",
             "Challan Count (High to Low)",
             "Repair Amount (High to Low)",
             "Delay Count (High to Low)",
             "Revenue (High to Low)"]
        )
    with col3:
        view_option = st.selectbox(
            "📊 View",
            ["Performance Summary", "Safety Details", "Financial Details", "All Columns"]
        )

    # Apply filters
    filtered_df = low_perf_df.copy()
    if filter_option == "Low Contribution (<30%)":
        filtered_df = filtered_df[filtered_df['contribution_pct'] < 30]
    elif filter_option == "High Challans (>3)":
        filtered_df = filtered_df[filtered_df['challan_count'] > 3]
    elif filter_option == "High Safety Violations (>20)":
        filtered_df = filtered_df[filtered_df['total_safety_violations'] > 20]
    elif filter_option == "High Repair Cost (>₹5,000)":
        filtered_df = filtered_df[filtered_df['repair_amount'] > 5000]
    elif filter_option == "High Delays (>2)":
        filtered_df = filtered_df[filtered_df['delay_count'] > 2]
    elif filter_option == "POD Damage Issues":
        filtered_df = filtered_df[filtered_df['pod_damage_count'] > 0]

    # Apply sort
    sort_map = {
        "Contribution % (Low to High)": ("contribution_pct", True),
        "Safety Violations (High to Low)": ("total_safety_violations", False),
        "Challan Count (High to Low)": ("challan_count", False),
        "Repair Amount (High to Low)": ("repair_amount", False),
        "Delay Count (High to Low)": ("delay_count", False),
        "Revenue (High to Low)": ("total_revenue", False)
    }
    sort_col, ascending = sort_map[sort_option]
    filtered_df = filtered_df.sort_values(sort_col, ascending=ascending)

    st.markdown(f"**Showing {len(filtered_df)} drivers**")

    # Create display based on view option
    if not filtered_df.empty:
        if view_option == "Performance Summary":
            display_cols = ['driver_code', 'driver_name', 'loaded_trip_count', 'total_revenue',
                           'total_running_kms', 'contribution', 'contribution_pct']
            col_names = ['Code', 'Driver Name', 'Trips', 'Revenue', 'Total KMs', 'Contribution', 'Contrib %']
        elif view_option == "Safety Details":
            display_cols = ['driver_code', 'driver_name', 'overspeed_days', 'night_drive_days',
                           'hard_brake_days', 'harsh_acc_count', 'freerun_days', 'total_safety_violations']
            col_names = ['Code', 'Driver Name', 'Overspeed', 'Night Drive', 'Hard Brake', 'Harsh Acc', 'Freerun', 'Total']
        elif view_option == "Financial Details":
            display_cols = ['driver_code', 'driver_name', 'total_revenue', 'total_advance',
                           'repair_amount', 'challan_count', 'challan_amount', 'contribution_pct']
            col_names = ['Code', 'Driver Name', 'Revenue', 'Advance', 'Repair', 'Challans', 'Challan Amt', 'Contrib %']
        else:  # All Columns
            display_cols = ['driver_code', 'driver_name', 'loaded_trip_count', 'total_revenue',
                           'total_running_kms', 'delay_count', 'pod_damage_count', 'repair_amount',
                           'challan_count', 'total_safety_violations', 'contribution_pct']
            col_names = ['Code', 'Name', 'Trips', 'Revenue', 'KMs', 'Delays', 'POD', 'Repair',
                        'Challans', 'Safety', 'Contrib %']

        display_filtered = filtered_df[display_cols].copy()

        # Format columns
        for col in display_filtered.columns:
            if col in ['total_revenue', 'total_advance', 'repair_amount', 'challan_amount', 'contribution']:
                display_filtered[col] = display_filtered[col].apply(lambda x: f"₹{x:,.0f}")
            elif col in ['total_running_kms', 'loaded_kms', 'empty_kms', 'gps_kms']:
                display_filtered[col] = display_filtered[col].apply(lambda x: f"{x:,.0f}")
            elif col == 'contribution_pct':
                display_filtered[col] = display_filtered[col].apply(lambda x: f"{x:.1f}%")

        display_filtered.columns = col_names
        st.markdown(create_detail_table(display_filtered, "Driver Performance"), unsafe_allow_html=True)
    else:
        st.info("No drivers match the selected filter criteria.")

def show_overall_performance(engine):
    """Show overall performance tab (existing dashboard)."""

    # Get all drivers
    all_drivers = get_all_drivers(engine)
    if all_drivers.empty:
        st.error("No drivers found in database. Please check database connection.")
        return

    # Driver Selector Section
    st.markdown("---")

    # Center the dropdown with smaller width
    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        driver_options = [f"{row['driver_name']}[{row['driver_code']}]" for _, row in all_drivers.iterrows()]
        # Set default to D1216 (MUFID ALI)
        default_index = 0
        for i, option in enumerate(driver_options):
            if 'D1216' in option:
                default_index = i
                break
        selected_driver = st.selectbox("**Select Driver with Code >>**", driver_options, index=default_index, key="driver_select")

    # Extract driver code
    driver_code = selected_driver.split("[")[-1].replace("]", "").strip()
    driver_name = selected_driver.split("[")[0].strip()

    # Get guarantor
    driver_row = all_drivers[all_drivers['driver_code'] == driver_code]
    guarantor = driver_row['guarantor'].values[0] if not driver_row.empty and pd.notna(driver_row['guarantor'].values[0]) else "N/A"

    # Set default date range
    start_date = datetime(2025, 9, 1)
    end_date = datetime.now()

    # Initialize session state for caching driver data
    if 'cached_driver_code' not in st.session_state:
        st.session_state.cached_driver_code = None
        st.session_state.cached_data = {}

    # Check if we need to fetch new data (driver changed or no cache)
    need_fetch = (st.session_state.cached_driver_code != driver_code or
                  not st.session_state.cached_data)

    if need_fetch:
        with st.spinner(f'Loading data for {driver_name}...'):
            # Fetch all data in single connection (faster)
            all_data = get_all_driver_data(engine, driver_code, start_date, end_date)

            trip_df = all_data['trip_df']
            if trip_df.empty:
                st.warning(f"No trip data found for {driver_name} [{driver_code}] in the selected date range.")
                return

            driver_info = all_data['driver_info']
            challan_df = all_data['challan_df']
            repair_df = all_data['repair_df']
            pod_damage_df = all_data['pod_damage_df']
            safety_data = all_data['safety_data']
            intangles_safety = all_data['intangles_safety']

            # Store in session state
            st.session_state.cached_driver_code = driver_code
            st.session_state.cached_data = {
                'trip_df': trip_df,
                'driver_info': driver_info,
                'challan_df': challan_df,
                'repair_df': repair_df,
                'pod_damage_df': pod_damage_df,
                'safety_data': safety_data,
                'intangles_safety': intangles_safety
            }

    # Use cached data
    trip_df = st.session_state.cached_data['trip_df']
    driver_info = st.session_state.cached_data['driver_info']
    challan_df = st.session_state.cached_data['challan_df']
    repair_df = st.session_state.cached_data['repair_df']
    pod_damage_df = st.session_state.cached_data['pod_damage_df']
    safety_data = st.session_state.cached_data['safety_data']
    intangles_safety = st.session_state.cached_data['intangles_safety']

    closing_balance = driver_info['closing_balance'].values[0] if not driver_info.empty else 0

    # Get vehicles used by driver
    vehicle_nos = trip_df['vehicle_no'].dropna().unique().tolist()

    # Convert dates
    trip_df['loading_date'] = pd.to_datetime(trip_df['loading_date'], errors='coerce')
    trip_df['month'] = trip_df['loading_date'].dt.to_period('M').astype(str)

    # Calculate months for performance table (current month + last 3 months)
    current_date = datetime.now()
    display_months = []
    for i in range(3, -1, -1):  # 3, 2, 1, 0 months ago
        year = current_date.year
        month = current_date.month - i
        if month <= 0:
            month += 12
            year -= 1
        month_str = f"{year}-{month:02d}"
        display_months.append(month_str)

    # Get vehicles run only in the displayed months from swift_trip_log
    trip_df_filtered = trip_df[trip_df['month'].isin(display_months)]
    vehicles_in_display_months = trip_df_filtered['vehicle_no'].dropna().unique().tolist()

    # === HEADER INFO ===
    # Get Appointment Date from swift_drivers
    appt_date = "N/A"
    if not driver_info.empty and 'app_date' in driver_info.columns and pd.notna(driver_info['app_date'].values[0]):
        appt_date = pd.to_datetime(driver_info['app_date'].values[0]).strftime('%d/%m/%Y')

    # Get Security Submitted from Excel
    security = get_security_from_excel(driver_code)

    # Get Unsettled Advance from swift_drivers
    unsettled_advance = driver_info['unsettled_advance'].values[0] if not driver_info.empty and 'unsettled_advance' in driver_info.columns and pd.notna(driver_info['unsettled_advance'].values[0]) else 0

    # Get Current Vehicle from swift_drivers
    current_vehicle = driver_info['current_vehicle_number'].values[0] if not driver_info.empty and 'current_vehicle_number' in driver_info.columns and pd.notna(driver_info['current_vehicle_number'].values[0]) else "N/A"

    # Exclude current vehicle from vehicles run list (only vehicles from displayed months)
    other_vehicles = [v for v in vehicles_in_display_months if v != current_vehicle]

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        st.markdown(f"""
        <div style="background: #2d1f3d; padding: 20px; border-radius: 12px; border-left: 5px solid #9b59b6;">
            <p style="margin:0; color: #bbb; font-size: 0.95rem;">Current Vehicle</p>
            <p style="margin: 8px 0 0 0; font-weight: bold; font-size: 1.3rem; color: #bb8fce;">{current_vehicle}</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: #1a2d3d; padding: 20px; border-radius: 12px; border-left: 5px solid #3498db;">
            <p style="margin:0; color: #bbb; font-size: 0.95rem;">Guarantor</p>
            <p style="margin: 8px 0 0 0; font-weight: bold; font-size: 1.1rem; color: #5dade2;">{guarantor}</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: #1a3d35; padding: 20px; border-radius: 12px; border-left: 5px solid #06d6a0;">
            <p style="margin:0; color: #bbb; font-size: 0.95rem;">Closing Balance</p>
            <p style="margin: 8px 0 0 0; font-weight: bold; font-size: 1.3rem; color: #58d68d;">₹{closing_balance:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div style="background: #3d3a1a; padding: 20px; border-radius: 12px; border-left: 5px solid #ffd60a;">
            <p style="margin:0; color: #bbb; font-size: 0.95rem;">Appointment Date</p>
            <p style="margin: 8px 0 0 0; font-weight: bold; font-size: 1.3rem; color: #f7dc6f;">{appt_date}</p>
        </div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div style="background: #3d1a2a; padding: 20px; border-radius: 12px; border-left: 5px solid #f72585;">
            <p style="margin:0; color: #bbb; font-size: 0.95rem;">Security Submitted</p>
            <p style="margin: 8px 0 0 0; font-weight: bold; font-size: 1.3rem; color: #f1948a;">₹{security:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col6:
        st.markdown(f"""
        <div style="background: #3d2a1a; padding: 20px; border-radius: 12px; border-left: 5px solid #ff6b35;">
            <p style="margin:0; color: #bbb; font-size: 0.95rem;">Unsettled Advance</p>
            <p style="margin: 8px 0 0 0; font-weight: bold; font-size: 1.3rem; color: #f5b041;">₹{unsettled_advance:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    with col7:
        other_vehicles_display = ', '.join(other_vehicles[:3]) + ('...' if len(other_vehicles) > 3 else '') if other_vehicles else "None"
        st.markdown(f"""
        <div style="background: #1a3d3d; padding: 20px; border-radius: 12px; border-left: 5px solid #00d4ff;">
            <p style="margin:0; color: #bbb; font-size: 0.95rem;">Vehicles Run</p>
            <p style="margin: 8px 0 0 0; font-weight: bold; color: #85c1e9; font-size: 1rem;">{other_vehicles_display}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # === PERFORMANCE SECTION ===
    st.markdown(f"""
    <div class="performance-title">
        Performance<br/>of<br/>{driver_name}[{driver_code}]
    </div>
    """, unsafe_allow_html=True)

    # Use display_months calculated earlier (last 4 months)
    months = display_months

    # Get GPS KM data for the driver from day_wise_gps_km table
    gps_km_data = get_gps_km_from_daily(engine, driver_code, start_date, end_date)

    # Performance metrics table
    metrics_data = {
        'Event': ['Total Revenue', 'Total no. Qty', 'Loaded Trip Count', 'Loaded KMS',
                  'Empty KMS', 'Total Running KMs', 'GPS KMs', 'Total Delays', 'POD Damage',
                  'Total Repair Cost', 'Total Cash/Diesel Advance & E-Toll Given', 'Total Contribution', 'Contribution %'],
        'Measurement': ['In Rs', 'In No of Cars Lifted', 'In No. of Trips', 'In KM', 'In KM', 'In KM',
                       'In KM', 'In No. of Trips', 'In No of Cars', 'In Rs', 'In Rs', 'In Rs', '%']
    }

    for month in months:
        month_df = trip_df[trip_df['month'] == month]
        loaded_df = month_df[month_df['trip_status'] == 'Loaded']
        empty_df = month_df[month_df['trip_status'] == 'Empty']

        total_revenue = month_df['freight'].sum()
        total_qty = month_df['car_qty'].sum()
        loaded_trips = len(loaded_df)
        loaded_kms = loaded_df['distance'].sum()
        empty_kms = empty_df['distance'].sum()
        total_kms = month_df['distance'].sum()

        # Repair cost for this month
        month_repair = repair_df[pd.to_datetime(repair_df['effective_date']).dt.to_period('M').astype(str) == month] if not repair_df.empty else pd.DataFrame()
        repair_cost = month_repair['amount'].sum() if not month_repair.empty else 0

        advance_given = month_df['tl_cash_advance'].sum() + month_df['tl_diesel_advance'].sum() + month_df['e_toll'].sum()
        contribution = total_revenue - repair_cost - advance_given
        contribution_pct = (contribution / total_revenue * 100) if total_revenue > 0 else 0

        # GPS KM for this month
        gps_km_month = gps_km_data.get(month, 0)

        # Calculate delays for this month (only loaded trips)
        month_delays = count_delays_for_trips(month_df)

        # Calculate POD damage qty for this month
        if not pod_damage_df.empty:
            pod_damage_df_temp = pod_damage_df.copy()
            pod_damage_df_temp['loading_date'] = pd.to_datetime(pod_damage_df_temp['loading_date'], errors='coerce')
            pod_damage_df_temp['month'] = pod_damage_df_temp['loading_date'].dt.to_period('M').astype(str)
            month_pod_damage = pod_damage_df_temp[pod_damage_df_temp['month'] == month]
            pod_damage_qty = month_pod_damage['qty'].sum() if not month_pod_damage.empty and 'qty' in month_pod_damage.columns else 0
        else:
            pod_damage_qty = 0

        metrics_data[month] = [
            f"₹{total_revenue:,.0f}",
            f"{total_qty:.0f}",
            f"{loaded_trips}",
            f"{loaded_kms:,.0f}",
            f"{empty_kms:,.0f}",
            f"{total_kms:,.0f}",
            f"{gps_km_month:,.0f}",
            f"{month_delays}",  # Delays calculated
            f"{int(pod_damage_qty)}",  # POD Damage qty
            f"₹{repair_cost:,.0f}",
            f"₹{advance_given:,.0f}",
            f"₹{contribution:,.0f}",
            f"{contribution_pct:.2f}%"
        ]

    # Calculate totals
    total_revenue = trip_df['freight'].sum()
    total_qty = trip_df['car_qty'].sum()
    loaded_trips = len(trip_df[trip_df['trip_status'] == 'Loaded'])
    loaded_kms = trip_df[trip_df['trip_status'] == 'Loaded']['distance'].sum()
    empty_kms = trip_df[trip_df['trip_status'] == 'Empty']['distance'].sum()
    total_kms = trip_df['distance'].sum()
    total_gps_km = gps_km_data.get('total', 0)
    total_repair = repair_df['amount'].sum() if not repair_df.empty else 0
    total_advance = trip_df['tl_cash_advance'].sum() + trip_df['tl_diesel_advance'].sum() + trip_df['e_toll'].sum()
    total_contribution = total_revenue - total_repair - total_advance
    total_contribution_pct = (total_contribution / total_revenue * 100) if total_revenue > 0 else 0

    # Calculate total delays for all loaded trips
    total_delays = count_delays_for_trips(trip_df)

    # Calculate total POD damage qty
    total_pod_damage = pod_damage_df['qty'].sum() if not pod_damage_df.empty and 'qty' in pod_damage_df.columns else 0

    metrics_data['Total'] = [
        f"₹{total_revenue:,.0f}",
        f"{total_qty:.0f}",
        f"{loaded_trips}",
        f"{loaded_kms:,.0f}",
        f"{empty_kms:,.0f}",
        f"{total_kms:,.0f}",
        f"{total_gps_km:,.0f}",
        f"{total_delays}",  # Total delays calculated
        f"{int(total_pod_damage)}",  # Total POD Damage qty
        f"₹{total_repair:,.0f}",
        f"₹{total_advance:,.0f}",
        f"₹{total_contribution:,.0f}",
        f"{total_contribution_pct:.2f}%"
    ]

    perf_df = pd.DataFrame(metrics_data)
    st.markdown(create_styled_table(perf_df), unsafe_allow_html=True)

    # Average metrics with dark mode styling (based on last 3 months, excluding current month)
    avg_months = months[:-1] if len(months) > 1 else months  # Exclude current month
    avg_trip_df = trip_df[trip_df['month'].isin(avg_months)]
    avg_repair_df = repair_df[pd.to_datetime(repair_df['effective_date']).dt.to_period('M').astype(str).isin(avg_months)] if not repair_df.empty else pd.DataFrame()

    avg_revenue = avg_trip_df['freight'].sum()
    avg_kms = avg_trip_df['distance'].sum()
    avg_repair = avg_repair_df['amount'].sum() if not avg_repair_df.empty else 0
    num_avg_months = len(avg_months) if avg_months else 1

    st.markdown("### 📊 Monthly Averages (Last 3 Months)")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4361ee 0%, #3a0ca3 100%); padding: 25px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 8px 32px rgba(67,97,238,0.4); border: 1px solid rgba(255,255,255,0.1);">
            <p style="margin:0; font-size: 0.9rem; opacity: 0.9;">Average Revenue Per Month</p>
            <h2 style="margin: 12px 0 0 0; font-size: 1.8rem; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">₹{avg_revenue/num_avg_months:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #06d6a0 0%, #118ab2 100%); padding: 25px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 8px 32px rgba(6,214,160,0.4); border: 1px solid rgba(255,255,255,0.1);">
            <p style="margin:0; font-size: 0.9rem; opacity: 0.9;">Average Running Kms Per Month</p>
            <h2 style="margin: 12px 0 0 0; font-size: 1.8rem; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">{avg_kms/num_avg_months:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #f72585 0%, #7209b7 100%); padding: 25px; border-radius: 15px; text-align: center; color: white; box-shadow: 0 8px 32px rgba(247,37,133,0.4); border: 1px solid rgba(255,255,255,0.1);">
            <p style="margin:0; font-size: 0.9rem; opacity: 0.9;">Average Repair Cost Per Month</p>
            <h2 style="margin: 12px 0 0 0; font-size: 1.8rem; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">₹{avg_repair/num_avg_months:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # === BEHAVIOUR AND SAFETY SECTIONS ===
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="behaviour-box">
            <h4 style="text-align:center; color:#2874a6;">Behaviour<br/>of<br/>{driver_name}[{driver_code}]</h4>
        </div>
        """, unsafe_allow_html=True)

        # Behaviour metrics - Month-wise
        behaviour_data = {
            'Event': ['Driver At Home Count', 'Driver At Home Days', 'Total Challan Count',
                     'Total Challan Amount', 'Total Repair Cost', 'Branch Repair', 'Enroute Repair'],
            'Measurement': ['Count (no. Of Times)', 'No. Of Days', 'In No. of Times',
                           'In Rs', 'In Rs', 'In Rs', 'In Rs']
        }

        # Add challan month column if not exists
        if not challan_df.empty:
            challan_df_temp = challan_df.copy()
            challan_df_temp['challan_date'] = pd.to_datetime(challan_df_temp['challan_date'], errors='coerce')
            challan_df_temp['month'] = challan_df_temp['challan_date'].dt.to_period('M').astype(str)
        else:
            challan_df_temp = pd.DataFrame()

        # Add repair month column if not exists
        if not repair_df.empty:
            repair_df_temp = repair_df.copy()
            repair_df_temp['effective_date'] = pd.to_datetime(repair_df_temp['effective_date'], errors='coerce')
            repair_df_temp['month'] = repair_df_temp['effective_date'].dt.to_period('M').astype(str)
        else:
            repair_df_temp = pd.DataFrame()

        # Calculate month-wise behaviour metrics
        for month in months:
            # Challan data for this month
            month_challan = challan_df_temp[challan_df_temp['month'] == month] if not challan_df_temp.empty else pd.DataFrame()
            challan_count_month = len(month_challan)
            challan_amount_month = month_challan['amount'].sum() if not month_challan.empty else 0

            # Repair data for this month
            month_repair_df = repair_df_temp[repair_df_temp['month'] == month] if not repair_df_temp.empty else pd.DataFrame()
            repair_cost_month = month_repair_df['amount'].sum() if not month_repair_df.empty else 0
            branch_repair_month = month_repair_df[month_repair_df['dr_party'].str.contains('Branch', case=False, na=False)]['amount'].sum() if not month_repair_df.empty else 0
            enroute_repair_month = month_repair_df[month_repair_df['dr_party'].str.contains('Enroute', case=False, na=False)]['amount'].sum() if not month_repair_df.empty else 0

            behaviour_data[month] = [
                "0",  # At Home Count
                "0",  # At Home Days
                f"{challan_count_month}",
                f"₹{challan_amount_month:,.0f}",
                f"₹{repair_cost_month:,.0f}",
                f"₹{branch_repair_month:,.0f}",
                f"₹{enroute_repair_month:,.0f}"
            ]

        # Calculate totals
        challan_count = len(challan_df) if not challan_df.empty else 0
        challan_amount = challan_df['amount'].sum() if not challan_df.empty else 0
        branch_repair = repair_df[repair_df['dr_party'].str.contains('Branch', case=False, na=False)]['amount'].sum() if not repair_df.empty else 0
        enroute_repair = repair_df[repair_df['dr_party'].str.contains('Enroute', case=False, na=False)]['amount'].sum() if not repair_df.empty else 0

        behaviour_data['Total'] = [
            "0",  # At Home Count - would need attendance data
            "0",  # At Home Days
            f"{challan_count}",
            f"₹{challan_amount:,.0f}",
            f"₹{total_repair:,.0f}",
            f"₹{branch_repair:,.0f}",
            f"₹{enroute_repair:,.0f}"
        ]

        behaviour_df = pd.DataFrame(behaviour_data)
        st.markdown(create_styled_table(behaviour_df), unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="safety-box">
            <h4 style="text-align:center; color:#d4ac0d;">Safety Parameter<br/>of<br/>{driver_name}[{driver_code}]</h4>
        </div>
        """, unsafe_allow_html=True)

        # Safety metrics - Month-wise from day_wise_gps_km and intangles_alert_logs tables
        safety_table_data = {
            'Event': [
                'Harsh Driving / Overspeeding',
                'Night Drives',
                'Hard Braking',
                'Harsh Acceleration',
                'Freerunning Count',
                'Total Idling Time',
                'Fuel Consumed while Idling'
            ],
            'Measurement': [
                'In No. of Days',
                'In No. of Days',
                'In No. of Days',
                'In No. of Times',
                'In No. of Days',
                'In Minutes',
                'In Litres'
            ]
        }

        # Add month-wise columns for safety
        for month in months:
            overspeed_count = safety_data['overspeeding'].get(month, 0)
            night_drive_count = safety_data['night_drives'].get(month, 0)
            hard_brake_count = intangles_safety['hard_brake'].get(month, 0)
            harsh_acc_count = intangles_safety['harsh_acc'].get(month, 0)
            freerun_count = intangles_safety['freerun'].get(month, 0)
            idling_time = intangles_safety['idling_time'].get(month, 0)
            idling_fuel = intangles_safety['idling_fuel'].get(month, 0)

            safety_table_data[month] = [
                f"{overspeed_count}",
                f"{night_drive_count}",
                f"{hard_brake_count}",
                f"{harsh_acc_count}",
                f"{freerun_count}",
                f"{idling_time:.1f}",
                f"{idling_fuel:.2f}"
            ]

        # Add totals
        total_overspeed = safety_data['overspeeding'].get('total', 0)
        total_night_drives = safety_data['night_drives'].get('total', 0)
        total_hard_brake = intangles_safety['hard_brake'].get('total', 0)
        total_harsh_acc = intangles_safety['harsh_acc'].get('total', 0)
        total_freerun = intangles_safety['freerun'].get('total', 0)
        total_idling_time = intangles_safety['idling_time'].get('total', 0)
        total_idling_fuel = intangles_safety['idling_fuel'].get('total', 0)

        safety_table_data['Total'] = [
            f"{total_overspeed}",
            f"{total_night_drives}",
            f"{total_hard_brake}",
            f"{total_harsh_acc}",
            f"{total_freerun}",
            f"{total_idling_time:.1f}",
            f"{total_idling_fuel:.2f}"
        ]

        safety_df = pd.DataFrame(safety_table_data)
        st.markdown(create_styled_table(safety_df), unsafe_allow_html=True)

    st.markdown("---")

    # === DETAIL VIEW SECTION ===
    st.markdown("### 🔍 View Details")
    detail_col1, detail_col2 = st.columns(2)

    with detail_col1:
        detail_metric = st.selectbox(
            "Select Metric",
            ["-- Select --", "Loaded Trip Count", "Total Delays", "POD Damage",
             "Total Repair Cost", "Total Challan", "Harsh Driving / Overspeeding", "Night Drives",
             "Hard Braking", "Harsh Acceleration", "Freerunning", "Idling"],
            key="detail_metric"
        )

    with detail_col2:
        month_options = ["Total"] + months
        detail_month = st.selectbox(
            "Select Month",
            month_options,
            key="detail_month",
            format_func=lambda x: format_month_header(x) if x != "Total" else "All Months"
        )

    # Show details based on selection
    if detail_metric != "-- Select --":
        with st.expander(f"📋 {detail_metric} Details - {format_month_header(detail_month) if detail_month != 'Total' else 'All Months'}", expanded=True):
            if detail_metric == "Loaded Trip Count":
                detail_df = get_trip_details(trip_df, detail_month if detail_month != "Total" else None)
                if not detail_df.empty:
                    st.markdown(f"**Total Trips: {len(detail_df)}**")
                    st.markdown(create_detail_table(detail_df, "Trip"), unsafe_allow_html=True)
                else:
                    st.info("No trip data available for selected period")

            elif detail_metric == "Total Delays":
                detail_df = get_delay_details(trip_df, detail_month if detail_month != "Total" else None)
                if not detail_df.empty:
                    st.markdown(f"**Total Delayed Trips: {len(detail_df)}**")
                    st.markdown(create_detail_table(detail_df, "Delayed Trips"), unsafe_allow_html=True)
                else:
                    st.info("No delayed trips for selected period")

            elif detail_metric == "POD Damage":
                detail_df = get_pod_damage_details(pod_damage_df, detail_month if detail_month != "Total" else None)
                if not detail_df.empty:
                    st.markdown(f"**Total POD Issues: {len(detail_df)}**")
                    st.markdown(create_detail_table(detail_df, "POD Damage"), unsafe_allow_html=True)
                else:
                    st.info("No POD damage data for selected period")

            elif detail_metric == "Total Repair Cost":
                detail_df = get_repair_details(repair_df, detail_month if detail_month != "Total" else None)
                if not detail_df.empty:
                    total_repair_amt = detail_df['Amount (₹)'].sum() if 'Amount (₹)' in detail_df.columns else 0
                    st.markdown(f"**Total Repairs: {len(detail_df)} | Total Amount: ₹{total_repair_amt:,.0f}**")
                    st.markdown(create_detail_table(detail_df, "Repair"), unsafe_allow_html=True)
                else:
                    st.info("No repair data for selected period")

            elif detail_metric == "Total Challan":
                detail_df = get_challan_details(challan_df, detail_month if detail_month != "Total" else None)
                if not detail_df.empty:
                    total_challan_amt = detail_df['Amount (₹)'].sum() if 'Amount (₹)' in detail_df.columns else 0
                    st.markdown(f"**Total Challans: {len(detail_df)} | Total Amount: ₹{total_challan_amt:,.0f}**")
                    st.markdown(create_detail_table(detail_df, "Challan"), unsafe_allow_html=True)
                else:
                    st.info("No challan data for selected period")

            elif detail_metric == "Harsh Driving / Overspeeding":
                overspeed_df = get_safety_details(engine, driver_code, start_date, end_date, 'overspeed')
                detail_df = format_safety_details(overspeed_df, detail_month if detail_month != "Total" else None)
                if not detail_df.empty:
                    total_count = detail_df['Count'].sum() if 'Count' in detail_df.columns else 0
                    st.markdown(f"**Total Overspeeding Days: {len(detail_df)} | Total Instances: {int(total_count)}**")
                    st.markdown(create_detail_table(detail_df, "Overspeeding"), unsafe_allow_html=True)
                else:
                    st.info("No overspeeding data for selected period")

            elif detail_metric == "Night Drives":
                night_df = get_safety_details(engine, driver_code, start_date, end_date, 'night_drive')
                detail_df = format_safety_details(night_df, detail_month if detail_month != "Total" else None)
                if not detail_df.empty:
                    total_count = detail_df['Count'].sum() if 'Count' in detail_df.columns else 0
                    st.markdown(f"**Total Night Drive Days: {len(detail_df)} | Total Instances: {int(total_count)}**")
                    st.markdown(create_detail_table(detail_df, "Night Drives"), unsafe_allow_html=True)
                else:
                    st.info("No night drive data for selected period")

            elif detail_metric == "Hard Braking":
                hard_brake_df = get_intangles_details(engine, driver_code, start_date, end_date, 'hard_brake')
                detail_df = format_intangles_details(hard_brake_df, detail_month if detail_month != "Total" else None, 'hard_brake')
                if not detail_df.empty:
                    st.markdown(f"**Total Hard Braking Events: {len(detail_df)}**")
                    st.markdown(create_detail_table(detail_df, "Hard Braking"), unsafe_allow_html=True)
                else:
                    st.info("No hard braking data for selected period")

            elif detail_metric == "Harsh Acceleration":
                harsh_acc_df = get_intangles_details(engine, driver_code, start_date, end_date, 'over_acc')
                detail_df = format_intangles_details(harsh_acc_df, detail_month if detail_month != "Total" else None, 'over_acc')
                if not detail_df.empty:
                    st.markdown(f"**Total Harsh Acceleration Events: {len(detail_df)}**")
                    st.markdown(create_detail_table(detail_df, "Harsh Acceleration"), unsafe_allow_html=True)
                else:
                    st.info("No harsh acceleration data for selected period")

            elif detail_metric == "Freerunning":
                freerun_df = get_intangles_details(engine, driver_code, start_date, end_date, 'freerun')
                detail_df = format_intangles_details(freerun_df, detail_month if detail_month != "Total" else None, 'freerun')
                if not detail_df.empty:
                    st.markdown(f"**Total Freerunning Events: {len(detail_df)}**")
                    st.markdown(create_detail_table(detail_df, "Freerunning"), unsafe_allow_html=True)
                else:
                    st.info("No freerunning data for selected period")

            elif detail_metric == "Idling":
                idling_df = get_intangles_details(engine, driver_code, start_date, end_date, 'idling')
                detail_df = format_intangles_details(idling_df, detail_month if detail_month != "Total" else None, 'idling')
                if not detail_df.empty:
                    total_duration = idling_df['duration_mins'].sum() if 'duration_mins' in idling_df.columns else 0
                    total_fuel = idling_df['fuel_consumed'].sum() if 'fuel_consumed' in idling_df.columns else 0
                    st.markdown(f"**Total Idling Events: {len(detail_df)} | Total Time: {total_duration:.1f} mins | Fuel: {total_fuel:.2f} L**")
                    st.markdown(create_detail_table(detail_df, "Idling"), unsafe_allow_html=True)
                else:
                    st.info("No idling data for selected period")

    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 25px; background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); border-radius: 15px; color: white; margin-top: 20px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 8px 32px rgba(0,0,0,0.3);">
        <p style="margin: 0; color: #00d4ff;">📅 Data Period: {start_date} to {end_date} | 🕐 Last Refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        <p style="margin: 8px 0 0 0; font-size: 0.85rem; color: #a0aec0;">Swift Road Link - Driver Performance Dashboard | Auto-refresh: 30 min</p>
    </div>
    """, unsafe_allow_html=True)

    # Auto-refresh every 30 minutes (1800 seconds)
    components.html(
        """
        <script>
            setTimeout(function() {
                window.parent.location.reload();
            }, 1800000);
        </script>
        """,
        height=0
    )

if __name__ == "__main__":
    main()
