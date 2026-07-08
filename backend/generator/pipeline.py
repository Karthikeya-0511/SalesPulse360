import pandas as pd
import boto3
import glob

import os

from services.activity_service import add_activity
from generator.state_service import save_control_state, load_control_state, mark_bootstrapped
from database import get_connection

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

dataset_path = os.path.join(
    BASE_DIR,
    "datasets",
    "Campfly Sales Analysis Dashboard (1).xlsx"
)

TEMP_FOLDER = os.path.join(
    BASE_DIR,
    "temp"
)

os.makedirs(
    TEMP_FOLDER,
    exist_ok=True
)

if not os.path.exists(dataset_path):
    raise FileNotFoundError(
        f"Dataset not found: {dataset_path}"
    )

# ===========================
# LOAD DATASET
# ===========================

sales_orders_df = pd.read_excel(
    dataset_path,
    sheet_name="Sales Orders"
)

customers_df = pd.read_excel(
    dataset_path,
    sheet_name="Customers"
)

regions_df = pd.read_excel(
    dataset_path,
    sheet_name="Regions"
)

products_df = pd.read_excel(
    dataset_path,
    sheet_name="Products"
)

print("=" * 60)

print("Dataset Loaded Successfully")

print(f"Sales Orders : {len(sales_orders_df)}")

print(f"Customers : {len(customers_df)}")

print(f"Products : {len(products_df)}")

print(f"Regions : {len(regions_df)}")

print("=" * 60)

"""# Replay Streaming Configuration

"""

import time
from datetime import datetime

BATCH_SIZE = 10
STREAM_DELAY = 30

"""# AWS S3 Integration"""

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
BUCKET_NAME = os.getenv("BUCKET_NAME")

required = {
    "AWS_ACCESS_KEY": AWS_ACCESS_KEY,
    "AWS_SECRET_KEY": AWS_SECRET_KEY,
    "AWS_REGION": AWS_REGION,
    "BUCKET_NAME": BUCKET_NAME,
}

print("=" * 50)
print("AWS_ACCESS_KEY :", AWS_ACCESS_KEY)
print("AWS_SECRET_KEY :", "Loaded" if AWS_SECRET_KEY else None)
print("AWS_REGION     :", AWS_REGION)
print("BUCKET_NAME    :", BUCKET_NAME)
print("=" * 50)

for key, value in required.items():

    if not value:

        raise ValueError(
            f"Missing Environment Variable : {key}"
        )

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

import boto3

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def clear_raw_bucket():

    objects = s3.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix="raw/"
    )

    if "Contents" in objects:

        delete_keys = [
            {"Key": obj["Key"]}
            for obj in objects["Contents"]
        ]

        s3.delete_objects(
            Bucket=BUCKET_NAME,
            Delete={"Objects": delete_keys}
        )

        print("Old S3 raw files deleted.")

    else:

        print("Raw folder already empty.")

# ---------------------------------------
# Snowflake Connection
# ---------------------------------------

import snowflake.connector

snowflake_connection = snowflake.connector.connect(

    user=os.getenv("SNOWFLAKE_USER"),

    password=os.getenv("SNOWFLAKE_PASSWORD"),

    account=os.getenv("SNOWFLAKE_ACCOUNT"),

    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),

    database=os.getenv("SNOWFLAKE_DATABASE"),

    schema=os.getenv("SNOWFLAKE_SCHEMA")

)

def reset_pipeline_tables():

    cursor = snowflake_connection.cursor()

    try:

        print("=" * 60)
        print("Resetting Snowflake Tables...")
        print("=" * 60)

        cursor.execute("""
        TRUNCATE TABLE RAW_SCHEMA.RAW_SALES_ORDERS;
        """)

        cursor.execute("""
        TRUNCATE TABLE STAGING_SCHEMA.STG_SALES_ORDERS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.SALES_ANALYTICS_MASTER;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.SALES_TREND_ANALYTICS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.MONTHLY_SALES_TRENDS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.WAREHOUSE_PERFORMANCE_ANALYTICS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.PRODUCT_PERFORMANCE_ANALYTICS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.REGIONAL_SALES_ANALYTICS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.CUSTOMER_BEHAVIOR_ANALYTICS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.CHANNEL_PERFORMANCE_ANALYTICS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.CURRENCY_ANALYTICS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.PROFITABILITY_ANALYTICS;
        """)

        cursor.execute("""
        TRUNCATE TABLE ANALYTICS_SCHEMA.EXECUTIVE_KPI_SUMMARY;
        """)

        print("All Snowflake tables cleared successfully.")

    finally:

        cursor.close()


def run_copy_into():

    cursor = snowflake_connection.cursor()

    try:

        # Select database
        cursor.execute("USE DATABASE SALESPULSE360_DB")

        # Select schema
        cursor.execute("USE SCHEMA RAW_SCHEMA")

        # Select warehouse
        cursor.execute("USE WAREHOUSE SALESPULSE360_WH")

        # Load new files from S3
        cursor.execute("""
            COPY INTO RAW_SALES_ORDERS
            FROM @SALES_RAW_STAGE
            FILE_FORMAT = (
                FORMAT_NAME = 'SALES_CSV_FORMAT'
            );
        """)

        print("RAW table updated successfully.")

    finally:

        cursor.close()

pipeline_state = {

    "running": False,
    "paused": False,
    "current_stage": "Idle",
    "current_batch": 0,
    "uploaded_rows": 0,
    "last_upload": "",
    "last_file": "",
    "replay_completed": False,
    "start_time": "",
    "end_time": "",
    "realtime_batches": 0,
    "total_batches": 0
}


# ============================================
# VERIFY S3 CONNECTION
# ============================================

def verify_s3_connection():

    try:

        s3_client.head_bucket(
            Bucket=BUCKET_NAME
        )

        print("=" * 60)
        print("S3 Bucket Connected Successfully")
        print("=" * 60)

    except Exception as e:

        raise Exception(
            f"S3 Connection Failed : {e}"
        )
    
# ==========================================================
# Refresh Analytics Tables in Snowflake
# ==========================================================

