# thin_film_iridescence

A creative coding project exploring thin-film interference, structural colour,
and the physics of iridescence.

## What This Is

The most vivid colours in nature are not pigment — they are **physics**.  Light
trapped between two surfaces, escaping in phase or out of phase, encoding the
thickness of the film that held it.  Soap bubbles, oil slicks, beetle shells,
Morpho butterfly wings, coated camera lenses: all interference, all
measurable, all beautiful.

This project renders interference phenomena with actual wavelength-based
colour.  The spectral pipeline integrates the CIE 1931 colour-matching
functions and converts through XYZ → linear sRGB → gamma-encoded sRGB, so
the colours are physically meaningful, not palette-painted.

---

## Project Structure

```
shaders/          # GLSL fragment shaders — one per phenomenon
  _soap_film.frag       draining soap film, gravity-driven colour flow
  _oil_slick.frag       petroleum on water, spreading topology
  _beetle_shell.frag    multi-layer chitin/air stack, metallic iridescence
  _nacre.frag           brick-and-mortar aragonite, diffuse luster
  _butterfly_wing.frag  Morpho lamellae, intense structural blue
  _ar_coating.frag      MgF₂ anti-reflection coating, purple bloom

films/            # Thickness maps and material data
  refractive_indices.md   n(λ) values, Cauchy / Sellmeier coefficients
  thickness_maps.py       Python: 2-D thickness arrays for all phenomena

phenomena/        # Physics notes for each interference phenomenon
  soap_film.md
  oil_slick.md
  beetle_shell.md
  nacre.md
  butterfly_wing.md
  ar_coating.md

spectra/          # Wavelength-to-colour pipelines
  wavelength.glsl     GLSL include: CIE CMFs, XYZ→sRGB, Cauchy dispersion,
                      thin_film_reflectance helper
  wavelength.py       Python reference: spectral integration, sRGB output
  dispersion.py       Cauchy & Sellmeier models for 11 materials
  color_chart.py      Terminal / PNG interference colour chart generator
```

---

## Running

### Shaders

Self-contained GLSL fragment shaders.  Drop into any WebGL environment:

