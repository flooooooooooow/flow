#!/usr/bin/env node
// Exports shaders emitted by the Flow P1 GPU stage library. No shader
// body is regenerated or substituted by JavaScript.
import {spawnSync} from "node:child_process";
import {mkdirSync,writeFileSync} from "node:fs";
import {join} from "node:path";

const result=spawnSync("./flow",["run","examples/gpu/vgpu/sampled_quad.flow"],{
    cwd:process.cwd(),encoding:"utf8",timeout:120000
});
if(result.error || result.status!==0){
    console.error(result.error?.message??result.stderr??result.stdout);
    process.exit(1);
}
function extract(begin,end){
    const start=result.stdout.indexOf(begin);
    if(start<0)throw new Error("Flow did not emit "+begin);
    const from=start+begin.length;
    const stop=result.stdout.indexOf(end,from);
    if(stop<0)throw new Error("Flow did not emit "+end);
    const text=result.stdout.slice(from,stop).trim();
    if(!text)throw new Error("Flow emitted an empty shader");
    return text+"\n";
}
const wgsl=extract("FLOW_SAMPLED_WGSL_BEGIN","FLOW_SAMPLED_WGSL_END");
const metal=extract("FLOW_SAMPLED_METAL_BEGIN","FLOW_SAMPLED_METAL_END");
if(!wgsl.includes("@vertex fn scene_vs") ||
   !wgsl.includes("@fragment fn scene_fs") ||
   !wgsl.includes("textureSample(") ||
   !metal.includes("vertex VSOut scene_vs") ||
   !metal.includes("fragment float4 scene_fs")){
    throw new Error("Flow stage emission did not contain required entry points");
}
const dir=join("site","wasm-crossings","gpu","generated");
mkdirSync(dir,{recursive:true});
writeFileSync(join(dir,"sampled_quad.wgsl"),wgsl);
writeFileSync(join(dir,"sampled_quad.metal"),metal);
console.log("Exported Flow sampled-quad shaders to "+dir);
