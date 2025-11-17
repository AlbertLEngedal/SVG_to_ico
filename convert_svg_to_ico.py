import argparse
from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image


DEFAULT_SIZES = (16, 24, 32, 48, 64, 128, 256)


def convert_svg_to_ico(svg_path: Path, output_dir: Path, sizes: tuple[int, ...] = DEFAULT_SIZES) -> Path:
    """Convert a single SVG file to an ICO file containing multiple sizes.

    Args:
        svg_path: Path to the source SVG file.
        output_dir: Directory where the resulting ICO file will be written.
        sizes: Sequence of square icon sizes (in pixels) to embed in the ICO.

    Returns:
        Path to the generated ICO file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    largest_size = max(sizes)

    png_bytes = cairosvg.svg2png(url=str(svg_path), output_width=largest_size, output_height=largest_size)

    icon_path = output_dir / f"{svg_path.stem}.ico"
    with Image.open(BytesIO(png_bytes)) as image:
        image = image.convert("RGBA")
        icon_sizes = [(size, size) for size in sizes]
        image.save(icon_path, format="ICO", sizes=icon_sizes)

    return icon_path


def convert_folder(folder: Path, output_dir: Path, sizes: tuple[int, ...]) -> list[Path]:
    """Convert all SVG files in a folder to ICO files.

    Args:
        folder: Folder to search for SVG files.
        output_dir: Directory to place generated ICO files.
        sizes: Sequence of icon sizes to embed.

    Returns:
        List of paths to generated ICO files.
    """
    svg_files = sorted(folder.glob("*.svg"))
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
    return sizes


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert all SVG files in a folder to ICO icons.")
    parser.add_argument("folder", type=Path, nargs="?", default=Path.cwd(), help="Folder containing SVG files (default: current directory)")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output directory for ICO files (default: same as input folder)")
    parser.add_argument("-s", "--sizes", type=str, help="Comma-separated icon sizes to include (default: 16,24,32,48,64,128,256)")

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
