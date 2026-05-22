// FILM: Anti-reflection coating — MgF₂ on borosilicate glass
// THICKNESS: ~99.6 nm (quarter-wave for λ₀=550 nm)
// INDEX: n_MgF₂ = 1.38, n_glass = 1.52, n_air = 1.00
// PHENOMENON: Destructive interference suppresses green reflection;
//             residual purple/violet bloom is the trademark of coated optics.
//
// Left half: uncoated glass (plain Fresnel, ~4.3% reflection, neutral)
// Right half: AR-coated glass (< 0.5% at 550 nm, purple bloom)

precision highp float;

uniform vec2 u_resolution;
uniform float u_time;

// ── CIE 1931 XYZ pipeline ──

vec3 wavelength_to_XYZ(float lambda) {
    float t1 = (lambda - 442.0) * ((lambda < 442.0) ? 0.0624 : 0.0374);
    float t2 = (lambda - 599.8) * ((lambda < 599.8) ? 0.0264 : 0.0323);
    float t3 = (lambda - 501.1) * ((lambda < 501.1) ? 0.0490 : 0.0382);
    float X  = 0.362 * exp(-0.5 * t1 * t1)
             + 1.056 * exp(-0.5 * t2 * t2)
             - 0.065 * exp(-0.5 * t3 * t3);
    float t4 = (lambda - 568.8) * ((lambda < 568.8) ? 0.0213 : 0.0247);
    float t5 = (lambda - 530.9) * ((lambda < 530.9) ? 0.0613 : 0.0322);
    float Y  = 0.821 * exp(-0.5 * t4 * t4)
             + 0.286 * exp(-0.5 * t5 * t5);
    float t6 = (lambda - 437.0) * ((lambda < 437.0) ? 0.0845 : 0.0278);
    float t7 = (lambda - 459.0) * ((lambda < 459.0) ? 0.0385 : 0.0725);
    float Z  = 1.217 * exp(-0.5 * t6 * t6)
             + 0.681 * exp(-0.5 * t7 * t7);
    return vec3(X, Y, Z);
}

vec3 XYZ_to_sRGB(vec3 XYZ) {
    mat3 M = mat3(
         3.2406, -0.9689,  0.0557,
        -1.5372,  1.8758, -0.2040,
        -0.4986,  0.0415,  1.0570
    );
    return M * XYZ;
}

vec3 linear_to_sRGB(vec3 c) {
    vec3 lo = 12.92 * c;
    vec3 hi = 1.055 * pow(max(c, vec3(0.0)), vec3(1.0 / 2.4)) - 0.055;
    return clamp(mix(lo, hi, step(vec3(0.0031308), c)), 0.0, 1.0);
}

// ── Single-layer reflectance (exact two-beam formula) ──
//
// For n₀→n₁→n₂ stack, amplitude reflectance:
//   r = (r₁₂ + r₂₃ · e^{2iδ}) / (1 + r₁₂·r₂₃ · e^{2iδ})
//   δ = 2π n₁ d cos(θ₁) / λ
//
// Both air→MgF₂ and MgF₂→glass go lower-to-higher index,
// so r₁₂ < 0 and r₂₃ < 0.  Both reflections carry a π phase flip.
// Destructive at δ = π/2  ⟺  d = λ₀/(4 n₁).

float ar_reflectance(float lambda, float d, float n1, float n2, float theta_i) {
    const float PI = 3.14159265;
    float n0 = 1.0;  // air

    // Snell's law into the coating
    float sin1 = sin(theta_i) / n1;
    float cos1 = sqrt(max(0.0, 1.0 - sin1 * sin1));
    float sin2 = sin(theta_i) / n2;
    float cos2 = sqrt(max(0.0, 1.0 - sin2 * sin2));
    float cos0 = cos(theta_i);

    // Fresnel amplitude coefficients (s-polarization)
    float r12 = (n0 * cos0 - n1 * cos1) / (n0 * cos0 + n1 * cos1);
    float r23 = (n1 * cos1 - n2 * cos2) / (n1 * cos1 + n2 * cos2);

    float delta = 2.0 * PI * n1 * d * cos1 / lambda;
    float cos2d = cos(2.0 * delta);
    float sin2d = sin(2.0 * delta);

    // |r|² from exact formula
    float re_num = r12 + r23 * cos2d;
    float im_num =       r23 * sin2d;
    float re_den = 1.0 + r12 * r23 * cos2d;
    float im_den =       r12 * r23 * sin2d;

    float R = (re_num * re_num + im_num * im_num) /
              (re_den * re_den + im_den * im_den);
    return clamp(R, 0.0, 1.0);
}

