import ntptime


def sync():
    """ESP32 saatini NTP üzerinden günceller. SSL için saat doğru olmalıdır."""
    try:
        print("NTP ile saat güncelleniyor...")
        ntptime.settime()
        print("Saat güncellendi.")
    except Exception as e:
        print(f"Saat güncellenemedi: {e}")
