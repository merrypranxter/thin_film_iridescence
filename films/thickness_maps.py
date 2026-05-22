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


def butterfly_wing_map(width: int = 512, height: int = 512) -> np.ndarray:
    """Morpho butterfly wing: per-scale keratin lamella thickness variation.

    Each scale has a slightly different lamella thickness (biological growth
    variation ±5 nm around the nominal 70 nm).

    Returns (height, width) array of keratin layer thickness in nm.
    """
    x = np.linspace(0.0, 1.0, width)
    y = np.linspace(0.0, 1.0, height)
    X, Y = np.meshgrid(x, y)

    # Imbricated scale tiling (~100 µm per scale, scaled aesthetically)
    scale_i = np.clip((X * 20).astype(int), 0, 19)
    scale_j = np.clip((Y * 20).astype(int), 0, 19)

    rng = np.random.default_rng(7)
    per_scale_noise = rng.uniform(-5.0, 5.0, (20, 20))
    d_var = per_scale_noise[scale_j, scale_i]

    d = 70.0 + d_var   # nominal keratin lamella thickness
    return np.clip(d, 55.0, 85.0)


def ar_coating_map(width: int = 512, height: int = 512) -> np.ndarray:
    """Ideal MgF₂ anti-reflection coating: quarter-wave at λ₀ = 550 nm.

    d = λ₀ / (4 n_MgF₂) ≈ 99.6 nm, with a small radial non-uniformity
    typical of physical vapour deposition.

    Returns (height, width) array of coating thickness in nm.
    """
    x = np.linspace(0.0, 1.0, width)
    y = np.linspace(0.0, 1.0, height)
    X, Y = np.meshgrid(x, y)

    d0 = 550.0 / (4.0 * 1.38)   # quarter-wave ≈ 99.64 nm

    # Slight deposition gradient (thicker at centre of vacuum chamber)
    r = np.sqrt((X - 0.5) ** 2 + (Y - 0.5) ** 2)
    gradient = 1.0 + 0.04 * (0.5 - r)

    return d0 * gradient


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
        d_map = soap_film_map(t=0.0)
        row   = int((1.0 - frac) * 511)
        d     = d_map[row, 256]
        R     = wl.thin_film_reflectance(lam, d, n=1.33)
        rgb   = wl.spectrum_to_srgb(R, lam)
        print(f"  y={frac:.1f}  d={d:.0f}nm  sRGB=({rgb[0]:.3f}, {rgb[1]:.3f}, {rgb[2]:.3f})")

    print("\nAR coating — MgF₂ quarter-wave, thickness at centre vs edge:")
    ar_map = ar_coating_map()
    for pos in [(256, 256), (10, 256), (256, 10)]:
        d = ar_map[pos[0], pos[1]]
        label = "centre" if pos == (256, 256) else "edge  "
        print(f"  {label}  d={d:.1f}nm")

    print("\nButterfly wing — per-scale thickness variation (5 samples):")
    bw_map = butterfly_wing_map()
    rng = np.random.default_rng(99)
    for _ in range(5):
        row = rng.integers(0, 512)
        col = rng.integers(0, 512)
        d = bw_map[row, col]
        print(f"  [{row:3d},{col:3d}]  d_keratin={d:.1f}nm")
