from pynput import mouse, keyboard
import time
import threading
import cv2
import torch
import subprocess
import os
import csv
from datetime import datetime
import zipfile
import json

# =============================
# Global Sabitler ve Değişkenler
# =============================
MODEL_PATH = 'C:/Windows/System32/yolov5/runs/train/exp2/weights/best.pt'  # Eğitimli model yolu (varsayılan)
AYARLAR_PATH = "ayarlar.json"  # Ayarlar dosyası
DEFAULT_IDLE_THRESHOLD = 10  # Varsayılan hareketsizlik süresi (saniye)
CONFIDENCE_THRESHOLD = 0.75  # %75 üzeri güven için eşik
CSV_FILE = "log_report.csv"  # Log dosyası

last_activity_time = time.time()  # Son kullanıcı etkileşim zamanı
idle_durations = []  # Hareketsizlik sürelerini toplamak için liste
model = None  # Global model nesnesi

# =============================
# Yardımcı Fonksiyonlar
# =============================

def ayarlari_yukle():
    # ayarlar.json'dan idle_threshold ve mode bilgisi alınır
    try:
        with open(AYARLAR_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            idle_threshold = data.get("idle_threshold", DEFAULT_IDLE_THRESHOLD)
            mode = data.get("mode", "main.py")
            return idle_threshold, mode
    except Exception as e:
        print(f"⚠️ Ayarlar okunamadı, varsayılanlar kullanıldı. Hata: {e}")
        return DEFAULT_IDLE_THRESHOLD, "main.py"

def model_yolunu_yukle():
    # model.json dosyasından model yolunu alır
    try:
        with open("model.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("model_path")
    except:
        return None

def update_average_idle(duration):
    # Hareketizlik ortalamasını hesaplayıp ort_sure.txt dosyasına yazar
    idle_durations.append(duration)
    ortalama = sum(idle_durations) / len(idle_durations)
    with open("ort_sure.txt", "w", encoding="utf-8") as f:
        f.write(f"Şu ana kadar ortalama hareketsizlik süresi: {ortalama:.1f} saniye\n")
        f.write("Bu değeri IDLE_THRESHOLD olarak kullanabilirsiniz.")
    print(f"📊 Ortalama hareketsizlik süresi güncellendi: {ortalama:.1f} sn")

def run_custom_script():
    # Kullanıcı ayarına göre main.py çalıştırılır veya ekran kilitlenir
    _, current_mode = ayarlari_yukle()
    print(f"💡 Seçilen mod: {current_mode}")
    if current_mode == "main.py":
        try:
            subprocess.Popen(["python", "main.py"])
            print("main.py başarıyla çalıştırıldı.")
        except Exception as e:
            print(f"main.py çalıştırılamadı: {e}")
    else:
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            print("💻 Ekran kilitlendi.")
        except Exception as e:
            print(f"Ekran kilitlenemedi: {e}")

def log_to_csv(image_path, confidence):
    # Tespit sonucu CSV dosyasına loglanır
    timestamp_str = image_path.split("/")[-1].replace(".jpg", "").replace(".png", "")
    readable_time = timestamp_str.replace("_", " ").replace("-", ":", 2).replace("-", ".", 1)
    image_name = os.path.basename(image_path)

    if confidence is None:
        result, main_triggered, confidence_display = "Tespit Yok", "Evet", "-"
    elif confidence >= CONFIDENCE_THRESHOLD:
        result, main_triggered, confidence_display = "Yetkili", "Hayır", f"{confidence * 100:.2f}"
    else:
        result, main_triggered, confidence_display = "Düşük Güven", "Evet", f"{confidence * 100:.2f}"

    row = [readable_time, image_name, confidence_display, result, main_triggered]
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Zaman", "Görsel", "Confidence (%)", "Sonuç", "main.py Çalıştı mı?"])
        writer.writerow(row)
    print(f"📝 CSV'ye kayıt yapıldı: {row}")

def detect_person_in_image(image_path):
    # Görselde "yetkili" kişi olup olmadığı tespit edilir
    global model
    if model is None:
        print("❌ Model yüklenmemiş.")
        return False

    results = model(image_path)
    detections = results.pandas().xyxy[0]
    log_path = image_path.replace(".jpg", ".txt")
    lines = []
    found = False
    max_confidence = None

    for _, row in detections.iterrows():
        label, confidence = row['name'], row['confidence']
        lines.append(f"{label}: %{confidence * 100:.2f}")
        if label == 'yetkili':
            if max_confidence is None or confidence > max_confidence:
                max_confidence = confidence
            if confidence >= CONFIDENCE_THRESHOLD:
                found = True

    with open(log_path, "w", encoding="utf-8") as f:
        if not detections.empty:
            f.write("\n".join(lines))
            print(f"📝 Confidence log kaydedildi: {log_path}")
        else:
            f.write("Hiçbir nesne tespit edilmedi.\n")

    log_to_csv(image_path, max_confidence)
    return found

def capture_photo():
    # Kameradan görüntü alır ve kontrol işlemini başlatır
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("Kamera açılamadı!")
        return

    ret, frame = cap.read()
    if ret:
        os.makedirs("control", exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"control/{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        print(f"📸 Fotoğraf kaydedildi: {filename}")

        if not detect_person_in_image(filename):
            run_custom_script()
    else:
        print("Fotoğraf çekilemedi.")
    cap.release()

def monitor_idle(stop_event):
    # Kullanıcının boşta olup olmadığını takip eder
    global last_activity_time
    while not stop_event.is_set():
        idle_threshold, _ = ayarlari_yukle()
        idle_time = time.time() - last_activity_time
        print(f"Boşta geçen süre: {int(idle_time)} sn (eşik: {idle_threshold})", end="\r")

        if idle_time > idle_threshold:
            print("\nKullanıcı boşta! Fotoğraf çekiliyor...")
            capture_photo()
            update_average_idle(idle_time)
            time.sleep(5)
        time.sleep(1)

def on_input(_):
    # Herhangi bir fare veya klavye etkileşiminde zamanı sıfırlar
    global last_activity_time
    last_activity_time = time.time()

def archive_control_folder():
    # control klasörünü zipleyip geçmiş klasörüne arşivler
    control_folder = "control"
    archive_folder = "gecmis"

    if not os.path.exists(control_folder):
        return

    files = os.listdir(control_folder)
    if not files:
        return

    os.makedirs(archive_folder, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_filename = os.path.join(archive_folder, f"{timestamp}.zip")

    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in files:
            full_path = os.path.join(control_folder, file)
            zipf.write(full_path, arcname=file)

    for file in files:
        os.remove(os.path.join(control_folder, file))

    print(f"📦 Kayıtlar arşivlendi: {zip_filename}")

# =============================
# İzleme Başlatma/Durdurma
# =============================

monitor_thread = None
keyboard_listener = None
mouse_listener = None
stop_event = None

def start_monitoring():
    # İzlemeyi başlatır, model yüklenir ve dinleyiciler devreye alınır
    global monitor_thread, keyboard_listener, mouse_listener, stop_event, model

    if monitor_thread and monitor_thread.is_alive():
        return

    MODEL_PATH = model_yolunu_yukle()
    if not MODEL_PATH or not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("❌ Model yolu geçersiz. GUI üzerinden bir .pt dosyası seçilmelidir.")

    print(f"📦 Model yükleniyor: {MODEL_PATH}")
    model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH)

    stop_event = threading.Event()

    keyboard_listener = keyboard.Listener(on_press=on_input)
    mouse_listener = mouse.Listener(on_move=on_input, on_click=on_input, on_scroll=on_input)
    keyboard_listener.start()
    mouse_listener.start()

    monitor_thread = threading.Thread(target=monitor_idle, args=(stop_event,), daemon=True)
    monitor_thread.start()
    print("✅ İzleme başlatıldı")

def stop_monitoring():
    # İzlemeyi durdurur ve dinleyicileri kapatır
    global stop_event, keyboard_listener, mouse_listener

    if stop_event:
        stop_event.set()
        print("⛔ İzleme durduruldu")

    if keyboard_listener:
        keyboard_listener.stop()
    if mouse_listener:
        mouse_listener.stop()

# =============================
# Manuel çalıştırma
# =============================

if __name__ == "__main__":
    archive_control_folder()

    keyboard_listener = keyboard.Listener(on_press=on_input)
    mouse_listener = mouse.Listener(on_move=on_input, on_click=on_input, on_scroll=on_input)
    keyboard_listener.start()
    mouse_listener.start()

    idle_thread = threading.Thread(target=monitor_idle, args=(threading.Event(),), daemon=True)
    idle_thread.start()

    print("📷 Sistem çalışıyor... Hareketsizlik kontrolü aktif.")
    keyboard_listener.join()
    mouse_listener.join()
