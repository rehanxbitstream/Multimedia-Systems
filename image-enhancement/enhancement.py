
import cv2
import numpy as np


def enhance_image(
    image,
    brightness=0,
    contrast=0,
    sharpness=0,
    grayscale=False,
    denoise=False,
    histogram=False
):
    """
    Apply image enhancement operations.

    image: Original image in BGR format
    brightness: -100 to 100
    contrast: -100 to 100
    sharpness: 0 to 100
    """

    result = image.copy()

    # 1. Noise Reduction
    if denoise:
        result = cv2.fastNlMeansDenoisingColored(
            result, None, 10, 10, 7, 21
        )

    # 2. Grayscale Conversion
    if grayscale:
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    # 3. Histogram Equalization
    if histogram:
        if grayscale:
            gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            equalized = cv2.equalizeHist(gray)
            result = cv2.cvtColor(
                equalized, cv2.COLOR_GRAY2BGR
            )
        else:
            ycrcb = cv2.cvtColor(result, cv2.COLOR_BGR2YCrCb)
            ycrcb[:, :, 0] = cv2.equalizeHist(ycrcb[:, :, 0])
            result = cv2.cvtColor(ycrcb, cv2.COLOR_YCrCb2BGR)

    # 4. Brightness and Contrast
    alpha = 1.0 + (contrast / 100.0)
    beta = brightness

    result = cv2.convertScaleAbs(
        result, alpha=alpha, beta=beta
    )

    # 5. Image Sharpening
    if sharpness > 0:
        blurred = cv2.GaussianBlur(result, (0, 0), 3)

        amount = sharpness / 100.0

        result = cv2.addWeighted(
            result, 1 + amount,
            blurred, -amount,
            0
        )

    return result
