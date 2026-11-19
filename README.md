# Gezegen Terazisi

Çocuklar tartıya çıkar; tablette Ay'da, Mars'ta, Jüpiter'de tartının ne göstereceği belirir.
Ucuz bir dijital banyo tartısının yük hücreleri, bir HX711 yükselticisi ve Raspberry Pi Pico 2 W ile yapılır.
İnternet gerekmez: Pico kendi Wi-Fi ağını açar, ekran tarayıcıda çalışır.

## Parçalar
- Dijital banyo tartısı (köşelerinde 4 yük hücresi olan tip)
- HX711 modülü
- Raspberry Pi Pico 2 W (header'lı)
- Jumper kablolar, mikro USB kablo, USB güç (powerbank olur)
- Tablet / telefon / projeksiyonlu bilgisayar

Fiyatlı parça listesi: `belgeler/alisveris-listesi.md` (Kasım 2026; almadan önce güncel fiyata bakın).

## Bağlantı
1. Tartının kapağını aç, 4 yük hücresinin kablolarını kartından ayır (genelde her birinde 3 kablo: kırmızı, beyaz, siyah).
2. 4 hücreyi "köprü" olarak HX711'e bağla (E+, E-, A+, A-). Banyo tartısında hücreler zaten bu düzende kablolanmıştır;
   kartın lehim noktalarını not alıp aynı şekilde HX711'e taşı.
3. HX711 → Pico: VCC → 3V3 (pin 36), GND → GND, DT → GP16, SCK → GP17.

## Kurulum
1. Pico'ya MicroPython yükle (Pico 2 W için resmi UF2).
2. Thonny ile `pico/hx711.py`, `pico/olcum.py`, `pico/main.py` dosyalarını ve `web/index.html`'i Pico'nun köküne kopyala.
3. Tartı boşken Pico'ya güç ver; açılışta kendini sıfırlar.
4. Tabletten `Gezegen-Terazisi` ağına bağlan (şifre `main.py` içinde), `http://192.168.4.1` aç.
5. **Bir kez kalibrasyon:** bilinen bir ağırlık koy (ör. 10 kg'lık bir kova su) ve
   `http://192.168.4.1/kalibre?kg=10` aç. Ayar Pico'da saklanır.

## Tartısız deneme
`web/index.html` dosyasını bilgisayarda aç: tartı bulunamayınca deneme moduna geçer, alttaki kaydırıcıyla ağırlık seç.
Doğrudan bağlantı: `index.html?kg=30&gezegen=Mars`.

## Test
`python testler/test_olcum.py` (ölçüm mantığı: dara, kalibrasyon, kararlılık, sıçrama süzme, sıfır kayması).

## Veri
NASA Planetary Fact Sheet yüzey çekimi değerleri. Ders planı: `belgeler/ders-plani.md`.

## Lisans
MIT. Okulda, atölyede, evde serbestçe kullanın ve geliştirin.
