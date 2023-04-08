
# Store the processed records in sqlite
from datetime import datetime
import os
import sqlite3
from util.logger import app_logger

DB_PATH = "data/processed_records.db"
inited = False
processed_map = {}
def init():
    global inited
    global processed_map
    if inited:
        return
    
    if not os.path.exists(DB_PATH):
        # create an empty database file
        open(DB_PATH, 'a').close()
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # table schema: id, timestamp
        c.execute("CREATE TABLE IF NOT EXISTS records (id TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        conn.commit()
        conn.close()
    else:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # fetch records within one day
        c.execute("SELECT * FROM records WHERE timestamp > datetime('now', '-1 day')")
        rows = c.fetchall()
        for row in rows:
            processed_map[row[0]] = row[1]
        app_logger.debug("init processed records: %s", processed_map)
        c.execute("DELETE FROM records WHERE timestamp < datetime('now', '-1 day')")
        conn.commit()
        conn.close()
    inited = True

def event_is_processed(event):
    init()
    global processed_map
    app_logger.debug("processed_map: %s", processed_map)
    app_logger.debug("message_id: %s", event.event.message.message_id)
    if event.event.message.message_id in processed_map:
        return True
    return False

def mark_event_processed(event):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # insert value with id and current timestamp
    now = datetime.now()
    c.execute("INSERT INTO records VALUES (?, ?)", (event.event.message.message_id,now))
    conn.commit()
    conn.close()
    processed_map[event.event.message.message_id] = True