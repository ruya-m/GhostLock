## 🙏 İlham ve Teşekkür

Bu proje, staj yaptığım **OzzTech** firmasındaki unutulmaz bir ofis kuralından ilham aldı:

> “Bilgisayarını açık unutan kişi, mail yoluyla ifşa edilir ve tüm ekibe baklava ısmarlar.” 

Bu gelenekle ilk tanışmam, bir stajyer arkadaşımın kurban gitmesiyle oldu.
Kendimi korumak (ve belki bir gün tersine çevirmek) için bu projeyi şaka amaçlı yazmaya başladım.
Ancak ilk örneği yöneticimiz **Halit Bey**'e sunduktan sonra, onun kıymetli geri bildirimleriyle proje ciddi bir güvenlik aracına dönüştü.

Bu yazılımın oluşmasında:

*  Başta **Halit Bey** olmak üzere tüm **OzzTech** çalışanlarına,
*  Hazırlık dönemimde bana Python’ı öğreten ve ChatGPT'sını kullanmama izin veren **Mustafa Hocama**,
*  Ve yazılımı yazarken bana ortaklık eden Chat'e
*  Son olarak ikide bir "bu nasıl olmuş" diye sorduğum Afra'ya

  emekleri ve katkıları için gönülden teşekkür ederim.

---

# GhostLock

GhostLock, hareketsiz kalan kullanıcıları sessizce gözlemleyen ve güvenlik kontrolü sağlayan Python tabanlı bir masaüstü uygulamasıdır. Yapay zeka destekli yüz tanıma algoritması sayesinde, yetkisiz kullanıcıların erişimini engeller veya bir honeypot (tuzak) ortamı oluşturarak kamera kaydı alır.

---

## 🚀 Özellikler

* 🔍 Fare/klavye hareketi izleme
* 📸 Webcam ile otomatik fotoğraf alma
* 🤖 YOLOv5 modeli ile "yetkili" yüz tespiti
* 🔒 Yetkisiz erişimde:

  * Ekran kilitleme
  * veya honeypot modu:

    * Sahte Google arayüzü (tam ekran)
    * Webcam kaydı (video)
    * Otomatik ekran kilidi
* 📊 CSV tabanlı loglama (zaman, confidence, sonuç)
* 💻 CustomTkinter arayüz (ayarlar, rapor, model, vb.)

---

## 🧰 Kullanım Senaryosu

> Ofisten çay almaya çıktın. Bilgisayarın açık kaldı.
>
> Meraklı biri geldi. Honeypot devreye girdi. Webcam kaydı alındı.
> Geri geldiğinde her şey loglanmıştı. 📅📹

---

## ⚙️ Kurulum

```bash
pip install -r requirements.txt
```

1. YOLOv5 model (.pt) dosyasını GUI üzerinden yükleyin
2. Uygulamayı başlatın:

```bash
python app.py
```

---

## 🔧 Kullanım

* "Ana Sayfa"dan izlemeyi başlatın
* Hareketsizlik olursa webcam ile foto alınır
* Yüz tanıma doğrulanmazsa honeypot devreye girer
* Video kaydedilir, ekran kilitlenir
* Tüm tespitler CSV ve klasör olarak kaydedilir

---

## 🛠️ Kullanılan Teknolojiler

* **Python 3.9+**
* **YOLOv5 (PyTorch)**
* **OpenCV** (`cv2`)
* **Flask** (honeypot arayüz)
* **PyQt5** (honeypot'u masaüstüne gömme)
* **CustomTkinter** (GUI)
* **pynput** (fare/klavye izlemesi)
* **pandas**, **Pillow**, **tkinter**, **win32gui**, **ctypes**, vs.

---

## 📁 Proje Yapısı (kısaca)

* `app.py` : GUI uygulama girişi
* `detect.py` : Etkinlik takibi, foto, yüz tanıma
* `main.py` : Honeypot arayüz ve video kaydı
* `model.json`, `ayarlar.json`: Yapılandırma dosyaları
* `log_report.csv`, `control/`, `gecmis/`: Kıyt ve arşivler

---

## 📝 Lisans

Bu proje MIT lisansı altındadır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

---

## 🤝 Katkı
Pull request'ler ve issue bildirimleri açıktır.
Geliştirici: Rüya Melis Ünver
Email: \[[ruyamelisunver.tr@gmail.com](ruyamelisunver.tr@gmail.com)]
