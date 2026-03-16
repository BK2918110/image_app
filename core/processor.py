# core/processor.py
import cv2
import numpy as np

# ==========================================
# 1. INTENSITY TRANSFORMATIONS
# ==========================================
def to_gray(image):
    """Converts a BGR image to Grayscale."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def negative(image):
    """Inverts the pixel values."""
    return 255 - image

def log_transform(image):
    """
    Applies Logarithmic transform dynamically to enhance dark details.
    Uses HSV color space to prevent color distortion.
    """
    # 1. Convert to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # 2. Find max value and CAST TO FLOAT to prevent uint8 overflow
    max_val = float(np.max(v))
    
    if max_val == 0.0:  # Prevent division by zero on a completely black image
        return image
        
    # 3. Calculate dynamic scaling constant
    c = 255.0 / np.log(1.0 + max_val)
    
    # 4. Apply math strictly to the V (brightness) channel
    log_v = c * np.log(1.0 + v.astype(np.float32))
    log_v = np.uint8(np.clip(log_v, 0, 255))
    
    # 5. Merge back and convert to BGR
    hsv_log = cv2.merge([h, s, log_v])
    return cv2.cvtColor(hsv_log, cv2.COLOR_HSV2BGR)

def gamma_transform(image, gamma=0.5):
    """
    Applies Power-Law (Gamma) transform.
    Uses HSV space to preserve original color hues.
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    
    # Normalize V channel to 0.0 - 1.0
    v_norm = v.astype(np.float32) / 255.0
    
    # Apply gamma correction
    gamma_v = np.power(v_norm, gamma)
    gamma_v = np.uint8(gamma_v * 255.0)
    
    hsv_gamma = cv2.merge([h, s, gamma_v])
    return cv2.cvtColor(hsv_gamma, cv2.COLOR_HSV2BGR)

def contrast_stretching(image, r_min=50, r_max=200):
    """
    Applies piecewise linear contrast stretching across a defined range.
    Values below r_min are pushed towards 0, values above r_max towards 255.
    """
    # Prevent division by zero if sliders overlap
    if r_min >= r_max:
        r_max = r_min + 1
        
    img_float = image.astype(np.float32)
    
    # Mathematical stretch formula
    stretched = ((img_float - r_min) / (r_max - r_min)) * 255.0
    
    return np.clip(stretched, 0, 255).astype(np.uint8)

def intensity_slicing(image, r_min=100, r_max=150):
    """
    Highlights a specific band of intensities between r_min and r_max by pushing them to 255.
    Preserves the original background.
    """
    # Enforce logical order
    if r_min > r_max:
        r_min, r_max = r_max, r_min
        
    if len(image.shape) == 3:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        # Create binary mask where pixels fall inside the exact range
        mask = cv2.inRange(v, r_min, r_max)
        
        v_sliced = v.copy()
        v_sliced[mask == 255] = 255
        
        return cv2.cvtColor(cv2.merge([h, s, v_sliced]), cv2.COLOR_HSV2BGR)
    else:
        mask = cv2.inRange(image, r_min, r_max)
        sliced = image.copy()
        sliced[mask == 255] = 255
        return sliced
    
# ==========================================
# 2. POINT-TO-POINT ARITHMETIC (Manual)
# ==========================================
def _align_matrices(img1, img2):
    """Internal helper to ensure img2 matches the dimensions of img1."""
    if img1 is None or img2 is None:
        return img2
    if img1.shape == img2.shape:
        return img2
    h, w = img1.shape[:2]
    return cv2.resize(img2, (w, h), interpolation=cv2.INTER_AREA)

def add_images(img1, img2):
    """Manual Saturation Addition using NumPy."""
    img2_aligned = _align_matrices(img1, img2)
    a = img1.astype(np.float32)
    b = img2_aligned.astype(np.float32)
    
    result = np.clip(a + b, 0, 255)
    return result.astype(np.uint8)

def subtract_images(img1, img2):
    """Manual Saturation Subtraction using NumPy."""
    img2_aligned = _align_matrices(img1, img2)
    a = img1.astype(np.float32)
    b = img2_aligned.astype(np.float32)
    
    result = np.clip(a - b, 0, 255)
    return result.astype(np.uint8)

def multiply_images(img1, img2):
    """Manual Multiplication with 1/255 normalization."""
    img2_aligned = _align_matrices(img1, img2)
    a = img1.astype(np.float32)
    b = img2_aligned.astype(np.float32)
    
    result = np.clip((a * b) / 255.0, 0, 255)
    return result.astype(np.uint8)

