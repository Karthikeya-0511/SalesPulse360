def save_control_state(pipeline_state, conn, record_counter, order_counter):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ANALYTICS_SCHEMA.PIPELINE_CONTROL_STATE
            SET IS_PAUSED = %s,
                CURRENT_STAGE = %s,
                CURRENT_BATCH = %s,
                TOTAL_BATCHES = %s,
                UPLOADED_ROWS = %s,
                REALTIME_BATCHES = %s,
                LAST_RECORD_NUMBER = %s,
                LAST_ORDER_NUMBER = %s,
                LAST_UPLOAD = %s,
                LAST_FILE = %s
            WHERE ID = 1
        """, (
            pipeline_state["paused"],
            pipeline_state["current_stage"],
            pipeline_state["current_batch"],
            pipeline_state["total_batches"],
            pipeline_state["uploaded_rows"],
            pipeline_state["realtime_batches"],
            record_counter,
            order_counter,
            pipeline_state["last_upload"],
            pipeline_state["last_file"],
        ))
        conn.commit()
    finally:
        cursor.close()


def mark_bootstrapped(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ANALYTICS_SCHEMA.PIPELINE_CONTROL_STATE
            SET HAS_BOOTSTRAPPED = TRUE
            WHERE ID = 1
        """)
        conn.commit()
    finally:
        cursor.close()


def load_control_state(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM ANALYTICS_SCHEMA.PIPELINE_CONTROL_STATE WHERE ID = 1")
        row = cursor.fetchone()
        if not row:
            return None
        cols = [c[0] for c in cursor.description]
        return dict(zip(cols, row))
    finally:
        cursor.close()

def save_bootstrap_progress(conn, phase, replay_next_index=None, backfill_year=None, backfill_month=None):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE ANALYTICS_SCHEMA.PIPELINE_CONTROL_STATE
            SET BOOTSTRAP_PHASE = %s,
                REPLAY_NEXT_INDEX = COALESCE(%s, REPLAY_NEXT_INDEX),
                BACKFILL_YEAR = COALESCE(%s, BACKFILL_YEAR),
                BACKFILL_MONTH = COALESCE(%s, BACKFILL_MONTH)
            WHERE ID = 1
        """, (phase, replay_next_index, backfill_year, backfill_month))
        conn.commit()
    finally:
        cursor.close()

def try_acquire_lock(conn, process_id, stale_after_seconds=90):
    """
    Only one process may hold this lock at a time. If the current holder's
    heartbeat is older than `stale_after_seconds`, it's considered dead
    and can be taken over (e.g. after a crash or Render restart).
    """
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT LOCK_HOLDER, LOCK_HEARTBEAT,
                   DATEDIFF(SECOND, LOCK_HEARTBEAT, CURRENT_TIMESTAMP()) AS AGE
            FROM PIPELINE_CONTROL_STATE WHERE ID = 1
        """)
        row = cursor.fetchone()
        holder, heartbeat, age = (row[0], row[1], row[2]) if row else (None, None, None)

        if holder is not None and holder != process_id and age is not None and age < stale_after_seconds:
            return False  # someone else actively holds it

        cursor.execute("""
            UPDATE PIPELINE_CONTROL_STATE
            SET LOCK_HOLDER = %s, LOCK_HEARTBEAT = CURRENT_TIMESTAMP()
            WHERE ID = 1
        """, (process_id,))
        conn.commit()
        return True
    finally:
        cursor.close()


def send_heartbeat(conn, process_id):
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE PIPELINE_CONTROL_STATE
            SET LOCK_HEARTBEAT = CURRENT_TIMESTAMP()
            WHERE ID = 1 AND LOCK_HOLDER = %s
        """, (process_id,))
        conn.commit()
    finally:
        cursor.close()