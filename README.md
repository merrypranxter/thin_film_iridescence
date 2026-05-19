# thin_film_iridescence

A creative coding project exploring thin-film interference, structural color, and the physics of iridescence.

## What This Is

The most vivid colors in nature are not pigment — they are **physics**. Light trapped between two surfaces, escaping in phase or out of phase, encoding the thickness of the film that held it. Soap bubbles, oil slicks, beetle shells, peacock feathers: all interference, all measurable, all beautiful.

This project renders interference phenomena with actual wavelength-based color, not rainbow gradients.

## Project Structure

```
shaders/          # GLSL fragment shaders — one per phenomenon
films/            # Thickness maps, refractive indices, spectral data
  refractive_indices.md   # n values for all materials in use
  thickness_maps.py       # Python: generate 2-D thickness arrays
phenomena/        # Physics notes for each interference phenomenon
  soap_film.md
  oil_slick.md
  beetle_shell.md
  nacre.md
spectra/          # Wavelength-to-colour pipelines
  wavelength.glsl # GLSL include: XYZ CMFs, sRGB conversion helpers
  wavelength.py   # Python reference: spectral integration, sRGB output
```

## Running

Shaders are self-contained GLSL fragment shaders. Run in any WebGL environment
(e.g. [Shadertoy](https://shadertoy.com), [glslViewer](https://github.com/patriciogonzalezvivo/glslViewer),
or a Three.js `ShaderMaterial`).

The GLSL include `spectra/wavelength.glsl` provides accurate CIE 1931 CMFs and
sRGB conversion helpers. Copy or `#include` it into any shader.

The Python reference in `spectra/wavelength.py` reproduces the same colour
pipeline in NumPy for offline validation. Run the thickness-map demos with:

```bash
python films/thickness_maps.py
```

## Current Phenomena

- [x] _soap_film — draining soap, thickness → color flow, gravity-driven dynamics
- [x] _oil_slick — petroleum on water, thickness topology as hue map
- [x] _beetle_shell — multi-layer interference, metallic angle-dependent color
- [x] _nacre — brick-and-mortar microstructure, diffuse luster

## Physics Notes

Constructive interference: `2nd cos(θ') = mλ`
- `n` = refractive index
- `d` = film thickness
- `θ'` = angle in film
- `λ` = wavelength
- `m` = order integer

## References

- Newton, I. (1704). *Opticks*.
- Vukusic, P. & Sambles, J.R. (2003). "Photonic structures in biology." *Nature*, 424, 852-855.

---

*The color is a measurement. The beauty is a side effect.*