def divide_images(img1, img2):
    """Manual Division handling ZeroDivision safely."""
    img2_aligned = _align_matrices(img1, img2)
    a = img1.astype(np.float32)
    b = img2_aligned.astype(np.float32)
    
    result = np.clip((a / (b + 1.0)) * 255.0, 0, 255)
    return result.astype(np.uint8)

# ==========================================
# 3. POINT-TO-POINT LOGICAL (Manual)
# ==========================================
def bitwise_and(img1, img2):
    """Manual bitwise AND using pure NumPy."""
    img2_aligned = _align_matrices(img1, img2)
    return np.bitwise_and(img1, img2_aligned)

def bitwise_or(img1, img2):
    """Manual bitwise OR using pure NumPy."""
    img2_aligned = _align_matrices(img1, img2)
    return np.bitwise_or(img1, img2_aligned)

def bitwise_xor(img1, img2):
    """Manual bitwise XOR using pure NumPy."""
    img2_aligned = _align_matrices(img1, img2)
    return np.bitwise_xor(img1, img2_aligned)

# ==========================================
# 4. HISTOGRAM ANALYSIS (Manual)
# ==========================================
def get_histogram(image):
    """
    Manually calculates the histogram frequencies of an image.
    Returns a 1D NumPy array of length 256.
    """
    if len(image.shape) == 3:
        # Extract V channel from HSV for color images
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)[:,:,2]
        
    hist = np.zeros(256, dtype=int)
    # np.unique is highly optimized for counting occurrences in arrays
    unique, counts = np.unique(image, return_counts=True)
    hist[unique] = counts
    return hist

def global_equalize(image):
    """
    Manually flattens the histogram using Cumulative Distribution Function (CDF).
    Applies only to the V channel in HSV space to protect color ratios.
    """
    if len(image.shape) == 3:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        
        hist = get_histogram(v)
        cdf = hist.cumsum()
        
        # Mask zeroes to avoid division errors
        cdf_masked = np.ma.masked_equal(cdf, 0)
        # Normalize to 0-255 range
        cdf_normalized = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
        cdf_final = np.ma.filled(cdf_normalized, 0).astype(np.uint8)
        
        v_eq = cdf_final[v]
        return cv2.cvtColor(cv2.merge([h, s, v_eq]), cv2.COLOR_HSV2BGR)
    else:
        hist = get_histogram(image)
        cdf = hist.cumsum()
        
        cdf_masked = np.ma.masked_equal(cdf, 0)
        cdf_normalized = (cdf_masked - cdf_masked.min()) * 255 / (cdf_masked.max() - cdf_masked.min())
        cdf_final = np.ma.filled(cdf_normalized, 0).astype(np.uint8)
        
        return cdf_final[image]

# ==========================================
# 5. SPATIAL FILTERING (Convolution)
# ==========================================
def apply_convolution(image, kernel):
    """
    Applies a spatial convolution mask (kernel) to an image.
    The kernel must be a 2D NumPy array (e.g., 3x3).
    """
    # cv2.filter2D with depth=-1 keeps the output depth the same as the input
    return cv2.filter2D(image, -1, kernel)

# ==========================================
# 6. CORRELATION (Template Matching)
# ==========================================
def apply_correlation(target_img, template_img):
    """
    Performs Normalized Cross-Correlation (NCC).
    Draws a red bounding box around the highest statistical match.
    """
    # 1. Convert to Grayscale for structural matching
    target_gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY)
    temp_gray = cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY)
    
    # 2. Prevent crash if template is larger than the target image
    if temp_gray.shape[0] > target_gray.shape[0] or temp_gray.shape[1] > target_gray.shape[1]:
        raise ValueError("Template cannot be larger than the Main Image.")
    
    # 3. Perform Normalized Cross-Correlation
    res = cv2.matchTemplate(target_gray, temp_gray, cv2.TM_CCOEFF_NORMED)
    
    # 4. Find the coordinates of the highest match peak
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    
    # 5. Draw the bounding box
    result_img = target_img.copy()
    h, w = temp_gray.shape
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    
    # Red rectangle (BGR: 0, 0, 255), thickness: 3
    cv2.rectangle(result_img, top_left, bottom_right, (0, 0, 255), 3)
    
    return result_img