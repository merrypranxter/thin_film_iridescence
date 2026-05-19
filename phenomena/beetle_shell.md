# Beetle Shell (Structural Colour)

## Physics

Many iridescent beetles — *Chrysochroa*, *Cetonia*, *Hoplia* — achieve their
metallic colour through **multi-layer thin-film interference** in the
exocuticle, not through pigment. The stack of chitin and melanin layers acts
as a biological dielectric mirror.

### Geometry

```
   air           (n = 1.00)
   ────────────────────────── ← epicuticle (waxy, n ≈ 1.4)
   chitin layer  (n ≈ 1.56)   ← high-index layer
   melanin/air   (n ≈ 1.0–2.0) ← low-index layer
   chitin layer  (n ≈ 1.56)
   melanin/air
        ⋮   (5–10 bilayers)
   ────────────────────────── ← procuticle substrate
```

### Bragg Condition (peak reflectance wavelength)

For a periodic stack with bilayer period Λ = d_high + d_low:

```
λ_peak = 2 (n_high d_high + n_low d_low) cos θ'
```

The factor `cos θ'` means the peak shifts to **shorter wavelengths** at
oblique angles — the signature blue-shift of structural colour.

### Transfer Matrix Method

The exact reflectance of an N-layer stack is computed by the
**characteristic matrix** (Heavens 1955):

```
M = ∏ᵢ [ cos δᵢ      -i sin δᵢ / nᵢ ]
       [-i nᵢ sin δᵢ   cos δᵢ        ]
```

where δᵢ = 2π nᵢ dᵢ cos θᵢ / λ.

The shader uses a simplified effective-medium approximation.

### Angle-Dependent Colour

At normal incidence a beetle may appear green (λ_peak ≈ 550 nm).
Tilting by 30° shifts the peak to ~490 nm (blue-green). This is the
**iridescence** — the chromatic angle-dependence that makes structural
colour fundamentally different from pigment.

### Cuticle Microstructure

Real beetle cuticle is not a perfect flat stack. Key features:

- **Helicoidal arrangement** (Bouligand structure) in some species produces
  circular polarisation (Chrysina gloriosa).
- **Micro-pillars** on the surface scatter light at shallow angles, creating
  a matte appearance around the glossy highlights.
- **Segment curvature** changes the effective viewing angle across the body.

### Shader Notes — `shaders/_beetle_shell.frag`

- Three body segments rendered with angular curvature
- Layer thicknesses vary per segment (biological growth variation)
- Hash-based micro-gloss mask for matte/glossy microstructure
- Multilayer reflectance: geometric-mean effective medium (simplified TMM)
- Specular highlight: warm tint (chitin is slightly yellow)

## References

- Vukusic, P. & Sambles, J.R. (2003). Photonic structures in biology. *Nature* 424, 852-855.
- Heavens, O.S. (1955). *Optical Properties of Thin Solid Films*. Butterworths.
- Seago, A.E. et al. (2009). Gold bugs and beyond. *J. R. Soc. Interface* 6 S165-S184.
