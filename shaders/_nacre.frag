// FILM: Nacre (mother-of-pearl) — aragonite platelets in protein matrix
// THICKNESS: ~500nm aragonite (n=1.59), ~30nm organic (n=1.35) per period
// STACK: 5-20 bilayers, total ~3-10µm
// PHENOMENON: Soft iridescent luster, brick-and-mortar microstructure,
//             diffuse scatter + thin-film interference combined

precision highp float;

uniform vec2 u_resolution;
uniform float u_time;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

vec2 hash2(vec2 p) {
    return fract(sin(vec2(dot(p, vec2(127.1, 311.7)),
                         dot(p, vec2(269.5, 183.3)))) * 43758.5453);
}

// Wavelength to approximate sRGB (CIE 1931 Gaussian fit)
// lambda in nm, range 380-780
vec3 wavelength_to_rgb(float lambda) {
    vec3 col = vec3(0.0);
    col.r = exp(-pow(lambda - 570.0, 2.0) / 2000.0)
          + 0.3 * exp(-pow(lambda - 610.0, 2.0) / 1500.0);
    col.g = exp(-pow(lambda - 545.0, 2.0) / 1500.0);
    col.b = exp(-pow(lambda - 440.0, 2.0) / 1800.0);
    return col;
}

// Transfer-matrix method (2-medium periodic stack, N bilayers)
// Approximated as coherent sum of N reflections with accumulated phase.
// Each period: d_ara of aragonite (n_ara), d_org of organic (n_org).
// Returns reflectance for wavelength lambda at cosine of refracted angle.
float nacre_reflectance(float lambda, float d_ara, float d_org,
                        float n_ara, float n_org, float cos_theta_in) {

    // Snell's law into first layer
    float sin_in = sqrt(max(0.0, 1.0 - cos_theta_in * cos_theta_in));
    float sin_ara = sin_in / n_ara;
    float cos_ara = sqrt(max(0.0, 1.0 - sin_ara * sin_ara));
    float sin_org = sin_in / n_org;
    float cos_org = sqrt(max(0.0, 1.0 - sin_org * sin_org));

    // Phase accumulated in each layer per round trip
    float phi_ara = 4.0 * 3.14159265 * n_ara * d_ara * cos_ara / lambda;
    float phi_org = 4.0 * 3.14159265 * n_org * d_org * cos_org / lambda;

    // Fresnel amplitude coefficients (air→ara, ara→org, org→ara cycle)
    float r_air_ara = (1.0 - n_ara) / (1.0 + n_ara);
    float r_ara_org = (n_ara - n_org) / (n_ara + n_org);

    // Intensity reflectances
    float R_top   = r_air_ara * r_air_ara;
    float R_inner = r_ara_org * r_ara_org;

    // Coherent sum over N=8 bilayers (nacre typically 5-20)
    float N = 8.0;
    float phi_period = phi_ara + phi_org;

    // Geometric series of reflections with phase
    // R_total ≈ |Σ r_n exp(i·n·phi)|²  (simplified)
    float real_sum = 0.0;
    float imag_sum = 0.0;
    float amp = sqrt(R_top);
    float propagation = 1.0;
    for (float k = 0.0; k < 10.0; k++) {
        if (k >= N) break;
        float phi = k * phi_period + phi_ara * 0.5;
        real_sum += amp * cos(phi) * propagation;
        imag_sum += amp * sin(phi) * propagation;
        // successive reflections attenuate
        amp *= sqrt(R_inner) * (1.0 - R_top);
        propagation *= (1.0 - R_inner);
    }
    float R = real_sum * real_sum + imag_sum * imag_sum;
    return clamp(R, 0.0, 1.0);
}

// Nacre platelet microstructure: brick-and-mortar tiling
// Returns local thickness perturbation and edge mask
vec2 platelet(vec2 uv) {
    // Staggered rows (brick offset)
    float row = floor(uv.y * 20.0);
    float offset = mod(row, 2.0) * 0.5;
    vec2 cell = vec2(floor((uv.x + offset) * 12.0), row);

    // Random thickness variation per platelet
    float d_var = hash(cell) * 60.0 - 30.0; // ±30 nm

    // Soft edge: organic mortar joints visible as dark seams
    vec2 local = fract(vec2((uv.x + offset) * 12.0, uv.y * 20.0));
    float joint = smoothstep(0.0, 0.08, local.x) * smoothstep(1.0, 0.92, local.x)
                * smoothstep(0.0, 0.10, local.y) * smoothstep(1.0, 0.90, local.y);

    return vec2(d_var, joint);
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;
    st.x *= u_resolution.x / u_resolution.y;

    // Gentle curvature — nacre viewed on a shell interior
    vec2 uv = st;
    float curve_x = (uv.x - 0.5) * (uv.x - 0.5) * 0.4;
    float curve_y = (uv.y - 0.5) * (uv.y - 0.5) * 0.2;

    // Viewing angle increases toward edges (curved shell)
    float theta = sqrt(curve_x + curve_y) * 1.8 + 0.05;
    float cos_theta = cos(theta);

    // Per-platelet microstructure
    vec2 plat = platelet(uv);
    float d_var    = plat.x;
    float joint_mask = plat.y;

    // Base aragonite thickness with slow waviness (growth layers)
    float wave = sin(uv.x * 8.0 + u_time * 0.1) * 20.0
               + sin(uv.y * 5.0 - u_time * 0.07) * 15.0;
    float d_ara = 490.0 + wave + d_var; // nm
    float d_org = 28.0;                 // nm — organic matrix is thin and uniform

    // Spectral integration
    vec3 col = vec3(0.0);
    for (float lambda = 380.0; lambda <= 780.0; lambda += 15.0) {
        float R = nacre_reflectance(lambda, d_ara, d_org, 1.59, 1.35, cos_theta);
        col += wavelength_to_rgb(lambda) * R;
    }

    // Tone map: nacre has soft, milky quality — less saturated than beetle
    col = col / (col + vec3(1.2));
    col = pow(col, vec3(0.88));

    // Diffuse white scatter (aragonite scatters some light isotropically)
    float scatter = 0.12;
    col = mix(col, vec3(dot(col, vec3(0.2126, 0.7152, 0.0722))), scatter);
    col += vec3(scatter * 0.5); // lifted blacks, creamy whites

    // Organic mortar joints: dark seams between platelets
    col *= 0.75 + 0.25 * joint_mask;

    // Subtle specular highlight — nacre is semi-glossy
    float spec = pow(max(cos(theta * 1.5), 0.0), 12.0);
    col += vec3(0.15, 0.15, 0.18) * spec;

    gl_FragColor = vec4(col, 1.0);
}
