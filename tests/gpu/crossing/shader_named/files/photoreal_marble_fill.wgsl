
struct FlowShaderUniforms {
    time: f32,
    width: f32,
    height: f32,
    _pad: f32,
};

@group(0) @binding(0)
var<uniform> uniforms: FlowShaderUniforms;

struct FlowVertexOut {
    @builtin(position) position: vec4<f32>,
    @location(0) uv: vec2<f32>,
};

@vertex
fn flow_shader_vertex(@builtin(vertex_index) vid: u32) -> FlowVertexOut {
    var pos: vec2<f32>;
    if (vid == 0u) {
        pos = vec2<f32>(-1.0, -1.0);
    } else if (vid == 1u) {
        pos = vec2<f32>(3.0, -1.0);
    } else {
        pos = vec2<f32>(-1.0, 3.0);
    }

    var out: FlowVertexOut;
    out.position = vec4<f32>(pos, 0.0, 1.0);
    out.uv = vec2<f32>(pos.x * 0.5 + 0.5, 1.0 - (pos.y * 0.5 + 0.5));
    return out;
}

fn fsl_hash11(value: f32) -> f32 {
    var p = fract(value * 0.1031);
    p = p * (p + 33.33);
    p = p * (p + p);
    return fract(p);
}

fn fsl_hash21(value: vec2<f32>) -> f32 {
    var p3 = fract(vec3<f32>(value.x, value.y, value.x) * vec3<f32>(0.1031));
    let d = dot(p3, p3.yzx + vec3<f32>(33.33));
    p3 = p3 + vec3<f32>(d);
    return fract((p3.x + p3.y) * p3.z);
}

fn fsl_noise(p: vec2<f32>) -> f32 {
    let i = floor(p);
    let f = fract(p);
    let a = fsl_hash21(i);
    let b = fsl_hash21(i + vec2<f32>(1.0, 0.0));
    let c = fsl_hash21(i + vec2<f32>(0.0, 1.0));
    let d = fsl_hash21(i + vec2<f32>(1.0, 1.0));
    let u = f * f * (vec2<f32>(3.0) - vec2<f32>(2.0) * f);
    return mix(a, b, u.x) + (c - a) * u.y * (1.0 - u.x) + (d - b) * u.x * u.y;
}

fn fsl_fbm(value: vec2<f32>) -> f32 {
    var p = value;
    var v = 0.0;
    var a = 0.5;
    for (var i: i32 = 0; i < 5; i = i + 1) {
        v = v + a * fsl_noise(p);
        p = p * vec2<f32>(2.0);
        a = a * 0.5;
    }
    return v;
}

fn fsl_palette(t: f32) -> vec3<f32> {
    let a = vec3<f32>(0.5, 0.5, 0.5);
    let b = vec3<f32>(0.5, 0.5, 0.5);
    let c = vec3<f32>(1.0, 1.0, 1.0);
    let d = vec3<f32>(0.00, 0.33, 0.67);
    return a + b * cos(vec3<f32>(6.28318) * (c * vec3<f32>(t) + d));
}


fn sd_sphere(p: vec3<f32>, r: f32) -> f32 {
    return (length(p) - r);
}


fn sd_box(p: vec3<f32>, b: vec3<f32>) -> f32 {
    let q: vec3<f32> = (abs(p) - b);
    return (length(max(q, vec3<f32>(0.0))) + min(max(q.x, max(q.y, q.z)), 0.0));
}


fn sd_torus(p: vec3<f32>, major: f32, minor: f32) -> f32 {
    let q: vec2<f32> = vec2<f32>((length(p.xz) - major), p.y);
    return (length(q) - minor);
}


fn camera_ray(screen: vec2<f32>, ro: vec3<f32>, target: vec3<f32>, focal: f32) -> vec3<f32> {
    let forward: vec3<f32> = normalize((target - ro));
    let right: vec3<f32> = normalize(cross(forward, vec3<f32>(0.0, 1.0, 0.0)));
    let up: vec3<f32> = cross(right, forward);
    return normalize((((forward * focal) + (right * screen.x)) + (up * screen.y)));
}


