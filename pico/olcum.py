"""Tartı okumasını kilograma çeviren saf mantık (MicroPython ve PC'de aynı çalışır).

Ham HX711 değerleri gürültülüdür. Bu sınıf:
  - açılışta sıfırlar (dara),
  - bilinen bir ağırlıkla kalibre edilir (ham birim -> kg),
  - kısa bir pencerede ortalama alır,
  - değer oturduğunda "kararlı" der (çocuk tartıda kıpırdasa da ekran zıplamasın),
  - boşken yavaşça sıfırı izler (sıcaklıkla kayan sıfır noktası).
"""


class Olcum:
    def __init__(self, katsayi=None, dara=0.0, pencere=8, kararli_kg=0.15, bos_kg=1.0):
        self.katsayi = katsayi          # ham birim / kg; None = kalibre edilmemiş
        self.dara = dara                # boş tartının ham değeri
        self.pencere = pencere
        self.kararli_kg = kararli_kg
        self.bos_kg = bos_kg
        self._son = []
        self._kararli_kg = 0.0

    # ---------- ham değer ----------
    def ekle(self, ham):
        self._son.append(ham)
        if len(self._son) > self.pencere:
            self._son.pop(0)

    def ortalama_ham(self):
        if not self._son:
            return None
        s = sorted(self._son)
        if len(s) >= 5:                 # en uç iki değeri at (tekil sıçramalar)
            s = s[1:-1]
        return sum(s) / len(s)

    # ---------- dönüşüm ----------
    def kg(self):
        o = self.ortalama_ham()
        if o is None or not self.katsayi:
            return None
        return (o - self.dara) / self.katsayi

    def yayilim_kg(self):
        if len(self._son) < 3 or not self.katsayi:
            return None
        return (max(self._son) - min(self._son)) / abs(self.katsayi)

    def durum(self):
        """{'kg': ekranda gösterilecek, 'kararli': bool, 'kalibre': bool}"""
        kg = self.kg()
        if kg is None:
            return {"kg": None, "kararli": False, "kalibre": bool(self.katsayi)}
        yayilim = self.yayilim_kg()
        kararli = yayilim is not None and yayilim <= self.kararli_kg and len(self._son) >= self.pencere
        if kararli:
            self._kararli_kg = kg
        if kg < self.bos_kg:
            kg = 0.0
            if kararli:                  # boş ve sakin: sıfır kaymasını yavaşça düzelt
                self.dara += (self.ortalama_ham() - self.dara) * 0.05
        return {"kg": round(max(kg, 0.0), 1), "kararli": kararli, "kalibre": True}

    # ---------- ayar ----------
    def sifirla(self):
        o = self.ortalama_ham()
        if o is not None:
            self.dara = o

    def kalibre_et(self, bilinen_kg):
        """Tartıda bilinen_kg varken çağrılır; katsayıyı hesaplar."""
        o = self.ortalama_ham()
        if o is None or bilinen_kg <= 0 or o == self.dara:
            return False
        self.katsayi = (o - self.dara) / bilinen_kg
        return True

    def ayarlar(self):
        return {"katsayi": self.katsayi, "dara": self.dara}
