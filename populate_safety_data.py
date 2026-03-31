"""
Script to populate overspeed and night_drive columns in day_wise_gps_km table.

Logic:
- Night Drive: vehicle_speed > 0 AND ignition = 'ON' AND time between 11 PM (23:00) to 6 AM (06:00)
- Overspeed: vehicle_speed > 65

This script:
1. Gets driver-vehicle mappings from swift_trip_log
2. Queries fvts_vehicles for GPS data
3. Calculates overspeed and night_drive counts per day per driver
4. Updates the day_wise_gps_km table
"""

import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

def get_database_connection():
    """Create database connection."""
    try:
        host = os.getenv('Host', 'swift.cj8i0e86a294.ap-south-1.rds.amazonaws.com')
        username = os.getenv('UserName', 'pradeep')
        password = os.getenv('Password', 'Amit__0411')
        port = os.getenv('Port', '5432')
        database = os.getenv('database_name', 'postgres')
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

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

def add_columns_if_not_exist(engine):
    """Add overspeed and night_drive columns to day_wise_gps_km if they don't exist."""
    try:
        with engine.connect() as conn:
            # Check if columns exist
            check_query = """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'day_wise_gps_km'
            AND column_name IN ('overspeed', 'night_drive')
            """
            result = conn.execute(text(check_query))
            existing_columns = [row[0] for row in result.fetchall()]

            if 'overspeed' not in existing_columns:
                conn.execute(text("ALTER TABLE day_wise_gps_km ADD COLUMN overspeed INTEGER DEFAULT 0"))
                print("Added 'overspeed' column to day_wise_gps_km")

            if 'night_drive' not in existing_columns:
                conn.execute(text("ALTER TABLE day_wise_gps_km ADD COLUMN night_drive INTEGER DEFAULT 0"))
                print("Added 'night_drive' column to day_wise_gps_km")

            conn.commit()
            print("Columns check complete.")
    except Exception as e:
        print(f"Error adding columns: {e}")

def get_driver_vehicle_mappings(engine, start_date, end_date):
    """Get driver to vehicle mappings from swift_trip_log."""
    query = f"""
    SELECT DISTINCT driver_code, vehicle_no, loading_date,
           COALESCE(unloading_date, loading_date + INTERVAL '2 days') as end_date
    FROM swift_trip_log
    WHERE driver_code IS NOT NULL
    AND vehicle_no IS NOT NULL
    AND loading_date >= '{start_date}'
    AND loading_date <= '{end_date}'
    ORDER BY driver_code, loading_date
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error getting driver-vehicle mappings: {e}")
        return pd.DataFrame()

def calculate_safety_counts(engine, gps_vehicle, start_date, end_date):
    """
    Calculate overspeed and night_drive counts from fvts_vehicles for a specific vehicle.
    Returns a DataFrame with date, overspeed_count, night_drive_count.
    - speed: integer column for vehicle speed
    - ignition: integer column (1 = ON, 0 = OFF)
    """
    query = f"""
    SELECT
        DATE(date_time) as date,
        SUM(CASE WHEN speed > 65 THEN 1 ELSE 0 END) as overspeed_count,
        SUM(CASE
            WHEN speed > 0
            AND ignition = 1
            AND (EXTRACT(HOUR FROM date_time) >= 23 OR EXTRACT(HOUR FROM date_time) < 6)
            THEN 1 ELSE 0
        END) as night_drive_count
    FROM fvts_vehicles
    WHERE vehicle_no = '{gps_vehicle}'
    AND date_time >= '{start_date}'
    AND date_time <= '{end_date}'
    GROUP BY DATE(date_time)
    ORDER BY date
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                df = pd.DataFrame(rows, columns=columns)
                return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error calculating safety counts for {gps_vehicle}: {e}")
        return pd.DataFrame()

def update_day_wise_gps_km(engine, driver_code, date, overspeed, night_drive):
    """Update overspeed and night_drive columns in day_wise_gps_km."""
    query = f"""
    UPDATE day_wise_gps_km
    SET overspeed = COALESCE(overspeed, 0) + {overspeed},
        night_drive = COALESCE(night_drive, 0) + {night_drive}
    WHERE driver_code = '{driver_code}'
    AND date = '{date}'
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
        return True
    except Exception as e:
        print(f"Error updating day_wise_gps_km for {driver_code} on {date}: {e}")
        return False

def reset_safety_columns(engine):
    """Reset overspeed and night_drive columns to 0 before repopulating."""
    query = """
    UPDATE day_wise_gps_km
    SET overspeed = 0, night_drive = 0
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(query))
            conn.commit()
        print("Reset overspeed and night_drive columns to 0.")
    except Exception as e:
        print(f"Error resetting columns: {e}")

def main():
    print("=" * 60)
    print("Populate Safety Data (Overspeed & Night Drive)")
    print("=" * 60)

    # Connect to database
    engine = get_database_connection()
    if engine is None:
        print("Failed to connect to database. Exiting.")
        return

    print("Connected to database.")

    # Add columns if they don't exist
    add_columns_if_not_exist(engine)

    # Set date range (last 6 months)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    print(f"Processing data from {start_date.date()} to {end_date.date()}")

    # Reset existing values
    reset_safety_columns(engine)

    # Get driver-vehicle mappings
    print("Getting driver-vehicle mappings...")
    mappings_df = get_driver_vehicle_mappings(engine, start_date, end_date)

    if mappings_df.empty:
        print("No driver-vehicle mappings found. Exiting.")
        return

    print(f"Found {len(mappings_df)} driver-vehicle trip records.")

    # Process each mapping
    total_updates = 0
    processed_drivers = set()

    for idx, row in mappings_df.iterrows():
        driver_code = row['driver_code']
        vehicle_no = row['vehicle_no']
        trip_start = row['loading_date']
        trip_end = row['end_date']

        # Convert vehicle number to GPS format
        gps_vehicle = convert_vehicle_no_to_gps_format(vehicle_no)
        if not gps_vehicle:
            continue

        # Calculate safety counts for this vehicle during the trip period
        safety_df = calculate_safety_counts(engine, gps_vehicle, trip_start, trip_end)

        if safety_df.empty:
            continue

        # Update day_wise_gps_km for each date
        for _, safety_row in safety_df.iterrows():
            date = safety_row['date']
            overspeed = int(safety_row['overspeed_count']) if safety_row['overspeed_count'] else 0
            night_drive = int(safety_row['night_drive_count']) if safety_row['night_drive_count'] else 0

            if overspeed > 0 or night_drive > 0:
                if update_day_wise_gps_km(engine, driver_code, date, overspeed, night_drive):
                    total_updates += 1

        processed_drivers.add(driver_code)

        # Progress indicator
        if (idx + 1) % 100 == 0:
            print(f"Processed {idx + 1}/{len(mappings_df)} records...")

    print("=" * 60)
    print(f"Completed!")
    print(f"Processed {len(processed_drivers)} unique drivers")
    print(f"Total database updates: {total_updates}")
    print("=" * 60)

if __name__ == "__main__":
    main()