fn env_sky(d: vec3<f32>) -> vec3<f32> {
    let h: f32 = clamp(((d.y * 0.5) + 0.5), 0.0, 1.0);
    let horizon: vec3<f32> = mix(vec3<f32>(0.72, 0.78, 0.88), vec3<f32>(0.08, 0.16, 0.30), h);
    let sun_dir: vec3<f32> = normalize(vec3<f32>((-0.45), 0.55, (-0.7)));
    let sun: f32 = pow(max(dot(d, sun_dir), 0.0), 256.0);
    let glow: f32 = pow(max(dot(d, sun_dir), 0.0), 12.0);
    return ((horizon + ((vec3<f32>(1.0, 0.72, 0.42) * glow) * 0.35)) + ((vec3<f32>(1.0, 0.92, 0.78) * sun) * 4.0));
}


fn filmic(c: vec3<f32>) -> vec3<f32> {
    let x: vec3<f32> = max(c, vec3<f32>(0.0));
    return (x / (x + vec3<f32>(1.0)));
}


fn scene_studio(p: vec3<f32>) -> vec2<f32> {
    var d: f32 = (p.y + 1.0);
    var material: f32 = 0.0;
    let sphere_d: f32 = sd_sphere((p - vec3<f32>((-0.78), (-0.12), 0.0)), 0.88);
    if ((sphere_d < d)) {
        d = sphere_d;
        material = 1.0;
    }
    let box_d: f32 = sd_box((p - vec3<f32>(0.95, (-0.42), 0.08)), vec3<f32>(0.52, 0.58, 0.52));
    if ((box_d < d)) {
        d = box_d;
        material = 2.0;
    }
    let torus_d: f32 = sd_torus((p - vec3<f32>(0.12, 0.15, (-0.9))), 0.66, 0.16);
    if ((torus_d < d)) {
        d = torus_d;
        material = 3.0;
    }
    return vec2<f32>(d, material);
}


fn studio_normal(p: vec3<f32>) -> vec3<f32> {
    let e: f32 = 0.0015;
    let dx: f32 = (scene_studio((p + vec3<f32>(e, 0.0, 0.0))).x - scene_studio((p - vec3<f32>(e, 0.0, 0.0))).x);
    let dy: f32 = (scene_studio((p + vec3<f32>(0.0, e, 0.0))).x - scene_studio((p - vec3<f32>(0.0, e, 0.0))).x);
    let dz: f32 = (scene_studio((p + vec3<f32>(0.0, 0.0, e))).x - scene_studio((p - vec3<f32>(0.0, 0.0, e))).x);
    return normalize(vec3<f32>(dx, dy, dz));
}


fn studio_shadow(ro: vec3<f32>, rd: vec3<f32>) -> f32 {
    var t: f32 = 0.025;
    var shade: f32 = 1.0;
    for (var i: i32 = i32(0.0); i < i32(28.0); i = i + 1) {
        let h: f32 = scene_studio((ro + (rd * t))).x;
        shade = min(shade, ((14.0 * h) / t));
        t = (t + clamp(h, 0.025, 0.22));
    }
    return clamp(shade, 0.0, 1.0);
}


fn studio_ao(p: vec3<f32>, n: vec3<f32>) -> f32 {
    var occ: f32 = 0.0;
    var weight: f32 = 1.0;
    for (var i: i32 = i32(1.0); i < i32(6.0); i = i + 1) {
        let h: f32 = (0.035 * f32(i));
        let sample_d: f32 = scene_studio((p + (n * h))).x;
        occ = (occ + ((h - sample_d) * weight));
        weight = (weight * 0.62);
    }
    return clamp((1.0 - (occ * 2.5)), 0.0, 1.0);
}


fn scene_orb(p: vec3<f32>) -> vec2<f32> {
    var d: f32 = (p.y + 1.05);
    var material: f32 = 0.0;
    let sphere_d: f32 = sd_sphere((p - vec3<f32>(0.0, (-0.05), 0.0)), 1.0);
    if ((sphere_d < d)) {
        d = sphere_d;
        material = 1.0;
    }
    return vec2<f32>(d, material);
}