def refresh_staging():

    cursor = snowflake_connection.cursor()

    try:

        cursor.execute("USE DATABASE SALESPULSE360_DB")
        cursor.execute("USE SCHEMA STAGING_SCHEMA")
        cursor.execute("USE WAREHOUSE SALESPULSE360_WH")

        cursor.execute("""
        CREATE OR REPLACE TABLE STG_SALES_ORDERS AS
        SELECT
            ORDER_NUMBER,
            ORDER_DATE,
            SHIP_DATE,
            CUSTOMER_NAME_INDEX,
            CHANNEL,
            CURRENCY_CODE,
            WAREHOUSE_CODE,
            DELIVERY_REGION_INDEX,
            PRODUCT_DESCRIPTION_INDEX,
            ORDER_QUANTITY,
            UNIT_PRICE,
            TOTAL_UNIT_COST,
            TOTAL_REVENUE,
            REPLAY_TIMESTAMP,

            DATEDIFF(
                DAY,
                ORDER_DATE,
                SHIP_DATE
            ) AS DELIVERY_DAYS,

            (
                TOTAL_REVENUE -
                (ORDER_QUANTITY * TOTAL_UNIT_COST)
            ) AS PROFIT,

            ROUND(
            (
                TOTAL_REVENUE -
                (ORDER_QUANTITY * TOTAL_UNIT_COST)
            )
            / NULLIF(TOTAL_REVENUE,0)
            *100,
            2
            ) AS PROFIT_MARGIN_PERCENT

        FROM SALESPULSE360_DB.RAW_SCHEMA.RAW_SALES_ORDERS;
        """)

        print("STAGING table refreshed successfully.")

    finally:

        cursor.close()


def refresh_analytics():

    cursor = snowflake_connection.cursor()

    try:

        print("=" * 60)
        print("Refreshing Analytics Tables...")
        print("=" * 60)

        cursor.execute("""
        CALL ANALYTICS_SCHEMA.REFRESH_ANALYTICS();
        """)

        print("Analytics tables refreshed successfully.")

    finally:

        cursor.close()


