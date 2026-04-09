"""
Daily update script for overspeed and night_drive columns in day_wise_gps_km table.

This script updates safety data for the last 7 days to catch any new/updated records.
Run this daily via cron job.

Cron example (run at 6 AM daily):
    0 6 * * * cd /Users/swiftroadlink/Documents/Dashboard/Driver\ Performance && python3 update_safety_data_daily.py >> safety_update.log 2>&1

Logic:
- Night Drive: speed > 0 AND ignition = 1 AND time between 11 PM (23:00) to 6 AM (06:00)
- Overspeed: speed > 65
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
        host = os.environ['Host']
        username = os.environ['UserName']
        password = os.environ['Password']
        port = os.getenv('Port', '5432')
        database = os.getenv('database_name', 'postgres')
        connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        engine = create_engine(connection_string)
        return engine
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def convert_vehicle_no_to_gps_format(vehicle_no):
    """Convert vehicle number from swift_trip_log format to fvts_vehicles format."""
    if not vehicle_no:
        return None
    v = vehicle_no.replace(' ', '')
    for i, c in enumerate(v):
        if c.isalpha():
            num_part = v[:i]
            letter_part = v[i:]
            return letter_part + num_part
    return v

def update_safety_for_date_range(engine, start_date, end_date):
    """Update overspeed and night_drive for a date range."""

    print(f"Updating safety data from {start_date} to {end_date}")

    # Reset values for the date range first
    reset_query = f"""
    UPDATE day_wise_gps_km
    SET overspeed = 0, night_drive = 0
    WHERE date >= '{start_date}' AND date <= '{end_date}'
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(reset_query))
            conn.commit()
        print("Reset existing values for date range.")
    except Exception as e:
        print(f"Error resetting values: {e}")
        return

    # Get driver-vehicle mappings for the date range
    trip_query = f"""
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
            result = conn.execute(text(trip_query))
            rows = result.fetchall()
            if rows:
                columns = result.keys()
                mappings_df = pd.DataFrame(rows, columns=columns)
            else:
                print("No trips found for date range.")
                return
    except Exception as e:
        print(f"Error getting mappings: {e}")
        return

    print(f"Found {len(mappings_df)} trip records to process.")

    total_updates = 0

    for idx, row in mappings_df.iterrows():
        driver_code = row['driver_code']
        vehicle_no = row['vehicle_no']
        trip_start = row['loading_date']
        trip_end = row['end_date']

        gps_vehicle = convert_vehicle_no_to_gps_format(vehicle_no)
        if not gps_vehicle:
            continue

        # Calculate safety counts
        safety_query = f"""
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
        AND date_time >= '{trip_start}'
        AND date_time <= '{trip_end}'
        GROUP BY DATE(date_time)
        """

        try:
            with engine.connect() as conn:
                result = conn.execute(text(safety_query))
                safety_rows = result.fetchall()

                for safety_row in safety_rows:
                    date = safety_row[0]
                    overspeed = int(safety_row[1]) if safety_row[1] else 0
                    night_drive = int(safety_row[2]) if safety_row[2] else 0

                    if overspeed > 0 or night_drive > 0:
                        update_query = f"""
                        UPDATE day_wise_gps_km
                        SET overspeed = COALESCE(overspeed, 0) + {overspeed},
                            night_drive = COALESCE(night_drive, 0) + {night_drive}
                        WHERE driver_code = '{driver_code}'
                        AND date = '{date}'
                        """
                        conn.execute(text(update_query))
                        conn.commit()
                        total_updates += 1
        except Exception as e:
            # Silently continue on errors
            pass

        if (idx + 1) % 50 == 0:
            print(f"Processed {idx + 1}/{len(mappings_df)} records...")

    print(f"Completed! Total updates: {total_updates}")

def main():
    print("=" * 60)
    print(f"Daily Safety Data Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    engine = get_database_connection()
    if engine is None:
        print("Failed to connect to database. Exiting.")
        return

    print("Connected to database.")

    # Update last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    update_safety_for_date_range(engine, start_date.date(), end_date.date())

    print("=" * 60)
    print("Daily update complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
