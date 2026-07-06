from datetime import datetime
from database import get_connection

def get_system_status():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT CURRENT_TIMESTAMP()")
        current_time = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return {
            "frontend": "Online",
            "backend": "Online",
            "snowflake": "Connected",
            "powerbi": "Connected",

            "warehouse": "SALESPULSE360_WH",
            "database": "SALESPULSE360_DB",
            "schema": "ANALYTICS_SCHEMA",

            "last_refresh": current_time.strftime("%I:%M:%S %p")
        }

    except Exception as e:

        return {
            "frontend": "Online",
            "backend": "Offline",
            "snowflake": "Disconnected",
            "powerbi": "Disconnected",
            "error": str(e)
        }