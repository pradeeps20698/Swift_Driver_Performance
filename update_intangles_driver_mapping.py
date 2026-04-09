#!/usr/bin/env python3
"""
Auto Update Driver Mapping in intangles_alert_logs Table
=========================================================
Maps driver_name and driver_code from driver_vehicle_mapping
based on vehicle_plate and event_time.

Run every 30 minutes via cron (after driver_vehicle_mapping updates).

Cron example (run at :10 and :40 past each hour):
    10,40 * * * * cd /Users/swiftroadlink/Documents/Dashboard/Driver\ Performance && python3 update_intangles_driver_mapping.py >> intangles_driver_mapping.log 2>&1
"""

import psycopg2
from datetime import datetime

import os

DB_CONFIG = {
    "host": os.environ["Host"],
    "user": os.environ["UserName"],
    "password": os.environ["Password"],
    "database": os.getenv("database_name", "postgres"),
    "port": int(os.getenv("Port", "5432")),
    "connect_timeout": 30,
}


def add_columns_if_not_exist(cur, conn):
    """Add driver_name and driver_code columns if they don't exist."""
    try:
        cur.execute("ALTER TABLE intangles_alert_logs ADD COLUMN IF NOT EXISTS driver_name VARCHAR(255)")
        cur.execute("ALTER TABLE intangles_alert_logs ADD COLUMN IF NOT EXISTS driver_code VARCHAR(50)")
        conn.commit()
        return True
    except Exception as e:
        print(f"   Error adding columns: {e}")
        conn.rollback()
        return False


def update_intangles_driver_mapping():
    """Update driver mapping in intangles_alert_logs table."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updating intangles_alert_logs driver mapping...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Step 1: Ensure columns exist
        add_columns_if_not_exist(cur, conn)

        # Step 2: Clear existing mappings (to handle driver changes)
        cur.execute("UPDATE intangles_alert_logs SET driver_name = NULL, driver_code = NULL")
        conn.commit()

        # Step 3: Map drivers based on vehicle_plate and event_time
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
        print(f"   Mapped {mapped} alert records with driver info.")

        # Step 4: Get statistics
        cur.execute("SELECT COUNT(*) FROM intangles_alert_logs")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM intangles_alert_logs WHERE driver_code IS NOT NULL")
        with_driver = cur.fetchone()[0]

        print(f"   Total alerts: {total}")
        print(f"   With driver: {with_driver}")
        print(f"   Without driver: {total - with_driver}")

        # Step 5: Show recent mappings
        cur.execute("""
            SELECT vehicle_plate, alert_type, DATE(event_time), driver_name, driver_code
            FROM intangles_alert_logs
            WHERE driver_code IS NOT NULL
            ORDER BY event_time DESC
            LIMIT 5
        """)
        print("   Recent mapped alerts:")
        for row in cur.fetchall():
            print(f"     {row[0]} | {row[1]} | {row[2]} | {row[3]} ({row[4]})")

    except Exception as e:
        conn.rollback()
        print(f"   Error: {e}")
    finally:
        cur.close()
        conn.close()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Done!")


if __name__ == "__main__":
    update_intangles_driver_mapping()
