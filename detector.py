import cv2
import numpy as np
import datetime
import requests
import serial
import tkinter as tk
from tkinter import ttk

class HumanDetector:
    def __init__(self, camera_index=0, usb_ports=None):
        self.url = "192.168.192.91"
        self.port = "8080"
        self.hog = cv2.HOGDescriptor()
        self.cap = cv2.VideoCapture(camera_index)
        self.out = cv2.VideoWriter(
            'output.avi',
            cv2.VideoWriter_fourcc(*'MJPG'),
            15.,
            (640, 480))  # Tasvir o'lchamlari
        self.people_count = 0
        self.usb_ports = usb_ports if usb_ports else []
        self.roi = None

    def detect(self):
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def send_signal(self, value, method="serial", port_name='/dev/ttyUSB0'):
        if method == "network":
            try:
                response = requests.post(f"http://{self.url}:{self.port}/signal", json={"signal": value})
                if response.status_code == 200:
                    print("Signal sent via network.")
                else:
                    print(f"Failed to send signal via network: {response.status_code}")
            except Exception as e:
                print(f"Network error: {e}")

        elif method == "serial":
            try:
                ser = serial.Serial(port_name, 9600, timeout=1)
                ser.write(b'True\n' if value else b'False\n')
                ser.close()
                print("Signal sent via serial port.")
            except Exception as e:
                print(f"Serial error: {e}")

    def signal(self, hour, count):
        if 6 <= hour < 17 and count >= 8:
            self.send_signal(True)
            return True
        elif 17 <= hour < 18 and count >= 4:
            self.send_signal(True)
            return True
        elif hour >= 18 and count >= 1:
            self.send_signal(True)
            return True
        self.send_signal(False)
        return False

    def select_roi(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Failed to capture frame for ROI selection")
            return

        cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)  # Oyna rejimini o'rnatish
        roi = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=True)
        self.roi = roi
        cv2.destroyWindow("Select ROI")

    def start(self):
        if self.roi is None:
            self.select_roi()

        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)  # Oyna rejimini o'rnatish

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            now = datetime.datetime.now()
            hour = now.hour

            frame = cv2.resize(frame, (640, 480))  # Tasvirni qayta o'lchamlash
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

            if self.roi:
                x, y, w, h = self.roi
                roi_frame = frame[y:y+h, x:x+w]
            else:
                roi_frame = frame

            boxes, weights = self.hog.detectMultiScale(roi_frame, winStride=(8, 8))
            boxes = np.array([[x + x1, y + y1, x + x1 + w1, y + y1 + h1] for (x1, y1, w1, h1) in boxes])

            self.people_count = len(boxes)

            if self.signal(hour, self.people_count):
                print(f"Signal sent at {now.strftime('%Y-%m-%d %H:%M:%S')} with {self.people_count} people detected.")
            else:
                print(f"No signal sent at {now.strftime('%Y-%m-%d %H:%M:%S')} with {self.people_count} people detected.")

            for (xA, yA, xB, yB) in boxes:
                cv2.rectangle(frame, (xA, yA), (xB, yB), (0, 255, 0), 2)

            if self.roi:
                x, y, w, h = self.roi
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

            self.out.write(frame.astype('uint8'))
            cv2.imshow('frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        self.out.release()
        cv2.destroyAllWindows()
        cv2.waitKey(1)

def detect_cameras():
    index = 0
    arr = []
    while True:
        cap = cv2.VideoCapture(index)
        if not cap.read()[0]:
            break
        else:
            arr.append(index)
        cap.release()
        index += 1
    return arr

def detect_usb_ports():
    ports = []
    for i in range(256):
        try:
            s = serial.Serial(f'COM{i}')
            s.close()
            ports.append(f'COM{i}')
        except (OSError, serial.SerialException):
            pass
    return ports

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Human Detector Settings")

        self.cameras = detect_cameras()
        self.usb_ports = detect_usb_ports()[:4]

        self.camera_label = tk.Label(root, text="Select Camera:")
        self.camera_label.pack()
        self.camera_var = tk.StringVar()
        self.camera_dropdown = ttk.Combobox(root, textvariable=self.camera_var)
        self.camera_dropdown['values'] = self.cameras + ['Default Camera']
        if self.cameras:
            self.camera_dropdown.current(0)
        else:
            self.camera_dropdown.set('Default Camera')
        self.camera_dropdown.pack()

        self.usb_labels = []
        self.usb_vars = []
        self.usb_dropdowns = []
        for i in range(1, 5):
            label = tk.Label(root, text=f"Select USB Port {i}:")
            label.pack()
            self.usb_labels.append(label)
            var = tk.StringVar()
            self.usb_vars.append(var)
            dropdown = ttk.Combobox(root, textvariable=var)
            dropdown['values'] = self.usb_ports
            if self.usb_ports:
                dropdown.current(0)
            dropdown.pack()
            self.usb_dropdowns.append(dropdown)

        self.start_button = tk.Button(root, text="Start Detector", command=self.start_detector)
        self.start_button.pack()

    def start_detector(self):
        cameras = detect_cameras()
        camera_index = cameras[0] if cameras else 0
        usb_ports = detect_usb_ports()[:4]
        self.detector = HumanDetector(camera_index=camera_index, usb_ports=usb_ports)
        self.detector.detect()
        self.detector.start()

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
