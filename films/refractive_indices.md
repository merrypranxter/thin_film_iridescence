# Refractive Index Data

Refractive indices for materials used in thin-film interference simulations.
Values are at λ = 550 nm unless noted. Dispersion (n varies with λ) is
described by Cauchy or Sellmeier coefficients where available.

---

## Materials

### Water (liquid, 20 °C)
| λ (nm) | n     |
|--------|-------|
| 400    | 1.343 |
| 500    | 1.335 |
| 550    | 1.333 |
| 600    | 1.332 |
| 700    | 1.331 |

Cauchy fit: `n(λ) = 1.3247 + 3462 / λ²`  (λ in nm)

**Used in**: soap film, any aqueous thin film.

---

### Soap film (water + ~0.1% surfactant)
`n ≈ 1.33–1.34` — effectively identical to water for most wavelengths.

**Used in**: `shaders/_soap_film.frag`

---

### Mineral oil / petroleum distillate
`n ≈ 1.44–1.48` (varies with fraction — light naphtha vs heavy fuel oil)

Representative value: **n = 1.45** at 550 nm.

Cauchy: `n(λ) = 1.433 + 6800 / λ²`

**Used in**: `shaders/_oil_slick.frag`

---

### Chitin (insect cuticle)
`n ≈ 1.54–1.58` (dry, at 550 nm)

Sellmeier (Vukusic 2003 approximation):
```
n²(λ) = 1 + 1.03λ² / (λ² − 0.006)    (λ in µm)
```

Representative: **n_chitin = 1.56**

**Used in**: `shaders/_beetle_shell.frag`

---

### Melanin granule (insect)
Absorbing layer — complex index: `ñ = n + ik`
- `n ≈ 1.7–2.0`
- `k ≈ 0.05–0.3` (absorption increases toward UV)

Simplified (non-absorbing): **n_melanin = 2.0**

**Used in**: `shaders/_beetle_shell.frag` (absorption currently ignored)

---

### Aragonite (CaCO₃ orthorhombic — nacre platelets)
`n_e ≈ 1.686`, `n_o ≈ 1.530` (birefringent)

Isotropic average for thin-film model: **n_ara = 1.59**

Sellmeier (ordinary ray, Bragg & Claringbull 1965):
```
n²(λ) = 2.3314 + 0.01224 / (λ² − 0.02390)    (λ in µm)
```

**Used in**: `shaders/_nacre.frag`

---

### Organic matrix (nacre — β-chitin + protein)
`n ≈ 1.35` (measured, Mayer 2005)

**Used in**: `shaders/_nacre.frag`

---

### Keratin (bird feather / butterfly wing)
`n ≈ 1.53–1.56` at 550 nm

Cauchy: `n(λ) = 1.532 + 5890 / λ²`  (λ in nm)

Representative: **n_keratin = 1.556**

Structurally similar to chitin; forms the lamellae in Morpho butterfly wings
and the barbule walls in peacock feathers.

**Used in**: `shaders/_butterfly_wing.frag`

---

### Magnesium Fluoride (MgF₂) — optical coating
`n ≈ 1.38` at 550 nm

Sellmeier (λ in µm):
```
n²(λ) = 1 + 0.48755 λ²/(λ² − 0.001882)
          + 0.38879 λ²/(λ² − 0.008951)
          + 2.31200 λ²/(λ² − 565.934)
```

**Used in**: `shaders/_ar_coating.frag` (AR coating layer)

Quarter-wave thickness for λ₀ = 550 nm:  **d = λ₀/(4n) ≈ 99.6 nm**

---

### Borosilicate Glass (Schott BK7)
`n ≈ 1.519` at 550 nm

Sellmeier (λ in µm):
```
n²(λ) = 1 + 1.03961 λ²/(λ² − 0.0000360)
          + 0.23179 λ²/(λ² − 0.0000400)
          + 1.01047 λ²/(λ² − 10724.7)
```

Standard optical glass. Uncoated surface reflectance (normal incidence):
```
R = ((n−1)/(n+1))² = ((1.519−1)/(1.519+1))² ≈ 4.26%
```

**Used in**: `shaders/_ar_coating.frag` (glass substrate)

---

### Titanium Dioxide (TiO₂, rutile) — high-index coating
`n ≈ 2.35` at 550 nm (varies significantly with deposition method)

High-index layer in multi-layer AR coatings and dielectric mirrors.
Paired with SiO₂ (n ≈ 1.46) for narrow-band optical filters.

---

## Dispersion Data Summary

All materials modelled with Cauchy or Sellmeier equations are available via
`spectra/dispersion.py`:

```python
from spectra.dispersion import dispersion_n
n_chitin_at_450nm = dispersion_n('chitin', 450.0)
n_water_spectrum  = dispersion_n('water', np.arange(380, 781, 5))
```

Materials in the database: `water`, `soap_film`, `oil`, `chitin`,
`keratin`, `aragonite`, `organic_matrix`, `mgf2`, `glass_bk7`, `sio2`,
`tio2`.

---

## Thickness Reference

| Phenomenon              | Typical range     | File                          |
|-------------------------|-------------------|-------------------------------|
| Soap film (black)       | 5–50 nm           | `shaders/_soap_film.frag`     |
| Soap film (white)       | 1 500–2 000 nm    | `shaders/_soap_film.frag`     |
| Oil slick               | 50–800 nm         | `shaders/_oil_slick.frag`     |
| Beetle cuticle          | 80–200 nm/layer   | `shaders/_beetle_shell.frag`  |
| Nacre aragonite         | 400–600 nm        | `shaders/_nacre.frag`         |
| Nacre organic           | 20–40 nm          | `shaders/_nacre.frag`         |
| Morpho keratin lamella  | 60–75 nm          | `shaders/_butterfly_wing.frag`|
| Morpho air gap          | 110–120 nm        | `shaders/_butterfly_wing.frag`|
| MgF₂ AR coating        | ~99.6 nm (λ/4n)   | `shaders/_ar_coating.frag`    |

---

## References

- Vukusic, P. & Sambles, J.R. (2003). Photonic structures in biology. *Nature* 424, 852-855.
- Mayer, G. (2005). Rigid biological systems as models for synthetic composites. *Science* 310, 1144-1147.
- Hecht, E. (2017). *Optics*, 5th ed. Pearson.
- Daimon, M. & Masumura, A. (2007). Measurement of the refractive index of distilled water. *Appl. Opt.* 46, 3811.
- Kinoshita, S., Yoshioka, S. & Miyazaki, J. (2008). Physics of structural colors. *Rep. Prog. Phys.* 71, 076401.
- Macleod, H.A. (2010). *Thin-Film Optical Filters*, 4th ed. CRC Press.
- Ghiradella, H. (1991). Light and colour on the wing. *Appl. Opt.* 30, 3492-3500.
