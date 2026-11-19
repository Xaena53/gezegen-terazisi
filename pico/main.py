"""Gezegen Terazisi: Raspberry Pi Pico 2 W üzerinde çalışan ana program (MicroPython).

Pico kendi Wi-Fi ağını açar. Tablet ya da telefon bu ağa bağlanıp http://192.168.4.1 adresini açar;
ekranda çocuğun ağırlığı Ay'da, Mars'ta, Jüpiter'de... görünür.

Bağlantı (HX711):  VCC -> 3V3,  GND -> GND,  DT -> GP16,  SCK -> GP17
Kalibrasyon: tartı boşken açılır (kendini sıfırlar). Bilinen bir ağırlık (ör. 10 kg) koyup
            http://192.168.4.1/kalibre?kg=10 adresini aç. Ayar kalibrasyon.json'a yazılır.
"""
import json

import network
import uasyncio as asyncio

from hx711 import HX711
from olcum import Olcum

AG_ADI = "Gezegen-Terazisi"
AG_SIFRE = "uzay2026"            # en az 8 karakter; sınıfta değiştirin
DT_PIN, SCK_PIN = 16, 17
AYAR_DOSYASI = "kalibrasyon.json"

hx = HX711(DT_PIN, SCK_PIN)


def ayar_oku():
    try:
        with open(AYAR_DOSYASI) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def ayar_yaz(olcum):
    with open(AYAR_DOSYASI, "w") as f:
        json.dump({"katsayi": olcum.katsayi}, f)


olcum = Olcum(katsayi=ayar_oku().get("katsayi"))


def ag_ac():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=AG_ADI, password=AG_SIFRE)
    ap.active(True)
    while not ap.active():
        pass
    print("Wi-Fi:", AG_ADI, "adres:", ap.ifconfig()[0])


async def olcum_dongusu():
    # açılışta boş tartıyı sıfırla
    for _ in range(olcum.pencere):
        ham = hx.oku()
        if ham is not None:
            olcum.ekle(ham)
        await asyncio.sleep_ms(100)
    olcum.sifirla()
    while True:
        ham = hx.oku()
        if ham is not None:
            olcum.ekle(ham)
        await asyncio.sleep_ms(80)       # HX711 10 örnek/sn verir


TURLER = {"html": "text/html; charset=utf-8", "webp": "image/webp", "woff2": "font/woff2", "png": "image/png"}
IZINLI = ("gezegenler/", "yazi/")          # yalnız bu klasörlerden dosya verilir


def dosya_boyu(yol):
    import os
    try:
        return os.stat(yol)[6]
    except OSError:
        return -1


async def dosya_gonder(yazici, yol):
    """Dosyayı 2 KB'lık parçalarla gönderir (Pico'nun belleği küçük)."""
    boy = dosya_boyu(yol)
    if boy < 0:
        yanit(yazici, 404, "yok", "text/plain")
        return
    tur = TURLER.get(yol.rsplit(".", 1)[-1], "application/octet-stream")
    yazici.write(b"HTTP/1.0 200 OK\r\nContent-Type: %s\r\nContent-Length: %d\r\n"
                 b"Cache-Control: max-age=86400\r\nConnection: close\r\n\r\n" % (tur.encode(), boy))
    with open(yol, "rb") as f:
        while True:
            parca = f.read(2048)
            if not parca:
                break
            yazici.write(parca)
            await yazici.drain()


def yanit(yazici, kod, govde, tur="application/json"):
    if isinstance(govde, str):
        govde = govde.encode()
    yazici.write(b"HTTP/1.0 %d OK\r\nContent-Type: %s\r\nContent-Length: %d\r\n"
                 b"Cache-Control: no-store\r\nConnection: close\r\n\r\n" % (kod, tur.encode(), len(govde)))
    yazici.write(govde)


async def istemci(okuyucu, yazici):
    try:
        satir = await okuyucu.readline()
        while (await okuyucu.readline()) not in (b"\r\n", b""):
            pass
        parca = satir.decode().split(" ")
        yol = parca[1] if len(parca) > 1 else "/"
        if yol.startswith("/olcum"):
            yanit(yazici, 200, json.dumps(olcum.durum()))
        elif yol.startswith("/sifirla"):
            olcum.sifirla()
            yanit(yazici, 200, '{"tamam": true}')
        elif yol.startswith("/kalibre"):
            try:
                kg = float(yol.split("kg=")[1].split("&")[0])
            except (IndexError, ValueError):
                kg = 0
            ok = olcum.kalibre_et(kg)
            if ok:
                ayar_yaz(olcum)
            yanit(yazici, 200, json.dumps({"tamam": ok, "katsayi": olcum.katsayi}))
        else:
            dosya = yol.split("?")[0].lstrip("/")
            if dosya.startswith(IZINLI) and ".." not in dosya:
                await dosya_gonder(yazici, dosya)
            else:
                await dosya_gonder(yazici, "index.html")
        await yazici.drain()
    except Exception as e:
        print("istemci hatası:", e)
    finally:
        yazici.close()
        await yazici.wait_closed()


async def ana():
    ag_ac()
    asyncio.create_task(olcum_dongusu())
    await asyncio.start_server(istemci, "0.0.0.0", 80)
    print("Hazır: http://192.168.4.1")
    while True:
        await asyncio.sleep(3600)


asyncio.run(ana())