def replay_old_dataset():

    global pipeline_state

    # ------------------------------------
    # Pipeline Status
    # ------------------------------------

    pipeline_state["running"] = True
    pipeline_state["python"] = "Running"
    pipeline_state["s3"] = "Waiting"
    pipeline_state["snowpipe"] = "Waiting"
    pipeline_state["snowflake"] = "Waiting"
    pipeline_state["sql"] = "Waiting"
    pipeline_state["powerbi"] = "Waiting"
    pipeline_state["start_time"] = datetime.now().strftime("%H:%M:%S")
    pipeline_state["current_stage"] = "Replay"
    pipeline_state["replay_completed"] = False

    print("=" * 60)
    print("Starting Historical Dataset Replay...")
    print("=" * 60)

    try:

        # ------------------------------------
        # Replay Historical Dataset
        # ------------------------------------

        for start_index in range(0, len(sales_orders_df), BATCH_SIZE):

            while pipeline_state["paused"]:
                print("Pipeline Paused...")

                time.sleep(1)

            if not pipeline_state["running"]:
                print("=" * 60)
                print("Replay stopped by user")
                print("=" * 60)
                pipeline_state["current_stage"] = "Stopped"
                return

            end_index = start_index + BATCH_SIZE

            batch_df = sales_orders_df.iloc[start_index:end_index].copy()

            # Replay Timestamp
            batch_df["replay_timestamp"] = datetime.now()

            # Batch Number
            batch_number = (start_index // BATCH_SIZE) + 1

            pipeline_state["total_batches"] = batch_number

            # File Name
            file_name = f"salespulse_batch_{batch_number}.csv"

            # Local File Path
            output_path = os.path.join(
                TEMP_FOLDER,
                file_name
            )

            # Save CSV
            batch_df.to_csv(
                output_path,
                index=False
            )

            # S3 Path
            s3_key = f"raw/{file_name}"

            # Upload to S3
            try:

                s3_client.upload_file(
                    output_path,
                    BUCKET_NAME,
                    s3_key
                )

                pipeline_state["s3"] = "Healthy"

                for _ in range(5):
                    if not pipeline_state["running"]:
                        print("Stopped during Snowpipe wait")
                        pipeline_state["current_stage"] = "Stopped"
                        return
                    time.sleep(1)
                run_copy_into()
                pipeline_state["snowpipe"] = "Healthy"
                refresh_staging()
                pipeline_state["snowflake"] = "Healthy"
                refresh_analytics()
                add_activity("Analytics Tables Refreshed")
                pipeline_state["sql"] = "Healthy"
                pipeline_state["powerbi"] = "Refreshing"

            except Exception as e:

                pipeline_state["running"] = False
                pipeline_state["current_stage"] = "Error"

                print(f"S3 Upload Failed : {e}")

                raise

            # ------------------------------------
            # Update Pipeline Status
            # ------------------------------------

            pipeline_state["current_batch"] = batch_number

            pipeline_state["uploaded_rows"] = min(
                end_index,
                len(sales_orders_df)
            )

            pipeline_state["last_upload"] = datetime.now().strftime("%H:%M:%S")

            pipeline_state["last_file"] = file_name

            print(
                f"Batch {batch_number} Uploaded | "
                f"{pipeline_state['uploaded_rows']} Rows Uploaded"
            )

            add_activity(f"Replay Batch {batch_number} Uploaded")
            pipeline_state["powerbi"] = "Healthy"

            for _ in range(STREAM_DELAY):
                if not pipeline_state["running"]:
                    print("Stopped during replay delay")
                    pipeline_state["current_stage"] = "Stopped"
                    return
                time.sleep(1)

        # ------------------------------------
        # Replay Completed
        # ------------------------------------

        pipeline_state["replay_completed"] = True
        pipeline_state["running"] = True
        pipeline_state["current_stage"] = "Realtime"
        pipeline_state["end_time"] = datetime.now().strftime("%H:%M:%S")

        print("=" * 60)
        print("Historical Replay Completed Successfully")
        print("Switching to Real-Time Generator...")
        print("=" * 60)

      

        # ------------------------------------
        # Delete Temporary CSV Files
        # ------------------------------------

        for file in glob.glob(
            os.path.join(
                TEMP_FOLDER,
                "*.csv"
            )
        ):
            os.remove(file)

        print("Temporary Files Deleted")

    except Exception as e:

        pipeline_state["running"] = False
        pipeline_state["current_stage"] = "Error"

        print("=" * 60)
        print("Replay Failed")
        print(e)
        print("=" * 60)

        raise

def upload_dimension_tables():

    print("Uploading Dimension Tables...")

    # -----------------------------
    # Customers
    # -----------------------------

    customers_path = os.path.join(
        TEMP_FOLDER,
        "customers.csv"
    )

    customers_df.to_csv(
        customers_path,
        index=False
    )

    s3_client.upload_file(
        customers_path,
        BUCKET_NAME,
        "dimensions/customers.csv"
    )

    print("Customers Uploaded")


    # -----------------------------
    # Products
    # -----------------------------

    products_path = os.path.join(
        TEMP_FOLDER,
        "products.csv"
    )

    products_df.to_csv(
        products_path,
        index=False
    )

    s3_client.upload_file(
        products_path,
        BUCKET_NAME,
        "dimensions/products.csv"
    )

    print("Products Uploaded")


    # -----------------------------
    # Regions
    # -----------------------------

    regions_path = os.path.join(
        TEMP_FOLDER,
        "regions.csv"
    )

    regions_df.to_csv(
        regions_path,
        index=False
    )

    s3_client.upload_file(
        regions_path,
        BUCKET_NAME,
        "dimensions/regions.csv"
    )

    print("Regions Uploaded")

    print("All Dimension Tables Uploaded Successfully")

"""# New events generator"""

"""
╔══════════════════════════════════════════════════════════════════╗
║         CAMPFLY SALESPULSE360 — REAL-TIME EVENT GENERATOR V2    ║
║                                                                  ║
║  Continues EXACTLY from record 7992, 7993, 7994...              ║
║  Seasonal patterns based on: Amazon, Flipkart, Myntra,          ║
║  AJIO — festive spikes, summer highs, monsoon lows,             ║
║  winter moderate — realistic company behaviour                   ║
║                                                                  ║
║  Pipeline: Python → CSV → AWS S3 → Snowpipe → Snowflake → PBI   ║
╚══════════════════════════════════════════════════════════════════╝

PASTE THIS INTO YOUR EXISTING GOOGLE COLAB NOTEBOOK
after your original 80 batches are uploaded.

HOW TO INTEGRATE WITH YOUR ORIGINAL CODE:
  1. Keep all your original code (library imports, S3 setup, batch upload)
  2. At the very end of your notebook, paste this entire script
  3. Run cell by cell
  4. New records will be 7992, 7993... appending to Snowflake automatically
"""

# ── IMPORTS (already imported in your notebook, kept here for standalone use) ──
import pandas as pd
import numpy as np
import random
import time
import os
import csv
import io
from datetime import datetime, timedelta, date
import calendar

# ── YOUR EXISTING S3 CLIENT ──
# In your Colab notebook, s3_client is already created.
# If running standalone, uncomment and fill these:
# import boto3
# s3_client = boto3.client('s3',
#     aws_access_key_id="YOUR_KEY",
#     aws_secret_access_key="YOUR_SECRET",
#     region_name="ap-south-1")

BUCKET_NAME = os.getenv("BUCKET_NAME")         # Your existing S3 bucket
S3_RAW_PREFIX = "raw/"                         # Same prefix as your original batches
STREAM_DELAY  =  30                           # Seconds between uploads (30 = realistic)
ORDERS_PER_BATCH = (4, 9)                      # Random 4–9 orders per upload

# ── CONTINUATION CONFIG ──
LAST_RECORD_NUMBER = 7991     # Your historical dataset ends here
LAST_ORDER_NUM     = 8091     # Last SO number in your dataset (SO - 0008091)
START_DATE         = datetime(2020, 1, 1)      # Continue from 2020 onwards

# ─────────────────────────────────────────────────────────────────
#  REAL COMPANY SEASONAL INTELLIGENCE
#  Based on: Amazon, Flipkart, Myntra, AJIO, Nykaa sales patterns
#  Adapted for NZ B2B wholesale market (Campfly dataset context)
#
#  KEY EVENTS THAT DRIVE SALES (company-realistic):
#  ► January   : New Year clearance + fresh budgets → MODERATE HIGH
#  ► February  : Post-new-year lull, Valentine's minor bump → LOW
#  ► March     : End of financial year (NZ FY ends Mar 31) → VERY HIGH SPIKE
#  ► April     : Easter buying + Autumn season changeover → MODERATE
#  ► May       : Mother's Day, Budget announcements → MODERATE
#  ► June     : EOFY (End of Financial Year NZ) → HIGH SPIKE (bulk orders)
#  ► July     : Winter mid-year, school holidays, low retail → LOW
#  ► August   : Winter clearance sales (like Amazon Prime Day effect) → HIGH
#  ► September  : Spring begins, new season stock orders → HIGH
#  ► October   : Pre-summer build-up, Halloween (minor in NZ) → HIGH
#  ► November  : BLACK FRIDAY, Singles Day equiv → VERY HIGH PEAK
#  ► December  : Christmas buying THEN sudden post-25 Dec cliff → HIGH→LOW
#
#  YEAR-LEVEL EVENTS:
#  2020 → COVID year: Q1 strong, Q2 CRASH (-40%), Q3 recovery, Q4 strong
#  2021 → Recovery year: steady growth, vaccine rollout boost
#  2022 → Post-COVID boom: strong across all quarters
#  2023 → Normalisation: slight cooling, inflation pressure
# ─────────────────────────────────────────────────────────────────

# Monthly multipliers — orders relative to base (222/month)
# 1.0 = normal, 1.3 = 30% more orders, 0.7 = 30% fewer
MONTHLY_MULTIPLIERS = {
    1:  1.08,   # January  — fresh budgets, new year orders
    2:  0.88,   # February — lull, lowest non-festive month
    3:  1.25,   # March    — SPIKE: NZ financial year end, bulk procurement
    4:  1.00,   # April    — Easter, moderate
    5:  1.05,   # May      — Mother's Day, budget cycle orders
    6:  1.18,   # June     — EOFY bulk orders, winter clearance begins
    7:  0.82,   # July     — Mid-winter low, school holidays slow B2B
    8:  1.12,   # August   — Winter sale season, stock replenishment
    9:  1.15,   # September— Spring launch, new season stock orders
    10: 1.10,   # October  — Pre-summer build-up, pre-Black Friday stocking
    11: 1.35,   # November — BLACK FRIDAY effect + Christmas stock rush (PEAK)
    12: 1.20,   # December — Christmas orders (spike early, cliff after 20th)
}

# Year-level multipliers — macro economic events
YEARLY_MULTIPLIERS = {
    2020: 0.72,   # COVID impact — strong Jan, crash Apr-Jun, recovery Aug+
    2021: 0.95,   # Recovery + vaccine confidence
    2022: 1.10,   # Post-COVID boom, pent-up demand
    2023: 1.05,   # Normalization, slight inflation headwind
    2024: 1.18,   # Stable growth
    2025: 1.26,   # Continued growth
}

# COVID monthly override — 2020 specific (overrides monthly multiplier)
COVID_2020_MONTHLY = {
    1:  1.10,   # Pre-COVID strong
    2:  1.05,   # Still pre-COVID
    3:  0.95,   # COVID begins (lockdown announced mid-March in NZ)
    4:  0.45,   # LOCKDOWN — massive crash (like real Amazon March/April 2020)
    5:  0.55,   # Partial recovery, essential goods only
    6:  0.72,   # Gradual reopening
    7:  0.85,   # Level 1, cautious recovery
    8:  0.90,   # Recovery continues
    9:  1.05,   # Near-normal
    10: 1.10,   # Strong rebound
    11: 1.25,   # Black Friday + vaccine news boost
    12: 1.18,   # Christmas recovery
}

# Day-of-week weights — B2B wholesale (Mon–Fri business, Sat/Sun low)
# From your actual data: Thu(1201) > Wed(1156) > Fri(1170) > Mon(1120) > Sun(1140) > Tue(1132) > Sat(1072)
DOW_WEIGHTS = {
    0: 1.04,   # Monday
    1: 1.02,   # Tuesday
    2: 1.07,   # Wednesday
    3: 1.12,   # Thursday — PEAK weekday for B2B
    4: 1.08,   # Friday
    5: 0.85,   # Saturday — lower (B2B weekend slowdown)
    6: 0.95,   # Sunday
}

# Week-within-month pattern — companies bulk order at month start and end
# Week 1 (days 1-7): high (new month budget released)
# Week 2 (days 8-14): moderate
# Week 3 (days 15-21): moderate
# Week 4 (days 22+): high (end of month rush, invoicing deadlines)
def get_day_weight(day_of_month):
    if day_of_month <= 7:
        return 1.12    # Month start — budget released
    elif day_of_month <= 14:
        return 0.95    # Mid-month quiet
    elif day_of_month <= 21:
        return 0.92    # Mid-month quiet
    else:
        return 1.08    # Month end — deadline rush


# ─────────────────────────────────────────────
#  EXACT DATA FROM YOUR HISTORICAL DATASET
# ─────────────────────────────────────────────

CUSTOMERS = [
    "Avon Corp", "WakeFern", "Elorac, Corp", "ETUDE Ltd", "Procter Corp",
    "PEDIFIX, Corp", "New Ltd", "Medsep Group", "Ei", "21st Ltd",
    "Apollo Ltd", "Medline", "Ole Group", "Linde", "Rochester Ltd",
    "3LAB, Ltd", "Pure Group", "Eminence Corp", "Qualitest", "Pacific Ltd",
    "Ohio", "Capweld", "E. Ltd", "Burt's Corp", "Prasco Group",
    "Mylan Corp", "Wuxi Group", "Dharma Ltd", "Apotheca, Ltd", "S.S.S. Group",
    "Uriel Group", "OHTA'S Corp", "Trigen", "OUR Ltd", "Amylin Group",
    "O.E. Ltd", "AuroMedics Corp", "Ascend Ltd", "Victory Ltd", "Select",
    "Weimei Corp", "Llorens Ltd", "Exact-Rx, Corp", "Winthrop", "Nipro",
    "U.S. Ltd", "Niconovum Corp", "Fenwal, Corp", "Bare", "Sundial"
]
CUSTOMER_INDICES = list(range(1, 51))

PRODUCTS = {
    1:  ("Product 1",  0.1644, {"mean":2304.64, "std":1691.73, "min":167.5,  "max":6566.0}),
    2:  ("Product 2",  0.1465, {"mean":2285.53, "std":1665.62, "min":167.5,  "max":6559.3}),
    3:  ("Product 3",  0.0201, {"mean":2194.27, "std":1656.68, "min":167.5,  "max":6452.1}),
    4:  ("Product 4",  0.0204, {"mean":2121.60, "std":1514.16, "min":167.5,  "max":6539.2}),
    5:  ("Product 5",  0.1081, {"mean":2349.16, "std":1656.28, "min":167.5,  "max":6559.3}),
    6:  ("Product 6",  0.0218, {"mean":2318.39, "std":1796.08, "min":167.5,  "max":6472.2}),
    7:  ("Product 7",  0.1662, {"mean":2313.74, "std":1695.36, "min":167.5,  "max":6545.9}),
    8:  ("Product 8",  0.0206, {"mean":2290.02, "std":1746.13, "min":167.5,  "max":6304.7}),
    9:  ("Product 9",  0.0611, {"mean":2171.29, "std":1721.36, "min":167.5,  "max":6539.2}),
    10: ("Product 10", 0.0204, {"mean":2214.62, "std":1599.60, "min":167.5,  "max":6016.6}),
    11: ("Product 11", 0.1329, {"mean":2295.32, "std":1658.54, "min":167.5,  "max":6532.5}),
    12: ("Product 12", 0.0195, {"mean":2300.51, "std":1797.82, "min":167.5,  "max":6505.7}),
    13: ("Product 13", 0.0787, {"mean":2198.21, "std":1593.64, "min":167.5,  "max":6559.3}),
    14: ("Product 14", 0.0191, {"mean":2409.55, "std":1651.77, "min":187.6,  "max":6552.6}),
}

CHANNELS    = {"Wholesale":0.5364, "Distributor":0.3141, "Export":0.1495}
CURRENCIES  = {"NZD":0.3787, "USD":0.2907, "AUD":0.1638, "GBP":0.0837, "EUR":0.0831}
WAREHOUSES  = {"AXW291":0.4700, "GUT930":0.2315, "NXH382":0.1963, "FLR025":0.1021}

REGIONS = [
    (1,"Freemans Bay","Auckland",1011,174.748652,-36.855732),
    (2,"Nightcaps","Southland",9630,168.028823,-45.970300),
    (3,"Northcote","North Shore",627,174.755505,-36.804712),
    (4,"Bay View","Napier",4104,176.871662,-39.440389),
    (5,"Parklands","Christchurch",8083,172.705997,-43.472699),
    (6,"Hamilton East","Hamilton",3216,175.305496,-37.781657),
    (7,"Te Kuiti","Waitomo",3910,175.163086,-38.330973),
    (8,"Opaheke","Papakura",2113,174.947631,-37.077401),
    (9,"North East Valley","Dunedin",9010,170.527081,-45.846837),
    (10,"Whangamata","Thames-Coromandel",3620,175.883257,-37.219172),
    (11,"Algies Bay","Rodney",920,174.745447,-36.437912),
    (12,"Henderson","Waitakere",610,174.634157,-36.870359),
    (13,"Atawhai","Nelson",7010,173.326718,-41.241585),
    (14,"Pleasant Point","Timaru",7903,171.122902,-44.258881),
    (15,"Frimley","Hastings",4120,176.832406,-39.621293),
    (16,"Harrowfield","Hamilton",3210,175.266597,-37.742625),
    (17,"Tapanui","Clutha",9522,169.262758,-45.942122),
    (18,"Tokoroa","South Waikato",3420,175.869172,-38.220872),
    (19,"Thames","Thames-Coromandel",3500,175.547120,-37.093270),
    (20,"Onekawa Industrial","Napier",4110,176.875116,-39.498856),
    (21,"Brightwater","Tasman",7022,173.109791,-41.377984),
    (22,"Stewart Island","Southland",9818,168.142741,-46.905258),
    (23,"Redwood","Christchurch",8051,172.624561,-43.473623),
    (24,"Parahaki","Whangarei",112,174.343159,-35.720964),
    (25,"Dannemora","Manukau",2016,174.927840,-36.925085),
    (26,"Kawakawa","Far North",210,174.060154,-35.383953),
    (27,"Grafton","Auckland",1023,174.760742,-36.887168),
    (28,"Napier South","Napier",4110,176.903281,-39.493863),
    (29,"Timaru Central","Timaru",7910,171.249248,-44.394775),
    (30,"Riverside","Whangarei",112,174.327519,-35.720207),
    (31,"Te Atatu Peninsula","Waitakere",610,174.655242,-36.843942),
    (32,"Dinsdale","Hamilton",3204,175.250387,-37.801230),
    (33,"Titirangi","Waitakere",604,174.651505,-36.923203),
    (34,"Kingsland","Auckland",1021,174.730933,-36.873186),
    (35,"Takaro","Palmerston North",4412,175.592231,-40.346893),
    (36,"Milson","Palmerston North",4414,175.603585,-40.325619),
    (37,"Putaruru","South Waikato",3411,175.779615,-38.045388),
    (38,"Matua","Tauranga",3110,176.118357,-37.667598),
    (39,"Rototuna","Hamilton",3210,175.271035,-37.736857),
    (40,"Oamaru North","Waitaki",9400,170.981917,-45.084561),
    (41,"Port Taranaki","New Plymouth",4310,174.037085,-39.062397),
    (42,"Okitu","Gisborne",4010,178.079269,-38.675235),
    (43,"Sandringham","Auckland",1041,174.740112,-36.889843),
    (44,"Dannevirke","Tararua",4930,176.101211,-40.209740),
    (45,"South Hill","Waitaki",9400,170.959593,-45.113433),
    (46,"Tapanui","Clutha",9522,169.260962,-45.947712),
    (47,"Kaiapoi","Waimakariri",7630,172.664763,-43.380606),
    (48,"Henderson","Waitakere",612,174.611989,-36.890277),
    (49,"Cannons Creek","Porirua",5024,174.871552,-41.134707),
    (50,"Favona","Manukau",2024,174.808787,-36.958178),
    (51,"Farm Cove","Manukau",2012,174.881171,-36.897446),
    (52,"Otaki Beach","Kapiti Coast",5512,175.117303,-40.743091),
    (53,"Hillsborough","Auckland",1042,174.759859,-36.930333),
    (54,"Cashmere","Christchurch",8022,172.637838,-43.583878),
    (55,"Taupo","Taupo",3330,176.096738,-38.712121),
    (56,"Barrington","Christchurch",8024,172.605552,-43.552524),
    (57,"Cambridge","Waipa",3434,175.461867,-37.881933),
    (58,"Chartwell","Hamilton",3210,175.269405,-37.759953),
    (59,"Otamatea","Wanganui",4500,175.030389,-39.912265),
    (60,"Regent","Whangarei",112,174.322224,-35.719880),
    (61,"Georgetown","Invercargill",9812,168.372072,-46.418892),
    (62,"Hunterville","Rangitikei",4730,175.565276,-39.927125),
    (63,"Birkdale","North Shore",626,174.691464,-36.808175),
    (64,"New Lynn","Waitakere",600,174.675729,-36.924723),
    (65,"Waimate","Waimate",7924,171.037652,-44.727649),
    (66,"Saint Kilda","Dunedin",9012,170.503414,-45.903724),
    (67,"Tokoroa","South Waikato",3420,175.873883,-38.225012),
    (68,"Queenwood","Hamilton",3210,175.265640,-37.746122),
    (69,"Brightwater","Tasman",7022,173.108682,-41.377238),
    (70,"Titirangi","Waitakere",604,174.645905,-36.931745),
    (71,"Wanaka","Queenstown-Lakes",9305,169.128174,-44.670586),
    (72,"Chartwell","Hamilton",3210,175.280068,-37.754249),
    (73,"Pukekohe","Franklin",2120,174.905423,-37.202057),
    (74,"Opawa","Christchurch",8023,172.662116,-43.555190),
    (75,"Ebdentown","Upper Hutt",5018,175.076852,-41.119622),
    (76,"Dannemora","Manukau",2016,174.913814,-36.953248),
    (77,"Cashmere","Christchurch",8022,172.620100,-43.573540),
    (78,"Manurewa East","Manukau",2102,174.906709,-37.026688),
    (79,"Whitianga","Thames-Coromandel",3510,175.703096,-36.835644),
    (80,"Aramoho","Wanganui",4500,175.067994,-39.897398),
    (81,"Ngapuna","Rotorua",3010,176.275761,-38.147231),
    (82,"Putaruru","South Waikato",3411,175.783241,-38.037438),
    (83,"Henderson","Waitakere",612,174.612803,-36.885762),
    (84,"Dannemora","Manukau",2016,174.902986,-36.942084),
    (85,"Eketahuna","Tararua",4900,175.706993,-40.646861),
    (86,"Timberlea","Upper Hutt",5018,175.118020,-41.095932),
    (87,"Harewood","Christchurch",8051,172.573287,-43.490223),
    (88,"Turangi","Taupo",3334,175.799419,-38.986085),
    (89,"Epsom","Auckland",1023,174.770677,-36.907152),
    (90,"Ranfurly","Central Otago",9332,170.107612,-45.124759),
    (91,"Highbury","Palmerston North",4412,175.578470,-40.364503),
    (92,"Maraenui","Napier",4110,176.900548,-39.516595),
    (93,"Bay View","Napier",4104,176.867338,-39.423452),
    (94,"Hataitai","Wellington",6021,174.799642,-41.299958),
    (95,"Te Aroha","Matamata-Piako",3320,175.708285,-37.530127),
    (96,"Caversham","Dunedin",9012,170.487737,-45.895704),
    (97,"Palmerston North","Palmerston North",4410,175.612095,-40.345933),
    (98,"Ngatea","Hauraki",3503,175.496443,-37.275142),
    (99,"Raglan","Waikato",3225,174.870013,-37.801056),
    (100,"Northcote","North Shore",627,174.739814,-36.805970),
]


# ─────────────────────────────────────────────
#  CORE HELPER FUNCTIONS
# ─────────────────────────────────────────────

def weighted_choice(options_dict):
    keys    = list(options_dict.keys())
    weights = list(options_dict.values())
    return random.choices(keys, weights=weights, k=1)[0]


def generate_unit_price(product_idx):
    """Realistic price — truncated normal, 1 decimal, never round number."""
    _, _, params = PRODUCTS[product_idx]
    for _ in range(50):
        price = np.random.normal(params["mean"], params["std"])
        if params["min"] <= price <= params["max"]:
            price = round(price, 1)
            # Ensure it has a non-zero decimal (not like 2300.0)
            if price % 1 == 0:
                price += random.choice([0.1,0.2,0.3,0.4,0.6,0.7,0.8,0.9])
            return round(price, 1)
    return round(params["mean"] + random.uniform(-50, 50), 1)


def generate_total_cost(unit_price, quantity, order_date):

    month = order_date.month

    if month in [11,12]:
        cost_ratio = random.uniform(0.52,0.62)

    elif month in [3,6]:
        cost_ratio = random.uniform(0.55,0.67)

    elif month in [7]:
        cost_ratio = random.uniform(0.70,0.82)

    else:
        cost_ratio = random.uniform(0.58,0.75)

    return round(unit_price * quantity * cost_ratio,3)


def get_monthly_order_target(year, month, base=222):
    """
    Get realistic order count for a given year+month.
    Applies: seasonal multiplier + yearly macro multiplier + COVID override + random noise
    """
    # COVID 2020 special case
    if year == 2020:
        seasonal = COVID_2020_MONTHLY[month]
    else:
        seasonal = MONTHLY_MULTIPLIERS[month]

    yearly = YEARLY_MULTIPLIERS.get(year, 1.10)  # default 10% growth for future years
    noise  = random.uniform(0.85, 1.20)           # ±7% random variation

    target = base * seasonal * yearly * noise
    return max(80, int(target))   # floor of 80 orders — even worst months have some


def generate_order_dates_for_month(year, month, n_orders):
    """
    Distribute n_orders realistically across a month.
    More orders at month start/end (B2B budget cycles).
    More orders on weekdays (Thursday peak).
    Simulates how real companies like Amazon have non-uniform daily order flow.
    """
    days_in_month = calendar.monthrange(year, month)[1]

    # Build weighted day list
    day_weights = []
    for day in range(1, days_in_month + 1):
        d = datetime(year, month, day)
        dow_w   = DOW_WEIGHTS[d.weekday()]
        week_w  = get_day_weight(day)
        day_weights.append(dow_w * week_w)

    # Normalize weights
    total_w = sum(day_weights)
    day_probs = [w / total_w for w in day_weights]

    # Sample days for all orders
    days = list(range(1, days_in_month + 1))
    chosen_days = random.choices(days, weights=day_probs, k=n_orders)

    return [datetime(year, month, d) for d in sorted(chosen_days)]


# ─────────────────────────────────────────────
#  MAIN ORDER GENERATOR
# ─────────────────────────────────────────────

# Track global record number and order SO number
_record_counter = [LAST_RECORD_NUMBER]      # mutable so inner functions can update
_order_so_counter = [LAST_ORDER_NUM + 1]    # next SO number after 8091
_used_so_numbers = set()


def next_order_number():
    so_num = _order_so_counter[0]
    _order_so_counter[0] += 1
    return f"SO - {str(so_num).zfill(7)}"


def generate_single_order(order_date):
    """
    Generate one realistic order row.
    Record counter increments: 7992, 7993, 7994...
    All fields match historical data format exactly.
    """
    _record_counter[0] += 1

    # Pick product (weighted by historical frequency)
    prod_idx  = random.choices(
        list(PRODUCTS.keys()),
        weights=[v[1] for v in PRODUCTS.values()],
        k=1
    )[0]
    prod_name, _, _ = PRODUCTS[prod_idx]

    # Pick customer uniformly (all 50 active)
    vip_customers = [1,2,5,7,11,18,25]
    if random.random() < 0.40:
      cust_idx = random.choice(vip_customers)
    else:
      cust_idx = random.randint(1,50)
    cust_name = CUSTOMERS[cust_idx - 1]

    # Pick region
    region    = random.choice(REGIONS)
    reg_idx, suburb, city, postcode, lon, lat = region

    # Channel, currency, warehouse — exact historical probabilities
    channel   = weighted_choice(CHANNELS)
    currency  = weighted_choice(CURRENCIES)
    warehouse = weighted_choice(WAREHOUSES)

    # Order quantity: uniform 5–12 (exactly as historical)
    month = order_date.month
    if month in [11,12]:
      quantity = random.randint(8,20)
    elif month in [3,6]:
      quantity = random.randint(7,16)
    elif month in [7]:
      quantity = random.randint(3,8)
    else:
      quantity = random.randint(5,12)

    # Pricing
    unit_price = generate_unit_price(prod_idx)
    if month in [11, 12]:
      unit_price = round(unit_price * random.uniform(1.10, 1.25), 1)
    elif month == 7:
      unit_price = round(unit_price * random.uniform(0.90, 0.97), 1)
    else:
      unit_price = round(unit_price, 1)

    total_revenue = round(unit_price * quantity, 1)
    total_cost    = generate_total_cost(unit_price, quantity, order_date)

    # Ship date: order_date + 3 to 18 days (uniform, as historical)
    month = order_date.month
    if month in [11,12]:
      delivery_days = random.randint(10,20)
    elif month in [6,7]:
      delivery_days = random.randint(8,16)
    elif month in [1,2]:
      delivery_days = random.randint(5,12)
    else:
      delivery_days = random.randint(2,10)

    if random.random() < 0.05:
      delivery_days += random.randint(3,10)
    ship_date = order_date + timedelta(days=delivery_days)

    # Order number (SO - XXXXXXX)
    order_number  = next_order_number()

    return {
        "OrderNumber":               order_number,
        "OrderDate":                 order_date.strftime("%Y-%m-%d"),
        "Ship Date":                 ship_date.strftime("%Y-%m-%d"),
        "Customer Name Index":       cust_idx,
        "Channel":                   channel,
        "Currency Code":             currency,
        "Warehouse Code":            warehouse,
        "Delivery Region Index":     reg_idx,
        "Product Description Index": prod_idx,
        "Order Quantity":            quantity,
        "Unit Price":                unit_price,
        "Total Unit Cost":           total_cost,
        "Total Revenue":             total_revenue,
        # Denormalized — helps Power BI & Snowflake directly
        "replay_timestamp":          datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

    }


# ─────────────────────────────────────────────
#  GENERATE FULL MONTH — for backfilling
# ─────────────────────────────────────────────

def generate_month(year, month):
    """
    Generate a full realistic month of orders.
    Returns list of order dicts.
    """
    n_orders = get_monthly_order_target(year, month)
    dates    = generate_order_dates_for_month(year, month, n_orders)
    orders   = [generate_single_order(d) for d in dates]
    return orders


def orders_to_csv_string(orders):
    """Convert list of order dicts to CSV string (for S3 upload)."""
    if not orders:
        return ""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(orders[0].keys()))
    writer.writeheader()
    writer.writerows(orders)
    return buf.getvalue()


