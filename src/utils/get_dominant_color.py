from gi.repository import GdkPixbuf
import math
from typing import Tuple

def _srgb_to_linear(c: float) -> float:
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4

def relative_luminance(r: int, g: int, b: int) -> float:
    R = _srgb_to_linear(r / 255.0)
    G = _srgb_to_linear(g / 255.0)
    B = _srgb_to_linear(b / 255.0)
    return 0.2126 * R + 0.7152 * G + 0.0722 * B

def contrast_ratio_with_white(r: int, g: int, b: int) -> float:
    L2 = relative_luminance(r, g, b)
    return (1.0 + 0.05) / (L2 + 0.05)

def _composite_over_white(r: int, g: int, b: int, a: int) -> Tuple[int, int, int]:
    if a >= 255:
        return r, g, b
    alpha = a / 255.0
    or_ = int(round(r * alpha + 255 * (1 - alpha)))
    og = int(round(g * alpha + 255 * (1 - alpha)))
    ob = int(round(b * alpha + 255 * (1 - alpha)))
    return or_, og, ob

def _apply_darkening(rgb: Tuple[int,int,int], factor: float) -> Tuple[int,int,int]:
    r, g, b = rgb
    return (int(round(r * factor)), int(round(g * factor)), int(round(b * factor)))

def get_dominant_color_from_pixbuf(
    pixbuf: GdkPixbuf.Pixbuf,
    sample_size: int = 32,
    quantize_shift: int = 3,
    min_contrast_with_white: float = 4.5,
    min_darkening_factor: float = 0.4
) -> Tuple[int, int, int]:
    """
    Return a 'dominant' color (r,g,b) from a Pixbuf while avoiding returning lots of pure black.
    - sample_size: scale image to at most sample_size x sample_size for speed
    - quantize_shift: reduce color resolution (e.g. 3 -> 32 levels per channel)
    - min_contrast_with_white: desired contrast ratio against white (WCAG style)
    - min_darkening_factor: do not darken below this fraction of original color (0..1)
    """

    if pixbuf is None:
        return (0, 0, 0)

    w = pixbuf.get_width()
    h = pixbuf.get_height()
    target_w = min(sample_size, w)
    target_h = min(sample_size, h)

    if w != target_w or h != target_h:
        sample = pixbuf.scale_simple(target_w, target_h, GdkPixbuf.InterpType.BILINEAR)
    else:
        sample = pixbuf

    pixels = sample.get_pixels()
    n_channels = sample.get_n_channels()
    rowstride = sample.get_rowstride()
    sw = sample.get_width()
    sh = sample.get_height()

    shift = quantize_shift
    buckets = {}  # key -> [sum_r, sum_g, sum_b, count]

    for y in range(sh):
        row_start = y * rowstride
        for x in range(sw):
            offset = row_start + x * n_channels
            r = pixels[offset]
            g = pixels[offset + 1]
            b = pixels[offset + 2]
            if n_channels == 4:
                a = pixels[offset + 3]
                r, g, b = _composite_over_white(r, g, b, a)

            kr = (r >> shift)
            kg = (g >> shift)
            kb = (b >> shift)
            key = (kr, kg, kb)

            if key in buckets:
                buckets[key][0] += r
                buckets[key][1] += g
                buckets[key][2] += b
                buckets[key][3] += 1
            else:
                buckets[key] = [r, g, b, 1]

    if not buckets:
        return (0, 0, 0)

    # Build candidate list: (count, avg_r, avg_g, avg_b)
    candidates = []
    for vals in buckets.values():
        sum_r, sum_g, sum_b, count = vals
        avg_r = int(round(sum_r / count))
        avg_g = int(round(sum_g / count))
        avg_b = int(round(sum_b / count))
        candidates.append((count, (avg_r, avg_g, avg_b)))

    # sort by frequency desc
    candidates.sort(reverse=True, key=lambda t: t[0])

    # 1) Try to find a natural candidate that already meets contrast -> prefer that
    for _, rgb in candidates:
        if contrast_ratio_with_white(*rgb) >= min_contrast_with_white:
            return rgb

    # 2) Try moderate darkening per candidate but do not go below min_darkening_factor
    # We'll search factor in [min_darkening_factor, 1.0] (binary search) for each candidate
    best_option = None  # tuple (achievable_contrast, rgb_after_factor, original_count)
    for count, rgb in candidates:
        low = min_darkening_factor
        high = 1.0
        found = None
        for _ in range(18):  # enough iterations
            mid = (low + high) / 2.0
            tr, tg, tb = _apply_darkening(rgb, mid)
            if contrast_ratio_with_white(tr, tg, tb) >= min_contrast_with_white:
                found = (mid, (tr, tg, tb))
                # try to find a lighter mid (bigger mid) that still works (we prefer lighter)
                low = mid
            else:
                high = mid
        if found:
            # found[1] is the rgb; prefer the candidate with highest original count (we iterate in that order)
            return found[1]

        # keep track of best achievable contrast without going below min_darkening_factor
        # compute contrast at min_darkening_factor
        tr, tg, tb = _apply_darkening(rgb, min_darkening_factor)
        achievable = contrast_ratio_with_white(tr, tg, tb)
        if best_option is None or (achievable > best_option[0] and count >= best_option[2]):
            best_option = (achievable, (tr, tg, tb), count)

    # 3) If we get here, no candidate could reach the full contrast without going below min_darkening_factor.
    # Return best_option (max achievable contrast with limited darkening), which avoids pure black.
    if best_option:
        return best_option[1]

    # Fallback: return the most frequent average color (should not happen)
    top = candidates[0][1]
    return top
