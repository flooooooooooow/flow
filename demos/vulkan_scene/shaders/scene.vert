#version 450

layout(location = 0) in vec3 inPos;
layout(location = 1) in vec3 inColor;
layout(location = 2) in vec2 inUV;
layout(location = 3) in vec3 inInstanceOffset;
layout(location = 4) in float inInstanceScale;

layout(location = 0) out vec3 vColor;
layout(location = 1) out vec2 vUV;

layout(set = 0, binding = 0) uniform UBO {
    mat4 view;
    mat4 proj;
    mat4 model;
} ubo;

layout(push_constant) uniform PushConstants {
    vec4 color;
    int texIndex;
    vec4 meshOffset;
} pc;

void main() {
    vec3 pos = inPos * inInstanceScale + inInstanceOffset + pc.meshOffset.xyz;
    gl_Position = ubo.proj * ubo.view * ubo.model * vec4(pos, 1.0);
    vColor = inColor;
    vUV = inUV;
}
