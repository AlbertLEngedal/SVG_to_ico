# SVG to ICO Converter

A simple script to convert all SVG files in a folder into Windows-compatible `.ico` files. Icons include multiple common sizes suitable for Windows 11 File Explorer.

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Usage

Run the converter against a folder containing SVG files:

```bash
python convert_svg_to_ico.py /path/to/svg/folder
```

By default, ICO files are created in the same folder as the SVGs and contain sizes 16, 24, 32, 48, 64, 128, and 256 pixels. You can customize options:

- Choose an output folder:

  ```bash
  python convert_svg_to_ico.py /path/to/svg/folder --output /path/to/output
  ```

- Specify sizes (comma-separated):

  ```bash
  python convert_svg_to_ico.py /path/to/svg/folder --sizes 32,64,128
  ```

The script reports the paths of all generated `.ico` files.
