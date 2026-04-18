from machine import UART, Pin
import struct
import time
import config

_uart = UART(1, baudrate=9600, tx=Pin(config.UART_TX), rx=Pin(config.UART_RX), timeout=2000)

# PZEM-004T V3.0 - Tüm verileri okuma komutu (Modbus RTU)
# Slave: 0x01 | Read Input Registers: 0x04 | Start: 0x0000 | Count: 0x000A | CRC: 0x700D
_READ_CMD = b'\x01\x04\x00\x00\x00\x0A\x70\x0D'


def read():
    """PZEM-004T'den bir ölçüm okur.

    Returns:
        Başarılıysa ölçüm verilerini içeren dict, hata durumunda None.
    """
    # Eski buffered veriyi temizle
    while _uart.any():
        _uart.read()

    _uart.write(_READ_CMD)
    time.sleep_ms(100)

    if _uart.any() < 25:
        print("Sensörden yanıt yok. Sensöre 220V AC geldiğinden ve TX/RX pinlerinden emin olun.")
        return None

    response = _uart.read(25)

    if not response or len(response) != 25:
        print("Eksik veri alındı.")
        return None

    try:
        # Başlık (3 byte) ve CRC (2 byte) atılıp 20 byte veri Big-Endian olarak çözümlenir
        regs = struct.unpack('>HHHHHHHHHH', response[3:23])

        return {
            "voltage":    regs[0] / 10.0,
            "current":    ((regs[2] << 16) | regs[1]) / 1000.0,
            "power":      ((regs[4] << 16) | regs[3]) / 10.0,
            "energy_kwh": ((regs[6] << 16) | regs[5]) / 1000.0,
            "frequency":  regs[7] / 10.0,
            "pf":         regs[8] / 100.0,
            "alarm":      regs[9],
        }
    except Exception as e:
        print(f"Veri çözümleme hatası: {e}")
        return None


def print_reading(data):
    print("-" * 35)
    print(f"Voltaj:      {data['voltage']:.1f} V")
    print(f"Akım:        {data['current']:.3f} A")
    print(f"Güç:         {data['power']:.1f} W")
    print(f"Enerji:      {data['energy_kwh']:.3f} kWh")
    print(f"Frekans:     {data['frequency']:.1f} Hz")
    print(f"Güç Faktörü: {data['pf']:.2f}")
    if data['alarm']:
        print(f"DURUM:       ALARM! (0x{data['alarm']:04X})")
