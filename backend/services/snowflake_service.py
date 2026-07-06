from database import get_connection


from database import get_connection


def get_kpis():

    conn = get_connection()
    cursor = conn.cursor()

    try:

        cursor.execute("SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();")
        print("Current DB/Schema :", cursor.fetchone())

        cursor.execute("""
        SELECT *
        FROM EXECUTIVE_KPI_SUMMARY;
        """)

        row = cursor.fetchone()

        print("KPI Row :", row)

        if row is None:
            return {
                "error": "EXECUTIVE_KPI_SUMMARY is empty"
            }

        return {
            "total_orders": row[0],
            "total_quantity_sold": row[1],
            "total_sales": float(row[2]),
            "total_cost": float(row[3]),
            "total_profit": float(row[4]),
            "avg_unit_price": float(row[5]),
            "avg_profit_margin": float(row[6]),
            "avg_delivery_days": float(row[7]),
            "total_customers": row[8],
            "total_products": row[9],
            "total_cities": row[10]
        }

    finally:
        cursor.close()
        conn.close()