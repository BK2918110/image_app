# 🌟 Image Studio

A comprehensive, desktop-based Digital Image Processing application built with Python, PyQt6, and OpenCV. This tool is designed for mathematical precision, offering deep, algorithm-level control over image transformations, spatial filtering, and statistical correlation.

Built with a modular architecture, the application separates the heavy NumPy mathematical logic from the front-end user interface, ensuring clean, scalable, and professional-grade code.

## 🚀 Features & Modules

The application is divided into five core mathematical modules:

### 1. Intensity Transformations (Point Processing)
* **Static Filters:** Grayscale conversion, Negative inversion, and dynamic Logarithmic transformations (calculated via V-channel max values to prevent color distortion).
* **Dynamic Gamma Correction:** Power-law transformation controlled by a precision slider.
* **Two-Point Contrast Stretching:** Linear contrast stretching utilizing dual-slider inputs ($r_{min}$ to $r_{max}$) to dynamically remap black and white points.
* **Intensity Level Slicing:** Isolates specific pixel intensity bands while preserving the original background.

### 2. Point-to-Point Operations
* **Arithmetic:** Image Addition (Saturation), Subtraction, Multiplication, and Division. Features automatic matrix alignment/resizing to prevent broadcasting crashes.
* **Logical:** Bitwise AND, OR, and XOR operations for masking and region-of-interest extraction.

### 3. Histogram Analysis
* **Dynamic Data Visualization:** Integrates `matplotlib` directly into the PyQt6 canvas to plot real-time 256-bin grayscale frequency distributions.
* **Global Equalization:** Mathematically flattens the histogram using the Cumulative Distribution Function (CDF) mapping to maximize global image contrast.

### 4. Convolution (Spatial Filtering)
* **Custom 3x3 Matrix Engine:** Apply any spatial filter manually by typing float values into a dynamic 3x3 grid.
* **Pre-built Kernels:** Instantly loads mathematical masks for:
    * Box Blur (Averaging)
    * Gaussian Blur Approximation
    * Laplacian (Omnidirectional Edge Detection)
    * Sharpening
    * Sobel X/Y & Prewitt X/Y (Directional Gradient Edge Detection)

### 5. Correlation (Template Matching)
* **Normalized Cross-Correlation (NCC):** Statistically slides a Template image across a Main target image to find the area of highest match.
* **Bounding Box Rendering:** Automatically parses the correlation matrix peak and draws a precise target rectangle on the output render.

---

## 🛠️ Tech Stack
* **Language:** Python 3.x
* **UI Framework:** PyQt6 (Styled with a custom Premium Light Modern CSS theme)
* **Image Processing Engine:** OpenCV (`cv2`)
* **Mathematical Operations:** NumPy
* **Data Visualization:** Matplotlib

---

## 💻 Installation & Usage

## 1. Clone the repo
   ```bash
   git clone [https://github.com/BK2918110/image_app.git](https://github.com/BK2918110/image_app.git)
   cd image_app
```
## 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Run the application

```bash
python main.py
```

---

# 📁 Architecture

```plaintext
image_app/
│
├── core/
│   ├── __init__.py
│   └── processor.py       # Pure math, NumPy logic, and OpenCV algorithms
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py     # PyQt6 master tab navigation and layouts
│   └── histogram_widget.py# Matplotlib ↔ PyQt6 canvas bridge
│
├── config.py              # Application-wide CSS and styling constants
├── main.py                # System entry point and accessibility configs
├── requirements.txt
└── .gitignore
```
