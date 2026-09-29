// Generated from Flow @gpu function `reserved_names` by tools/gpu/main.flow
const WORKGROUP_SIZE: i32 = 64;

@group(0) @binding(0) var<storage, read> loop_: array<f32>;
@group(0) @binding(1) var<storage, read_write> ref_: array<f32>;

struct Params {
    target_: i32,
    __tmp_: i32,
    switch_: i32,
    _pad0: u32,
};
@group(0) @binding(2) var<uniform> params: Params;

@compute @workgroup_size(64)
fn reserved_names(
    @builtin(global_invocation_id) global_id: vec3<u32>,
    @builtin(workgroup_id) group_id: vec3<u32>,
    @builtin(local_invocation_id) local_id: vec3<u32>,
) {
    let tid: i32 = i32(global_id.x);
    let filter_: i32 = (params.target_ + params.__tmp_);
    var self_: f32 = 0.0;
    ref_[filter_] = loop_[(filter_ + params.switch_)];
}
