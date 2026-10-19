import duckdb
import random
from datetime import datetime, timedelta

DB_FILE = "wildlife_conservation.duckdb"

def init_database():
    con = duckdb.connect(DB_FILE)

    # Drop existing tables for a clean initialization
    tables = [
        "field_surveys", "conservation_projects", "health_rescue_logs",
        "env_sensor_logs", "gps_telemetry", "animals", "protected_zones"
    ]
    for t in tables:
        con.execute(f"DROP TABLE IF EXISTS {t};")

    # 1. Protected Zones Table
    con.execute("""
        CREATE TABLE protected_zones (
            zone_id VARCHAR PRIMARY KEY,
            zone_name VARCHAR,
            category VARCHAR,
            state VARCHAR,
            area_sq_km DOUBLE,
            base_lat DOUBLE,
            base_lon DOUBLE
        );
    """)

    zones_data = [
        ("ZONE-KAZ", "Kaziranga National Park", "National Park", "Assam", 1090.0, 26.5775, 93.1711),
        ("ZONE-COR", "Jim Corbett Tiger Reserve", "Wildlife Sanctuary", "Uttarakhand", 1288.0, 29.5300, 78.7747),
        ("ZONE-SUN", "Sundarbans Biosphere Reserve", "Protected Forest", "West Bengal", 1330.0, 21.9497, 88.9000),
        ("ZONE-RAN", "Ranthambore National Park", "National Park", "Rajasthan", 1334.0, 26.0173, 76.5026)
    ]
    con.executemany("INSERT INTO protected_zones VALUES (?, ?, ?, ?, ?, ?, ?);", zones_data)

    # 2. Animals Table (GPS Collars & RFID Tags)
    con.execute("""
        CREATE TABLE animals (
            animal_id VARCHAR PRIMARY KEY,
            name VARCHAR,
            species VARCHAR,
            common_name VARCHAR,
            tag_type VARCHAR,
            tag_id VARCHAR,
            zone_id VARCHAR,
            age INTEGER,
            sex VARCHAR,
            health_status VARCHAR,
            conservation_status VARCHAR
        );
    """)

    animals_data = [
        ("ANI-101", "Brahmaputra King", "Panthera tigris", "Royal Bengal Tiger", "GPS Collar", "GPS-TX-8801", "ZONE-KAZ", 6, "M", "Healthy", "Endangered"),
        ("ANI-102", "Kaziranga Pride", "Rhinoceros unicornis", "One-Horned Rhino", "RFID Tag", "RFID-RN-4412", "ZONE-KAZ", 9, "F", "Healthy", "Vulnerable"),
        ("ANI-103", "Gajraj", "Elephas maximus", "Asian Elephant", "GPS Collar", "GPS-EL-3091", "ZONE-KAZ", 14, "M", "Healthy", "Endangered"),
        ("ANI-104", "Ramganga Queen", "Panthera tigris", "Royal Bengal Tiger", "GPS Collar", "GPS-TX-8804", "ZONE-COR", 5, "F", "Healthy", "Endangered"),
        ("ANI-105", "Tusk Master", "Elephas maximus", "Asian Elephant", "GPS Collar", "GPS-EL-3095", "ZONE-COR", 11, "M", "Under Observation", "Endangered"),
        ("ANI-106", "Delta Prowler", "Panthera tigris", "Royal Bengal Tiger", "GPS Collar", "GPS-TX-8809", "ZONE-SUN", 7, "M", "Healthy", "Endangered"),
        ("ANI-107", "Mangrove Watcher", "Prionailurus viverrinus", "Fishing Cat", "RFID Tag", "RFID-FC-1102", "ZONE-SUN", 3, "F", "Healthy", "Vulnerable"),
        ("ANI-108", "Machli Lineage", "Panthera tigris", "Royal Bengal Tiger", "GPS Collar", "GPS-TX-8812", "ZONE-RAN", 4, "F", "In Rehabilitation", "Endangered"),
        ("ANI-109", "Aravalli Ghost", "Panthera pardus", "Indian Leopard", "GPS Collar", "GPS-LP-5501", "ZONE-RAN", 6, "M", "Healthy", "Vulnerable")
    ]
    con.executemany("INSERT INTO animals VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", animals_data)

    # 3. Historical GPS Telemetry Table (Last 25 timestamps per animal)
    con.execute("""
        CREATE TABLE gps_telemetry (
            ts TIMESTAMP,
            animal_id VARCHAR,
            zone_id VARCHAR,
            latitude DOUBLE,
            longitude DOUBLE,
            speed_kmh DOUBLE,
            heart_rate_bpm INTEGER,
            activity_state VARCHAR
        );
    """)

    zone_coords = {z[0]: (z[5], z[6]) for z in zones_data}
    activities = ["Feeding", "Migrating", "Resting", "Patrolling Territory", "At Waterhole"]
    now = datetime.now()

    gps_rows = []
    for i in range(25, 0, -1):
        ts = now - timedelta(minutes=i * 5)
        for a in animals_data:
            animal_id, zone_id = a[0], a[6]
            base_lat, base_lon = zone_coords[zone_id]
            lat = round(base_lat + random.uniform(-0.025, 0.025), 5)
            lon = round(base_lon + random.uniform(-0.025, 0.025), 5)
            speed = round(random.uniform(0.5, 14.0), 1)
            hr = random.randint(58, 98)
            act = random.choice(activities)
            gps_rows.append((ts, animal_id, zone_id, lat, lon, speed, hr, act))

    con.executemany("INSERT INTO gps_telemetry VALUES (?, ?, ?, ?, ?, ?, ?, ?);", gps_rows)

    # 4. IoT Environmental Sensor Logs Table
    con.execute("""
        CREATE TABLE env_sensor_logs (
            ts TIMESTAMP,
            station_id VARCHAR,
            zone_id VARCHAR,
            temperature_c DOUBLE,
            humidity_pct DOUBLE,
            rainfall_mm DOUBLE,
            water_availability_pct DOUBLE,
            aqi INTEGER,
            fire_alert BOOLEAN
        );
    """)

    sensor_rows = []
    for i in range(25, 0, -1):
        ts = now - timedelta(minutes=i * 5)
        for z in zones_data:
            z_id = z[0]
            station_id = f"IOT-{z_id.split('-')[1]}-01"
            temp = round(random.uniform(26.0, 34.0), 1)
            hum = round(random.uniform(55.0, 82.0), 1)
            rain = round(random.choice([0.0, 0.0, 0.0, 1.2, 3.5]), 1)
            water = round(random.uniform(72.0, 95.0), 1)
            aqi = random.randint(35, 85)
            fire = False
            sensor_rows.append((ts, station_id, z_id, temp, hum, rain, water, aqi, fire))

    con.executemany("INSERT INTO env_sensor_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", sensor_rows)

    # 5. Animal Health, Breeding, Disease Outbreaks & Rescue Logs
    con.execute("""
        CREATE TABLE health_rescue_logs (
            log_id INTEGER,
            log_time TIMESTAMP,
            animal_id VARCHAR,
            zone_id VARCHAR,
            event_category VARCHAR,
            details VARCHAR,
            vet_or_researcher VARCHAR,
            rehab_status VARCHAR
        );
    """)

    health_rows = [
        (1, now - timedelta(days=12), "ANI-108", "ZONE-RAN", "Rescue & Rehabilitation", "Minor paw laceration from territorial dispute; tranquilized and treated at field clinic.", "Dr. A. Sharma (WII)", "In Rehabilitation"),
        (2, now - timedelta(days=8), "ANI-102", "ZONE-KAZ", "Breeding Activity", "Observed courtship and mating behavior near central marshland sector.", "Dr. R. Bora (Assam Forest Dept)", "Completed"),
        (3, now - timedelta(days=5), "ANI-105", "ZONE-COR", "Disease Outbreak Alert", "Mild foot-and-mouth viral symptoms spotted in adjacent herd; prophylactic vaccination administered.", "Dr. V. Negi (IVRI)", "Under Observation"),
        (4, now - timedelta(days=2), "ANI-101", "ZONE-KAZ", "Health Check & Tagging", "Routine GPS collar battery verification and blood sample collection; optimal vitals.", "Dr. K. Baruah (WWF-India)", "Released / Active"),
        (5, now - timedelta(days=15), "ANI-104", "ZONE-COR", "Health Check & Tagging", "Collar firmware updated via Bluetooth proximity link; body weight ~138 kg, within expected range.", "Dr. P. Singh (WTI)", "Released / Active"),
        (6, now - timedelta(days=20), "ANI-103", "ZONE-KAZ", "Feeding Behavior Observation", "Herd foraging near eastern grassland buffer; calf following elder matriarch observed.", "Dr. M. Hazarika (AAECL)", "Completed"),
        (7, now - timedelta(days=9), "ANI-106", "ZONE-SUN", "Disease Outbreak Alert", "Suspected canine distemper exposure near peripheral forest edge; isolation and booster vaccination completed.", "Dr. T. Roy (ZSI)", "Under Observation"),
        (8, now - timedelta(days=3), "ANI-109", "ZONE-RAN", "Rescue & Rehabilitation", "Found with snare injury on left foreleg; surgically removed under field anesthesia, recovering well.", "Dr. A. Sharma (NCBS)", "In Rehabilitation"),
        (9, now - timedelta(days=1), "ANI-107", "ZONE-SUN", "Breeding Activity", "Camera trap footage confirmed mating pair near tidal creek; first confirmed breeding in this sector.", "Dr. M. Chatterjee (BNHS)", "Completed"),
        (10, now - timedelta(hours=6), "ANI-102", "ZONE-KAZ", "Health Check & Tagging", "Post-breeding health assessment; blood panels normal; weight 2,100 kg, horn growth 4.2 cm/yr.", "Dr. R. Bora (Assam Forest Dept)", "Released / Active")
    ]
    con.executemany("INSERT INTO health_rescue_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?);", health_rows)

    # 6. Conservation Projects & Funding Table
    con.execute("""
        CREATE TABLE conservation_projects (
            project_id VARCHAR PRIMARY KEY,
            project_title VARCHAR,
            funding_agency VARCHAR,
            grant_amount_lakhs DOUBLE,
            zone_id VARCHAR,
            target_species VARCHAR,
            start_date DATE,
            status VARCHAR
        );
    """)

    projects_data = [
        ("PRJ-2026-01", "Project Tiger Corridor Telemetry Phase IV", "NTCA & MoEFCC (Govt. of India)", 420.0, "ZONE-COR", "Royal Bengal Tiger", "2025-04-01", "Active"),
        ("PRJ-2026-02", "Kaziranga Anti-Poaching & Flood Sensor Grid", "WWF-India & Assam State Govt", 315.0, "ZONE-KAZ", "One-Horned Rhino", "2025-06-15", "Active"),
        ("PRJ-2026-03", "Sundarbans Mangrove Salinity & Tiger Prey Study", "UNEP & WII Dehradun", 190.0, "ZONE-SUN", "Royal Bengal Tiger", "2025-08-10", "Active"),
        ("PRJ-2026-04", "Aravalli Dry-Zone Waterhole & Leopard Recovery", "Rajasthan Forest Dept & IUCN", 150.0, "ZONE-RAN", "Indian Leopard", "2025-11-01", "Active")
    ]
    con.executemany("INSERT INTO conservation_projects VALUES (?, ?, ?, ?, ?, ?, ?, ?);", projects_data)

    # 7. Field Surveys & Biodiversity Assessments Table
    con.execute("""
        CREATE TABLE field_surveys (
            survey_id VARCHAR PRIMARY KEY,
            project_id VARCHAR,
            zone_id VARCHAR,
            lead_researcher VARCHAR,
            institution VARCHAR,
            survey_date DATE,
            estimated_population INTEGER,
            biodiversity_index DOUBLE,
            report_summary VARCHAR
        );
    """)

    surveys_data = [
        ("SRV-901", "PRJ-2026-01", "ZONE-COR", "Dr. S. Qureshi", "Wildlife Institute of India (WII)", "2026-08-14", 260, 8.9, "High prey density observed; corridor connectivity improved by 14%."),
        ("SRV-902", "PRJ-2026-02", "ZONE-KAZ", "Dr. R. Bora", "Assam Forest Research Inst.", "2026-09-02", 2613, 9.2, "Rhino calf survival rate up 8%; highland flood shelters heavily utilized."),
        ("SRV-903", "PRJ-2026-03", "ZONE-SUN", "Dr. M. Chatterjee", "BNHS & Jadavpur University", "2026-09-20", 101, 8.4, "Estuarine water salinity stable; fishing cat camera-trap sightings increased."),
        ("SRV-904", "PRJ-2026-04", "ZONE-RAN", "Dr. A. Sharma", "NCBS Bengaluru", "2026-10-05", 88, 7.8, "Solar-pumped waterholes mitigated summer heat stress across core zone.")
    ]
    con.executemany("INSERT INTO field_surveys VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", surveys_data)

    con.close()
    print(f"\n[OK] Database '{DB_FILE}' initialized and seeded successfully!")
    print(f"   -> 4 Protected Zones (Kaziranga, Corbett, Sundarbans, Ranthambore)")
    print(f"   -> 9 Tagged Animals (GPS Collar & RFID)")
    print(f"   -> 225 GPS Telemetry Records (25 ticks x 9 animals)")
    print(f"   -> 100 IoT Sensor Records (25 ticks x 4 zones)")
    print(f"   -> 10 Health & Rescue Event Logs")
    print(f"   -> 4 Conservation Projects (Rs.1,075 Lakhs total grants)")
    print(f"   -> 4 Field Survey Reports\n")

if __name__ == "__main__":
    init_database()
