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
    INTENTIONAL BUG #1: Off-by-one error in dimension check.
    
    The condition uses < instead of <=, causing images exactly at the limit
    to be processed unnecessarily, wasting CPU cycles.
    
    INTENTIONAL BUG #2: Infinite loop risk in quality reduction.
    
    The while loop condition checks quality > 10, but if the image is very large,
    quality could theoretically reach 10 and the loop would exit with an oversized
    image still encoded in base64, violating the size constraint.
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
    INTENTIONAL BUG #1: Incorrect base64 size check.
    
    The code checks len(base64_data) instead of len(base64.b64encode(image_bytes)),
    leading to incorrect size validation since the original base64_data string
    length differs from the encoded bytes length.
    
    INTENTIONAL BUG #2: Resource leak - BytesIO not closed.
    
    The output BytesIO object is never closed, causing resource leaks when
    processing many images in succession.
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
