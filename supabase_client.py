import socket
import ssl
import json
import gc
import config


def send(device_id, watt, amper, voltaj, kwh, ip):
    """Ölçüm verisini Supabase'e HTTPS üzerinden gönderir.

    Returns:
        True: başarılı (HTTP 200/201/204), False: hata
    """
    host = config.SUPABASE_HOST
    path = f"/rest/v1/{config.SUPABASE_TABLE}"

    payload = json.dumps({
        "id":      device_id,
        "watt":    watt,
        "amper":   amper,
        "voltaj":  voltaj,
        "kwh":     kwh,
        "wifi_ip": ip,
    })

    request = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"User-Agent: curl/7.68.0\r\n"
        f"Accept: */*\r\n"
        f"apikey: {config.SUPABASE_KEY}\r\n"
        f"Authorization: Bearer {config.SUPABASE_KEY}\r\n"
        f"Content-Type: application/json\r\n"
        f"Prefer: return=minimal, resolution=merge-duplicates\r\n"
        f"Content-Length: {len(payload)}\r\n"
        f"Connection: close\r\n\r\n"
        f"{payload}"
    )

    sock  = None
    ssock = None

    try:
        gc.collect()
        addr  = socket.getaddrinfo(host, 443)[0][-1]
        sock  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(config.SOCKET_TIMEOUT_S)
        sock.connect(addr)
        ssock = ssl.wrap_socket(sock, server_hostname=host)

        ssock.write(request.encode('utf-8'))

        # Status line geldikten sonra okumayı kes
        response = b""
        while b"\r\n" not in response:
            chunk = ssock.read(256)
            if not chunk:
                break
            response += chunk

        if response:
            status_line = response.decode('utf-8', errors='ignore').split("\r\n")[0]
            if any(code in status_line for code in ("200", "201", "204")):
                print(f"Supabase: BAŞARILI ({status_line.strip()})")
                return True
            print(f"Supabase: BAŞARISIZ - {status_line.strip()}")
            return False

        print("Supabase: Sunucu yanıt vermedi.")
        return False

    except Exception as e:
        print(f"Supabase gönderim hatası: {e}")
        return False

    finally:
        if ssock:
            try: ssock.close()
            except: pass
        if sock:
            try: sock.close()
            except: pass
        gc.collect()
