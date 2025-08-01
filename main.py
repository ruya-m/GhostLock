import sys
import cv2
import threading
import time
import ctypes
from flask import Flask, render_template, request
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from werkzeug.serving import make_server
import win32gui

# Flask uygulaması başlatılıyor (arka plan sunucusu)
app = Flask(__name__)

recording = False  # Video kaydı devam ediyor mu?
video_writer = None  # VideoWriter nesnesi

# =============================
# Yardımcı Fonksiyonlar
# =============================

def is_window_focused(window_title):
    # Odaktaki pencere belirtilen başlığa sahip mi kontrol eder
    fg_window = win32gui.GetForegroundWindow()
    window_text = win32gui.GetWindowText(fg_window)
    return window_title in window_text

def monitor_focus(main_window):
    # Ana pencere odaktan çıkarsa ekranı kilitler
    while True:
        time.sleep(1)
        if not is_window_focused(main_window.windowTitle()):
            ctypes.windll.user32.LockWorkStation()
            break

def record_video():
    # Webcam'den video kaydını başlatır
    global recording, video_writer
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video_writer = cv2.VideoWriter('yuzleri.avi', fourcc, 20.0, (640, 480))
    recording = True

    while recording and cap.isOpened():
        ret, frame = cap.read()
        if ret:
            video_writer.write(frame)
        else:
            break
    cap.release()
    video_writer.release()

# =============================
# Flask Route'ları
# =============================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    # Kayıt başlatılır
    global recording
    if not recording:
        threading.Thread(target=record_video).start()
    return "Recording started", 200

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    # Kayıt durdurulur
    global recording
    recording = False
    return "Recording stopped", 200

@app.route('/lock', methods=['POST'])
def lock():
    # Manuel olarak ekran kilitlenir
    def do_lock():
        time.sleep(0.5)
        ctypes.windll.user32.LockWorkStation()
    threading.Thread(target=do_lock).start()
    return "Locked", 200

# =============================
# Flask'ı ayrı thread'de çalıştırmak için sınıf
# =============================
class FlaskThread(threading.Thread):
    def run(self):
        make_server('127.0.0.1', 5000, app).serve_forever()

# =============================
# PyQt Ana Pencere
# =============================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fake Google Lock")
        self.showFullScreen()

        central_widget = QWidget()
        layout = QVBoxLayout()

        self.setContentsMargins(0, 0, 0, 0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:5000"))  # Flask arayüzünü yükler

        layout.addWidget(self.browser)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

# =============================
# Program Başlatma
# =============================
if __name__ == "__main__":
    flask_thread = FlaskThread()
    flask_thread.start()  # Flask'ı arka planda çalıştır

    app_qt = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()

    threading.Thread(target=monitor_focus, args=(main_window,), daemon=True).start()  # Fokus kontrolü

    sys.exit(app_qt.exec_())  # Uygulama döngüsü başlatılır
