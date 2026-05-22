"""
spectra/color_chart.py
Terminal interference colour chart: thickness → sRGB colour.

Prints a table showing which colours appear at each film thickness for a
given material at normal incidence.  Supports ANSI 24-bit colour swatches
in terminals that accept them (most modern terminal emulators).

Usage
-----
    python spectra/color_chart.py                     # soap film (water)
    python spectra/color_chart.py oil                 # oil slick
    python spectra/color_chart.py chitin              # beetle shell
    python spectra/color_chart.py aragonite           # nacre
    python spectra/color_chart.py --step 25           # finer steps
    python spectra/color_chart.py --all               # all materials
    python spectra/color_chart.py --png               # save PNG strip

Available materials:
    water, soap_film, oil, chitin, keratin, aragonite,
    organic_matrix, mgf2, glass_bk7, sio2, tio2
"""

import sys
import argparse
import pathlib
import numpy as np

_here = pathlib.Path(__file__).parent
sys.path.insert(0, str(_here))

from wavelength import spectrum_to_srgb
from dispersion import dispersion_n, thin_film_reflectance_dispersive, MATERIALS

LAM = np.arange(380.0, 781.0, 5.0)
# Precompute XYZ white normalisation (∫ Y_bar dλ)
from wavelength import wavelength_to_XYZ as _xyz
_white_Y = float(np.trapezoid(_xyz(LAM)[:, 1], LAM))


def thickness_to_rgb(d: float, material: str) -> tuple:
    """Return (r, g, b) in [0, 255] for the given thickness and material."""
    R = thin_film_reflectance_dispersive(LAM, d, material)
    rgb = spectrum_to_srgb(R, LAM)
    return tuple(int(np.clip(v * 255, 0, 255)) for v in rgb)


def ansi_swatch(r: int, g: int, b: int, width: int = 4) -> str:
    """Return an ANSI 24-bit colour block string."""
    return f"\x1b[48;2;{r};{g};{b}m{' ' * width}\x1b[0m"


