// spectra/wavelength.glsl
//
// Shared wavelength utilities for thin-film GLSL shaders.
// Include (or copy) into any fragment shader that needs spectral colour.
//
// All wavelengths in nanometres (nm).  Visible range: 380–780 nm.
//
// Recommended usage pattern (spectral integration loop):
//
//   const float STEP    = 10.0;
//   const float WHITE_Y = 40.1;   // ∫ Y_bar(λ) dλ, 380–780 step=10
//   // WHITE_Y at other steps: step=5→80.2, step=15→26.7, step=20→20.1
//
//   vec3 XYZ = vec3(0.0);
//   for (float lam = 380.0; lam <= 780.0; lam += STEP) {
//       float R = thin_film_reflectance(lam, d, n, cos_theta);
//       XYZ += wavelength_to_XYZ(lam) * R * STEP;
//   }
//   XYZ /= WHITE_Y;   // normalise so perfect white reflector → (1,1,1)
//   vec3 col = linear_to_sRGB(clamp(XYZ_to_sRGB(XYZ), 0.0, 1.0));

// ──────────────────────────────────────────────────────────────────────────────
// CIE 1931 colour-matching functions — Gaussian-mixture approximation
// (Wyman et al. 2013, "Simple Analytic Approximations to the CIE XYZ
//  Color Matching Functions")
// ──────────────────────────────────────────────────────────────────────────────
vec3 wavelength_to_XYZ(float lambda) {
    // X
    float t1 = (lambda - 442.0) * ((lambda < 442.0) ? 0.0624 : 0.0374);
    float t2 = (lambda - 599.8) * ((lambda < 599.8) ? 0.0264 : 0.0323);
    float t3 = (lambda - 501.1) * ((lambda < 501.1) ? 0.0490 : 0.0382);
    float X  = 0.362 * exp(-0.5 * t1 * t1)
             + 1.056 * exp(-0.5 * t2 * t2)
             - 0.065 * exp(-0.5 * t3 * t3);

    // Y
    float t4 = (lambda - 568.8) * ((lambda < 568.8) ? 0.0213 : 0.0247);
    float t5 = (lambda - 530.9) * ((lambda < 530.9) ? 0.0613 : 0.0322);
    float Y  = 0.821 * exp(-0.5 * t4 * t4)
             + 0.286 * exp(-0.5 * t5 * t5);

    // Z
    float t6 = (lambda - 437.0) * ((lambda < 437.0) ? 0.0845 : 0.0278);
    float t7 = (lambda - 459.0) * ((lambda < 459.0) ? 0.0385 : 0.0725);
    float Z  = 1.217 * exp(-0.5 * t6 * t6)
             + 0.681 * exp(-0.5 * t7 * t7);

    return vec3(X, Y, Z);
}

// XYZ D65 → linear sRGB (IEC 61966-2-1)
vec3 XYZ_to_sRGB(vec3 XYZ) {
    mat3 M = mat3(
         3.2406, -0.9689,  0.0557,
        -1.5372,  1.8758, -0.2040,
        -0.4986,  0.0415,  1.0570
    );
    return M * XYZ;
}

// sRGB gamma encoding (IEC 61966-2-1)
vec3 linear_to_sRGB(vec3 linear) {
    vec3 a = 12.92 * linear;
    vec3 b = 1.055 * pow(max(linear, vec3(0.0)), vec3(1.0 / 2.4)) - 0.055;
    return mix(a, b, step(vec3(0.0031308), linear));
}

// ──────────────────────────────────────────────────────────────────────────────
// Fast approximate RGB from wavelength (Gaussian cone-response peaks)
// Suitable for real-time use where colour accuracy is secondary.
// ──────────────────────────────────────────────────────────────────────────────
vec3 wavelength_to_rgb_fast(float lambda) {
    vec3 col;
    col.r = exp(-pow(lambda - 570.0, 2.0) / 2000.0)
          + 0.3 * exp(-pow(lambda - 610.0, 2.0) / 1500.0);
    col.g = exp(-pow(lambda - 545.0, 2.0) / 1500.0);
    col.b = exp(-pow(lambda - 440.0, 2.0) / 1800.0);
    return col;
}

// ──────────────────────────────────────────────────────────────────────────────
// Cauchy dispersion: n(λ) = A + B/λ²   (λ in nm)
//
// Material constants (A, B in nm²):
//   water      (1.3247, 3462.0)   soap film ≈ same
//   oil        (1.433,  6800.0)   mineral oil / petroleum
//   keratin    (1.532,  5890.0)   butterfly wing, bird feather
//
// Usage: float n = cauchy_n(lambda, 1.3247, 3462.0);
// ──────────────────────────────────────────────────────────────────────────────
float cauchy_n(float lambda, float A, float B) {
    return A + B / (lambda * lambda);
}

// ──────────────────────────────────────────────────────────────────────────────
// Two-beam thin-film reflectance
//   lambda    : wavelength (nm)
//   d         : film thickness (nm)
//   n         : film refractive index (use cauchy_n() for dispersive media)
//   cos_theta : cosine of refracted angle inside the film
//
// Phase difference:  delta = 4π n d cos(θ') / λ
// Simplified Fresnel (equal-index media on both sides):
//   r = ((1−n)/(1+n))²
// ──────────────────────────────────────────────────────────────────────────────
float thin_film_reflectance(float lambda, float d, float n, float cos_theta) {
    float delta = 4.0 * 3.14159265 * n * d * cos_theta / lambda;
    float r = pow((1.0 - n) / (1.0 + n), 2.0);
    float num = r + r - 2.0 * r * cos(delta);
    float den = 1.0 + r * r - 2.0 * r * cos(delta);
    return num / den;
}
