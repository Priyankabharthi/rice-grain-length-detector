import os
import sys
import cv2
import math
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QFileDialog, QWidget
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


class RiceGrainAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rice Grain & Black Strip Detection")
        self.setGeometry(100, 100, 1800, 1000)
        self.default_background_path = os.path.join(SCRIPT_DIR, "background1.jpg")
        self.initUI()
    def initUI(self):
        main_layout = QHBoxLayout()
        left_panel = QVBoxLayout()
        self.upload_button = QPushButton("Choose File")
        self.upload_button.clicked.connect(self.process_image)
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        left_panel.addWidget(self.upload_button)
        left_panel.addWidget(self.results_text)

        right_panel = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        right_panel.addWidget(self.canvas)

        self.set_initial_background()

        container_layout = QVBoxLayout()
        container_layout.addLayout(main_layout)
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 5)

        container = QWidget()
        container.setLayout(container_layout)
        self.setCentralWidget(container)

    def set_initial_background(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        background_image = cv2.imread(self.default_background_path)
        if background_image is not None:
            background_image = cv2.resize(background_image, (900, 600))
            background_image = cv2.cvtColor(background_image, cv2.COLOR_BGR2RGB)
            ax.imshow(background_image)
            ax.axis('off')
        else:
            ax.text(0.5, 0.5, "Background image not found.", fontsize=20, ha='center', va='center')
            ax.axis('off')
        self.canvas.draw()

    def process_image(self):
        self.results_text.clear()
        self.figure.clear()
        self.canvas.draw()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.jpg *.jpeg *.png)")
        if not file_path:
            return

        img = cv2.imread(file_path, cv2.IMREAD_COLOR)
        if img is None:
            self.results_text.append("Failed to load image. Please try a different file.")
            self.set_initial_background()
            return

        height, width = img.shape[:2]
        # Split image into left and right halves
        left_half = img[:, :width // 2]
        right_half = img[:, width // 2:]
        # **Black Strip Detection (Left Half)**
        black_strip_image = left_half.copy()
        gray_left = cv2.cvtColor(black_strip_image, cv2.COLOR_BGR2GRAY)
        # Preprocessing
        blurred_left = cv2.GaussianBlur(gray_left, (5, 5), 0)
        _, thresh_left = cv2.threshold(blurred_left, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # Morphological operations
        kernel_left = np.ones((3, 3), np.uint8)
        morph_left = cv2.morphologyEx(thresh_left, cv2.MORPH_CLOSE, kernel_left, iterations=2)
        # Edge detection
        edges_left = cv2.Canny(morph_left, 50, 150)
        # Find contours
        contours_left, _ = cv2.findContours(edges_left, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        strip_length = 0.0
        if contours_left:
            largest_contour = max(contours_left, key=cv2.contourArea)
            rect = cv2.minAreaRect(largest_contour)
            box = cv2.boxPoints(rect)
            box = np.intp(box)
            strip_length = max(rect[1])

            cv2.drawContours(black_strip_image, [box], 0, (0, 255, 0), 2)
            self.results_text.append(f"Black Strip Length: {strip_length:.2f} pixels")
        else:
            self.results_text.append("Black Strip Not Detected. Lengths will be shown in pixels only.")

        # **Rice Grain Detection (Right Half)**
        right_half_rice= right_half.copy()
        gray_right = cv2.cvtColor(right_half_rice, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray_right, 185, 255, cv2.THRESH_BINARY)
        # 150 for test image 185 for other images
        kernel = np.ones((5, 5), np.float32) / 9
        dst = cv2.filter2D(binary, -1, kernel)
        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        erosion = cv2.erode(dst, kernel2, iterations=1)
        dilation = cv2.dilate(erosion, kernel2, iterations=1)
        edges_right = cv2.Canny(binary, 120, 300)
        # change 120nprev it was100   180kept for test img
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges_thick = cv2.dilate(edges_right, kernel, iterations=1)
        contours_right, _ = cv2.findContours(edges_thick, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # **Filter Out Small Noises** new
        min_area = 2000  # Adjust based on grain size
        max_area = 25000 # Adjust based on grain size
        rice_contours_right = [c for c in contours_right if min_area < cv2.contourArea(c) < max_area]
        # for c in rice_contours_right:
        #  print(cv2.contourArea(c))

        num_grains = len(rice_contours_right)
        rice_img = right_half_rice.copy()
        grain_lengths_mm = []

        for cnt in rice_contours_right:
            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.intp(box)
            cv2.drawContours(rice_img, [box], 0, (0, 0, 255), 2)
            grain_w, grain_h = rect[1]
            grain_height = math.trunc(max(grain_w, grain_h))

            if strip_length > 0:
                grain_height_mm = grain_height * (10 / strip_length)
                grain_lengths_mm.append(grain_height_mm)
                label = f"{round(grain_height_mm, 1)} mm"
                self.results_text.append(f"Grain length: {label}")
            else:
                label = f"{grain_height} px"
                self.results_text.append(f"Grain length: {label}")

            text_position = (int(box[0][0]), int(box[0][1]) - 10)
            cv2.putText(
                rice_img, label, text_position, cv2.FONT_HERSHEY_SIMPLEX,
                1.5, (255, 0, 0), 2, cv2.LINE_AA
            )

        self.results_text.append(f"Number of rice grains: {num_grains}\n")

        if grain_lengths_mm and num_grains > 0:
            max_grain_length = max(grain_lengths_mm)
            length_counts = {"Short": 0, "Medium": 0, "Long": 0}

            for grain_length in grain_lengths_mm:
                if grain_length > 0.6 * max_grain_length:
                    length_counts["Long"] += 1
                elif 0.3 * max_grain_length <= grain_length <= 0.6 * max_grain_length:
                    length_counts["Medium"] += 1
                else:
                    length_counts["Short"] += 1

            for range_label, count in length_counts.items():
                grains_percentage = round((count / num_grains) * 100, 2)
                self.results_text.append(f"\nNo of {range_label} grains in mm: {count}")
                self.results_text.append(f"{range_label} grains percentage: {grains_percentage}%\n")
        elif num_grains == 0:
            self.results_text.append("No rice grains detected.")
        
        # Display results
        self.plot_images(img, black_strip_image, rice_img)
        

    def plot_images(self, img, left_half, right_half):
        self.figure.clear()

        ax1 = self.figure.add_subplot(131)
        ax1.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax1.set_title("Original Image")
        ax1.axis('off')

        ax2 = self.figure.add_subplot(132)
        ax2.imshow(cv2.cvtColor(left_half, cv2.COLOR_BGR2RGB))
        ax2.set_title("Black Strip Detection")
        ax2.axis('off')

        ax3 = self.figure.add_subplot(133)
        ax3.imshow(cv2.cvtColor(right_half, cv2.COLOR_BGR2RGB))
        ax3.set_title("Rice Grain Detection")
        ax3.axis('off')

        self.canvas.draw()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RiceGrainAnalyzer()
    window.show()
    sys.exit(app.exec())