def upload_batch_to_s3(orders, batch_label, s3_client_ref):
    """Upload a batch of orders to S3 — same path as your original batches."""
    csv_str = orders_to_csv_string(orders)
    s3_key  = f"{S3_RAW_PREFIX}realtime_{batch_label}.csv"
    s3_client_ref.put_object(
        Bucket      = BUCKET_NAME,
        Key         = s3_key,
        Body        = csv_str.encode("utf-8"),
        ContentType = "text/csv"
    )
    return s3_key


# ─────────────────────────────────────────────
#  MODE 1: BACKFILL 2020–2022
#  Run this FIRST to populate missing years
#  into Snowflake before going live
# ─────────────────────────────────────────────

def run_backfill(s3_client_ref, start_year=2020, end_year=2025):
  _record_counter[0] = LAST_RECORD_NUMBER
  _order_so_counter[0] = LAST_ORDER_NUM + 1
  print("=" * 60)
  print("  CAMPFLY BACKFILL — 2020 to 2022")
  print(f"  Continuing from record #{LAST_RECORD_NUMBER + 1}")
  print("=" * 60)
  total_uploaded = 0
  carry_forward = []
  batch_no = 1

  for year in range(start_year, end_year + 1):
    print(f"\n── Year {year} ──")
    for month in range(1, 13):
      orders = generate_month(year, month)
      label  = f"{year}_{str(month).zfill(2)}"

      carry_forward.extend(orders)
      while len(carry_forward) >= 10:
        batch_orders = carry_forward[:10]
        carry_forward = carry_forward[10:]

        s3_key = upload_batch_to_s3(
            batch_orders,
            f"batch_{batch_no}",
            s3_client_ref
        )

        time.sleep(5)

        run_copy_into()

        refresh_staging()

        refresh_analytics()

        print(
            f"Batch {batch_no} | "
            f"{batch_orders[0]['OrderNumber']} -> "
            f"{batch_orders[-1]['OrderNumber']} | "
            f"{len(batch_orders)} orders"
        )

        total_uploaded += len(batch_orders)

        batch_no += 1

        time.sleep(8) # small delay between batches

  # Process any remaining orders in carry_forward after the loops finish
  if len(carry_forward) > 0:
    s3_key = upload_batch_to_s3(
        carry_forward,
        f"batch_{batch_no}",
        s3_client_ref
    )

    time.sleep(5)

    run_copy_into()

    refresh_staging()

    refresh_analytics()

    total_uploaded += len(carry_forward)

    print(
        f"Final Batch {batch_no} | "
        f"{len(carry_forward)} orders"
    )

  print(f"\n✓ Backfill complete! Total new records: {total_uploaded:,}")
  print(f"  Last record number: #{_record_counter[0]}")
  print(f"  Last SO number:     SO - {str(_order_so_counter[0]-1).zfill(7)}")


