import math
from collections.abc import Mapping


def validate_tactile_frame(frame, hand_side):
    """
    Validate tactile force data.

    hand_side:
        0 = left
        1 = right

    Returns:
        (channel, force_norm) for valid frames.
        None for invalid frames.
    """

    if hand_side not in (0, 1):
        raise ValueError("hand_side must be 0 or 1")

    if not isinstance(frame, Mapping):
        return None

    ch = frame.get("channel")

    if type(ch) is not int:
        return None

    allowed = range(5, 10) if hand_side == 0 else range(0, 5)

    if ch not in allowed:
        return None

    content = frame.get("content")

    if not isinstance(content, Mapping):
        return None

    f6 = content.get("F6")

    if f6 is None:
        return None

    try:
        # Supports flat arrays and single-row arrays.
        if hasattr(f6, "flatten"):
            values = list(f6.flatten())
        elif len(f6) == 1 and hasattr(f6[0], "__iter__"):
            values = list(f6[0])
        else:
            values = list(f6)

        if len(values) < 3:
            return None

        fx, fy, fz = map(float, values[:3])

        if not all(math.isfinite(v) for v in (fx, fy, fz)):
            return None

        force_norm = math.sqrt(fx**2 + fy**2 + fz**2)

        if not math.isfinite(force_norm):
            return None

    except (TypeError, ValueError, OverflowError, IndexError):
        return None

    return ch, force_norm