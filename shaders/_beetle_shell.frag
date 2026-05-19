// FILM: Multi-layer beetle shell — 5-10 layers of chitin, melanin, and air
// THICKNESS: 100nm - 500nm per layer, total stack ~1-2µm
// INDEX: n_chitin = 1.56, n_melanin = 2.0, n_air = 1.0
// PHENOMENON: Structural color, metallic angle-dependent iridescence

precision highp float;

uniform vec2 u_resolution;
uniform float u_time;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

vec3 wavelength_to_rgb(float lambda) {
    vec3 col = vec3(0.0);
    col.r = exp(-pow(lambda - 570.0, 2.0) / 2000.0) + 0.3 * exp(-pow(lambda - 610.0, 2.0) / 1500.0);
    col.g = exp(-pow(lambda - 545.0, 2.0) / 1500.0);
    col.b = exp(-pow(lambda - 440.0, 2.0) / 1800.0);
    return col;
}

// Transfer matrix method for multi-layer thin film
// Returns reflectance for given wavelength and angle
float multilayer_reflectance(float lambda, float d_chitin, float d_air, float n_chitin, float n_air, float theta) {
    // Simplified: treat as effective medium with periodic structure
    // Actual transfer matrix is complex; approximate with interference from effective path
    
    float n_eff = sqrt(n_chitin * n_air); // geometric mean approximation
    float d_period = d_chitin + d_air;
    
    float delta = 4.0 * 3.14159265 * n_eff * d_period * cos(theta) / lambda;
    
    // Fresnel at each interface
    float r1 = pow((1.0 - n_chitin) / (1.0 + n_chitin), 2.0);
    float r2 = pow((n_chitin - n_air) / (n_chitin + n_air), 2.0);
    float r3 = pow((n_air - 1.0) / (n_air + 1.0), 2.0);
    
    // Multiple reflections (simplified)
    float R = r1 + r2 * (1.0 - r1) * (1.0 - r1) + r3 * (1.0 - r1) * (1.0 - r2);
    
    // Interference modulation
    R *= 0.5 + 0.5 * cos(delta);
    
    return R;
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;
    st.x *= u_resolution.x / u_resolution.y;
    
    // Beetle shell surface: curved, segmented
    vec2 uv = st * 1.2;
    float segment = floor(uv.x * 3.0);
    float local_x = fract(uv.x * 3.0) - 0.5;
    
    // Curvature per segment
    float curve = local_x * local_x * 2.0;
    uv.y += curve;
    
    // Shell texture: micro-pillars create matte vs glossy regions
    float micro = hash(floor(uv * 50.0));
    float gloss = smoothstep(0.3, 0.7, micro);
    
    // Angle of incidence varies across curvature
    float theta = abs(local_x) * 1.5 + length(st - 0.5) * 0.3;
    float cos_theta = cos(theta);
    
    // Layer thickness varies: thicker in center of segment, thinner at edges
    float d_chitin = 120.0 + 30.0 * (1.0 - abs(local_x) * 2.0); // nm
    float d_air = 80.0 + 20.0 * sin(segment * 3.0);
    
    vec3 col = vec3(0.0);
    for (float lambda = 380.0; lambda <= 780.0; lambda += 15.0) {
        float R = multilayer_reflectance(lambda, d_chitin, d_air, 1.56, 1.0, theta);
        col += wavelength_to_rgb(lambda) * R;
    }
    
    col = col / (col + vec3(0.8));
    col = pow(col, vec3(0.9));
    
    // Metallic quality: high specularity
    float spec = pow(max(cos(theta * 2.0), 0.0), 16.0);
    col += vec3(0.6, 0.5, 0.4) * spec * gloss;
    
    // Segment boundary: dark suture line
    float suture = smoothstep(0.45, 0.48, abs(local_x));
    col *= 1.0 - suture * 0.3;
    
    // Micro-pillar matte regions
    col *= 0.7 + 0.3 * gloss;
    
    gl_FragColor = vec4(col, 1.0);
}