# ─────────────────────────────────────────────
#  MODE 2: REAL-TIME STREAMING LOOP
#  After backfill, run this for continuous flow
# ─────────────────────────────────────────────

def run_realtime_stream(s3_client_ref, simulate_from=None):
    """
    Continuous real-time event generator.
    Every STREAM_DELAY seconds: generates 4–9 orders → uploads to S3 → Snowpipe → Snowflake.

    simulate_from: datetime to simulate orders from (default: today)
    """
    print("=" * 60)
    print("  CAMPFLY REAL-TIME STREAM — STARTED")
    print(f"  Interval : every {STREAM_DELAY} seconds")
    print(f"  Orders   : {ORDERS_PER_BATCH[0]}–{ORDERS_PER_BATCH[1]} per batch")
    print(f"  Continuing from record #{_record_counter[0] + 1}")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    current_sim_date = simulate_from or datetime.now()
    batch_num        = 0

    try:
        while pipeline_state["running"]:
            try:
                batch_num  += 1
                pipeline_state["realtime_batches"] += 1
                pipeline_state["current_batch"] += 1
                n           = random.randint(*ORDERS_PER_BATCH)
                now_str     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Generate orders for current simulated date
                orders = [generate_single_order(current_sim_date) for _ in range(n)]

                # Upload to S3
                label  = datetime.now().strftime("%Y%m%d_%H%M%S")
                s3_key = upload_batch_to_s3(orders, f"live_{label}", s3_client_ref)

                time.sleep(5)
                pipeline_state["snowpipe"] = "Running"

                run_copy_into()

                pipeline_state["snowpipe"] = "Healthy"

                pipeline_state["snowflake"] = "Running"

                refresh_staging()

                pipeline_state["snowflake"] = "Healthy"

                pipeline_state["sql"] = "Running"

                refresh_analytics()

                pipeline_state["sql"] = "Healthy"

                pipeline_state["powerbi"] = "Refreshing"

                time.sleep(2)

                pipeline_state["powerbi"] = "Healthy"

                pipeline_state["current_stage"] = "Realtime"
                pipeline_state["last_upload"] = datetime.now().strftime("%H:%M:%S")
                pipeline_state["last_file"] = s3_key
                pipeline_state["uploaded_rows"] += n
                add_activity(f"Realtime Batch {batch_num} Uploaded")

            # Log
                sample = orders[0]
                print(f"[{now_str}] Batch #{batch_num} — {n} orders uploaded → {s3_key}")
                print(f"  Orders: {orders[0]['OrderNumber']} - {orders[-1]['OrderNumber']}")
                print(f"  Sample : {sample['OrderNumber']} | Qty:{sample['Order Quantity']} | "
        f"${sample['Total Revenue']:>10,.1f} | {sample['Currency Code']} | "
        f"{sample['Channel']}")
                print()

            # Advance simulated date
                current_sim_date += timedelta(hours=random.randint(2, 8))

                pipeline_state["last_upload"] = datetime.now().strftime("%H:%M:%S")
                pipeline_state["current_stage"] = "Realtime"

                try:
                    conn = get_connection()
                    save_control_state(pipeline_state, conn, _record_counter[0], _order_so_counter[0])
                    conn.close()
                except Exception as e:
                    print("Failed to save control state:", e)

                time.sleep(STREAM_DELAY)

            except Exception as e:
                print("="*60)
                print("Realtime Stream Error")
                print(e)
                print("="*60)

            continue

    except KeyboardInterrupt:
        print(f"\n✓ Stream stopped after {batch_num} batches.")
        print(f"  Total records generated: {_record_counter[0] - LAST_RECORD_NUMBER:,}")
        print(f"  Last record number: #{_record_counter[0]}")

        pipeline_state["running"] = False
        pipeline_state["current_stage"] = "Stopped"



