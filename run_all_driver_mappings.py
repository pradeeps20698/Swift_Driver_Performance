#!/usr/bin/env python3
"""
Master Script: Run All Driver Mappings
======================================
This script runs all driver mapping updates in sequence:
1. challan_data driver mapping
2. intangles_alert_logs driver mapping

Run manually or schedule via cron/launchd.

Usage:
    python3 run_all_driver_mappings.py
"""

import os
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.environ["Host"],
    "user": os.environ["UserName"],
    "password": os.environ["Password"],
    "database": os.getenv("database_name", "postgres"),
    "port": int(os.getenv("Port", "5432")),
    "connect_timeout": 30,
}


def update_challan_driver_mapping(cur, conn):
    """Update driver mapping in challan_data table."""
    print("\n--- Updating challan_data driver mapping ---")

    # Add columns if needed
    cur.execute("ALTER TABLE challan_data ADD COLUMN IF NOT EXISTS driver_name VARCHAR(255)")
    cur.execute("ALTER TABLE challan_data ADD COLUMN IF NOT EXISTS driver_code VARCHAR(50)")
    conn.commit()

    # Clear and remap
    cur.execute("UPDATE challan_data SET driver_name = NULL, driver_code = NULL")
    conn.commit()

    cur.execute("""
        UPDATE challan_data cd
        SET
            driver_name = dvm.driver_name,
            driver_code = dvm.driver_code
        FROM driver_vehicle_mapping dvm
        WHERE cd.vehicle_no = dvm.gps_vehicle_no
          AND DATE(cd.challan_date) >= DATE(dvm.start_date)
          AND DATE(cd.challan_date) < DATE(dvm.end_date)
    """)
    mapped = cur.rowcount
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM challan_data")
    total = cur.fetchone()[0]

    print(f"   Challan: {mapped}/{total} records mapped")
    return mapped


def update_intangles_driver_mapping(cur, conn):
    """Update driver mapping in intangles_alert_logs table."""
    print("\n--- Updating intangles_alert_logs driver mapping ---")

    # Add columns if needed
    cur.execute("ALTER TABLE intangles_alert_logs ADD COLUMN IF NOT EXISTS driver_name VARCHAR(255)")
    cur.execute("ALTER TABLE intangles_alert_logs ADD COLUMN IF NOT EXISTS driver_code VARCHAR(50)")
    conn.commit()

    # Clear and remap
    cur.execute("UPDATE intangles_alert_logs SET driver_name = NULL, driver_code = NULL")
    conn.commit()

    cur.execute("""
        UPDATE intangles_alert_logs ial
        SET
            driver_name = dvm.driver_name,
            driver_code = dvm.driver_code
        FROM driver_vehicle_mapping dvm
        WHERE ial.vehicle_plate = dvm.gps_vehicle_no
          AND DATE(ial.event_time) >= DATE(dvm.start_date)
          AND DATE(ial.event_time) < DATE(dvm.end_date)
    """)
    mapped = cur.rowcount
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM intangles_alert_logs")
    total = cur.fetchone()[0]

    print(f"   Intangles: {mapped}/{total} records mapped")
    return mapped


def main():
    print("=" * 60)
    print(f"Driver Mapping Update - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Connected to database.")

        # Run all mappings
        challan_count = update_challan_driver_mapping(cur, conn)
        intangles_count = update_intangles_driver_mapping(cur, conn)

        print("\n" + "=" * 60)
        print("Summary:")
        print(f"   Challan records mapped: {challan_count}")
        print(f"   Intangles records mapped: {intangles_count}")
        print("=" * 60)

        cur.close()
        conn.close()
        print("\nAll driver mappings updated successfully!")

    except Exception as e:
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
