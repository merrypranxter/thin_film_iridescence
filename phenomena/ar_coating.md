# Anti-Reflection Coating

## Physics

An anti-reflection (AR) coating is the **engineered inverse** of structural
colour: instead of enhancing reflectance at chosen wavelengths, it
eliminates it. The characteristic **purple bloom** on camera lenses,
telescope eyepieces, and spectacle lenses is AR coating working as designed.

### Geometry

```
   air       (n₀ = 1.00)
   ─────────────────────────  ← r₁₂: phase flip (n₀ → n₁, denser)
   MgF₂ coating  (n₁ = 1.38)
   ─────────────────────────  ← r₂₃: phase flip (n₁ → n₂, denser)
   glass     (n₂ = 1.52)
```

Both interfaces step from a **less dense to a more dense** medium, so both
reflections carry a **π phase inversion**. The two phase flips cancel each
other, and interference behaviour is determined by the optical path alone.

### Quarter-Wave Condition

Destructive interference requires the round-trip optical path in the
coating to equal a half-wavelength:

```
2 n₁ d cos θ₁ = λ/2
→  d = λ₀ / (4 n₁)
```

For green light at λ₀ = 550 nm with MgF₂ (n₁ = 1.38):

```
d = 550 / (4 × 1.38) ≈ 99.6 nm
```

At this thickness, green is almost completely cancelled in reflection.

### Why the Reflected Colour is Purple/Violet

The quarter-wave condition is met **only at λ₀**. At other wavelengths the
cancellation is partial. The reflectance spectrum looks like this:

```
R(λ)  ^
 4% ─ │█              █
      │  ██        ███
 2% ─ │     ██████
 0% ─ └─────────────────────→ λ
       400  500  600  700 nm
             ↑
         deep null at 550 nm
```

Blues (~450 nm) and reds (~650 nm) reflect more than green → the eye sees
their combination: **purple/magenta/violet**, the complement of green.

This is not a failure of the coating; it is the residual after 90%+ of the
green reflectance has been eliminated. Uncoated glass reflects ~4.3% at
normal incidence; a single MgF₂ layer reduces that to **< 0.5%**.

### Perfect Cancellation Condition

For complete destructive interference (zero reflection), the two reflected
amplitudes must be exactly equal:

```
|r₁₂| = |r₂₃|
(n₀ - n₁)/(n₀ + n₁) = (n₁ - n₂)/(n₁ + n₂)
→  n₁ = √(n₀ n₂) = √(1.00 × 1.52) ≈ 1.233
```

No common solid has n ≈ 1.233 (MgF₂ is the closest at 1.38, cryolite at
1.35). Single-layer coatings always leave a small residual — multi-layer
V-coatings achieve < 0.05% with stacked high/low index pairs.

### Angle Dependence

The quarter-wave condition is met at angle θ:

```
d = λ₀ / (4 n₁ cos θ₁)
```

At oblique incidence, cos θ₁ < 1, so the effective quarter-wave wavelength
**shifts to the blue**. A lens that appears purple-bloomed at normal
incidence will look greenish-blue at ~45° — which is why the bloom colour
changes as you tilt a coated lens.

### Multi-Layer Coatings

A V-coat uses two or more layers to achieve near-zero reflection at one
wavelength. A **broad-band AR** coating (as on high-quality camera lenses)
uses 5–9 layers to keep reflectance < 0.25% across 420–680 nm. Each layer
is designed so the multiple partial reflections destructively interfere
across a wide spectral range.

### Exact Reflectance Formula

For a single coating layer (exact two-beam):

```
r = (r₁₂ + r₂₃ e^{2iδ}) / (1 + r₁₂ r₂₃ e^{2iδ})
δ = 2π n₁ d cos θ₁ / λ

R = |r|² = [r₁₂² + r₂₃² + 2r₁₂r₂₃ cos(2δ)] /
           [1 + r₁₂²r₂₃² + 2r₁₂r₂₃ cos(2δ)]
```

At the quarter-wave minimum (2δ = π):

```
R_min = (r₁₂ - r₂₃)² / (1 - r₁₂ r₂₃)²
```

### Shader Notes — `shaders/_ar_coating.frag`

- Split-screen: left half is bare glass, right half is AR-coated MgF₂.
- Uses the exact single-layer amplitude formula (not the simplified
  constructive/destructive approximation).
- Proper CIE XYZ pipeline for colour accuracy.
- Viewing angle increases toward the lens edge, shifting the null wavelength
  blueward — the bloom colour changes across the lens surface.
- n_MgF₂ = 1.38, n_glass = 1.52, d = 99.6 nm.

## References

- Macleod, H.A. (2010). *Thin-Film Optical Filters*, 4th ed. CRC Press.
- Heavens, O.S. (1955). *Optical Properties of Thin Solid Films*. Butterworths.
- Born, M. & Wolf, E. (2019). *Principles of Optics*, 7th ed. Cambridge.
