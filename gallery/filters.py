"""
Generic 'artistic / painterly' photo filter.

Intentionally generic — a soft warm-tone, slightly painterly look built
from standard PIL operations. This does NOT reproduce any specific
studio's or artist's copyrighted visual style; it's just a nice-looking
food photo filter. Swap this function out any time for a different
effect or a licensed third-party filter API.
"""
from PIL import Image, ImageFilter, ImageEnhance
from io import BytesIO
from django.core.files.base import ContentFile


def apply_artistic_filter(django_image_field, target_name="filtered.jpg"):
    """
    Takes a Django ImageField file, applies a soft painterly effect,
    and returns a ContentFile ready to be saved on another ImageField.
    """
    img = Image.open(django_image_field)
    img = img.convert("RGB")

    # Soften edges a touch (painterly feel) then sharpen key edges back in
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img = img.filter(ImageFilter.EDGE_ENHANCE)

    # Boost color + warmth slightly
    img = ImageEnhance.Color(img).enhance(1.35)
    img = ImageEnhance.Contrast(img).enhance(1.12)
    img = ImageEnhance.Brightness(img).enhance(1.05)

    # Gentle warm overlay
    overlay = Image.new("RGB", img.size, (255, 200, 120))
    img = Image.blend(img, overlay, alpha=0.08)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=88)
    return ContentFile(buffer.getvalue(), name=target_name)
