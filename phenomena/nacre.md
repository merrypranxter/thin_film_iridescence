# Nacre (Mother-of-Pearl)

## Physics

Nacre is a biological composite produced by molluscs as the inner lining of
their shells. It achieves its characteristic **lustrous iridescence** through
multi-layer interference in a precisely ordered brick-and-mortar
microarchitecture of aragonite platelets.

### Microstructure

```
   ══════════════════════  aragonite platelet  (d ≈ 500 nm, n ≈ 1.59)
   ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  organic matrix      (d ≈ 30 nm,  n ≈ 1.35)
   ══════════════════════  aragonite platelet
   ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  organic matrix
        ⋮   (5–20 bilayers)
```

Platelets are laterally staggered — the classic **brick-and-mortar**
arrangement. Each platelet is a single crystal of aragonite (CaCO₃) with
its c-axis perpendicular to the layer plane.

### Optical Path Difference

For a single bilayer period Λ = d_ara + d_org:

```
OPD = 2 (n_ara d_ara + n_org d_org) cos θ'
    ≈ 2 (1.59 × 500 + 1.35 × 30) cos θ'
    ≈ 2 × 835.5 nm × cos θ'
    ≈ 1671 cos θ'  nm
```

Peak constructive wavelength (1st order): **λ_peak ≈ 1671 / 1 ≈ 560 nm**
(yellow-green at normal incidence) — consistent with the warm gold–green
luster of most nacre.

### Why Nacre Looks Different from Beetle

1. **Lower index contrast** (1.59 vs 1.35 vs beetle's 1.56/1.0): fewer
   Fabry–Perot fringes, broader spectral peak → milky, not metallic.
2. **Diffuse scatter**: the organic matrix and platelet boundaries scatter
   ~10–15% of light isotropically, lifting the blacks and desaturating.
3. **Platelet variation**: random ±30 nm thickness variation per platelet
   blends nearby interference orders, further softening the colour.

### Birefringence

Aragonite is **birefringent** (nₑ = 1.686, n₀ = 1.530). Under polarised
light nacre shows a characteristic extinction pattern. The shader uses the
isotropic average n ≈ 1.59 (close to n₀).

### Shader Notes — `shaders/_nacre.frag`

- 8-bilayer coherent sum (approximate transfer matrix)
- Per-platelet thickness variation via 2-D hash lookup
- Staggered brick rows with organic joint seams
- Diffuse scatter mixed in (~12%) for creamy luster
- Semi-glossy specular: cool-tinted highlight

## References

- Mayer, G. (2005). Rigid biological systems as models for synthetic composites.
  *Science* 310, 1144-1147.
- Nudelman, F. et al. (2006). Nacre biomineralisation: A multi-scale phenomenon.
  *J. Struct. Biol.* 153, 176-187.
- Shawkey, M.D. & Hill, G.E. (2006). Significance of a basal melanin layer to
  production of non-iridescent structural plumage color. *J. Exp. Biol.* 209, 1245-1250.
