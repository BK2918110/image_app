# ui/main_window.py
import cv2
import numpy as np
from PyQt6.QtWidgets import (
    QMainWindow, QPushButton, QLabel, QFileDialog, 
    QVBoxLayout, QHBoxLayout, QWidget, QSizePolicy, 
    QGraphicsDropShadowEffect, QMessageBox, QStackedWidget,
    QSlider, QButtonGroup, QComboBox, QLineEdit, QGridLayout
)
from PyQt6.QtGui import QPixmap, QImage, QColor, QDoubleValidator
from PyQt6.QtCore import Qt

from config import LIGHT_MODERN_STYLE
import core.processor as processor 
from ui.histogram_widget import HistogramCanvas

class ImageApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("image_app")
        self.setMinimumSize(1200, 750)
        self.setStyleSheet(LIGHT_MODERN_STYLE)

        # State Variables
        self.original_image = None
        self.current_display = None
        
        self.pt_image1 = None
        self.pt_image2 = None
        self.pt_result = None
        
        self.hist_image = None
        self.hist_result = None

        self.conv_image = None
        self.conv_result = None

        self.corr_target = None
        self.corr_template = None
        self.corr_result = None

        self._init_master_layout()

    # =========================================================
    # MASTER NAVIGATION ARCHITECTURE
    # =========================================================
    def _init_master_layout(self):
        main_container = QWidget()
        master_layout = QHBoxLayout(main_container)
        master_layout.setContentsMargins(0, 0, 0, 0) 
        master_layout.setSpacing(0)

        # 1. Master Navigation Sidebar (Far Left)
        self.master_nav = QWidget()
        self.master_nav.setObjectName("MasterNav")
        self.master_nav.setFixedWidth(220)
        nav_layout = QVBoxLayout(self.master_nav)
        nav_layout.setContentsMargins(0, 20, 0, 20)
        nav_layout.setSpacing(5)

        lbl_logo = QLabel("IMAGE\nSTUDIO")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_logo.setStyleSheet("color: white; font-weight: bold; font-size: 16px; margin-bottom: 20px;")
        nav_layout.addWidget(lbl_logo)

        # 2. Main Deck System (Right Side)
        self.stacked_widget = QStackedWidget()

        # 3. Create Navigation Tabs
        self.nav_group = QButtonGroup(self)
        
        tabs = [
            ("Intensity Transforms", self._init_intensity_page),
            ("Point Operations", self._init_point_ops_page),
            ("Histogram Analysis", self._init_histogram_page),
            ("Convolution", self._init_convolution_page),
            ("Correlation", self._init_correlation_page)
        ]

        for index, (name, init_func) in enumerate(tabs):
            btn = QPushButton(name)
            btn.setObjectName("MasterNavButton")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Switch the stacked widget when clicked
            btn.clicked.connect(lambda checked, idx=index: self.stacked_widget.setCurrentIndex(idx))
            
            self.nav_group.addButton(btn, index)
            nav_layout.addWidget(btn)
            
            # Initialize and add the page to the stack
            init_func()

        nav_layout.addStretch()
        self.nav_group.button(0).setChecked(True) # Set default tab

        master_layout.addWidget(self.master_nav)
        master_layout.addWidget(self.stacked_widget)
        self.setCentralWidget(main_container)

    # =========================================================
    # PAGE 1: INTENSITY TRANSFORMATIONS
    # =========================================================
    def _init_intensity_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20) 
        main_layout.setSpacing(20)

        sidebar = self._create_sidebar()
        sidebar_layout = sidebar.layout()

        lbl_file = QLabel("File")
        lbl_file.setObjectName("SectionHeader")
        
        btn_open = QPushButton("Open Image")
        btn_open.setObjectName("PrimaryButton")
        btn_open.clicked.connect(self.open_image)
        
        file_actions_layout = QHBoxLayout()
        btn_original = QPushButton("Reset")
        btn_original.clicked.connect(self.reset_image)
        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("DangerButton")
        btn_clear.clicked.connect(self.clear_intensity_image)
        file_actions_layout.addWidget(btn_original)
        file_actions_layout.addWidget(btn_clear)

        lbl_filters = QLabel("Static Transforms")
        lbl_filters.setObjectName("SectionHeader")

        btn_gray = QPushButton("Grayscale")
        btn_neg = QPushButton("Negative")
        btn_log = QPushButton("Log Transform")
        
        btn_gray.clicked.connect(self.apply_gray)
        btn_neg.clicked.connect(self.apply_negative)
        btn_log.clicked.connect(self.apply_log)

        lbl_dynamic = QLabel("Dynamic Transforms")
        lbl_dynamic.setObjectName("SectionHeader")

        # --- Gamma Group ---
        gamma_group = QWidget()
        gamma_layout = QVBoxLayout(gamma_group)
        gamma_layout.setContentsMargins(0, 0, 0, 0)
        gamma_layout.setSpacing(5)
        self.btn_gamma = QPushButton("Gamma (0.5)")
        self.btn_gamma.clicked.connect(self.apply_gamma)
        self.slider_gamma = QSlider(Qt.Orientation.Horizontal)
        self.slider_gamma.setRange(1, 30) 
        self.slider_gamma.setValue(5)     
        self.slider_gamma.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_gamma.valueChanged.connect(self._update_gamma_label)
        gamma_layout.addWidget(self.btn_gamma)
        gamma_layout.addWidget(self.slider_gamma)

        # --- Contrast Stretching Group (Dual Sliders) ---
        contrast_group = QWidget()
        contrast_layout = QVBoxLayout(contrast_group)
        contrast_layout.setContentsMargins(0, 0, 0, 0)
        contrast_layout.setSpacing(5)
        
        self.btn_contrast = QPushButton("Contrast Stretch (50 - 200)")
        self.btn_contrast.clicked.connect(self.apply_contrast)
        
        self.slider_cont_min = QSlider(Qt.Orientation.Horizontal)
        self.slider_cont_min.setRange(0, 254) 
        self.slider_cont_min.setValue(50)
        self.slider_cont_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_cont_min.valueChanged.connect(self._update_contrast_label)
        
        self.slider_cont_max = QSlider(Qt.Orientation.Horizontal)
        self.slider_cont_max.setRange(1, 255) 
        self.slider_cont_max.setValue(200)
        self.slider_cont_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_cont_max.valueChanged.connect(self._update_contrast_label)
        
        # Tiny labels to identify the sliders
        lbl_c_min = QLabel("Min:"); lbl_c_min.setStyleSheet("color: #9CA3AF; font-size: 10px;")
        lbl_c_max = QLabel("Max:"); lbl_c_max.setStyleSheet("color: #9CA3AF; font-size: 10px;")
        
        c_min_layout = QHBoxLayout(); c_min_layout.addWidget(lbl_c_min); c_min_layout.addWidget(self.slider_cont_min)
        c_max_layout = QHBoxLayout(); c_max_layout.addWidget(lbl_c_max); c_max_layout.addWidget(self.slider_cont_max)

        contrast_layout.addWidget(self.btn_contrast)
        contrast_layout.addLayout(c_min_layout)
        contrast_layout.addLayout(c_max_layout)

        # --- Intensity Slicing Group (Dual Sliders) ---
        slicing_group = QWidget()
        slicing_layout = QVBoxLayout(slicing_group)
        slicing_layout.setContentsMargins(0, 0, 0, 0)
        slicing_layout.setSpacing(5)
        
        self.btn_slicing = QPushButton("Intensity Slice (100 - 150)")
        self.btn_slicing.clicked.connect(self.apply_slicing)
        
        self.slider_slice_min = QSlider(Qt.Orientation.Horizontal)
        self.slider_slice_min.setRange(0, 254)
        self.slider_slice_min.setValue(100)
        self.slider_slice_min.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_slice_min.valueChanged.connect(self._update_slicing_label)
        
        self.slider_slice_max = QSlider(Qt.Orientation.Horizontal)
        self.slider_slice_max.setRange(1, 255)
        self.slider_slice_max.setValue(150)
        self.slider_slice_max.setCursor(Qt.CursorShape.PointingHandCursor)
        self.slider_slice_max.valueChanged.connect(self._update_slicing_label)
        
        lbl_s_min = QLabel("Min:"); lbl_s_min.setStyleSheet("color: #9CA3AF; font-size: 10px;")
        lbl_s_max = QLabel("Max:"); lbl_s_max.setStyleSheet("color: #9CA3AF; font-size: 10px;")
        
        s_min_layout = QHBoxLayout(); s_min_layout.addWidget(lbl_s_min); s_min_layout.addWidget(self.slider_slice_min)
        s_max_layout = QHBoxLayout(); s_max_layout.addWidget(lbl_s_max); s_max_layout.addWidget(self.slider_slice_max)

        slicing_layout.addWidget(self.btn_slicing)
        slicing_layout.addLayout(s_min_layout)
        slicing_layout.addLayout(s_max_layout)

        # Populate Layout
        sidebar_layout.addWidget(lbl_file)
        sidebar_layout.addWidget(btn_open)
        sidebar_layout.addLayout(file_actions_layout)
        sidebar_layout.addSpacing(10)
        
        sidebar_layout.addWidget(lbl_filters)
        for btn in [btn_gray, btn_neg, btn_log]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            sidebar_layout.addWidget(btn)
            
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(lbl_dynamic)
        sidebar_layout.addWidget(gamma_group)
        sidebar_layout.addWidget(contrast_group)
        sidebar_layout.addWidget(slicing_group)
        sidebar_layout.addStretch()

        self.btn_save_intensity = QPushButton("Save Image")
        self.btn_save_intensity.setObjectName("SuccessButton")
        self.btn_save_intensity.setEnabled(False)
        self.btn_save_intensity.clicked.connect(lambda: self.save_image(self.current_display))
        sidebar_layout.addWidget(self.btn_save_intensity)

        self.image_label = self._create_image_label("click 'Open Image'")

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.image_label)
        self.stacked_widget.addWidget(page) 

    # =========================================================
    # PAGE 2: POINT-TO-POINT OPERATIONS
    # =========================================================
    def _init_point_ops_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20) 
        main_layout.setSpacing(20)

        sidebar = self._create_sidebar()
        sidebar_layout = sidebar.layout()

        lbl_inputs = QLabel("Inputs")
        lbl_inputs.setObjectName("SectionHeader")
        
        img1_layout = QHBoxLayout()
        btn_img1 = QPushButton("Load Image 1")
        btn_img1.setObjectName("PrimaryButton")
        btn_img1.clicked.connect(lambda: self.load_pt_image(1))
        btn_clear1 = QPushButton("Clear")
        btn_clear1.setObjectName("DangerButton")
        btn_clear1.clicked.connect(lambda: self.clear_pt_image(1))
        img1_layout.addWidget(btn_img1)
        img1_layout.addWidget(btn_clear1)
        
        img2_layout = QHBoxLayout()
        btn_img2 = QPushButton("Load Image 2")
        btn_img2.setObjectName("PrimaryButton")
        btn_img2.clicked.connect(lambda: self.load_pt_image(2))
        btn_clear2 = QPushButton("Clear")
        btn_clear2.setObjectName("DangerButton")
        btn_clear2.clicked.connect(lambda: self.clear_pt_image(2))
        img2_layout.addWidget(btn_img2)
        img2_layout.addWidget(btn_clear2)

        lbl_arithmetic = QLabel("Arithmetic Ops")
        lbl_arithmetic.setObjectName("SectionHeader")
        btn_add = QPushButton("Addition")
        btn_sub = QPushButton("Subtraction")
        btn_mul = QPushButton("Multiplication")
        btn_div = QPushButton("Division")

        lbl_logical = QLabel("Logical Ops")
        lbl_logical.setObjectName("SectionHeader")
        btn_and = QPushButton("AND")
        btn_or = QPushButton("OR")
        btn_xor = QPushButton("XOR")

        btn_add.clicked.connect(lambda: self.apply_pt_op(processor.add_images))
        btn_sub.clicked.connect(lambda: self.apply_pt_op(processor.subtract_images))
        btn_mul.clicked.connect(lambda: self.apply_pt_op(processor.multiply_images))
        btn_div.clicked.connect(lambda: self.apply_pt_op(processor.divide_images))
        btn_and.clicked.connect(lambda: self.apply_pt_op(processor.bitwise_and))
        btn_or.clicked.connect(lambda: self.apply_pt_op(processor.bitwise_or))
        btn_xor.clicked.connect(lambda: self.apply_pt_op(processor.bitwise_xor))

        sidebar_layout.addWidget(lbl_inputs)
        sidebar_layout.addLayout(img1_layout)
        sidebar_layout.addLayout(img2_layout)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(lbl_arithmetic)
        for btn in [btn_add, btn_sub, btn_mul, btn_div]: sidebar_layout.addWidget(btn)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(lbl_logical)
        for btn in [btn_and, btn_or, btn_xor]: sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        self.btn_save_pt = QPushButton("Save Result")
        self.btn_save_pt.setObjectName("SuccessButton")
        self.btn_save_pt.setEnabled(False)
        self.btn_save_pt.clicked.connect(lambda: self.save_image(self.pt_result))
        sidebar_layout.addWidget(self.btn_save_pt)

        image_area_layout = QVBoxLayout()
        top_images_layout = QHBoxLayout()
        
        self.lbl_pt_img1 = self._create_image_label("Image 1")
        self.lbl_pt_img2 = self._create_image_label("Image 2")
        self.lbl_pt_result = self._create_image_label("Resultant Image")

        top_images_layout.addWidget(self.lbl_pt_img1)
        top_images_layout.addWidget(self.lbl_pt_img2)
        
        image_area_layout.addLayout(top_images_layout)
        image_area_layout.addWidget(self.lbl_pt_result)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(image_area_layout)
        self.stacked_widget.addWidget(page)

    # =========================================================
    # PAGE 3: HISTOGRAM ANALYSIS
    # =========================================================
    def _init_histogram_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20) 
        main_layout.setSpacing(20)

        sidebar = self._create_sidebar()
        sidebar_layout = sidebar.layout()

        lbl_inputs = QLabel("Inputs")
        lbl_inputs.setObjectName("SectionHeader")
        
        btn_load = QPushButton("Load Image")
        btn_load.setObjectName("PrimaryButton")
        btn_load.clicked.connect(self.load_hist_image)
        
        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("DangerButton")
        btn_clear.clicked.connect(self.clear_hist_image)

        file_actions_layout = QHBoxLayout()
        file_actions_layout.addWidget(btn_load)
        file_actions_layout.addWidget(btn_clear)

        lbl_ops = QLabel("Histogram Operations")
        lbl_ops.setObjectName("SectionHeader")
        
        btn_equalize = QPushButton("Global Equalization")
        btn_equalize.clicked.connect(self.apply_global_equalization)

        sidebar_layout.addWidget(lbl_inputs)
        sidebar_layout.addLayout(file_actions_layout)
        sidebar_layout.addSpacing(15)
        sidebar_layout.addWidget(lbl_ops)
        sidebar_layout.addWidget(btn_equalize)
        sidebar_layout.addStretch()

        self.btn_save_hist = QPushButton("Save Result")
        self.btn_save_hist.setObjectName("SuccessButton")
        self.btn_save_hist.setEnabled(False)
        self.btn_save_hist.clicked.connect(lambda: self.save_image(self.hist_result))
        sidebar_layout.addWidget(self.btn_save_hist)

        display_layout = QVBoxLayout()
        
        self.lbl_hist_img = self._create_image_label("Image Preview")
        self.hist_canvas = HistogramCanvas(self, width=5, height=3)

        display_layout.addWidget(self.lbl_hist_img, stretch=2) 
        display_layout.addWidget(self.hist_canvas, stretch=1)  

        main_layout.addWidget(sidebar)
        main_layout.addLayout(display_layout)
        self.stacked_widget.addWidget(page)

    # =========================================================
    # PAGE 4: CONVOLUTION (Spatial Filtering)
    # =========================================================
    def _init_convolution_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20) 
        main_layout.setSpacing(20)

        sidebar = self._create_sidebar()
        sidebar_layout = sidebar.layout()

        lbl_inputs = QLabel("Inputs")
        lbl_inputs.setObjectName("SectionHeader")
        
        btn_load = QPushButton("Load Image")
        btn_load.setObjectName("PrimaryButton")
        btn_load.clicked.connect(self.load_conv_image)
        
        btn_clear = QPushButton("Clear")
        btn_clear.setObjectName("DangerButton")
        btn_clear.clicked.connect(self.clear_conv_image)

        file_actions_layout = QHBoxLayout()
        file_actions_layout.addWidget(btn_load)
        file_actions_layout.addWidget(btn_clear)

        lbl_presets = QLabel("Kernel Presets")
        lbl_presets.setObjectName("SectionHeader")
        
        self.kernel_dropdown = QComboBox()
        self.kernel_dropdown.addItems([
            "Custom", "Box Blur (Averaging)", "Gaussian Blur (Approx)", 
            "Laplacian (Edge Detection)", "Sharpen"
        ])
        self.kernel_dropdown.currentIndexChanged.connect(self.on_kernel_preset_changed)
        self.kernel_dropdown.setCursor(Qt.CursorShape.PointingHandCursor)

        lbl_matrix = QLabel("3x3 Convolution Matrix")
        lbl_matrix.setObjectName("SectionHeader")
        
        matrix_widget = QWidget()
        matrix_layout = QGridLayout(matrix_widget)
        matrix_layout.setContentsMargins(0, 0, 0, 0)
        matrix_layout.setSpacing(5)
        
        self.matrix_inputs = []
        validator = QDoubleValidator(decimals=4) 

        for row in range(3):
            for col in range(3):
                line_edit = QLineEdit("0.0")
                line_edit.setObjectName("MatrixInput")
                line_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
                line_edit.setValidator(validator)
                matrix_layout.addWidget(line_edit, row, col)
                self.matrix_inputs.append(line_edit)

        self.on_kernel_preset_changed(0) 

        btn_apply = QPushButton("Apply Convolution")
        btn_apply.setObjectName("PrimaryButton")
        btn_apply.clicked.connect(self.apply_convolution_filter)

        sidebar_layout.addWidget(lbl_inputs)
        sidebar_layout.addLayout(file_actions_layout)
        sidebar_layout.addSpacing(15)
        sidebar_layout.addWidget(lbl_presets)
        sidebar_layout.addWidget(self.kernel_dropdown)
        sidebar_layout.addSpacing(15)
        sidebar_layout.addWidget(lbl_matrix)
        sidebar_layout.addWidget(matrix_widget)
        sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(btn_apply)
        sidebar_layout.addStretch()

        self.btn_save_conv = QPushButton("Save Result")
        self.btn_save_conv.setObjectName("SuccessButton")
        self.btn_save_conv.setEnabled(False)
        self.btn_save_conv.clicked.connect(lambda: self.save_image(self.conv_result))
        sidebar_layout.addWidget(self.btn_save_conv)

        display_layout = QHBoxLayout()
        self.lbl_conv_orig = self._create_image_label("Original Image")
        self.lbl_conv_result = self._create_image_label("Filtered Result")

        display_layout.addWidget(self.lbl_conv_orig)
        display_layout.addWidget(self.lbl_conv_result)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(display_layout)
        self.stacked_widget.addWidget(page)

    # =========================================================
    # PAGE 5: CORRELATION (Template Matching)
    # =========================================================
    def _init_correlation_page(self):
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(20, 20, 20, 20) 
        main_layout.setSpacing(20)

        sidebar = self._create_sidebar()
        sidebar_layout = sidebar.layout()

        lbl_inputs = QLabel("Inputs")
        lbl_inputs.setObjectName("SectionHeader")
        
        # Target Image (Main Image)
        target_layout = QHBoxLayout()
        btn_target = QPushButton("Load Main Image")
        btn_target.setObjectName("PrimaryButton")
        btn_target.clicked.connect(lambda: self.load_corr_image(1))
        btn_clear_target = QPushButton("Clear")
        btn_clear_target.setObjectName("DangerButton")
        btn_clear_target.clicked.connect(lambda: self.clear_corr_image(1))
        target_layout.addWidget(btn_target)
        target_layout.addWidget(btn_clear_target)
        
        # Template Image (The cutout to find)
        template_layout = QHBoxLayout()
        btn_template = QPushButton("Load Template")
        btn_template.setObjectName("PrimaryButton")
        btn_template.clicked.connect(lambda: self.load_corr_image(2))
        btn_clear_template = QPushButton("Clear")
        btn_clear_template.setObjectName("DangerButton")
        btn_clear_template.clicked.connect(lambda: self.clear_corr_image(2))
        template_layout.addWidget(btn_template)
        template_layout.addWidget(btn_clear_template)

        btn_apply = QPushButton("Run Template Matching")
        btn_apply.setObjectName("PrimaryButton")
        btn_apply.clicked.connect(self.apply_correlation_match)

        sidebar_layout.addWidget(lbl_inputs)
        sidebar_layout.addLayout(target_layout)
        sidebar_layout.addLayout(template_layout)
        sidebar_layout.addSpacing(15)
        sidebar_layout.addWidget(btn_apply)
        sidebar_layout.addStretch()

        self.btn_save_corr = QPushButton("Save Result")
        self.btn_save_corr.setObjectName("SuccessButton")
        self.btn_save_corr.setEnabled(False)
        self.btn_save_corr.clicked.connect(lambda: self.save_image(self.corr_result))
        sidebar_layout.addWidget(self.btn_save_corr)

        # Display Area: Top for inputs, Bottom for result
        image_area_layout = QVBoxLayout()
        top_images_layout = QHBoxLayout()
        
        self.lbl_corr_target = self._create_image_label("Main Image (Target)")
        self.lbl_corr_template = self._create_image_label("Template (To Find)")
        self.lbl_corr_result = self._create_image_label("Correlation Result")

        top_images_layout.addWidget(self.lbl_corr_target, stretch=2)
        top_images_layout.addWidget(self.lbl_corr_template, stretch=1)
        
        image_area_layout.addLayout(top_images_layout)
        image_area_layout.addWidget(self.lbl_corr_result)

        main_layout.addWidget(sidebar)
        main_layout.addLayout(image_area_layout)
        self.stacked_widget.addWidget(page)

    # =========================================================
    # HELPER METHODS
    # =========================================================
    def _create_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(260)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(12)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(3)
        shadow.setColor(QColor(0, 0, 0, 15))
        sidebar.setGraphicsEffect(shadow)
        return sidebar

    def _create_image_label(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("ImageLabel")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        return lbl

    def _reset_label(self, label, default_text):
        label.clear()
        label.setText(default_text)
        label.setStyleSheet("""
            background-color: #FFFFFF;
            border: 2px dashed #D1D5DB;
            border-radius: 10px;
            color: #6B7280;
        """)

    def _render_pixmap(self, cv_img, label):
        if cv_img is None: return
        label.setStyleSheet("border: 1px solid #E5E7EB; background-color: #FFFFFF; border-radius: 10px;")
        img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = img_rgb.shape
        q_img = QImage(img_rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        scaled_pixmap = QPixmap.fromImage(q_img).scaled(
            label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        label.setPixmap(scaled_pixmap)

    def resizeEvent(self, event):
        if hasattr(self, 'image_label'):
            self._render_pixmap(self.current_display, self.image_label)
        if hasattr(self, 'lbl_pt_img1'):
            self._render_pixmap(self.pt_image1, self.lbl_pt_img1)
            self._render_pixmap(self.pt_image2, self.lbl_pt_img2)
            self._render_pixmap(self.pt_result, self.lbl_pt_result)
        if hasattr(self, 'lbl_hist_img'):
            self._render_pixmap(self.hist_result, self.lbl_hist_img)
        if hasattr(self, 'lbl_conv_orig'):
            self._render_pixmap(self.conv_image, self.lbl_conv_orig)
            self._render_pixmap(self.conv_result, self.lbl_conv_result)
            
        # 5. Correlation Page (NEW CHECK)
        if hasattr(self, 'lbl_corr_target'):
            self._render_pixmap(self.corr_target, self.lbl_corr_target)
            self._render_pixmap(self.corr_template, self.lbl_corr_template)
            self._render_pixmap(self.corr_result, self.lbl_corr_result)
            
        super().resizeEvent(event)

    def save_image(self, target_image):
        if target_image is None: return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "result.jpg", "JPEG (*.jpg *.jpeg);;PNG (*.png);;Bitmap (*.bmp)")
        if file_path:
            if cv2.imwrite(file_path, target_image):
                QMessageBox.information(self, "Success", "Image saved successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to save the image.")

    # =========================================================
    # LOGIC: INTENSITY OPS
    # =========================================================
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.original_image = cv2.imread(file_path)
            if self.original_image is not None:
                self.current_display = self.original_image.copy()
                self._render_pixmap(self.current_display, self.image_label)
                self.btn_save_intensity.setEnabled(False)

    def reset_image(self):
        if self.original_image is not None:
            self.current_display = self.original_image.copy()
            self._render_pixmap(self.current_display, self.image_label)
            self.btn_save_intensity.setEnabled(False)

    def clear_intensity_image(self):
        self.original_image = None
        self.current_display = None
        self._reset_label(self.image_label, "click 'Open Image'")
        self.btn_save_intensity.setEnabled(False)

    def apply_gray(self):
        if self.original_image is not None:
            self.current_display = cv2.cvtColor(processor.to_gray(self.original_image), cv2.COLOR_GRAY2BGR)
            self._render_pixmap(self.current_display, self.image_label)
            self.btn_save_intensity.setEnabled(True)

    def apply_negative(self):
        if self.original_image is not None:
            self.current_display = processor.negative(self.original_image)
            self._render_pixmap(self.current_display, self.image_label)
            self.btn_save_intensity.setEnabled(True)

    def apply_log(self):
        if self.original_image is not None:
            self.current_display = processor.log_transform(self.original_image)
            self._render_pixmap(self.current_display, self.image_label)
            self.btn_save_intensity.setEnabled(True)

    def _update_gamma_label(self, value):
        gamma_val = value / 10.0
        self.btn_gamma.setText(f"Gamma ({gamma_val:.1f})")

    def apply_gamma(self):
        if self.original_image is not None:
            gamma_val = self.slider_gamma.value() / 10.0
            self.current_display = processor.gamma_transform(self.original_image, gamma_val)
            self._render_pixmap(self.current_display, self.image_label)
            self.btn_save_intensity.setEnabled(True)

    # ---------------------------------------------------------
    # Dynamic Contrast & Slicing Controllers (Two-Point)
    # ---------------------------------------------------------
    def _update_contrast_label(self):
        r_min = self.slider_cont_min.value()
        r_max = self.slider_cont_max.value()
        # Visual enforcement for the user
        if r_min >= r_max:
            r_max = r_min + 1
        self.btn_contrast.setText(f"Contrast Stretch ({r_min} - {r_max})")

    def apply_contrast(self):
        if self.original_image is not None:
            r_min = self.slider_cont_min.value()
            r_max = self.slider_cont_max.value()
            self.current_display = processor.contrast_stretching(self.original_image, r_min, r_max)
            self._render_pixmap(self.current_display, self.image_label)
            self.btn_save_intensity.setEnabled(True)

    def _update_slicing_label(self):
        r_min = self.slider_slice_min.value()
        r_max = self.slider_slice_max.value()
        if r_min > r_max:
            r_min, r_max = r_max, r_min
        self.btn_slicing.setText(f"Intensity Slice ({r_min} - {r_max})")

    def apply_slicing(self):
        if self.original_image is not None:
            r_min = self.slider_slice_min.value()
            r_max = self.slider_slice_max.value()
            self.current_display = processor.intensity_slicing(self.original_image, r_min, r_max)
            self._render_pixmap(self.current_display, self.image_label)
            self.btn_save_intensity.setEnabled(True)

    # =========================================================
    # LOGIC: POINT OPS
    # =========================================================
    def load_pt_image(self, index):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Open Image {index}", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                if index == 1:
                    self.pt_image1 = img
                    self._render_pixmap(self.pt_image1, self.lbl_pt_img1)
                else:
                    self.pt_image2 = img
                    self._render_pixmap(self.pt_image2, self.lbl_pt_img2)

    def clear_pt_image(self, index):
        if index == 1:
            self.pt_image1 = None
            self._reset_label(self.lbl_pt_img1, "Image 1")
        else:
            self.pt_image2 = None
            self._reset_label(self.lbl_pt_img2, "Image 2")
        self.pt_result = None
        self._reset_label(self.lbl_pt_result, "Resultant Image")
        self.btn_save_pt.setEnabled(False)

    def apply_pt_op(self, operation_func):
        if self.pt_image1 is None or self.pt_image2 is None:
            QMessageBox.warning(self, "Warning", "Please load BOTH Image 1 and Image 2 first.")
            return
        self.pt_result = operation_func(self.pt_image1, self.pt_image2)
        if len(self.pt_result.shape) == 2:
            self.pt_result = cv2.cvtColor(self.pt_result, cv2.COLOR_GRAY2BGR)
        self._render_pixmap(self.pt_result, self.lbl_pt_result)
        self.btn_save_pt.setEnabled(True)

    # =========================================================
    # LOGIC: HISTOGRAM OPS
    # =========================================================
    def load_hist_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.hist_image = cv2.imread(file_path)
            if self.hist_image is not None:
                self.hist_result = self.hist_image.copy()
                self._render_pixmap(self.hist_result, self.lbl_hist_img)
                self.hist_canvas.plot_histogram(processor.get_histogram(self.hist_result))
                self.btn_save_hist.setEnabled(False)

    def clear_hist_image(self):
        self.hist_image = None
        self.hist_result = None
        self._reset_label(self.lbl_hist_img, "Image Preview")
        self.hist_canvas.clear_plot()
        self.btn_save_hist.setEnabled(False)

    def apply_global_equalization(self):
        if self.hist_image is not None:
            self.hist_result = processor.global_equalize(self.hist_image)
            self._render_pixmap(self.hist_result, self.lbl_hist_img)
            self.hist_canvas.plot_histogram(processor.get_histogram(self.hist_result))
            self.btn_save_hist.setEnabled(True)
    
    # =========================================================
    # LOGIC: CONVOLUTION OPS
    # =========================================================
    def load_conv_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.conv_image = cv2.imread(file_path)
            if self.conv_image is not None:
                self.conv_result = self.conv_image.copy()
                self._render_pixmap(self.conv_image, self.lbl_conv_orig)
                self._render_pixmap(self.conv_result, self.lbl_conv_result)
                self.btn_save_conv.setEnabled(False)

    def clear_conv_image(self):
        self.conv_image = None
        self.conv_result = None
        self._reset_label(self.lbl_conv_orig, "Original Image")
        self._reset_label(self.lbl_conv_result, "Filtered Result")
        self.btn_save_conv.setEnabled(False)

    def on_kernel_preset_changed(self, index):
        presets = {
            0: [0,0,0, 0,1,0, 0,0,0],
            1: [1/9]*9,
            2: [1/16, 2/16, 1/16, 2/16, 4/16, 2/16, 1/16, 2/16, 1/16],
            3: [0, -1, 0, -1, 4, -1, 0, -1, 0],
            4: [0, -1, 0, -1, 5, -1, 0, -1, 0]
        }
        values = presets.get(index, presets[0])
        for i, val in enumerate(values):
            self.matrix_inputs[i].setText(f"{val:.4f}")

    def apply_convolution_filter(self):
        if self.conv_image is None:
            QMessageBox.warning(self, "Warning", "Please load an image first.")
            return
        try:
            kernel_values = [float(input_field.text()) for input_field in self.matrix_inputs]
            kernel = np.array(kernel_values, dtype=np.float32).reshape((3, 3))
            self.conv_result = processor.apply_convolution(self.conv_image, kernel)
            self._render_pixmap(self.conv_result, self.lbl_conv_result)
            self.btn_save_conv.setEnabled(True)
        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid matrix input.")

    # =========================================================
    # LOGIC: CORRELATION OPS
    # =========================================================
    def load_corr_image(self, index):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Open Image {index}", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            img = cv2.imread(file_path)
            if img is not None:
                if index == 1:
                    self.corr_target = img
                    self._render_pixmap(self.corr_target, self.lbl_corr_target)
                else:
                    self.corr_template = img
                    self._render_pixmap(self.corr_template, self.lbl_corr_template)

    def clear_corr_image(self, index):
        if index == 1:
            self.corr_target = None
            self._reset_label(self.lbl_corr_target, "Main Image (Target)")
        else:
            self.corr_template = None
            self._reset_label(self.lbl_corr_template, "Template (To Find)")
            
        self.corr_result = None
        self._reset_label(self.lbl_corr_result, "Correlation Result")
        self.btn_save_corr.setEnabled(False)

    def apply_correlation_match(self):
        if self.corr_target is None or self.corr_template is None:
            QMessageBox.warning(self, "Warning", "Please load BOTH the Main Image and the Template first.")
            return
            
        try:
            self.corr_result = processor.apply_correlation(self.corr_target, self.corr_template)
            self._render_pixmap(self.corr_result, self.lbl_corr_result)
            self.btn_save_corr.setEnabled(True)
        except ValueError as e:
            QMessageBox.critical(self, "Error", str(e))