def hex_color(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


_COLOR_NAMES = [
    # (hue range in degrees, saturation threshold, name)
    # Uses a simplified HSL model
]


def color_description(r: int, g: int, b: int) -> str:
    """Rough perceptual colour name from sRGB."""
    rf, gf, bf = r / 255.0, g / 255.0, b / 255.0
    brightness = (rf + gf + bf) / 3.0

    if brightness < 0.10:
        return "black film"
    if brightness > 0.88:
        return "white / high-order"

    hi = max(rf, gf, bf)
    lo = min(rf, gf, bf)
    s = (hi - lo) / (hi + 1e-9)

    if s < 0.12:
        return "grey / silver"

    # Hue
    if hi == rf:
        hue = (gf - bf) / (hi - lo + 1e-9) % 6
    elif hi == gf:
        hue = (bf - rf) / (hi - lo + 1e-9) + 2
    else:
        hue = (rf - gf) / (hi - lo + 1e-9) + 4

    hue_deg = hue * 60.0 % 360.0

    if hue_deg < 20 or hue_deg >= 340:
        return "red"
    if hue_deg < 45:
        return "orange"
    if hue_deg < 70:
        return "yellow"
    if hue_deg < 150:
        return "green"
    if hue_deg < 200:
        return "cyan / teal"
    if hue_deg < 260:
        return "blue"
    if hue_deg < 290:
        return "violet"
    return "magenta / pink"


def print_chart(material: str = 'water', step: int = 50,
                d_min: int = 50, d_max: int = 2000) -> None:
    """Print a terminal interference colour chart."""
    supports_ansi = sys.stdout.isatty()
    entry = MATERIALS.get(material, {})

    print(f"\n── Thin-film interference colours ──────────────────────────────")
    print(f"  Material : {material}")
    if entry:
        print(f"  n(550nm) : {entry.get('n_550', '?'):.3f}")
        print(f"  Model    : {entry.get('notes', '')}")
    print(f"  Range    : {d_min}–{d_max} nm  (step {step} nm)")
    print()

    if supports_ansi:
        header = f"  {'d (nm)':>8}  {'hex':>8}  {'colour':>22}  swatch"
    else:
        header = f"  {'d (nm)':>8}  {'hex':>8}  {'colour':>22}  R    G    B"
    print(header)
    print("  " + "─" * (len(header) - 2))

    for d in range(d_min, d_max + 1, step):
        r, g, b = thickness_to_rgb(float(d), material)
        h = hex_color(r, g, b)
        name = color_description(r, g, b)
        if supports_ansi:
            swatch = ansi_swatch(r, g, b, width=8)
            print(f"  {d:>8}  {h:>8}  {name:>22}  {swatch}")
        else:
            print(f"  {d:>8}  {h:>8}  {name:>22}  {r:3d}  {g:3d}  {b:3d}")


def print_all_charts(step: int = 100) -> None:
    """Print a compact comparison of all materials at key thicknesses."""
    supports_ansi = sys.stdout.isatty()
    thicknesses = [100, 200, 300, 400, 500, 600, 700, 800, 1000, 1500]

    col_w = 10 if supports_ansi else 8
    header = f"  {'d (nm)':>8} " + " ".join(f"{m[:9]:>9}" for m in MATERIALS)
    print(f"\n── All-material comparison (step={step} nm) ──────────────────")
    print(header)
    print("  " + "─" * (len(header) - 2))

    for d in thicknesses:
        row = f"  {d:>8} "
        for mat in MATERIALS:
            r, g, b = thickness_to_rgb(float(d), mat)
            if supports_ansi:
                row += ansi_swatch(r, g, b, width=9)
            else:
                row += f" #{r:02x}{g:02x}{b:02x}"
        print(row)


def save_png(material: str = 'water', filename: str | None = None,
             height: int = 80, width: int = 900,
             d_min: float = 50.0, d_max: float = 2000.0) -> None:
    """Save a horizontal interference colour strip to a PNG file.

    Requires Pillow: pip install pillow
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow not installed. Install with:  pip install pillow")
        return

    if filename is None:
        filename = f"color_chart_{material}.png"

    d_values = np.linspace(d_min, d_max, width)
    pixels = np.zeros((width, 3), dtype=np.uint8)
    for i, d in enumerate(d_values):
        pixels[i] = thickness_to_rgb(d, material)

    # Colour strip
    strip = np.tile(pixels[None, :, :], (height - 16, 1, 1))

    # Tick marks at round thicknesses
    tick_row = np.ones((16, width, 3), dtype=np.uint8) * 30
    for d_tick in range(0, int(d_max) + 1, 200):
        xi = int((d_tick - d_min) / (d_max - d_min) * (width - 1))
        if 0 <= xi < width:
            tick_row[:8, xi] = [200, 200, 200]

    img_data = np.vstack([strip, tick_row])
    img = Image.fromarray(img_data)

    try:
        draw = ImageDraw.Draw(img)
        for d_tick in range(0, int(d_max) + 1, 200):
            xi = int((d_tick - d_min) / (d_max - d_min) * (width - 1))
            if 0 <= xi < width - 20:
                draw.text((xi + 2, height - 14), f"{d_tick}", fill=(180, 180, 180))
    except Exception:
        pass

    img.save(filename)
    print(f"Saved {filename}  ({width}×{height}px, {material}, {d_min:.0f}–{d_max:.0f} nm)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Print a thin-film interference colour chart.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        'material', nargs='?', default='water',
        choices=list(MATERIALS.keys()),
        help='Material name (default: water)',
    )
    parser.add_argument('--step', type=int, default=50,
                        help='Thickness step in nm (default: 50)')
    parser.add_argument('--min', type=int, default=50, dest='d_min',
                        help='Minimum thickness in nm (default: 50)')
    parser.add_argument('--max', type=int, default=2000, dest='d_max',
                        help='Maximum thickness in nm (default: 2000)')
    parser.add_argument('--all', action='store_true',
                        help='Compare all materials side by side')
    parser.add_argument('--png', action='store_true',
                        help='Save a PNG colour strip instead of printing')
    args = parser.parse_args()

    if args.all:
        print_all_charts(step=args.step)
    elif args.png:
        save_png(args.material)
    else:
        print_chart(args.material, step=args.step,
                    d_min=args.d_min, d_max=args.d_max)


if __name__ == "__main__":
    main()
