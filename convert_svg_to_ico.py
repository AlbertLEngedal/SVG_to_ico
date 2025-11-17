"""Batch convert SVG files to Windows-compatible ICO icons without native deps.

This script rasterizes SVG images with ``svglib``/``reportlab`` and bundles
multiple icon sizes into a single ``.ico`` file using Pillow. No external
``cairo`` or ``ImageMagick`` libraries are required.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg


DEFAULT_SIZES = (16, 24, 32, 48, 64, 128, 256)


def rasterize_svg(svg_path: Path, size: int) -> Image.Image:
    """Render an SVG to a square Pillow image of the requested size.

    The SVG is scaled so that its largest dimension matches the target size
    while preserving aspect ratio.
    """

    drawing = svg2rlg(str(svg_path))
    if not drawing.width or not drawing.height:
        raise ValueError(f"Unable to read SVG dimensions for {svg_path}")

    scale = size / max(drawing.width, drawing.height)
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)

    image = renderPM.drawToPIL(drawing, dpi=72)
    image = image.convert("RGBA")
    image = image.resize((size, size), Image.LANCZOS)
    return image


def convert_svg_to_ico(svg_path: Path, output_dir: Path, sizes: tuple[int, ...] = DEFAULT_SIZES) -> Path:
    """Convert a single SVG file to an ICO file containing multiple sizes."""

    output_dir.mkdir(parents=True, exist_ok=True)
    icon_path = output_dir / f"{svg_path.stem}.ico"

    images = [rasterize_svg(svg_path, size) for size in sizes]
    images[0].save(icon_path, format="ICO", sizes=[(size, size) for size in sizes], save_all=True)
    return icon_path


def convert_folder(folder: Path, output_dir: Path, sizes: tuple[int, ...]) -> list[Path]:
    """Convert all SVG files in a folder to ICO files."""

    svg_files = sorted(folder.glob("*.svg")) + sorted(folder.glob("*.SVG"))
    converted: list[Path] = []
    for svg_file in svg_files:
        converted.append(convert_svg_to_ico(svg_file, output_dir, sizes))
    return converted


def parse_sizes(size_argument: str | None) -> tuple[int, ...]:
    if not size_argument:
        return DEFAULT_SIZES

    sizes = tuple(sorted({int(size) for size in size_argument.split(",") if size.strip()}))
    if not sizes:
        raise ValueError("At least one valid size must be provided.")
    if any(size <= 0 for size in sizes):
        raise ValueError("Icon sizes must be positive integers.")
    return sizes


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert all SVG files in a folder to ICO icons.")
    parser.add_argument(
        "folder",
        type=Path,
        nargs="?",
        default=Path.cwd(),
        help="Folder containing SVG files (default: current directory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output directory for ICO files (default: same as input folder)",
    )
    parser.add_argument(
        "-s",
        "--sizes",
        type=str,
        help="Comma-separated icon sizes to include (default: 16,24,32,48,64,128,256)",
    )

    args = parser.parse_args()
    target_folder = args.folder.resolve()
    output_dir = (args.output or args.folder).resolve()
    sizes = parse_sizes(args.sizes)

    if not target_folder.is_dir():
        raise SystemExit(f"Input folder does not exist: {target_folder}")

    converted = convert_folder(target_folder, output_dir, sizes)

    if converted:
        print("Generated ICO files:")
        for path in converted:
            print(path)
    else:
        print(f"No SVG files found in {target_folder}")


if __name__ == "__main__":
    main()
