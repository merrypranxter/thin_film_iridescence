"""
spectra/wavelength.py
Reference implementation: wavelength → XYZ → sRGB colour pipeline.

Uses the Wyman et al. (2013) Gaussian-mixture approximation to the
CIE 1931 2° colour-matching functions (CMFs), then applies the
standard D65 XYZ→sRGB matrix and gamma encoding.

Usage
-----
>>> from wavelength import spectrum_to_srgb, thin_film_spectrum
>>> rgb = spectrum_to_srgb(thin_film_spectrum(d=500, n=1.33))
>>> print(rgb)  # (R, G, B) in [0, 1]
"""

import numpy as np


# ──────────────────────────────────────────────────────────────────────────────
# CIE 1931 CMF approximation (Wyman et al. 2013)
# ──────────────────────────────────────────────────────────────────────────────

def wavelength_to_XYZ(lam: np.ndarray) -> np.ndarray:
    """Return CIE XYZ tristimulus values for wavelengths lam (nm array).

    Shape: (N,) → (N, 3)
    """
    lam = np.asarray(lam, dtype=float)

    def _g(lam, mu, sig1, sig2, amp):
        sig = np.where(lam < mu, sig1, sig2)
        return amp * np.exp(-0.5 * ((lam - mu) / sig) ** 2)

    X = (_g(lam, 442.0, 1/0.0624, 1/0.0374, 0.362) +
         _g(lam, 599.8, 1/0.0264, 1/0.0323, 1.056) +
         _g(lam, 501.1, 1/0.0490, 1/0.0382, -0.065))

    Y = (_g(lam, 568.8, 1/0.0213, 1/0.0247, 0.821) +
         _g(lam, 530.9, 1/0.0613, 1/0.0322, 0.286))

    Z = (_g(lam, 437.0, 1/0.0845, 1/0.0278, 1.217) +
         _g(lam, 459.0, 1/0.0385, 1/0.0725, 0.681))

    return np.stack([X, Y, Z], axis=-1)


# IEC 61966-2-1  XYZ D65 → linear sRGB
XYZ_TO_SRGB = np.array([
    [ 3.2406, -1.5372, -0.4986],
    [-0.9689,  1.8758,  0.0415],
    [ 0.0557, -0.2040,  1.0570],
])


def XYZ_to_linear_sRGB(XYZ: np.ndarray) -> np.ndarray:
    """XYZ (N,3) → linear sRGB (N,3)."""
    return (XYZ_TO_SRGB @ XYZ.T).T


def linear_to_sRGB(linear: np.ndarray) -> np.ndarray:
    """Apply sRGB gamma encoding (IEC 61966-2-1)."""
    linear = np.clip(linear, 0.0, None)
    gamma = np.where(
        linear <= 0.0031308,
        12.92 * linear,
        1.055 * linear ** (1.0 / 2.4) - 0.055,
    )
    return np.clip(gamma, 0.0, 1.0)


def spectrum_to_srgb(reflectance: np.ndarray,
                     lam: np.ndarray | None = None) -> np.ndarray:
    """Integrate a reflectance spectrum into an sRGB colour.

    Parameters
    ----------
    reflectance : (N,) array — reflectance R(λ) at each wavelength
    lam         : (N,) array — wavelengths in nm; defaults to 380–780 step 5

    Returns
    -------
    (3,) array — sRGB colour in [0, 1]
    """
    if lam is None:
        lam = np.arange(380.0, 781.0, 5.0)
    cmf = wavelength_to_XYZ(lam)                    # (N, 3)
    XYZ = np.trapezoid(cmf * reflectance[:, None], lam, axis=0)
    # Normalise so a perfect white (R=1) maps to roughly (1,1,1)
    white_XYZ = np.trapezoid(cmf, lam, axis=0)
    XYZ /= white_XYZ[1]                              # normalise by Y of white
    linear = XYZ_to_linear_sRGB(XYZ[None, :])[0]
    return linear_to_sRGB(linear)


# ──────────────────────────────────────────────────────────────────────────────
# Reference thin-film reflectance (two-beam, equal Fresnel at both interfaces)
# ──────────────────────────────────────────────────────────────────────────────

def thin_film_reflectance(lam: np.ndarray, d: float, n: float,
                          theta_i: float = 0.0) -> np.ndarray:
    """Two-beam thin-film reflectance at normal or oblique incidence.

    Parameters
    ----------
    lam     : wavelengths (nm)
    d       : film thickness (nm)
    n       : film refractive index (real)
    theta_i : angle of incidence in air (radians)

    Returns
    -------
    R(λ) array — reflectance in [0, 1]
    """
    lam = np.asarray(lam, dtype=float)
    sin_t = np.sin(theta_i) / n
    cos_t = np.sqrt(1.0 - sin_t ** 2)

    delta = 4.0 * np.pi * n * d * cos_t / lam   # phase difference

    r1 = ((1.0 - n) / (1.0 + n)) ** 2            # R at air→film
    r2 = ((n - 1.0) / (n + 1.0)) ** 2            # R at film→air

    R = (r1 + r2 - 2.0 * np.sqrt(r1 * r2) * np.cos(delta)) / \
        (1.0 + r1 * r2 - 2.0 * np.sqrt(r1 * r2) * np.cos(delta))
    return R


def thin_film_spectrum(d: float, n: float = 1.33,
                       theta_i: float = 0.0,
                       step: float = 5.0) -> tuple[np.ndarray, np.ndarray]:
    """Return (lam, R) for a soap-like film of thickness d nm."""
    lam = np.arange(380.0, 781.0, step)
    R = thin_film_reflectance(lam, d, n, theta_i)
    return lam, R


# ──────────────────────────────────────────────────────────────────────────────
# Quick demo
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"{'Thickness':>12}  {'R':>6}  {'G':>6}  {'B':>6}")
    print("-" * 40)
    for d in [100, 200, 300, 400, 500, 600, 700, 800]:
        lam, R = thin_film_spectrum(d=d, n=1.33)
        r, g, b = spectrum_to_srgb(R, lam)
        print(f"{d:>10}nm  {r:.4f}  {g:.4f}  {b:.4f}")
