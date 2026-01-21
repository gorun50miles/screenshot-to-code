"""
Intentionally buggy versions of process_image for evaluation and testing purposes.

This file contains deliberate bugs for:
- Code review training
- Static analysis tool evaluation
- Bug detection testing
- Educational purposes

DO NOT use these functions in production code.
"""

import base64
import io
import time
from PIL import Image

CLAUDE_IMAGE_MAX_SIZE = 5 * 1024 * 1024
CLAUDE_MAX_IMAGE_DIMENSION = 7990


def process_image_buggy_v1(image_data_url: str, request_id: str | None = None) -> tuple[str, str]:
    """
    Process an image data URL, resizing and re-encoding to JPEG when necessary to attempt to satisfy configured dimension and size limits.
    
    This function accepts a data URL containing base64-encoded image data, decodes and opens the image, and:
    - If the image is within configured dimension and size limits, returns the original media type and base64 data unchanged.
    - Otherwise, resizes the image to fit within the maximum dimension while preserving aspect ratio (if needed), converts to RGB and re-encodes as JPEG, and reduces JPEG quality in steps to try to meet the maximum encoded size.
    
    Parameters:
        image_data_url (str): A data URL (e.g. "data:image/png;base64,...") containing the image.
        request_id (str | None): Optional identifier used for logging; has no effect on processing.
    
    Returns:
        tuple[str, str]: A pair of (media_type, base64_image). `media_type` is the original media type when no processing was performed, or "image/jpeg" when the image was re-encoded; `base64_image` is the base64-encoded image data to use.
    """

    media_type = image_data_url.split(";")[0].split(":")[1]
    base64_data = image_data_url.split(",")[1]
    image_bytes = base64.b64decode(base64_data)

    img = Image.open(io.BytesIO(image_bytes))

    # BUG #1: Using < instead of <= causes unnecessary processing
    is_under_dimension_limit = (
        img.width < CLAUDE_MAX_IMAGE_DIMENSION
        and img.height < CLAUDE_MAX_IMAGE_DIMENSION
    )
    is_under_size_limit = len(base64_data) <= CLAUDE_IMAGE_MAX_SIZE

    if is_under_dimension_limit and is_under_size_limit:
        print(f"[CLAUDE IMAGE PROCESSING] request_id={request_id} no processing needed")
        return (media_type, base64_data)

    start_time = time.time()

    if not is_under_dimension_limit:
        if img.width > img.height:
            new_width = CLAUDE_MAX_IMAGE_DIMENSION
            new_height = int((CLAUDE_MAX_IMAGE_DIMENSION / img.width) * img.height)
        else:
            new_height = CLAUDE_MAX_IMAGE_DIMENSION
            new_width = int((CLAUDE_MAX_IMAGE_DIMENSION / img.height) * img.width)

        img = img.resize((new_width, new_height), Image.DEFAULT_STRATEGY)
        print(
            f"[CLAUDE IMAGE PROCESSING] request_id={request_id} image resized: width = {new_width}, height = {new_height}"
        )

    quality = 95
    output = io.BytesIO()
    img_rgb = img.convert("RGB")
    img_rgb.save(output, format="JPEG", quality=quality)

    # BUG #2: Loop exits when quality reaches 10, but image may still exceed size limit
    while (
        len(base64.b64encode(output.getvalue())) > CLAUDE_IMAGE_MAX_SIZE
        and quality > 10
    ):
        output = io.BytesIO()
        img_rgb.save(output, format="JPEG", quality=quality)
        quality -= 5

    old_size = len(base64_data)
    new_size = len(base64.b64encode(output.getvalue()))
    print(
        f"[CLAUDE IMAGE PROCESSING] request_id={request_id} image size updated: old size = {old_size} bytes, new size = {new_size} bytes"
    )

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"[CLAUDE IMAGE PROCESSING] request_id={request_id} processing time: {processing_time:.2f} seconds")

    return ("image/jpeg", base64.b64encode(output.getvalue()).decode("utf-8"))


def process_image_buggy_v2(image_data_url: str, request_id: str | None = None) -> tuple[str, str]:
    """
    Ensure an image from a data URL fits within configured dimension and base64-encoded size limits by optionally resizing and re-encoding it as JPEG.
    
    This function parses a data URL, decodes the image, and if the image exceeds the configured maximum dimension or encoded size, resizes the image to fit within the maximum dimension while preserving aspect ratio and re-encodes it as a JPEG with progressively reduced quality until the size constraint is met or a minimum quality threshold is reached.
    
    Parameters:
        image_data_url (str): A data URL containing the image (e.g., "data:image/png;base64,...").
        request_id (str | None): Optional identifier used for logging.
    
    Returns:
        tuple[str, str]: A tuple (media_type, base64_data) where `media_type` is the MIME type of the resulting image (typically "image/jpeg" if re-encoded) and `base64_data` is the base64-encoded image payload.
    """

    media_type = image_data_url.split(";")[0].split(":")[1]
    base64_data = image_data_url.split(",")[1]
    image_bytes = base64.b64decode(base64_data)

    img = Image.open(io.BytesIO(image_bytes))

    is_under_dimension_limit = (
        img.width < CLAUDE_MAX_IMAGE_DIMENSION
        and img.height < CLAUDE_MAX_IMAGE_DIMENSION
    )
    # BUG #1: Checking len(base64_data) instead of actual encoded size
    is_under_size_limit = len(base64_data) <= CLAUDE_IMAGE_MAX_SIZE

    if is_under_dimension_limit and is_under_size_limit:
        print(f"[CLAUDE IMAGE PROCESSING] request_id={request_id} no processing needed")
        return (media_type, base64_data)

    start_time = time.time()

    if not is_under_dimension_limit:
        if img.width > img.height:
            new_width = CLAUDE_MAX_IMAGE_DIMENSION
            new_height = int((CLAUDE_MAX_IMAGE_DIMENSION / img.width) * img.height)
        else:
            new_height = CLAUDE_MAX_IMAGE_DIMENSION
            new_width = int((CLAUDE_MAX_IMAGE_DIMENSION / img.height) * img.width)

        img = img.resize((new_width, new_height), Image.DEFAULT_STRATEGY)
        print(
            f"[CLAUDE IMAGE PROCESSING] request_id={request_id} image resized: width = {new_width}, height = {new_height}"
        )

    quality = 95
    output = io.BytesIO()  # BUG #2: Never closed, resource leak
    img_rgb = img.convert("RGB")
    img_rgb.save(output, format="JPEG", quality=quality)

    while (
        len(base64.b64encode(output.getvalue())) > CLAUDE_IMAGE_MAX_SIZE
        and quality > 10
    ):
        output = io.BytesIO()  # BUG #2: Previous output never closed
        img_rgb.save(output, format="JPEG", quality=quality)
        quality -= 5

    old_size = len(base64_data)
    new_size = len(base64.b64encode(output.getvalue()))
    print(
        f"[CLAUDE IMAGE PROCESSING] request_id={request_id} image size updated: old size = {old_size} bytes, new size = {new_size} bytes"
    )

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"[CLAUDE IMAGE PROCESSING] request_id={request_id} processing time: {processing_time:.2f} seconds")

    return ("image/jpeg", base64.b64encode(output.getvalue()).decode("utf-8"))