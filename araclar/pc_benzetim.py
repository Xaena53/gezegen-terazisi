"""Pico yokken PC'de deneme: pico/main.py'yi sahte Wi-Fi ve sahte tartıyla aynen çalıştırır.

    python araclar/pc_benzetim.py          # http://127.0.0.1:8080

Sahte tartı: 4 sn boş, sonra bir çocuk çıkar (32,4 kg, ilk saniyelerde kıpırdar), 25 sn durur, iner; döngü.
"""
import asyncio
import json
import math
import os
import random
import runpy
import shutil
import sys
import tempfile
import time
import types

KOK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KAPI = int(os.environ.get("KAPI", "8080"))
KATSAYI, SIFIR = 21000.0, 84000.0


def sahte_kg(t):
    t = t % 40
    if t < 4 or t > 33:
        return 0.0
    if t < 5.5:                                   # tartıya çıkıyor
        return 32.4 * (t - 4) / 1.5
    if t < 9:                                     # kıpırdıyor
        return 32.4 + 1.6 * math.sin(t * 9)
    return 32.4


# MicroPython modüllerinin PC karşılıkları
network = types.ModuleType("network")
network.AP_IF = 1


class WLAN:
    def __init__(self, *_):
        self._acik = False

    def config(self, **_):
        pass

    def active(self, v=None):
        if v is not None:
            self._acik = v
        return self._acik

    def ifconfig(self):
        return ("127.0.0.1",)


network.WLAN = WLAN
hx711 = types.ModuleType("hx711")


class HX711:
    def __init__(self, *_):
        self.bas = time.time()

    def oku(self, *_):
        return SIFIR + sahte_kg(time.time() - self.bas) * KATSAYI + random.gauss(0, 250)


hx711.HX711 = HX711


async def _uyku_ms(ms):
    await asyncio.sleep(ms / 1000)


asyncio.sleep_ms = _uyku_ms
_asil_sunucu = asyncio.start_server


async def _sunucu(istemci, adres, kapi, **kw):
    return await _asil_sunucu(istemci, "127.0.0.1", KAPI if kapi == 80 else kapi, **kw)


asyncio.start_server = _sunucu
sys.modules.update({"network": network, "hx711": hx711, "uasyncio": asyncio})

# Pico'nun dosya sistemini taklit eden geçici klasör
calisma = tempfile.mkdtemp(prefix="gezegen-terazisi-")
for ad in ("index.html",):
    shutil.copy(os.path.join(KOK, "web", ad), calisma)
for klasor in ("gezegenler", "yazi"):
    shutil.copytree(os.path.join(KOK, "web", klasor), os.path.join(calisma, klasor))
shutil.copy(os.path.join(KOK, "pico", "olcum.py"), calisma)
with open(os.path.join(calisma, "kalibrasyon.json"), "w") as f:
    json.dump({"katsayi": KATSAYI}, f)
os.chdir(calisma)
sys.path.insert(0, calisma)
print(f"Benzetim: http://127.0.0.1:{KAPI}  (Ctrl+C ile çık)")
try:
    runpy.run_path(os.path.join(KOK, "pico", "main.py"), run_name="__main__")
except KeyboardInterrupt:
    pass