# ─────────────────────────────────────────────
#  QUICK TEST — Run this first to verify output
# ─────────────────────────────────────────────

def run_quick_test():
    """
    Generates 10 sample orders and prints them.
    No S3 upload needed — just verify the data looks right.
    """
    print("═" * 65)
    print("  CAMPFLY GENERATOR — QUICK TEST (no S3 upload)")
    print("═" * 65)
    print()

    test_cases = [
        ("Normal month",    datetime(2020, 5, 15)),
        ("COVID crash",     datetime(2020, 4, 8)),
        ("EOFY spike",      datetime(2021, 3, 28)),
        ("Black Friday",    datetime(2021, 11, 26)),
        ("Summer peak",     datetime(2022, 9, 10)),
    ]

    for label, dt in test_cases:
        o = generate_single_order(dt)
        print(f"   {o['OrderNumber']} | {o['OrderDate']}")
        print(f"   Qty:{o['Order Quantity']} | "
              f"Price:${o['Unit Price']:>8,.1f} | "
              f"Revenue:${o['Total Revenue']:>10,.1f} | "
              f"Cost:${o['Total Unit Cost']:>10,.3f}")
        print(f"   {o['Channel']} | {o['Currency Code']} | "
              f"{o['Warehouse Code']}")
        print()

    print("═" * 65)
    print("  MONTHLY ORDER VOLUME PROJECTION")
    print("═" * 65)
    _record_counter[0] = LAST_RECORD_NUMBER  # reset for clean display
    for year in [2020, 2021, 2022,2023,2024,2025]:
        yearly_total = sum(get_monthly_order_target(year, m) for m in range(1,13))
        print(f"\n  {year} (yearly_mult={YEARLY_MULTIPLIERS.get(year,'~1.10')}):\n")
        for m in range(1, 13):
            target = get_monthly_order_target(year, m)
            bar    = "█" * (target // 10)
            covid  = " ← COVID CRASH" if year == 2020 and m in [4,5] else ""
            fest   = " ← BLACK FRIDAY" if m == 11 else ""
            eofy   = " ← EOFY SPIKE" if m in [3,6] else ""
            print(f"    {year}-{str(m).zfill(2)}: {target:>4} orders  {bar}{covid}{fest}{eofy}")
        print(f"    TOTAL: {yearly_total:,} orders")


# ═════════════════════════════════════════════
#  HOW TO USE IN YOUR COLAB NOTEBOOK
#  Add these lines at the end of your notebook:
# ═════════════════════════════════════════════
"""
# ── STEP 1: Test without S3 first ──────────────────────────
run_quick_test()

# ── STEP 2: Backfill 2020–2022 into Snowflake ──────────────
# (Run ONCE — uploads 3 years of realistic data to S3/Snowflake)
run_backfill(s3_client, start_year=2020, end_year=2022)

# ── STEP 3: Start real-time stream ─────────────────────────
# (Runs continuously — generates live events every 30 seconds)
run_realtime_stream(s3_client)

# ── STEP 4: Setup Snowpipe ─────────────────────────────────
# (Run ONCE in Snowflake SQL Worksheet)
print(SNOWPIPE_SQL)
"""

# ─────────────────────────────────────────────
#  STANDALONE RUN (outside Colab)
# ─────────────────────────────────────────────

def bootstrap_pipeline():
    """
    Runs ONLY the very first time the Start button is ever clicked.
    This is the destructive setup: wipes S3, wipes Snowflake tables,
    replays the historical dataset, backfills, then goes real-time.
    """

    print("=" * 60)
    print("BOOTSTRAP: Starting SalesPulse360 Pipeline for the first time")
    print("=" * 60)

    pipeline_state["running"] = True
    pipeline_state["python"] = "Running"

    print("STEP 1")
    verify_s3_connection()
    add_activity("S3 Connection Verified")

    pipeline_state["python"] = "Healthy"

    clear_raw_bucket()
    pipeline_state["s3"] = "Healthy"

    reset_pipeline_tables()

    print("STEP 2")
    upload_dimension_tables()
    add_activity("Dimension Tables Uploaded")

    print("STEP 3")
    time.sleep(5)

    print("STEP 4")
    replay_old_dataset()

    if not pipeline_state["running"]:
        print("Pipeline terminated by user.")
        return

    print("STEP 5")
    run_backfill(
        s3_client,
        start_year=2020,
        end_year=2025
    )

    if not pipeline_state["running"]:
        print("Pipeline terminated by user.")
        return

    # mark in Snowflake that bootstrap is done — never run this again
    conn = get_connection()
    mark_bootstrapped(conn)
    conn.close()

    print("STEP 6 — switching to forever real-time mode")
    run_realtime_stream(s3_client)


def resume_pipeline(state):
    """
    Runs when the app restarts (Render woke up again) and the pipeline
    had already been bootstrapped before. Does NOT touch S3 or Snowflake
    tables — just keeps generating new batches from where it left off.
    """

    print("=" * 60)
    print("RESUME: Continuing pipeline from saved state")
    print("=" * 60)

    _record_counter[0] = state["LAST_RECORD_NUMBER"]
    _order_so_counter[0] = state["LAST_ORDER_NUMBER"] + 1

    pipeline_state["running"] = True
    pipeline_state["paused"] = False
    pipeline_state["current_stage"] = "Realtime"
    pipeline_state["current_batch"] = state["CURRENT_BATCH"]
    pipeline_state["total_batches"] = state["TOTAL_BATCHES"]
    pipeline_state["uploaded_rows"] = state["UPLOADED_ROWS"]
    pipeline_state["realtime_batches"] = state["REALTIME_BATCHES"]
    pipeline_state["python"] = "Healthy"
    pipeline_state["s3"] = "Healthy"
    pipeline_state["snowpipe"] = "Healthy"
    pipeline_state["snowflake"] = "Healthy"
    pipeline_state["sql"] = "Healthy"
    pipeline_state["powerbi"] = "Healthy"

    run_realtime_stream(s3_client)


if __name__ == "__main__":
    pass