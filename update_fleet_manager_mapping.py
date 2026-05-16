#!/usr/bin/env python3
"""
Update Fleet Manager Mapping
=============================
Updates the fleet_manager_mapping table with current vehicle-to-fleet-manager assignments.
"""

import psycopg2
from datetime import datetime

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import os

# Load from .streamlit/secrets.toml
secrets_path = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
with open(secrets_path, "rb") as f:
    secrets = tomllib.load(f)

db_secrets = secrets["database"]
DB_CONFIG = {
    "host": db_secrets["Host"],
    "user": db_secrets["UserName"],
    "password": db_secrets["Password"],
    "database": db_secrets.get("database_name", "postgres"),
    "port": int(db_secrets.get("Port", "5432")),
    "connect_timeout": 30,
}

# Fleet Manager -> Vehicle mappings (updated 2026-05-16)
FLEET_MANAGER_VEHICLES = {
    "GOPI": [
        "0020 NL01AJ", "0167 NL01AH", "0218 NL01AH", "0219 NL01AH", "0283 NL01AH",
        "0523 GJ08AU", "0536 GJ08AU", "0628 GJ08AU", "0740 GJ08AU", "0863 GJ08AU",
        "0908 GJ08AU", "0951 GJ08AU", "0983 GJ08AU", "0986 GJ08AU",
        "1107 NL01AH", "1108 NL01AH", "1109 NL01AH", "1110 NL01AH", "1111 NL01AH",
        "1112 NL01AH", "1113 NL01AH", "1114 NL01AH", "1115 NL01AH",
        "2210NL01AJ", "2211NL01AJ",
        "2396 NL01N", "2397 NL01N", "2398 NL01N", "2399 NL01N", "2400 NL01N",
        "2625 NL01AG",
        "3431 NL01AG", "3432 NL01AG", "3433 NL01AG",
        "3748 HR55AR",
        "3906 NL01N", "3907 NL01N", "3908 NL01N", "3909 NL01N", "3910 NL01N",
        "4061 NL01N", "4062 NL01N", "4064 NL01N", "4065 NL01N", "4066 NL01N",
        "4067 NL01N", "4068 NL01N", "4069 NL01N",
        "4388 NL01AJ", "4390 NL01AJ",
        "4525 NL01AH", "4526 NL01AH", "4527 NL01AH", "4528 NL01AH", "4529 NL01AH",
        "4530 NL01AH", "4531 HR55AR", "4531 NL01AH", "4532 NL01AH", "4533 NL01AH",
        "4534 NL01AH", "4535 NL01AH", "4536 NL01AH", "4537 NL01AH", "4538 NL01AH",
        "4539 NL01AH",
        "5825NL01AJ", "5826NL01AJ", "5827NL01AJ", "5828NL01AJ",
        "6158 HR55AQ", "6429 HR55AQ",
        "6456NL01AJ", "6457NL01AJ", "6458NL01AJ", "6459NL01AJ", "6460NL01AJ",
        "6469 HR55AQ", "6484HR55AQ",
        "7175NL01AJ", "7176 NL01AJ", "7177NL01AJ", "7178NL01AJ",
        "7220 NL01AF", "7222 NL01AF", "7223 NL01AF", "7224 NL01AF", "7225 NL01AF",
        "8204 NL01AH", "8224 HR55AQ",
        "8314 NL01AG", "8315 NL01AG",
        "8450 HR55AQ", "8593 HR55AR", "8597 HR55AR", "8739 HR55AQ", "8752 HR55AR",
        "8795 HR55AR",
        "9392 NL01AH", "9452 NL01L", "9460 NL01L", "9494 HR55AQ",
    ],
    "JAGDISH": [
        "0284 NL01AH", "0285 NL01AH", "0286 NL01AH",
        "0722 GJ08AU", "0739 GJ08AU", "0764 GJ08AU", "0814 GJ08AU", "0815 GJ08AU",
        "0816 GJ08AU", "0824 GJ08AU",
        "2624 NL01AG",
        "3136 NL01AG",
        "4063 NL01N",
        "7226 NL01AF",
        "8630 NL01AG",
        "9451NL01L", "9889 NL01AF",
        "NL01Q 8157", "HR55AP 1974",
        "HR55AM 2340", "HR55AM 9667", "HR55AM 0907", "HR55AM 4278", "HR55AM 6059",
        "HR55AN 5307", "HR55AN 5406", "HR55AM 8703",
        "NL01Q8150", "NL01Q9547",
    ],
    "PRAVEEN": [
        "0570 GJ08AU", "0572 GJ08AU", "0639 GJ08AU", "0699 GJ08AU",
        "0959 HR55AQ",
        "1171 HR55AR", "1564 HR55AQ", "1652 NL01AH", "1741 HR55AR", "1797 PB11BR",
        "2081NL01AJ", "2082NL01AJ", "2083NL01AJ", "2084NL01AJ",
        "2206NL01AJ", "2207NL01AJ", "2208NL01AJ", "2209NL01AJ",
        "2829 HR55AR", "2885 HR55AQ", "2942 HR55AQ",
        "3135 NL01AG",
        "4078 NL01AG", "4080 NL01AG",
        "4149 HR55AQ", "4180 HR55AQ", "4274 HR55AR",
        "4385 NL01AJ", "4387 NL01AJ", "4389 NL01AJ",
        "4521 NL01AH", "4522 NL01AH", "4523 NL01AH", "4524 NL01AH", "4540 NL01AH",
        "4849 NL01AH", "4850 NL01AH", "4851 NL01AH", "4852 NL01AH", "4853 NL01AH",
        "4854 NL01AH", "4855 NL01AH", "4856 NL01AH", "4857 NL01AH", "4858 NL01AH",
        "5077 HR55AQ",
        "5305 NL01N", "5306 NL01N", "5307 NL01N", "5309 NL01N",
        "5417 HR55AQ", "5495 HR55AR", "5578 HR55AR", "5709 HR55AR",
        "5819NL01AJ", "5820NL01AJ", "5821NL01AJ", "5822NL01AJ", "5823NL01AJ",
        "5824 HR55AQ", "5824NL01AJ",
        "6017 HR55AR",
        "7169NL01AJ", "7170NL01AJ", "7171NL01AJ", "7172NL01AJ", "7173NL01AJ",
        "7174NL01AJ",
        "7219 NL01AF", "7221 NL01AF",
        "7521 NL01N", "7522 NL01N", "7523 NL01N", "7524 NL01N", "7525 NL01N",
        "7526 NL01N", "7527 NL01N", "7528 NL01N", "7529 NL01N", "7530 NL01N",
        "7553 HR55AR", "7745 HR55AR", "8008 HR55AR", "8078 HR55AR",
        "8193 NL01AH",
        "9080 HR55AQ", "9104 HR55AR", "9244 HR55AQ", "9256 HR55AQ",
        "9450 NL01L", "9453 NL01L", "9454 NL01L", "9455 NL01L", "9456 NL01L",
        "9457 NL01L", "9458 NL01L",
        "9566 NL01AH", "9702 HR55AR", "9851 NL01AH",
        "9890 NL01AF", "9991 NL01AG",
    ],
    "CHANCHAL": [
        "2623 NL01AG",
        "3137 NL01AG",
        "4079 NL01AG",
        "HR55AM 1370",
        "9891 NL01AF",
    ],
}