fn orb_normal(p: vec3<f32>) -> vec3<f32> {
    let e: f32 = 0.0015;
    let dx: f32 = (scene_orb((p + vec3<f32>(e, 0.0, 0.0))).x - scene_orb((p - vec3<f32>(e, 0.0, 0.0))).x);
    let dy: f32 = (scene_orb((p + vec3<f32>(0.0, e, 0.0))).x - scene_orb((p - vec3<f32>(0.0, e, 0.0))).x);
    let dz: f32 = (scene_orb((p + vec3<f32>(0.0, 0.0, e))).x - scene_orb((p - vec3<f32>(0.0, 0.0, e))).x);
    return normalize(vec3<f32>(dx, dy, dz));
}


fn orb_shadow(ro: vec3<f32>, rd: vec3<f32>) -> f32 {
    var t: f32 = 0.025;
    var shade: f32 = 1.0;
    for (var i: i32 = i32(0.0); i < i32(24.0); i = i + 1) {
        let h: f32 = scene_orb((ro + (rd * t))).x;
        shade = min(shade, ((12.0 * h) / t));
        t = (t + clamp(h, 0.025, 0.24));
    }
    return clamp(shade, 0.0, 1.0);
}


@fragment
fn photoreal_marble_frag(in: FlowVertexOut) -> @location(0) vec4<f32> {
    let uv: vec2<f32> = in.uv;
    var color: vec4<f32> = vec4<f32>(0.0, 0.0, 0.0, 1.0);
    let raw: vec2<f32> = ((uv * 2.0) - vec2<f32>(1.0));
    let screen: vec2<f32> = vec2<f32>(((raw.x * vec2<f32>(uniforms.width, uniforms.height).x) / vec2<f32>(uniforms.width, uniforms.height).y), (-raw.y));
    let ro: vec3<f32> = vec3<f32>(3.8, 1.2, 3.4);
    let rd: vec3<f32> = camera_ray(screen, ro, vec3<f32>(0.0, (-0.22), 0.0), 1.9);
    var travel: f32 = 0.0;
    var material: f32 = (-1.0);
    var hit: bool = false;
    var active: bool = true;
    for (var i: i32 = i32(0.0); i < i32(80.0); i = i + 1) {
        if (active) {
            let sample: vec2<f32> = scene_orb((ro + (rd * travel)));
            if ((sample.x < 0.0012)) {
                material = sample.y;
                hit = true;
                active = false;
            } else {
                travel = (travel + (sample.x * 0.82));
                if ((travel > 16.0)) {
                    active = false;
                }
            }
        }
    }
    var col: vec3<f32> = env_sky(rd);
    if (hit) {
        let pos: vec3<f32> = (ro + (rd * travel));
        let n: vec3<f32> = orb_normal(pos);
        let view: vec3<f32> = normalize((ro - pos));
        let light_dir: vec3<f32> = normalize((vec3<f32>((-3.2), 5.2, 1.7) - pos));
        let shadow: f32 = orb_shadow((pos + (n * 0.012)), light_dir);
        let diffuse: f32 = (max(dot(n, light_dir), 0.0) * shadow);
        let reflected: vec3<f32> = env_sky(reflect((-view), n));
        let spec: f32 = (pow(max(dot(reflect((-light_dir), n), view), 0.0), 110.0) * shadow);
        let warp: f32 = fsl_fbm(((pos.xz * 2.4) + vec2<f32>((pos.y * 0.8), (pos.y * 0.35))));
        let veins: f32 = smoothstep(0.72, 0.92, (0.5 + (0.5 * sin((((pos.x + pos.z) * 7.0) + (warp * 14.0))))));
        var marble: vec3<f32> = mix(vec3<f32>(0.72, 0.74, 0.70), vec3<f32>(0.96, 0.95, 0.90), fsl_fbm((pos.xz * 5.0)));
        marble = mix(marble, vec3<f32>(0.18, 0.21, 0.20), (veins * 0.72));
        if ((material < 0.5)) {
            let tile: f32 = ((floor((pos.x * 1.25)) + floor((pos.z * 1.25))) % 2.0);
            marble = mix((marble * 0.45), (marble * 0.75), tile);
        }
        let fresnel: f32 = (0.035 + (0.965 * pow((1.0 - max(dot(n, view), 0.0)), 5.0)));
        col = (((marble * (0.11 + (diffuse * 1.4))) + (reflected * (0.10 + (fresnel * 0.34)))) + (vec3<f32>(spec) * 0.9));
    }
    color = vec4<f32>(filmic(col), 1.0);
    return color;
}
