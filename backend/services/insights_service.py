from snowflake.connector import connect
import os
from dotenv import load_dotenv

load_dotenv()

conn = connect(
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database=os.getenv("SNOWFLAKE_DATABASE"),
    schema="ANALYTICS_SCHEMA"
)


def get_ai_insights():

    cur = conn.cursor()

    cur.execute("""

        SELECT

        TOTAL_ORDERS,
        TOTAL_SALES,
        TOTAL_PROFIT,
        AVG_PROFIT_MARGIN,
        AVG_DELIVERY_DAYS

        FROM EXECUTIVE_KPI_SUMMARY

    """)

    row = cur.fetchone()

    if row is None:
        cur.close()
        return {
            "insights": [
                "Waiting for pipeline to load data..."
            ]
        }

    orders = row[0]
    sales = row[1]
    profit = row[2]
    margin = row[3]
    delivery = row[4]

    insights = []

    insights.append(
        f"📦 {orders:,} orders processed successfully."
    )

    insights.append(
        f"💰 Revenue reached ${sales:,.2f}."
    )

    insights.append(
        f"📈 Profit stands at ${profit:,.2f}."
    )

    insights.append(
        f"🎯 Average Profit Margin is {margin:.2f}%."
    )

    insights.append(
        f"🚚 Average Delivery Time is {delivery:.1f} days."
    )

    cur.close()

    return {

        "insights": insights

    }