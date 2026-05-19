// FILM: Single soap film in air, water-glycol mixture
// THICKNESS: 200nm - 2000nm, draining downward
// INDEX: n = 1.33 (water) to 1.35 (glycol mix)
// PHENOMENON: Soap film drainage, thinning from bottom, interference color flow

precision highp float;

uniform vec2 u_resolution;
uniform float u_time;

// Wavelength to RGB approximation (CIE 1931-ish)
vec3 wavelength_to_rgb(float lambda) {
    // lambda in nm, 380-780 range
    vec3 col = vec3(0.0);
    
    // Approximate Gaussian peaks for R, G, B cone responses
    col.r = exp(-pow(lambda - 570.0, 2.0) / 2000.0) + 0.3 * exp(-pow(lambda - 610.0, 2.0) / 1500.0);
    col.g = exp(-pow(lambda - 545.0, 2.0) / 1500.0);
    col.b = exp(-pow(lambda - 440.0, 2.0) / 1800.0);
    
    return col;
}

// Thin-film interference: reflected intensity for wavelength lambda
// d = thickness, n = refractive index, theta = incident angle
float thin_film_reflectance(float lambda, float d, float n, float cos_theta) {
    // Phase difference
    float delta = 4.0 * 3.14159265 * n * d * cos_theta / lambda;
    
    // Fresnel reflectance at air-film interface (simplified, unpolarized)
    float r1 = pow((1.0 - n) / (1.0 + n), 2.0);
    float r2 = pow((n - 1.0) / (n + 1.0), 2.0); // film-air on other side
    
    // Interference
    float R = r1 + r2 + 2.0 * sqrt(r1 * r2) * cos(delta);
    R /= (1.0 + r1 * r2 + 2.0 * sqrt(r1 * r2) * cos(delta));
    
    return R;
}

// Film thickness at position (draining soap film)
float film_thickness(vec2 uv, float time) {
    // Gravity drainage: thicker at top, thinning at bottom
    float base = 1500.0; // nm at top
    float drain = 1200.0 * (1.0 - uv.y); // nm lost at bottom
    
    // Turbulent drainage instability
    float wave = sin(uv.x * 20.0 + time * 0.5) * 50.0;
    wave += sin(uv.x * 7.0 - time * 0.3) * 80.0;
    
    // Thin film "black" at bottom when drained
    float thickness = base - drain + wave;
    
    // Newton's rings: slight curvature
    float curve = length(uv - vec2(0.5, 0.5)) * 100.0;
    thickness += sin(curve * 5.0) * 30.0;
    
    return max(thickness, 50.0); // minimum ~50nm (black film)
}

// Helper: signed distance box
float sdBox(vec2 p, vec2 b) {
    vec2 d = abs(p) - b;
    return length(max(d, 0.0)) + min(max(d.x, d.y), 0.0);
}

vec3 render_soap_film(vec2 uv, float time) {
    float d = film_thickness(uv, time);
    float n = 1.33; // water
    
    // Incident angle varies across film (viewing angle)
    float theta = length(uv - 0.5) * 0.8;
    float cos_theta = cos(theta);
    
    // Sample visible spectrum
    vec3 col = vec3(0.0);
    float total_intensity = 0.0;
    
    for (float lambda = 380.0; lambda <= 780.0; lambda += 20.0) {
        float R = thin_film_reflectance(lambda, d, n, cos_theta);
        vec3 rgb = wavelength_to_rgb(lambda);
        col += rgb * R;
        total_intensity += R;
    }
    
    // Normalize and tone map
    col = col / (col + vec3(1.0)); // simple Reinhard-ish
    col = pow(col, vec3(0.85)); // gamma
    
    return col;
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;
    st.x *= u_resolution.x / u_resolution.y;
    
    // Frame the soap film
    vec2 uv = st * 0.8 + vec2(0.1, 0.1);
    
    vec3 col = vec3(0.05); // dark background
    
    // Film bounds
    float film = 1.0 - smoothstep(0.0, 0.02, sdBox(uv - 0.5, vec2(0.4, 0.35)));
    
    if (film > 0.01) {
        col = render_soap_film(uv, u_time);
        
        // Film edge meniscus: slightly thicker, brighter
        float meniscus = smoothstep(0.0, 0.03, sdBox(uv - 0.5, vec2(0.4, 0.35)));
        col += vec3(0.1, 0.1, 0.15) * meniscus;
    }
    
    // Subtle grain
    float grain = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
    col *= 0.97 + 0.03 * grain;
    
    gl_FragColor = vec4(col, 1.0);
}
