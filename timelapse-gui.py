import sys
import os
import cv2
import time
import threading
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QFileDialog, QComboBox, QSlider, QCheckBox, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from datetime import datetime
import subprocess
import re

def get_working_cameras(max_tested=10):
    cameras = []
    for i in range(max_tested):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                cameras.append(i)
            cap.release()
    return cameras

def get_supported_resolutions():
    return [
        (640, 360), (1280, 720), (1920, 1080), (720, 1280), (1080, 1920)
    ]

class TimelapseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timelapse GUI")
        self.cap = None
        self.timer = QTimer()
        self.capturing = False
        self.frame_list = []
        self.frame_dir = ""
        self.video_dir = ""
        self.camera_indexes = get_working_cameras()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.preview_label = QLabel("Предпросмотр")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(320, 180)
        layout.addWidget(self.preview_label)

        camera_layout = QHBoxLayout()
        self.camera_box = QComboBox()
        for idx in self.camera_indexes:
            self.camera_box.addItem(f"Камера {idx}")
        self.camera_box.currentIndexChanged.connect(self.restart_camera)
        camera_layout.addWidget(QLabel("Камера:"))
        camera_layout.addWidget(self.camera_box)
        layout.addLayout(camera_layout)

        resolution_layout = QHBoxLayout()
        self.resolution_box = QComboBox()
        for w, h in get_supported_resolutions():
            self.resolution_box.addItem(f"{w}x{h}")
        resolution_layout.addWidget(QLabel("Разрешение:"))
        resolution_layout.addWidget(self.resolution_box)
        layout.addLayout(resolution_layout)

        aspect_layout = QHBoxLayout()
        self.aspect_ratio_box = QComboBox()
        self.aspect_ratio_box.addItems(["16:9", "9:16"])
        self.aspect_ratio_box.currentTextChanged.connect(self.update_preview_size)
        aspect_layout.addWidget(QLabel("Формат кадра:"))
        aspect_layout.addWidget(self.aspect_ratio_box)
        layout.addLayout(aspect_layout)

        self.fps_label = QLabel("FPS: 25")
        self.fps_slider = QSlider(Qt.Horizontal)
        self.fps_slider.setRange(1, 60)
        self.fps_slider.setValue(25)
        self.fps_slider.valueChanged.connect(lambda val: self.fps_label.setText(f"FPS: {val}"))
        layout.addWidget(self.fps_label)
        layout.addWidget(self.fps_slider)

        self.interval_label = QLabel("Интервал съёмки (сек): 10")
        self.interval_slider = QSlider(Qt.Horizontal)
        self.interval_slider.setRange(1, 60)
        self.interval_slider.setValue(10)
        self.interval_slider.valueChanged.connect(lambda val: self.interval_label.setText(f"Интервал съёмки (сек): {val}"))
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_slider)

        folder_layout = QHBoxLayout()
        self.folder_button = QPushButton("Папка фото")
        self.folder_button.clicked.connect(self.select_frame_dir)
        self.video_button = QPushButton("Папка видео")
        self.video_button.clicked.connect(self.select_video_dir)
        folder_layout.addWidget(self.folder_button)
        folder_layout.addWidget(self.video_button)
        layout.addLayout(folder_layout)

        self.frame_dir_label = QLabel("Фото → (не выбрана)")
        self.video_dir_label = QLabel("Видео → (не выбрана)")
        layout.addWidget(self.frame_dir_label)
        layout.addWidget(self.video_dir_label)

        self.keep_frames_checkbox = QCheckBox("Сохранять фотографии")
        self.keep_frames_checkbox.setChecked(True)
        layout.addWidget(self.keep_frames_checkbox)

        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Старт")
        self.start_btn.clicked.connect(self.start_capture)
        self.stop_btn = QPushButton("Остановить съёмку")
        self.stop_btn.clicked.connect(self.stop_capture)
        self.stop_btn.setEnabled(False)
        self.video_btn = QPushButton("Сделать видео")
        self.video_btn.clicked.connect(self.make_video)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.video_btn)
        layout.addLayout(btn_layout)

        photo_layout = QHBoxLayout()
        self.photo_btn = QPushButton("Сделать фото")
        self.photo_btn.clicked.connect(self.take_photo)
        photo_layout.addWidget(self.photo_btn)
        layout.addLayout(photo_layout)

        self.setLayout(layout)
        self.timer.timeout.connect(self.update_preview)
        self.restart_camera()

    def update_preview_size(self):
        aspect = self.aspect_ratio_box.currentText()
        if aspect == "9:16":
            self.preview_label.setFixedSize(180, 320)
        else:
            self.preview_label.setFixedSize(320, 180)

    def restart_camera(self):
        if self.cap:
            self.cap.release()
        if self.camera_box.currentIndex() < len(self.camera_indexes):
            idx = self.camera_indexes[self.camera_box.currentIndex()]
            self.cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if not self.cap.isOpened():
                QMessageBox.critical(self, "Ошибка", f"Не удалось открыть камеру {idx}")
                return
            res_text = self.resolution_box.currentText()
            w, h = map(int, res_text.split("x"))
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
            self.timer.start(100)

    def update_preview(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        frame = self.process_aspect_ratio(frame)
        frame = cv2.resize(frame, (self.preview_label.width(), self.preview_label.height()))
        image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        self.preview_label.setPixmap(QPixmap.fromImage(image))

    def process_aspect_ratio(self, frame):
        aspect = self.aspect_ratio_box.currentText()
        h, w = frame.shape[:2]
        target_ratio = 9 / 16 if aspect == "9:16" else 16 / 9
        current_ratio = w / h
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            offset = (w - new_w) // 2
            return frame[:, offset:offset + new_w]
        else:
            new_h = int(w / target_ratio)
            offset = (h - new_h) // 2
            return frame[offset:offset + new_h, :]

    def get_next_filename(self, base_name="timelapse", ext=".mp4"):
        if not os.path.isdir(self.video_dir):
            return os.path.join(os.getcwd(), f"{base_name}_1{ext}")
        existing = [f for f in os.listdir(self.video_dir) if f.startswith(base_name) and f.endswith(ext)]
        nums = [int(re.findall(rf"{base_name}_(\d+)", f)[0]) for f in existing if re.findall(rf"{base_name}_(\d+)", f)]
        next_num = max(nums) + 1 if nums else 1
        return os.path.join(self.video_dir, f"{base_name}_{next_num}{ext}")

    def select_frame_dir(self):
        dir_ = QFileDialog.getExistingDirectory(self, "Выбрать папку для фото")
        if dir_:
            self.frame_dir = dir_
            self.frame_dir_label.setText(f"Фото → {dir_}")

    def select_video_dir(self):
        dir_ = QFileDialog.getExistingDirectory(self, "Выбрать папку для видео")
        if dir_:
            self.video_dir = dir_
            self.video_dir_label.setText(f"Видео → {dir_}")

    def start_capture(self):
        if not self.frame_dir:
            QMessageBox.warning(self, "Внимание", "Выберите папку для фотографий")
            return
        self.capturing = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        threading.Thread(target=self.capture_loop, daemon=True).start()

    def stop_capture(self):
        self.capturing = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def capture_loop(self):
        while self.capturing:
            ret, frame = self.cap.read()
            if not ret:
                continue
            frame = self.process_aspect_ratio(frame)
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(self.frame_dir, f"frame_{now}.jpg")
            cv2.imwrite(path, frame)
            self.frame_list.append(path)
            time.sleep(self.interval_slider.value())

    def make_video(self):
        if not self.video_dir or not self.frame_list:
            QMessageBox.warning(self, "Ошибка", "Нет кадров или не выбрана папка для видео")
            return
        
        # Создаем временный файл со списком кадров
        list_file = os.path.join(self.video_dir, "frames.txt")
        try:
            with open(list_file, 'w', encoding='utf-8') as f:
                for img in self.frame_list:
                    # Используем raw-строки и нормализуем пути
                    img_path = os.path.normpath(img)
                    f.write(f"file '{img_path}'\n")
                    f.write(f"duration {1/self.fps_slider.value():.6f}\n")
            
            output = self.get_next_filename("timelapse")
            output_path = os.path.normpath(output)
            
            # Формируем команду с правильными путями
            cmd = [
                'ffmpeg',
                '-y',
                '-f', 'concat',
                '-safe', '0',
                '-i', os.path.normpath(list_file),
                '-vsync', 'vfr',
                '-pix_fmt', 'yuv420p',
                output_path
            ]
            
            # Запускаем процесс с захватом вывода
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Ждем завершения
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                error_msg = f"Ошибка ffmpeg (код {process.returncode}):\n{stderr}"
                QMessageBox.critical(self, "Ошибка ffmpeg", error_msg)
            else:
                QMessageBox.information(self, "Готово", f"Видео сохранено: {output_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            # Удаляем временный файл
            try:
                if os.path.exists(list_file):
                    os.remove(list_file)
            except:
                pass
            
            if not self.keep_frames_checkbox.isChecked():
                for img in self.frame_list:
                    try:
                        os.remove(img)
                    except:
                        pass
                self.frame_list.clear()

    def take_photo(self):
        ret, frame = self.cap.read()
        if ret:
            frame = self.process_aspect_ratio(frame)
            now = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = os.path.join(self.frame_dir or ".", f"photo_{now}.jpg")
            cv2.imwrite(path, frame)
            QMessageBox.information(self, "Фото", f"Снимок сохранён: {path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TimelapseApp()
    window.show()
    sys.exit(app.exec_())
