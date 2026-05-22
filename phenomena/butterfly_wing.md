# Morpho Butterfly Wing (Structural Blue)

## Physics

*Morpho rhetenor*, *M. didius*, and related species produce an intense,
saturated blue through **multi-layer thin-film interference** in the
microscopic structure of their wing scales — no blue pigment is involved.

### Microstructure: the "Christmas Tree" Lamellae

Each scale (~100 µm long) is covered by parallel ridges (~2 µm apart).
Every ridge carries a stack of 5–7 thin keratin lamellae that branch away
from a central spine at increasing heights, like a Christmas tree in
cross-section:

```
        ──────   ──────            ← lamella 6  (keratin, ~70 nm)
      ────────────────────         ← air gap     (~115 nm)
       ────     ────               ← lamella 5
      ────────────────────         ← air gap
   ──────       ──────             ← lamella 4
      ────────────────────         ← air gap
          ⋮         ⋮
   ━━━━━━━━━━━━━━━━━━━━━━━━━━      ← central spine (melanin substrate)
```

- Keratin layer: n ≈ 1.56, d ≈ 70 nm
- Air gap:       n = 1.00, d ≈ 115 nm
- Bilayer period: Λ ≈ 185 nm

### Bragg Condition — Peak Wavelength

Constructive interference for a periodic stack:

```
λ_peak = 2 (n_k d_k + n_a d_a) cos θ'
       = 2 (1.56 × 70 + 1.00 × 115) cos θ'
       = 2 × 224.2 × cos θ'
       ≈ 448 nm    at θ' = 0  (normal incidence)
```

448 nm is **deep blue — violet**, exactly matching the vivid Morpho colour.

As the viewing angle increases, the peak shifts toward shorter wavelengths
(UV), causing the wing to darken and eventually appear black: the classic
blue-shift of multi-layer structural colour.

### Why Morpho Blue is Unusually Stable

A simple flat multilayer would show very sharp angle-dependence. The
"Christmas tree" geometry distributes the lamellae at different heights on
each ridge. Rays scattered from different lamellae travel slightly different
path lengths, so the angular response is an **average over a small cone
(±5–8°)**. This broadens the blue peak angularly, making Morpho blue
stable over a wider cone than a flat stack of equal optical depth would be.

This is not a defect but an evolved engineering solution: iridescence is
preserved across typical viewing angles while pigment is entirely absent.

### Melanin Substrate

Below the lamella stack, the barbule contains a dense melanin base layer
(n ≈ 2.0, strongly absorbing). Light that passes through all the keratin
layers without reflecting is absorbed by the melanin rather than
back-scattering diffusely. This keeps the colour pure — without the
melanin, transmitted light would add white scatter and desaturate the blue.

### Comparing to Nacre and Beetle

| Property          | Morpho wing        | Beetle cuticle   | Nacre           |
|-------------------|--------------------|------------------|-----------------|
| High-index layer  | keratin (n=1.56)   | chitin (n=1.56)  | aragonite (n=1.59)|
| Low-index layer   | air (n=1.00)       | air (n=1.00)     | organic (n=1.35)|
| Index contrast    | 0.56 (high)        | 0.56 (high)      | 0.24 (low)      |
| Bilayers          | 5–7                | 5–10             | 5–20            |
| Peak reflectance  | > 70%              | 40–80%           | 10–30%          |
| Luster            | metallic, vivid    | metallic         | soft, milky     |

High index contrast → narrow, intense spectral peak → saturated colour.
Low contrast → broad, weak peak → diffuse iridescent luster.

### Shader Notes — `shaders/_butterfly_wing.frag`

- Uses the proper CIE XYZ pipeline (wavelength_to_XYZ + XYZ_to_sRGB)
  rather than the fast Gaussian RGB approximation used in earlier shaders.
- Morpho reflectance: coherent amplitude sum over N=6 bilayers.
- Angular broadening: average over 3 angles (θ − 0.07, θ, θ + 0.07 rad)
  to simulate Christmas-tree height distribution.
- Wing veins modelled as Voronoi-ish sinusoidal network.
- Scale tiling: imbricated rectangle cells with per-cell angle variation.
- Melanin substrate: darkens the colour base so interference is the only
  light source (no diffuse bleed).

## References

- Vukusic, P., Sambles, J.R., Lawrence, C.R. & Wootton, R.J. (1999).
  Quantified interference and diffraction in single Morpho butterfly scales.
  *Proc. R. Soc. Lond. B* 266, 1403-1411.
- Kinoshita, S., Yoshioka, S. & Miyazaki, J. (2008). Physics of structural
  colors. *Rep. Prog. Phys.* 71, 076401.
- Ghiradella, H. (1991). Light and colour on the wing. *Appl. Opt.* 30,
  3492-3500.
