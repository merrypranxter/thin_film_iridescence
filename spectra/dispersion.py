"""
spectra/dispersion.py
Wavelength-dependent refractive index: Cauchy and Sellmeier models.

Accurate colour simulation requires n(λ) — a constant refractive index
underestimates the colour spread at thin thicknesses and shifts interference
peaks at the UV/red ends of the spectrum.

Usage
-----
>>> from dispersion import dispersion_n, MATERIALS
>>> n_550 = dispersion_n('water', 550.0)
>>> n_arr = dispersion_n('chitin', np.arange(380, 781, 5))
>>> R = thin_film_reflectance_dispersive(lam, d=300.0, material='oil')
"""

import numpy as np


# ──────────────────────────────────────────────────────────────────────────────
# Dispersion models
# ──────────────────────────────────────────────────────────────────────────────

def cauchy_n(lam_nm, A: float, B: float, C: float = 0.0):
    """Cauchy equation: n(λ) = A + B/λ² + C/λ⁴.

    Parameters
    ----------
    lam_nm : wavelength(s) in nm
    A, B   : Cauchy coefficients; B in nm², C in nm⁴
    """
    lam = np.asarray(lam_nm, dtype=float)
    return A + B / lam ** 2 + C / lam ** 4


def sellmeier_n(lam_um, coeffs: list, base: float = 1.0,
                numerator_has_lam2: bool = True):
    """Sellmeier equation: n²(λ) = base + Σ termᵢ, λ in µm.

    Parameters
    ----------
    lam_um : wavelength(s) in µm
    coeffs : list of (B, C) pairs — Sellmeier oscillator parameters
    base   : constant term in n²(λ)
    numerator_has_lam2 : when True use Bλ²/(λ²−C), else use B/(λ²−C)
    """
    lam = np.asarray(lam_um, dtype=float)
    lam2 = lam ** 2
    n2 = np.full_like(lam2, base, dtype=float)
    for B_i, C_i in coeffs:
        if numerator_has_lam2:
            term = B_i * lam2 / (lam2 - C_i)
        else:
            term = B_i / (lam2 - C_i)
        n2 = n2 + term
    return np.sqrt(np.maximum(n2, 1.0))


# ──────────────────────────────────────────────────────────────────────────────
# Material database
# Each entry: model, params, n_550 (approximate), notes
# ──────────────────────────────────────────────────────────────────────────────

MATERIALS = {
    # ── Thin-film phenomena ──
    'water': {
        'model': 'cauchy',
        'params': {'A': 1.3247, 'B': 3462.0},
        'n_550': 1.333,
        'notes': 'Liquid water 20°C (Daimon & Masumura 2007)',
    },
    'soap_film': {
        'model': 'cauchy',
        'params': {'A': 1.334, 'B': 3100.0},
        'n_550': 1.340,
        'notes': 'Water + ~0.1% surfactant; effectively identical to water',
    },
    'oil': {
        'model': 'cauchy',
        'params': {'A': 1.433, 'B': 6800.0},
        'n_550': 1.455,
        'notes': 'Mineral oil / light petroleum distillate',
    },
    'chitin': {
        'model': 'sellmeier',
        'params': [(1.03, 0.006)],
        'n_550': 1.560,
        'notes': 'Insect cuticle, dry (Vukusic 2003 approximation; λ in µm)',
    },
    'keratin': {
        'model': 'cauchy',
        'params': {'A': 1.532, 'B': 5890.0},
        'n_550': 1.556,
        'notes': 'Bird / butterfly wing keratin (λ in nm)',
    },
    'aragonite': {
        'model': 'sellmeier',
        'params': {
            'coeffs': [(0.01224, 0.0239)],
            'base': 2.3314,
            'numerator_has_lam2': False,
        },
        'n_550': 1.541,
        'notes': 'CaCO₃ orthorhombic, ordinary ray Sellmeier fit (Bragg & Claringbull 1965; λ in µm)',
    },
    'organic_matrix': {
        'model': 'cauchy',
        'params': {'A': 1.340, 'B': 3200.0},
        'n_550': 1.350,
        'notes': 'Nacre β-chitin + protein organic matrix (Mayer 2005)',
    },
    # ── Optical coatings ──
    'mgf2': {
        'model': 'sellmeier',
        'params': [(0.48755108, 0.04338408 ** 2),
                   (0.39875031, 0.09461442 ** 2),
                   (2.31200700, 23.793604  ** 2)],
        'n_550': 1.380,
        'notes': 'Magnesium fluoride — standard single-layer AR coating (λ in µm)',
    },
    'glass_bk7': {
        'model': 'sellmeier',
        'params': [(1.03961212, 0.00600069 ** 2),
                   (0.23179234, 0.02001791 ** 2),
                   (1.01046945, 103.560653 ** 2)],
        'n_550': 1.519,
        'notes': 'Schott BK7 borosilicate (Schott 2014; λ in µm)',
    },
    'sio2': {
        'model': 'sellmeier',
        'params': [(0.6961663, 0.0684043 ** 2),
                   (0.4079426, 0.1162414 ** 2),
                   (0.8974794, 9.896161  ** 2)],
        'n_550': 1.461,
        'notes': 'Fused silica (Malitson 1965; λ in µm)',
    },
    'tio2': {
        'model': 'sellmeier',
        'params': [(5.913, 0.2441 ** 2)],
        'n_550': 2.350,
        'notes': 'Rutile TiO₂ — high-index coating layer (λ in µm)',
    },
}


