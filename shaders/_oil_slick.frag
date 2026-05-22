// PHENOMENON: Oil slick on water — thickness topology as color map
// THICKNESS: 50nm - 800nm
// INDEX: n_oil = 1.4 - 1.5

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

float thin_film_reflectance(float lambda, float d, float n, float cos_theta) {
    float delta = 4.0 * 3.14159265 * n * d * cos_theta / lambda;
    float r1 = pow((1.0 - n) / (1.0 + n), 2.0);
    float r2 = pow((n - 1.0) / (n + 1.0), 2.0);
    float R = r1 + r2 - 2.0 * sqrt(r1 * r2) * cos(delta);
    R /= (1.0 + r1 * r2 - 2.0 * sqrt(r1 * r2) * cos(delta));
    return R;
}

// Oil thickness: spreading, thinning at edges
float oil_thickness(vec2 uv, float time) {
    // Radial spread from center
    float dist = length(uv - 0.5);
    float spread = 0.3 + time * 0.02; // growing radius
    
    // Thickness profile: thick center, thin edges
    float base = 600.0 * (1.0 - smoothstep(0.0, spread, dist));
    
    // Irregular edges: fingering instability
    float fingers = sin(atan(uv.y - 0.5, uv.x - 0.5) * 8.0 + hash(floor(uv * 10.0)) * 10.0);
    base += fingers * 100.0 * smoothstep(spread * 0.5, spread, dist);
    
    // Thin film "holes"
    float hole = smoothstep(0.4, 0.5, hash(floor(uv * 30.0)));
    base *= hole;
    
    return max(base, 30.0);
}

void main() {
    vec2 st = gl_FragCoord.xy / u_resolution.xy;
    st.x *= u_resolution.x / u_resolution.y;
    
    vec2 uv = st * 0.8 + vec2(0.1);
    
    // Water background
    vec3 water = vec3(0.05, 0.15, 0.25);
    float water_ripple = sin(uv.x * 20.0 + u_time) * 0.02;
    water += vec3(0.02, 0.03, 0.04) * water_ripple;
    
    vec3 col = water;
    
    // Oil film
    float d = oil_thickness(uv, u_time);
    float n = 1.45;
    float theta = length(uv - 0.5) * 1.2;
    float cos_theta = cos(theta);
    
    vec3 film_col = vec3(0.0);
    for (float lambda = 380.0; lambda <= 780.0; lambda += 20.0) {
        float R = thin_film_reflectance(lambda, d, n, cos_theta);
        film_col += wavelength_to_rgb(lambda) * R;
    }
    film_col = film_col / (film_col + vec3(1.0));
    film_col = pow(film_col, vec3(0.85));
    
    // Oil coverage mask
    float oil_mask = smoothstep(0.0, 0.02, d - 40.0);
    col = mix(col, film_col, oil_mask);
    
    // Specular highlight on oil
    float spec = pow(max(cos(theta * 2.0), 0.0), 32.0);
    col += vec3(0.5, 0.4, 0.3) * spec * oil_mask;
    
    gl_FragColor = vec4(col, 1.0);
}
