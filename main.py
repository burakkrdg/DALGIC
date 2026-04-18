import time
import gc
import machine

import config
import led
import wifi_manager
import ntp_sync
import pzem_sensor
import supabase_client


def main():
    led.blink(times=2, on_ms=200, off_ms=200)  # Başlangıç sinyali

    if not wifi_manager.connect():
        print("WiFi bağlantısı kurulamadı. 5 saniye sonra yeniden başlatılıyor...")
        time.sleep(5)
        machine.reset()

    ntp_sync.sync()

    device_id = f"{config.DEVICE_PREFIX}-{wifi_manager.get_mac()}"
    print(f"Cihaz ID: {device_id}")
    print("Veri okuma döngüsü başlıyor...\n")

    while True:
        if not wifi_manager.ensure_connected():
            print("WiFi bağlantısı kurulamadı. 10 saniye bekleniyor...")
            time.sleep(10)
            continue

        data = pzem_sensor.read()

        if data:
            pzem_sensor.print_reading(data)

            success = supabase_client.send(
                device_id=device_id,
                watt=data["power"],
                amper=data["current"],
                voltaj=data["voltage"],
                kwh=data["energy_kwh"],
                ip=wifi_manager.get_ip(),
            )

            if success:
                led.blink(times=1)

        gc.collect()
        time.sleep(config.SEND_INTERVAL_S)


if __name__ == "__main__":
    main()