float bare_glass_reflectance(float n_glass, float theta_i) {
    float n0  = 1.0;
    float cos0 = cos(theta_i);
    float sin1 = sin(theta_i) / n_glass;
    float cos1 = sqrt(max(0.0, 1.0 - sin1 * sin1));
    float rs = (n0 * cos0 - n_glass * cos1) / (n0 * cos0 + n_glass * cos1);
    return rs * rs;
}

// ── Lens SDF helpers ──

float sdCircle(vec2 p, float r) { return length(p) - r; }

float sdLens(vec2 p) {
    float outer = sdCircle(p, 0.38);
    float inner = sdCircle(p - vec2(0.0, 0.62), 0.70);
    return max(outer, -inner);
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;
    st.x *= u_resolution.x / u_resolution.y;
    vec2 p = st - vec2(0.5 * u_resolution.x / u_resolution.y, 0.5);

    // Dark scene background
    vec3 col = vec3(0.02, 0.02, 0.03);

    float lens_dist = sdLens(p);
    bool on_lens = lens_dist < 0.0;

    if (on_lens) {
        // Viewing angle increases toward lens edge
        float theta = clamp(length(p) * 1.8, 0.0, 1.2);

        // MgF₂ coating: n=1.38, d≈99.6 nm (quarter-wave at 550 nm)
        float n_mgf2  = 1.38;
        float n_glass = 1.52;
        float d_qw    = 550.0 / (4.0 * n_mgf2);  // 99.64 nm

        // Divide left/right by screen centre
        bool is_coated = (p.x > 0.0);

        const float STEP  = 10.0;
        const float WHITE_Y = 40.1;  // ∫ Y dλ at step=10, 380–780

        vec3 XYZ = vec3(0.0);
        for (float lambda = 380.0; lambda <= 780.0; lambda += STEP) {
            float R;
            if (is_coated) {
                R = ar_reflectance(lambda, d_qw, n_mgf2, n_glass, theta);
            } else {
                R = bare_glass_reflectance(n_glass, theta);
            }
            XYZ += wavelength_to_XYZ(lambda) * R * STEP;
        }
        XYZ /= WHITE_Y;

        vec3 reflection_col = linear_to_sRGB(XYZ_to_sRGB(XYZ));

        // Glass body: deep teal/grey, slightly transparent
        vec3 glass_body = vec3(0.04, 0.06, 0.09)
                        + reflection_col * (is_coated ? 1.5 : 3.0);

        col = glass_body;

        // Rim highlight — glass edge catches light
        float rim = smoothstep(-0.01, 0.0, lens_dist + 0.01);
        col = mix(col, vec3(0.6, 0.65, 0.7), rim * 0.6);

        // Dividing line between coated and bare halves
        float divider = smoothstep(0.004, 0.0, abs(p.x));
        col = mix(col, vec3(0.15), divider);
    }

    // Labels (encoded as two faint rectangular regions for uncoated/coated)
    float label_bare   = smoothstep(0.003, 0.0, abs(p.x + 0.20) - 0.14)
                       * smoothstep(0.003, 0.0, abs(p.y + 0.44) - 0.03);
    float label_coated = smoothstep(0.003, 0.0, abs(p.x - 0.20) - 0.14)
                       * smoothstep(0.003, 0.0, abs(p.y + 0.44) - 0.03);
    col += vec3(0.3, 0.3, 0.3) * label_bare;
    col += vec3(0.3, 0.2, 0.4) * label_coated;

    gl_FragColor = vec4(col, 1.0);
}
