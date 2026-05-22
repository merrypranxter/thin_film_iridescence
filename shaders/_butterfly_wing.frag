// FILM: Morpho butterfly wing — keratin lamellae / air multilayer
// THICKNESS: ~70 nm keratin (n=1.56), ~115 nm air gaps per period
// BILAYERS: 5–7 lamellae per ridge ("Christmas tree" arrangement)
// PEAK: ~448 nm (deep blue) at normal incidence — shifts UV at oblique angles
// PHENOMENON: Structural colour, intense saturated blue, stable across viewing cone

precision highp float;

uniform vec2 u_resolution;
uniform float u_time;

// ── CIE 1931 XYZ colour pipeline (Wyman et al. 2013 Gaussian-mixture CMFs) ──

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
    // Column-major GLSL mat3: transposed relative to the row-major matrix
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

// ── Morpho multilayer reflectance (coherent sum over N keratin/air bilayers) ──
//
// Keratin ridges on barbule spines form a "Christmas tree" of lamellae.
// Each lamella: ~70 nm keratin (n=1.56) over ~115 nm air gap.
// Constructive condition: λ_peak = 2(n_k d_k + n_a d_a) ≈ 448 nm at θ=0.
//
// The "Christmas tree" geometry (lamellae at different heights on each ridge)
// averages over a ±5° cone of angles, broadening the angular acceptance and
// making Morpho blue stable across a wider viewing cone than a flat stack.

float morpho_reflectance(float lambda, float d_ker, float d_air,
                          float n_ker, float theta_i) {
    const float PI = 3.14159265;
    float N = 6.0;

    float sin_i  = sin(theta_i);
    float sin_k  = sin_i / n_ker;
    float cos_k  = sqrt(max(0.0, 1.0 - sin_k * sin_k));
    float cos_a  = sqrt(max(0.0, 1.0 - sin_i * sin_i));  // air gaps: n=1

    float phi_ker = 4.0 * PI * n_ker * d_ker * cos_k / lambda;
    float phi_air = 4.0 * PI *         d_air * cos_a / lambda;
    float phi_period = phi_ker + phi_air;

    // Fresnel amplitude at air→keratin interface (s-polarization dominant)
    float r_ak = (cos_a - n_ker * cos_k) / (cos_a + n_ker * cos_k);
    float t2   = 1.0 - r_ak * r_ak;   // power transmittance factor

    float re = 0.0, im = 0.0;
    float amp = abs(r_ak);
    float phase = phi_ker * 0.5;       // half-phase offset at first interface

    for (float k = 0.0; k < 7.0; k++) {
        if (k >= N) break;
        re += amp * cos(phase);
        im += amp * sin(phase);
        phase += phi_period;
        amp  *= abs(r_ak) * t2;        // successive reflections attenuate
    }
    return clamp(re * re + im * im, 0.0, 1.0);
}

// ── Wing microstructure ──

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// Scale tiling with biological imperfection
// Returns (angle_perturbation, scale_edge_mask)
vec2 wing_scale(vec2 uv) {
    // Overlapping imbricated scales (~100µm, but tiled aesthetically)
    vec2 scale_coord = vec2(uv.x * 10.0, uv.y * 14.0 + uv.x * 1.5);
    vec2 cell = floor(scale_coord);
    vec2 local = fract(scale_coord);

    // Each scale is slightly different (biological variation)
    float angle_var = (hash(cell) - 0.5) * 0.25;

    // Scale edge: narrow rim where adjacent scales overlap
    float edge = smoothstep(0.0, 0.06, local.x)  * smoothstep(1.0, 0.94, local.x)
               * smoothstep(0.0, 0.04, local.y)  * smoothstep(1.0, 0.96, local.y);

    return vec2(angle_var, edge);
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;
    st.x *= u_resolution.x / u_resolution.y;
    vec2 uv = st;

    // Wing vein network (coarse scale)
    float vein_a = abs(fract(uv.x * 3.2) - 0.5);
    float vein_b = abs(fract(uv.y * 2.6 + sin(uv.x * 5.0) * 0.12) - 0.5);
    float vein = 1.0 - smoothstep(0.44, 0.50, min(vein_a, vein_b));

    // Scale microstructure
    vec2 scale = wing_scale(uv);
    float angle_var  = scale.x;
    float scale_edge = scale.y;

    // Viewing angle: wing has gentle outward curve from spine
    float theta_base = length(uv - vec2(0.5, 0.5)) * 0.55;
    float theta = theta_base + angle_var;

    // "Christmas tree" broadening: average over a ±0.07 rad cone
    // (simulates lamellae at different heights contributing different path lengths)
    const float STEP = 10.0;
    const float WHITE_Y = 40.1;  // ∫ Y_bar(λ) dλ over 380–780 at step=10

    vec3 XYZ = vec3(0.0);
    for (float lambda = 380.0; lambda <= 780.0; lambda += STEP) {
        float R = 0.0;
        R += morpho_reflectance(lambda, 70.0, 115.0, 1.56, theta - 0.07);
        R += morpho_reflectance(lambda, 70.0, 115.0, 1.56, theta);
        R += morpho_reflectance(lambda, 70.0, 115.0, 1.56, theta + 0.07);
        R /= 3.0;
        XYZ += wavelength_to_XYZ(lambda) * R * STEP;
    }
    XYZ /= WHITE_Y;

    vec3 linear = XYZ_to_sRGB(XYZ);
    vec3 col = linear_to_sRGB(linear);

    // Dark melanin substrate absorbs transmitted light → colours are pure interference
    col *= 0.88 + 0.12 * hash(uv * 300.0 + u_time * 0.01);

    // Scale overlap darkens edges
    col *= 0.65 + 0.35 * scale_edge;

    // Wing veins: dark chitin, slightly warm
    col = mix(col, vec3(0.04, 0.03, 0.02), (1.0 - vein) * 0.92);

    gl_FragColor = vec4(col, 1.0);
}
