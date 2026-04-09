#!/usr/bin/env python3
"""
Auto Update Driver Mapping in challan_data Table
=================================================
Maps driver_name and driver_code from driver_vehicle_mapping
based on vehicle_no and challan_date.

Run every 30 minutes via cron (after driver_vehicle_mapping updates).

Cron example (run at :05 and :35 past each hour):
    5,35 * * * * cd /Users/swiftroadlink/Documents/Dashboard/Driver\ Performance && python3 update_challan_driver_mapping.py >> challan_driver_mapping.log 2>&1
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
        cur.execute("ALTER TABLE challan_data ADD COLUMN IF NOT EXISTS driver_name VARCHAR(255)")
        cur.execute("ALTER TABLE challan_data ADD COLUMN IF NOT EXISTS driver_code VARCHAR(50)")
        conn.commit()
        return True
    except Exception as e:
        print(f"   Error adding columns: {e}")
        conn.rollback()
        return False


def update_challan_driver_mapping():
    """Update driver mapping in challan_data table."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updating challan_data driver mapping...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Step 1: Ensure columns exist
        add_columns_if_not_exist(cur, conn)

        # Step 2: Clear existing mappings (to handle driver changes)
        cur.execute("UPDATE challan_data SET driver_name = NULL, driver_code = NULL")
        conn.commit()

        # Step 3: Map drivers based on vehicle_no and challan_date
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
        print(f"   Mapped {mapped} challan records with driver info.")

        # Step 4: Get statistics
        cur.execute("SELECT COUNT(*) FROM challan_data")
        total = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM challan_data WHERE driver_code IS NOT NULL")
        with_driver = cur.fetchone()[0]

        print(f"   Total challans: {total}")
        print(f"   With driver: {with_driver}")
        print(f"   Without driver: {total - with_driver}")

        # Step 5: Show recent mappings
        cur.execute("""
            SELECT vehicle_no, DATE(challan_date), driver_name, driver_code
            FROM challan_data
            WHERE driver_code IS NOT NULL
            ORDER BY challan_date DESC
            LIMIT 5
        """)
        print("   Recent mapped challans:")
        for row in cur.fetchall():
            print(f"     {row[0]} | {row[1]} | {row[2]} ({row[3]})")

    except Exception as e:
        conn.rollback()
        print(f"   Error: {e}")
    finally:
        cur.close()
        conn.close()

    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Done!")


if __name__ == "__main__":
    update_challan_driver_mapping()
