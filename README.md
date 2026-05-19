# thin_film_iridescence

A creative coding project exploring thin-film interference, structural color, and the physics of iridescence.

## What This Is

The most vivid colors in nature are not pigment — they are **physics**. Light trapped between two surfaces, escaping in phase or out of phase, encoding the thickness of the film that held it. Soap bubbles, oil slicks, beetle shells, peacock feathers: all interference, all measurable, all beautiful.

This project renders interference phenomena with actual wavelength-based color, not rainbow gradients.

## Project Structure

```
shaders/          # GLSL fragments — one per phenomenon
films/            # Thickness maps, refractive indices, spectral data
phenomena/        # Soap, oil, beetle, nacre, structural color references
spectra/          # Wavelength-to-RGB conversions, CIE matching
```

## Running

Shaders are self-contained GLSL fragment shaders. Run in any WebGL environment.

## Current Phenomena

- [ ] _soap_film — draining soap, thickness → color flow, gravity-driven dynamics
- [ ] _oil_slick — petroleum on water, thickness topology as hue map
- [ ] _beetle_shell — multi-layer interference, metallic angle-dependent color
- [ ] _nacre — brick-and-mortar microstructure, diffuse luster

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