def update_fleet_manager_mapping():
    """Replace all fleet_manager_mapping entries with updated assignments."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Updating fleet_manager_mapping...")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    try:
        # Create table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS fleet_manager_mapping (
                vehicle_no VARCHAR(50) PRIMARY KEY,
                fleet_manager VARCHAR(100)
            )
        """)

        # Clear existing mappings
        cur.execute("DELETE FROM fleet_manager_mapping")
        deleted = cur.rowcount
        print(f"   Deleted {deleted} old mappings")

        # Insert new mappings
        insert_count = 0
        for fm_name, vehicles in FLEET_MANAGER_VEHICLES.items():
            for vehicle_no in vehicles:
                cur.execute(
                    "INSERT INTO fleet_manager_mapping (vehicle_no, fleet_manager) VALUES (%s, %s) "
                    "ON CONFLICT (vehicle_no) DO UPDATE SET fleet_manager = EXCLUDED.fleet_manager",
                    (vehicle_no, fm_name)
                )
                insert_count += 1

        conn.commit()
        print(f"   Inserted {insert_count} mappings:")
        for fm_name, vehicles in FLEET_MANAGER_VEHICLES.items():
            print(f"     {fm_name}: {len(vehicles)} vehicles")
        print(f"   Done!")

    except Exception as e:
        conn.rollback()
        print(f"   Error: {e}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    update_fleet_manager_mapping()
