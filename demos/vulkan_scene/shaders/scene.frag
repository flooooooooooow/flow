#version 450

layout(location = 0) in vec3 vColor;
layout(location = 1) in vec2 vUV;

layout(location = 0) out vec4 outColor;

layout(set = 0, binding = 1) uniform sampler2D texSampler[2];

layout(push_constant) uniform PushConstants {
    vec4 color;
    int texIndex;
    vec4 meshOffset;
} pc;

void main() {
    int idx = clamp(pc.texIndex, 0, 1);
    vec4 tex = texture(texSampler[idx], vUV);
    outColor = vec4(vColor, 1.0) * tex * pc.color;
}
