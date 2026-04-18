import network
import time
import config

_wlan = network.WLAN(network.STA_IF)


def connect():
    _wlan.active(False)
    time.sleep_ms(500)
    _wlan.active(True)
    time.sleep_ms(500)

    print(f"WiFi bağlanıyor: {config.WIFI_SSID}...")
    _wlan.connect(config.WIFI_SSID, config.WIFI_PASS)

    timeout = config.WIFI_TIMEOUT_S
    while not _wlan.isconnected() and timeout > 0:
        print(".", end="")
        time.sleep(1)
        timeout -= 1

    if _wlan.isconnected():
        print(f"\nBağlantı başarılı! IP: {_wlan.ifconfig()[0]}")
        return True

    print("\nBağlantı başarısız!")
    return False


def ensure_connected():
    """Bağlantı kopmuşsa yeniden bağlanmaya çalışır."""
    if _wlan.isconnected():
        return True
    print("WiFi bağlantısı kesildi, yeniden bağlanıyor...")
    return connect()


def get_ip():
    return _wlan.ifconfig()[0] if _wlan.isconnected() else "0.0.0.0"


def get_mac():
    mac = _wlan.config('mac')
    return ':'.join(['{:02x}'.format(b) for b in mac])
