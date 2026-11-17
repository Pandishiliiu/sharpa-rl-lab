import math
import time


def check_tactile_freshness(
    last_seen,
    hand_side,
    disabled_fingers=(),
    max_age=0.5,
    now=None,
):
    """
    Check tactile frame freshness.

    last_seen:
        dict[channel] = time.monotonic() timestamp

    hand_side:
        0 = left
        1 = right

    disabled_fingers:
        Finger indices (0=thumb, 4=pinky), not SDK channels.

    Returns:
        {
            "ready": bool,
            "missing": list[int],
            "stale": list[int],
        }
    """

    if hand_side not in (0, 1):
        raise ValueError("Invalid hand_side")

    if not math.isfinite(max_age) or max_age <= 0:
        raise ValueError("max_age must be positive and finite")

    if now is None:
        now = time.monotonic()

    missing = []
    stale = []

    for finger in range(5):

        if finger in disabled_fingers:
            continue

        # Convert policy finger index to SDK channel.
        ch = 4 - finger + 5 * (1 - hand_side)

        timestamp = last_seen.get(ch)

        if timestamp is None:
            missing.append(ch)
            continue

        age = now - timestamp

        if not math.isfinite(age) or age < 0 or age > max_age:
            stale.append(ch)

    return {
        "ready": not missing and not stale,
        "missing": missing,
        "stale": stale,
    }
