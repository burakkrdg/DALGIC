import time
import random
from db import get_connection

def log_reading(device_id, watt):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO energy_readings (device_id, watt) VALUES (%s, %s)",
        (device_id, watt)
    )
    conn.commit()
    cur.close()
    conn.close()
    print(f"[LOG] Cihaz {device_id} → {watt}W kaydedildi")

def get_device_summary(device_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            d.name,
            AVG(watt) as ort_watt,
            SUM(watt) / 1000.0 as toplam_kwh,
            COUNT(*) as olcum_sayisi
        FROM energy_readings er
        JOIN devices d ON d.id = er.device_id
        WHERE er.device_id = %s
        GROUP BY d.name
    """, (device_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row

# --- Test: Her 5 saniyede bir sahte veri gönder ---
if __name__ == "__main__":
    print("Veri gönderimi başladı... (Ctrl+C ile durdur)")
    while True:
        for device_id in [1, 2, 3]:
            watt = round(random.uniform(50, 500), 2)
            log_reading(device_id, watt)
        time.sleep(5)