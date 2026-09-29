// Generated from Flow @gpu function `control` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read> a: array<f32>;
@group(0) @binding(1) var<storage, read_write> out: array<f32>;

struct Params {
    n: i32,
    flag: bool,
    _pad0: u32,
    _pad1: u32,
};
@group(0) @binding(2) var<uniform> params: Params;

@compute @workgroup_size(64)
fn control(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    let i: i32 = tid;
    var acc: f32 = 0.0;
    var k: i32 = 0;
    let h: i32 = 16;
    let t: bool = true;
    if (((i < params.n) && params.flag)) {
        acc = (acc + a[i]);
    } else if (((i == params.n) || (!params.flag))) {
        acc = 1.5e3;
    } else if ((!t)) {
        acc = (-acc);
    } else {
        acc = 2.0;
    }
    if ((i >= params.n)) {
        return;
    }
    while ((k < 4)) {
        k = (k + 1);
        acc = (acc * 2.0);
    }
    for (var s: i32 = 0; s < params.n; s = s + 2) {
        acc = (acc - 0.25);
    }
    for (var q: i32 = 1; q < 10; q = q + 1) {
        acc = (acc + 1.0);
    }
    out[i] = (((sqrt(abs(acc)) + sin(acc)) + floor(acc)) + max(acc, 1.0));
    workgroupBarrier();
    let x: i32 = (((i32(global_id.x) + i32(group_id.y)) + i32(local_id.x)) + WORKGROUP_SIZE);
}
