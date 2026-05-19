# Soap Film

## Physics

A soap film is a freestanding sheet of water sandwiched between two surfactant
monolayers. Its optical behaviour is governed by interference between the two
partial reflections at the air–film and film–air interfaces.

### Geometry

```
   air (n=1)
   ──────────────────────────  ← reflection r₁ (phase flip: Δφ = π)
   soap film (n ≈ 1.33)
   ──────────────────────────  ← reflection r₂ (no phase flip)
   air (n=1)
```

Both surfaces have the same index contrast (air↔water), but only the **top**
surface produces a phase inversion on reflection (denser medium below).
This **half-wave loss** shifts the colour sequence relative to an oil-on-water
film (which has index contrast only at one interface).

### Interference Condition

Round-trip optical path difference (OPD):

```
OPD = 2 n d cos θ'
```

- n = film refractive index  
- d = local film thickness  
- θ' = refraction angle inside film (Snell's law: sin θ' = sin θ / n)

Including the π phase flip at the top surface:

- **Destructive** (black film): `2nd cos θ' = mλ`  
- **Constructive** (bright colour): `2nd cos θ' = (m + ½)λ`

### Newton's Colour Sequence

As a film drains from top to bottom, thickness decreases and the colour cycles
through Newton's series (order 1 → 0):

| Thickness (approx., n=1.33) | Colour       |
|-----------------------------|--------------|
| 1 500–2 000 nm              | High-order white |
| ~550 nm                     | 1st-order green  |
| ~400 nm                     | 1st-order violet |
| ~180 nm                     | 1st-order yellow |
| < 50 nm                     | Black film (no OPD, destructive) |

### Drainage Dynamics

Gravity drains liquid downward; the local drain rate scales as d³ (lubrication
approximation). Result: a continuous thickness gradient — thick at the top,
thin black at the bottom. Turbulence adds lateral colour modulation.

### Shader Notes — `shaders/_soap_film.frag`

- Thickness function: gravity ramp + sinusoidal turbulence
- `sdBox` SDF used to frame the film and paint the meniscus
- Spectrum sampled at 20 nm steps, 380–780 nm
- Tone map: Reinhard + γ = 0.85

## References

- Mysels, K.J., Shinoda, K. & Frankel, S. (1959). *Soap Films: Studies of Their
  Thinning*. Pergamon.
- Isenberg, C. (1992). *The Science of Soap Films and Soap Bubbles*. Dover.
