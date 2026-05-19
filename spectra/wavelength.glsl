// spectra/wavelength.glsl
//
// Shared wavelength utilities for thin-film GLSL shaders.
// Include (or copy) into any fragment shader that needs spectral color.
//
// All wavelengths in nanometres (nm), range 380–780.

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
// Spectral integration helper
// Call inside a for-loop:
//
//   vec3 XYZ = vec3(0.0);
//   for (float lam = 380.0; lam <= 780.0; lam += STEP) {
//       float R = thin_film_reflectance(lam, ...);
//       XYZ += wavelength_to_XYZ(lam) * R;
//   }
//   vec3 col = linear_to_sRGB(clamp(XYZ_to_sRGB(XYZ / NUM_STEPS), 0.0, 1.0));
//
// ──────────────────────────────────────────────────────────────────────────────
