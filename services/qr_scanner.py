"""
services/qr_scanner.py
-----------------------
Decodes QR codes from image files or in-memory frames using
OpenCV for image loading/preprocessing and pyzbar for decoding.
"""

import cv2
import numpy as np
from pyzbar.pyzbar import decode as pyzbar_decode

from utils.constants import QR_TYPE_URL, QR_TYPE_TEXT, QR_TYPE_UNKNOWN
from utils.validators import is_valid_url


class QRDecodeError(Exception):
    """Raised when a QR code cannot be found or decoded in an image."""
    pass


def _classify_content(content: str) -> str:
    """Classify decoded QR content as URL, plain text, or unknown."""
    if not content:
        return QR_TYPE_UNKNOWN
    stripped = content.strip()
    if stripped.lower().startswith(("http://", "https://")) or is_valid_url(stripped):
        return QR_TYPE_URL
    return QR_TYPE_TEXT


def _preprocess_for_detection(image: np.ndarray):
    """
    Generate a few preprocessed variants of the image to improve
    decode robustness (pyzbar can be picky about contrast/noise).
    """
    variants = [image]

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variants.append(gray)

    # Adaptive threshold helps with uneven lighting / low-contrast prints
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, 11
    )
    variants.append(thresh)

    # Slight blur to reduce sensor/JPEG noise before a second threshold pass
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(otsu)

    return variants


def decode_qr_from_image_path(image_path: str) -> dict:
    """
    Load an image from disk and attempt to decode a QR code from it.
    Returns a dict: {"content": str, "type": str}
    Raises QRDecodeError if no QR code could be found.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise QRDecodeError("Unable to read the uploaded image. It may be corrupted or an unsupported format.")

    return _decode_from_array(image)


def decode_qr_from_bytes(image_bytes: bytes) -> dict:
    """
    Decode a QR code from raw image bytes (e.g. a webcam frame
    captured client-side and posted as base64/binary).
    """
    np_arr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise QRDecodeError("Unable to decode the captured frame.")

    return _decode_from_array(image)


def _decode_from_array(image: np.ndarray) -> dict:
    """Run pyzbar over several preprocessed variants until one succeeds."""
    for variant in _preprocess_for_detection(image):
        results = pyzbar_decode(variant)
        if results:
            # Use the first detected QR/barcode symbol
            raw_data = results[0].data.decode("utf-8", errors="replace")
            return {
                "content": raw_data,
                "type": _classify_content(raw_data),
            }

    raise QRDecodeError("No QR code could be detected in the image. Try a clearer or higher-resolution image.")
