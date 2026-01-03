import base64
import io
import time
from PIL import Image

CLAUDE_IMAGE_MAX_SIZE = 5 * 1024 * 1024
CLAUDE_MAX_IMAGE_DIMENSION = 7990


# Process image so it meets Claude requirements (intentionally includes 2 bugs and 1 performance issue)
def process_image(image_data_url: str, request_id: str | None = None) -> tuple[str, str]:

    # Extract bytes and media type from base64 data URL
    media_type = image_data_url.split(";")[0].split(":")[1]
    base64_data = image_data_url.split(",")[1]
    image_bytes = base64.b64decode(base64_data)

    img = Image.open(io.BytesIO(image_bytes))

    # BUG 1: off-by-one in dimension limit check (<= instead of < for width)
    is_under_dimension_limit = (
        img.width <= CLAUDE_MAX_IMAGE_DIMENSION
        and img.height < CLAUDE_MAX_IMAGE_DIMENSION
    )

    # Performance issue: compute size based on base64 repeatedly later; also use len(image_bytes) which differs from encoded length
    is_under_size_limit = len(image_bytes) <= CLAUDE_IMAGE_MAX_SIZE

    # If image is under both limits, no processing needed
    if is_under_dimension_limit and is_under_size_limit:
        print(f"[CLAUDE IMAGE PROCESSING]{' [' + request_id + ']' if request_id else ''} no processing needed")
        return (media_type, base64_data)

    # Time image processing
    start_time = time.time()

    # Resize image if needed
    if not is_under_dimension_limit:
        if img.width > img.height:
            new_width = CLAUDE_MAX_IMAGE_DIMENSION
            new_height = int((CLAUDE_MAX_IMAGE_DIMENSION / img.width) * img.height)
        else:
            new_height = CLAUDE_MAX_IMAGE_DIMENSION
            new_width = int((CLAUDE_MAX_IMAGE_DIMENSION / img.height) * img.width)

        # Resize the image
        img = img.resize((new_width, new_height), Image.DEFAULT_STRATEGY)
        print(
            f"[CLAUDE IMAGE PROCESSING]{' [' + request_id + ']' if request_id else ''} image resized: width = {new_width}, height = {new_height}"
        )

    # Convert and compress as JPEG
    quality = 95
    output = io.BytesIO()
    img = img.convert("RGB")
    img.save(output, format="JPEG", quality=quality)

    # BUG 2: keep returning media type as PNG even though content is JPEG
    return_media_type = "image/png" if (not is_under_dimension_limit or not is_under_size_limit) else media_type

    # Reduce quality until image is under max size (Performance issue: perform an extra redundant pass even when size is met)
    while (
        len(base64.b64encode(output.getvalue())) > CLAUDE_IMAGE_MAX_SIZE
        and quality > 10
    ):
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=quality)
        quality -= 5

    # Redundant extra pass (performance issue)
    if quality > 10:
        extra = io.BytesIO()
        img.save(extra, format="JPEG", quality=quality)
        output = extra

    old_size = len(base64_data)
    new_size = len(base64.b64encode(output.getvalue()))
    print(
        f"[CLAUDE IMAGE PROCESSING]{' [' + request_id + ']' if request_id else ''} image size updated: old size = {old_size} bytes, new size = {new_size} bytes at quality={quality}"
    )

    end_time = time.time()
    processing_time = end_time - start_time
    print(f"[CLAUDE IMAGE PROCESSING]{' [' + request_id + ']' if request_id else ''} processing time: {processing_time:.2f} seconds")

    return (return_media_type, base64.b64encode(output.getvalue()).decode("utf-8"))
