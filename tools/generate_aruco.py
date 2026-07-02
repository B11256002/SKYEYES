import argparse
import sys
from pathlib import Path

import cv2

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from config import ARUCO_DICTIONARY, PROJECT_ROOT


def generate_marker(marker_id, size, output):
    if not hasattr(cv2.aruco, ARUCO_DICTIONARY):
        raise ValueError(f"Unknown ArUco dictionary: {ARUCO_DICTIONARY}")

    dictionary_id = getattr(cv2.aruco, ARUCO_DICTIONARY)
    dictionary = cv2.aruco.getPredefinedDictionary(dictionary_id)
    marker = cv2.aruco.generateImageMarker(dictionary, marker_id, size)

    output.parent.mkdir(parents=True, exist_ok=True)

    if not cv2.imwrite(str(output), marker):
        raise RuntimeError(f"Failed to write marker image: {output}")

    return output


def main():
    parser = argparse.ArgumentParser(description="Generate an ArUco marker image.")
    parser.add_argument("--id", type=int, default=7, help="Marker ID to generate.")
    parser.add_argument("--size", type=int, default=800, help="Image size in pixels.")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output image path. Defaults to assets/aruco/aruco_<dictionary>_id_<id>.png."
    )
    args = parser.parse_args()

    output = args.output

    if output is None:
        dictionary_label = ARUCO_DICTIONARY.lower()
        output = PROJECT_ROOT / "assets" / "aruco" / f"aruco_{dictionary_label}_id_{args.id}.png"

    output = generate_marker(args.id, args.size, output)

    print(f"Generated {ARUCO_DICTIONARY} marker ID {args.id}: {output}")


if __name__ == "__main__":
    main()
