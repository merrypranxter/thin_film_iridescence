"""
films/thickness_maps.py
Generate thickness maps for thin-film interference phenomena.

Each function returns a 2-D NumPy array of film thickness in nm,
suitable for feeding into the spectral pipeline in spectra/wavelength.py.
"""

import numpy as np


def soap_film_map(width: int = 512, height: int = 512,
                  t: float = 0.0) -> np.ndarray:
    """Draining soap film: thick at top, thin at bottom.

    Gravity pulls liquid downward; drainage rate is proportional to
    local film thickness (lubrication approximation).

    Returns (height, width) array of thickness in nm.
    """
    x = np.linspace(0.0, 1.0, width)
    y = np.linspace(1.0, 0.0, height)   # y=1 at top, y=0 at bottom
    X, Y = np.meshgrid(x, y)

    base  = 1500.0
    drain = 1200.0 * (1.0 - Y)

    wave  = (np.sin(X * 20.0 + t * 0.5) * 50.0 +
             np.sin(X *  7.0 - t * 0.3) * 80.0)

    curve = np.sqrt((X - 0.5) ** 2 + (Y - 0.5) ** 2) * 100.0
    rings = np.sin(curve * 5.0) * 30.0

    d = base - drain + wave + rings
    return np.clip(d, 50.0, None)


def oil_slick_map(width: int = 512, height: int = 512,
                  t: float = 0.0) -> np.ndarray:
    """Oil spreading on water: thick centre, thin irregular edges.

    Models a radially-spreading slick with fingering instability.

    Returns (height, width) array of thickness in nm.
    """
    x = np.linspace(0.0, 1.0, width)
    y = np.linspace(0.0, 1.0, height)
    X, Y = np.meshgrid(x, y)

    dist  = np.sqrt((X - 0.5) ** 2 + (Y - 0.5) ** 2)
    spread = 0.3 + t * 0.02

    base = 600.0 * (1.0 - np.clip(dist / spread, 0.0, 1.0) ** 0.5)

    angle = np.arctan2(Y - 0.5, X - 0.5)
    rng = np.random.default_rng(42)
    noise = rng.random((8,))
    fingers = np.zeros_like(angle)
    for k in range(8):
        fingers += np.sin(angle * (k + 3) + noise[k] * 10.0) * 15.0
    fingers *= np.clip((dist - spread * 0.5) / (spread * 0.5), 0.0, 1.0)
    base += fingers

    return np.clip(base, 30.0, None)


def nacre_map(width: int = 512, height: int = 512,
              t: float = 0.0) -> np.ndarray:
    """Nacre platelet thickness variation (aragonite layer only).

    Staggered brick-and-mortar microstructure: each platelet has a
    slightly different thickness, modulated by slow growth-layer waves.

    Returns (height, width) array of thickness in nm.
    """
    x = np.linspace(0.0, 1.0, width)
    y = np.linspace(0.0, 1.0, height)
    X, Y = np.meshgrid(x, y)

    # Staggered row offset
    row   = np.floor(Y * 20.0)
    offset = (row % 2) * 0.5
    cell_x = np.floor((X + offset) * 12.0)

    rng = np.random.default_rng(0)
    platelet_noise = rng.uniform(-30.0, 30.0, size=(20, 12))
    # Vectorised lookup (clip indices to valid range)
    row_idx  = np.clip(row.astype(int),   0, 19)
    cell_idx = np.clip(cell_x.astype(int), 0, 11)
    d_var = platelet_noise[row_idx, cell_idx]

    wave = (np.sin(X * 8.0 + t * 0.1) * 20.0 +
            np.sin(Y * 5.0 - t * 0.07) * 15.0)

    d = 490.0 + wave + d_var
    return np.clip(d, 400.0, 600.0)


if __name__ == "__main__":
    import importlib.util, sys, pathlib
    # Try to import spectrum pipeline for a quick colour preview
    spec_path = pathlib.Path(__file__).parent.parent / "spectra" / "wavelength.py"
    spec = importlib.util.spec_from_file_location("wavelength", spec_path)
    wl   = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wl)

    lam = np.arange(380.0, 781.0, 5.0)
    print("Soap film colour at three vertical positions:")
    for frac in [0.9, 0.5, 0.1]:
        # sample centre column at this fractional height
        d_map = soap_film_map(t=0.0)
        row   = int((1.0 - frac) * 511)
        d     = d_map[row, 256]
        R     = wl.thin_film_reflectance(lam, d, n=1.33)
        rgb   = wl.spectrum_to_srgb(R, lam)
        print(f"  y={frac:.1f}  d={d:.0f}nm  sRGB=({rgb[0]:.3f}, {rgb[1]:.3f}, {rgb[2]:.3f})")
