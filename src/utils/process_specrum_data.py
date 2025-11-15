import math
from typing import List, Optional, Tuple

def process_spectrum_data(
    data_db: List[float],
    num_display_bars: int,
    prev_display: Optional[List[float]] = None,
    min_db: float = -60.0,
    max_db: float = 0.0,
    hf_boost: float = 1.0,
    hf_curve: float = 1.3,
    attack_alpha: float = 0.7,
    decay_alpha: float = 0.15,
    agg: str = 'max',
) -> Tuple[List[float], List[float]]:
    '''
    Convert linear-spectrum dB values to logarithmic display bars with HF boost and smoothing.

    Params
    - data_db: list of dB values from the 'spectrum' element (e.g. [-60..0]).
    - num_display_bars: number of bars you want to display (e.g. 31).
    - prev_display: previous frame's display values for smoothing (pass None to init).
    - min_db, max_db: clipping range for dB (default -60..0).
    - hf_boost: how strongly to boost high frequencies (1.0 = moderate, 0 = no boost).
    - hf_curve: exponent shaping the HF boost curve (>1 emphasizes highest bands more).
    - attack_alpha: smoothing weight when level rises (0..1, larger => faster attack).
    - decay_alpha: smoothing weight when level falls (0..1, smaller => slower decay).
    - agg: 'max' or 'mean' aggregator for combining many small bins into one display bar.

    Returns
    - display: list of normalized floats 0..1 (ready for GUI)
    - new_prev: the values to store and pass back as prev_display next frame
    '''

    n = len(data_db)
    if n == 0 or num_display_bars <= 0:
        return [], []

    num_display_bars += 1  #Todo: The last bar shows wierd behavior. Until later refactor I will just clip it

    # step 1: create logarithmic ranges and aggregate (db) per display bar
    log_bins_db = []
    for i in range(num_display_bars):
        # map i -> start/end index in original linear-array (using base-10 style mapping)
        start = int(n * (math.pow(10, i / num_display_bars) - 1.0) / 9.0)
        end = int(n * (math.pow(10, (i + 1) / num_display_bars) - 1.0) / 9.0)
        # ensure at least one index and clamp
        if start < 0:
            start = 0
        if end <= start:
            end = min(start + 1, n)
        if end > n:
            end = n

        chunk = data_db[start:end]
        if not chunk:
            chunk_db = min_db
        elif agg == 'mean':
            chunk_db = sum(chunk) / len(chunk)
        else:  # default 'max'
            chunk_db = max(chunk)
        log_bins_db.append(chunk_db)

    # step 2: convert dB -> normalized 0..1
    normalized = []
    denom = (max_db - min_db) if (max_db - min_db) != 0 else 1.0
    for db in log_bins_db:
        db_clamped = db
        if db_clamped < min_db:
            db_clamped = min_db
        if db_clamped > max_db:
            db_clamped = max_db
        val = (db_clamped - min_db) / denom  # 0..1
        normalized.append(val)

    # step 3: apply high-frequency boost (gain is >1 for higher-index bars)
    boosted = []
    if num_display_bars == 1:
        indices = [0.0]
    else:
        indices = [i / (num_display_bars - 1) for i in range(num_display_bars)]
    for i, val in enumerate(normalized):
        gain = 1.0 + hf_boost * (indices[i] ** hf_curve)
        v = val * gain
        if v > 1.0:
            v = 1.0
        boosted.append(v)

    # step 4: smoothing (attack/decay). If prev not supplied, init with boosted values.
    if prev_display is None or len(prev_display) != num_display_bars:
        new_prev = boosted[:]  # initialize
        display = boosted[:]
        return display[:-1], new_prev[:-1] #Todo: Cutting of the last values until fix

    display = [0.0] * num_display_bars
    new_prev = [0.0] * num_display_bars
    for i in range(num_display_bars):
        prev = prev_display[i]
        cur = boosted[i]
        if cur >= prev:
            alpha = attack_alpha
        else:
            alpha = decay_alpha
        out = alpha * cur + (1.0 - alpha) * prev
        # clamp
        if out < 0.0:
            out = 0.0
        elif out > 1.0:
            out = 1.0
        display[i] = out
        new_prev[i] = out

    return display[:-1], new_prev[:-1] #Todo: Cutting of the last values until fix
