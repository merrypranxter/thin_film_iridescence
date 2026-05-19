# Oil Slick

## Physics

An oil slick is a thin layer of petroleum distillate floating on water.
Unlike a soap film (symmetric), the oil–water system has **different** media
on each side — so each interface has a different Fresnel coefficient, and
only the **air–oil** boundary produces a phase inversion.

### Geometry

```
   air      (n = 1.00)
   ──────────────────────────  ← r₁: phase flip (going into denser medium)
   oil       (n ≈ 1.45)
   ──────────────────────────  ← r₂: no phase flip (oil→water, n decreases)
   water    (n = 1.33)
```

The phase condition is therefore **opposite** to a soap film:

- **Constructive**: `2nd cos θ' = mλ`  (m = 0, 1, 2, …)
- **Destructive**:  `2nd cos θ' = (m + ½)λ`

At zero thickness (m = 0) the film is bright rather than black.

### Colour vs Thickness

| Thickness (nm) | Dominant colour |
|----------------|----------------|
| 40–80          | Brown/grey (low OPD) |
| 100–200        | Yellow/green (1st order) |
| 200–300        | Red/magenta    |
| 300–400        | Blue/violet    |
| 400–600        | 2nd-order green–yellow |
| > 600          | Higher orders (pale, mixed) |

### Spreading Dynamics

Oil on water obeys Marangoni spreading: a surface tension gradient drives
outward flow. The leading edge thins; fingering instability produces an
irregular boundary. A fresh slick shows vivid colours near the spreading
front (thin film) and more muted, higher-order colours near the origin
(thicker deposit).

### Shader Notes — `shaders/_oil_slick.frag`

- Thickness: radial ramp from 600 nm at centre to ≈30 nm at edge
- Fingering: sinusoidal perturbation on the boundary angle
- Cosine-law angle variation with radial distance from centre
- Water background rendered separately; oil mask blended on top
- Specular highlight from petroleum surface (warm tint)

## Environmental Note

Oil on water absorbs more green–UV sunlight than oil on other substrates.
The **rainbow sheen** is often the only visible indicator of a thin film
too optically thin to detect by eye.

## References

- Lissant, K.J. (1974). *Emulsions and Emulsion Technology*. Marcel Dekker.
- Hoult, D.I. (1972). Oil spreading on the sea. *Ann. Rev. Fluid Mech.* 4, 341-368.
