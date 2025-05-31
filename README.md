# Timelapse-GUI

Graphical user interface (GUI) for capturing timelapse photos and generating video from a webcam. Designed for Windows using Python and PyQt5. Author: [iXimik](https://github.com/iXimik)

---

## Features

- Live camera preview
- Interval-based photo capture
- Adjustable resolution and aspect ratio (16:9 / 9:16)
- FPS and capture interval control
- Folder selection for frames and videos
- Optional storage of individual frames
- Video creation using ffmpeg
- Snapshot function
- GUI in Russian

---

## Installation

1. Clone the repository:

~~~
git clone https://github.com/iXimik/timelapse-gui.git
cd timelapse-gui
~~~

2. Create and activate a virtual environment (optional but recommended):

~~~
python -m venv venv
venv\\Scripts\\activate
~~~

3. Install dependencies:

~~~
pip install -r requirements.txt
~~~

Requirements file content:

~~~
PyQt5
opencv-python
~~~

---

## Run

To launch the GUI:

~~~
python timelapse_gui.py
~~~

---

## Video Creation (ffmpeg)

Make sure you have ffmpeg installed and available in PATH. You can download it from: https://www.gyan.dev/ffmpeg/builds/

---

# Timelapse-GUI

Графическая программа для съёмки таймлапсов с веб-камеры и создания видео. Работает под Windows. Автор: [iXimik](https://github.com/iXimik)

---

## Возможности

- Предпросмотр с камеры
- Съёмка фото по интервалу
- Выбор разрешения и пропорций кадра (16:9 / 9:16)
- Настройка FPS и интервала
- Выбор папок для кадров и видео
- Хранение или удаление кадров после видео
- Создание видео через ffmpeg
- Снимок фото одной кнопкой
- Интерфейс на русском языке

---

## Установка

1. Клонируйте репозиторий:

~~~
git clone https://github.com/iXimik/timelapse-gui.git
cd timelapse-gui
~~~

2. Создайте и активируйте виртуальное окружение:

~~~
python -m venv venv
venv\\Scripts\\activate
~~~

3. Установите зависимости:

~~~
pip install -r requirements.txt
~~~

Содержимое requirements.txt:

~~~
PyQt5
opencv-python
~~~

---

## Запуск

Для запуска программы:

~~~
python timelapse_gui.py
~~~

---

## Создание видео (ffmpeg)

Убедитесь, что ffmpeg установлен и добавлен в PATH. Скачать можно отсюда: https://www.gyan.dev/ffmpeg/builds/
"""