- **[Shadertoy](https://shadertoy.com)** — paste the shader, set
  `iResolution → u_resolution` and `iTime → u_time`.
- **[glslViewer](https://github.com/patriciogonzalezvivo/glslViewer)** —
  `glslViewer shaders/_soap_film.frag -w 800 -h 600`
- **Three.js ShaderMaterial** — pass the source as `fragmentShader`.

The newer shaders (`_butterfly_wing.frag`, `_ar_coating.frag`) embed the
full CIE XYZ pipeline inline.  Older shaders (`_soap_film.frag`, etc.) use
the fast Gaussian RGB approximation and are suitable for real-time use.

### Python spectral pipeline

```bash
pip install numpy
python spectra/wavelength.py          # thickness → sRGB table
python spectra/dispersion.py          # constant-n vs dispersive comparison
python films/thickness_maps.py        # soap film colours at three heights
```

### Interference colour chart

```bash
python spectra/color_chart.py                   # soap film, 50–2000 nm
python spectra/color_chart.py oil               # oil slick colours
python spectra/color_chart.py chitin --step 25  # beetle, finer steps
python spectra/color_chart.py --all             # all materials side-by-side
python spectra/color_chart.py --png             # save PNG strip (needs Pillow)
```

The chart uses ANSI 24-bit colour codes for terminal swatches where
supported, and falls back to hex + RGB values.

---

## Physics Summary

### Constructive / Destructive Interference

Light reflecting from the top and bottom surfaces of a thin film travels
different path lengths.  The round-trip **optical path difference** (OPD) is:

```
OPD = 2 n d cos θ'
```

- `n` = film refractive index
- `d` = local film thickness
- `θ'` = refraction angle inside film: `sin θ' = sin θ / n`

Add or subtract a half-wavelength **phase flip** for each interface that
crosses from a lower to a higher refractive index.

### Phase Flips and Colour Sequence

The phase flip determines whether a thin film is bright or dark at zero
thickness:

| System          | Air↔film | Film↔substrate | Zero-thickness | Example           |
|-----------------|----------|----------------|----------------|-------------------|
| Soap film       | flip     | no flip        | **black**      | soap bubble       |
| Oil on water    | flip     | no flip        | **bright**     | oil slick         |
| AR coating      | flip     | flip           | **bright**     | MgF₂ on glass     |
| Butterfly wing  | flip     | flip (melanin) | complex        | Morpho scales     |

### Constructive Interference (soap film)

```
Constructive: 2nd cos θ' = (m + ½)λ
Destructive:  2nd cos θ' = mλ          (m = 0, 1, 2, …)
```

At zero thickness (m=0, d→0): destructive → **black film**.

### Newton's Colour Sequence (soap film draining, n=1.33)

```
Thickness (nm)   Colour
─────────────────────────────
1500 – 2000      High-order white (many orders overlap)
   ~ 550         1st-order green
   ~ 400         1st-order violet
   ~ 180         1st-order yellow
  < 50           Black film (destructive, no OPD)
```

### Bragg Condition (multilayer structural colour)

For a periodic stack (bilayer period Λ = d_high + d_low):

```
λ_peak = 2 (n_high d_high + n_low d_low) cos θ'
```

The `cos θ'` factor causes a **blue-shift at oblique angles** — the
hallmark of structural colour vs. pigment.

| Material      | n_high d_high  | n_low d_low    | λ_peak (θ=0)  |
|---------------|----------------|----------------|---------------|
| Beetle chitin | 1.56 × 120 nm  | 1.00 × 80 nm   | 534 nm (green)|
| Morpho keratin| 1.56 × 70 nm   | 1.00 × 115 nm  | 448 nm (blue) |
| Nacre         | 1.59 × 490 nm  | 1.35 × 28 nm   | 1634 nm (IR!) |

Nacre's OPD is well into the infrared for a single bilayer — but with 8–20
layers the coherent sum creates a broad visible reflection band.

---

## Phenomena

### Soap Film
Single water layer (n=1.33) between air.  Half-wave loss at top surface
causes black film at zero thickness.  Gravity drains liquid downward;
colours cycle from high-order white (top) to black (bottom) as the film
thins.  See `phenomena/soap_film.md`.

### Oil Slick
Petroleum (n≈1.45) floating on water (n=1.33).  Both interfaces go
lower→higher index, so two phase flips cancel and the sequence is opposite
to soap film (bright at zero thickness).  Spreading Marangoni dynamics
produce a radial thickness gradient.  See `phenomena/oil_slick.md`.

### Beetle Shell
Chitin/melanin multi-layer stack (n_chitin=1.56, n_melanin≈2.0).  5–10
bilayers produce metallic, angle-dependent structural colour.  The shader
uses a geometric-mean effective-medium approximation.  See
`phenomena/beetle_shell.md`.

### Nacre (Mother-of-Pearl)
Brick-and-mortar aragonite (n=1.59) / organic matrix (n=1.35).  Low
index contrast → broad, weak spectral peak → soft milky luster rather than
metallic flash.  Per-platelet thickness variation desaturates further.  See
`phenomena/nacre.md`.

### Morpho Butterfly Wing *(new)*
Keratin lamellae (n=1.56, 70 nm) over air gaps (115 nm), 5–7 bilayers per
ridge.  Peak constructive at **~448 nm (deep blue)**.  The "Christmas tree"
arrangement of lamellae at different heights averages over a ±7° cone,
making Morpho blue stable across a wide viewing angle.  Melanin substrate
absorbs all transmitted light so the colour is purely interference.  See
`phenomena/butterfly_wing.md`.

### Anti-Reflection Coating *(new)*
MgF₂ (n=1.38, d≈99.6 nm) on borosilicate glass (n=1.52).  Quarter-wave
condition destructively cancels green (550 nm) reflection.  Residual purple
bloom = blues + reds not fully cancelled.  Split-screen shader shows bare
vs. coated glass side-by-side.  See `phenomena/ar_coating.md`.

---

## Colour Pipeline

### GLSL (shaders)

The file `spectra/wavelength.glsl` provides:
- `wavelength_to_XYZ(float lambda)` — CIE 1931 CMFs (Wyman et al. 2013)
- `XYZ_to_sRGB(vec3 XYZ)` — IEC 61966-2-1 D65 matrix
- `linear_to_sRGB(vec3 c)` — gamma encoding
- `cauchy_n(float lambda, float A, float B)` — Cauchy dispersion
- `thin_film_reflectance(float lambda, float d, float n, float cos_theta)`
- `wavelength_to_rgb_fast(float lambda)` — fast Gaussian approximation

Include pattern (integration loop):

```glsl
const float STEP    = 10.0;
const float WHITE_Y = 40.1;   // ∫ Y_bar(λ) dλ at step=10 over 380–780

vec3 XYZ = vec3(0.0);
for (float lam = 380.0; lam <= 780.0; lam += STEP) {
    float n     = cauchy_n(lam, 1.3247, 3462.0);   // dispersive water
    float cos_t = sqrt(max(0.0, 1.0 - pow(sin(theta)/n, 2.0)));
    float R     = thin_film_reflectance(lam, d, n, cos_t);
    XYZ += wavelength_to_XYZ(lam) * R * STEP;
}
XYZ /= WHITE_Y;
vec3 col = linear_to_sRGB(clamp(XYZ_to_sRGB(XYZ), 0.0, 1.0));
```

### Python (reference / offline)

```python
import numpy as np
from spectra.wavelength import thin_film_reflectance, spectrum_to_srgb
from spectra.dispersion import dispersion_n, thin_film_reflectance_dispersive

lam = np.arange(380.0, 781.0, 5.0)

# Constant-n (fast)
R = thin_film_reflectance(lam, d=300.0, n=1.33)
rgb = spectrum_to_srgb(R, lam)

# Dispersive n(λ) — more accurate at UV/red edges
R_d = thin_film_reflectance_dispersive(lam, d=300.0, material='water')
rgb_d = spectrum_to_srgb(R_d, lam)
```

---

## Example Output

Running `python spectra/wavelength.py`:

```
  Thickness      R       G       B
----------------------------------------
     100nm   0.0023  0.0027  0.0161
     200nm   0.1021  0.0308  0.2024
     300nm   0.4581  0.1073  0.1082
     400nm   0.1534  0.4219  0.1147
     500nm   0.0132  0.3241  0.5022
     600nm   0.1927  0.3156  0.1041
     700nm   0.4502  0.1694  0.0361
     800nm   0.5031  0.4017  0.1589
```

Running `python spectra/color_chart.py oil --step 50`:

```
  d (nm)       hex               colour  swatch
  ──────────────────────────────────────────────
      50    #030507              black film  ████████
     100    #8c7014          orange/yellow  ████████
     150    #6c0b2f            red/magenta  ████████
     200    #231060          violet/purple  ████████
     250    #0b3b8a                   blue  ████████
     300    #0f7b3d                  green  ████████
     ...
```

---

## References

- Newton, I. (1704). *Opticks*.
- Mysels, K.J. et al. (1959). *Soap Films: Studies of Their Thinning*.
- Heavens, O.S. (1955). *Optical Properties of Thin Solid Films*.
- Vukusic, P. & Sambles, J.R. (2003). Photonic structures in biology.
  *Nature* 424, 852-855.
- Kinoshita, S., Yoshioka, S. & Miyazaki, J. (2008). Physics of structural
  colors. *Rep. Prog. Phys.* 71, 076401.
- Wyman, C., Sloan, P-P. & Shirley, P. (2013). Simple Analytic
  Approximations to the CIE XYZ Color Matching Functions.
  *Journal of Computer Graphics Techniques* 2(2).
- Macleod, H.A. (2010). *Thin-Film Optical Filters*, 4th ed.
- Born, M. & Wolf, E. (2019). *Principles of Optics*, 7th ed.
- Daimon, M. & Masumura, A. (2007). Measurement of the refractive index of
  distilled water. *Appl. Opt.* 46, 3811.
- Mayer, G. (2005). Rigid biological systems as models for synthetic
  composites. *Science* 310, 1144-1147.

---

*The colour is a measurement.  The beauty is a side effect.*
