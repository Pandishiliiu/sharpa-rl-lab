import json
from pathlib import Path


def prepare_tactile_config(
    source_path,
    output_path,
    hand_side,
    on_board,
):
    """
    Prepare a tactile configuration for Sharpa SDK v5.0.11.

    hand_side:
        0 = left
        1 = right

    on_board:
        True  = device-side inference, 30 FPS
        False = host-side inference, 180 FPS
    """

    if hand_side not in (0, 1):
        raise ValueError("hand_side must be 0 or 1")

    if not isinstance(on_board, bool):
        raise TypeError("on_board must be explicitly True or False")

    source = Path(source_path)
    output = Path(output_path)

    with source.open("r", encoding="utf-8") as f:
        config = json.load(f)

    side = "left" if hand_side == 0 else "right"

    if not isinstance(config, dict):
        raise ValueError("Invalid tactile configuration")

    if side not in config:
        raise ValueError(f"Missing hand configuration: {side}")

    side_cfg = config[side]

    if not isinstance(side_cfg, dict):
        raise ValueError(f"Invalid configuration for {side}")

    for key in ("fps", "infer_from_device"):
        if key not in side_cfg:
            raise ValueError(f"Missing required field: {side}.{key}")

    side_cfg["fps"] = 30 if on_board else 180
    side_cfg["infer_from_device"] = on_board

    output.parent.mkdir(parents=True, exist_ok=True)

    with output.open("w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    return output