def dispersion_n(material: str, lam_nm):
    """Return n(λ) for a named material.

    Parameters
    ----------
    material : key in MATERIALS (see keys for available choices)
    lam_nm   : wavelength(s) in nm (scalar or array)

    Returns
    -------
    n scalar or array (same shape as lam_nm)
    """
    if material not in MATERIALS:
        raise ValueError(
            f"Unknown material '{material}'. "
            f"Available: {sorted(MATERIALS.keys())}"
        )
    entry = MATERIALS[material]
    lam = np.asarray(lam_nm, dtype=float)

    if entry['model'] == 'cauchy':
        return cauchy_n(lam, **entry['params'])
    elif entry['model'] == 'sellmeier':
        params = entry['params']
        if isinstance(params, dict):
            return sellmeier_n(lam / 1000.0, **params)
        return sellmeier_n(lam / 1000.0, params)
    else:
        raise ValueError(f"Unknown model '{entry['model']}'")


# ──────────────────────────────────────────────────────────────────────────────
# Dispersive thin-film reflectance
# ──────────────────────────────────────────────────────────────────────────────

def thin_film_reflectance_dispersive(lam, d: float, material: str,
                                      theta_i: float = 0.0):
    """Two-beam thin-film reflectance with wavelength-dependent n(λ).

    Same as wavelength.thin_film_reflectance but n varies with λ via the
    material's Cauchy/Sellmeier model.

    Parameters
    ----------
    lam      : wavelengths (nm), array-like
    d        : film thickness (nm)
    material : key in MATERIALS
    theta_i  : angle of incidence in air (radians)

    Returns
    -------
    R(λ) array
    """
    lam = np.asarray(lam, dtype=float)
    n = dispersion_n(material, lam)

    sin_t = np.sin(theta_i) / n
    cos_t = np.sqrt(np.maximum(1.0 - sin_t ** 2, 0.0))

    delta = 4.0 * np.pi * n * d * cos_t / lam

    r1 = ((1.0 - n) / (1.0 + n)) ** 2
    r2 = ((n - 1.0) / (n + 1.0)) ** 2

    R = (r1 + r2 - 2.0 * np.sqrt(r1 * r2) * np.cos(delta)) / \
        (1.0 + r1 * r2 - 2.0 * np.sqrt(r1 * r2) * np.cos(delta))
    return R


# ──────────────────────────────────────────────────────────────────────────────
# Quick demo
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from wavelength import spectrum_to_srgb, thin_film_reflectance

    lam = np.arange(380.0, 781.0, 5.0)

    print("Dispersive vs constant-n comparison for several materials at d=300 nm")
    print(f"{'material':>16}  {'n(550)':>7}  {'const-n RGB':>20}  {'dispersive RGB':>20}")
    print("-" * 72)

    for mat, entry in MATERIALS.items():
        n0 = entry['n_550']
        R_const = thin_film_reflectance(lam, 300.0, n0)
        rgb_c = spectrum_to_srgb(R_const, lam)

        R_disp = thin_film_reflectance_dispersive(lam, 300.0, mat)
        rgb_d = spectrum_to_srgb(R_disp, lam)

        def fmt(rgb):
            return f"({rgb[0]:.3f},{rgb[1]:.3f},{rgb[2]:.3f})"

        print(f"{mat:>16}  {n0:>7.3f}  {fmt(rgb_c):>20}  {fmt(rgb_d):>20}")
