"""Ölçüm mantığı testleri (PC'de: python testler/test_olcum.py)."""
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pico"))
from olcum import Olcum  # noqa: E402

KATSAYI = 21000.0     # ham birim / kg (tipik banyo tartısı düzeni)
SIFIR = 84000.0       # boş tartının ham değeri


def ham(kg, gurultu=300):
    return SIFIR + kg * KATSAYI + random.gauss(0, gurultu)


def doldur(o, kg, n=10, gurultu=300):
    for _ in range(n):
        o.ekle(ham(kg, gurultu))


def test():
    random.seed(1)
    o = Olcum()
    doldur(o, 0)
    assert o.durum()["kg"] is None and not o.durum()["kalibre"]          # kalibrasyonsuz sayı uydurmaz
    o.sifirla()
    doldur(o, 10)
    assert o.kalibre_et(10)
    assert abs(o.katsayi - KATSAYI) / KATSAYI < 0.01

    doldur(o, 32.4)
    d = o.durum()
    assert d["kararli"] and abs(d["kg"] - 32.4) <= 0.1, d

    # çocuk tartıda kıpırdıyor: ekran "kararlı" demez
    for i in range(8):
        o.ekle(ham(32.4 + (1.5 if i % 2 else -1.5)))
    assert not o.durum()["kararli"]

    # tek bir sıçrama ortalamayı bozmaz
    doldur(o, 25)
    o.ekle(ham(25) + 40 * KATSAYI)
    assert abs(o.durum()["kg"] - 25) < 0.3, o.durum()

    # boş tartı 0 gösterir, eksiye düşmez; sıfır kayması yavaşça düzelir
    doldur(o, 0)
    assert o.durum()["kg"] == 0.0
    eski = o.dara
    for _ in range(40):
        o.ekle(ham(0.3, gurultu=50))
        o.durum()
    assert o.dara > eski                                               # sıfır yukarı kaydı, izlendi
    assert o.kalibre_et(0) is False                                    # saçma kalibrasyon reddedilir
    print("ölçüm testi geçti")


if __name__ == "__main__":
    test()
