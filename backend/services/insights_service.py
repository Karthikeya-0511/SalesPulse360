from database import get_connection


def get_ai_insights():

    conn = get_connection()
    cur = conn.cursor()

    try:
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

        return {
            "insights": insights
        }

    finally:
        cur.close()
        conn.close()