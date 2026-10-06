#!/usr/bin/env node
// Builds a browser-consumable WGSL module and reflection directly from Flow.
// No WebGPU shader source is handwritten or substituted here.
import {spawnSync} from "node:child_process";
import {mkdirSync,writeFileSync} from "node:fs";
import {join} from "node:path";

const example="examples/gpu/vgpu/copy_graph.flow";
const run=spawnSync("./flow",["run",example],{
    cwd:process.cwd(),encoding:"utf8",timeout:120000
});
if(run.error || run.status !== 0){
    console.error(run.error?.message ?? run.stderr ?? run.stdout);
    process.exit(1);
}
const stdout=run.stdout;
function between(a,b) {
    const start=stdout.indexOf(a);
    if(start<0)throw new Error("Flow output lacks "+a);
    const lo=start+a.length;
    const hi=stdout.indexOf(b,lo);
    if(hi<0)throw new Error("Flow output lacks "+b);
    const content=stdout.slice(lo,hi).trim();
    if(!content)throw new Error("Flow emitted empty "+a);
    return content;
}
const wgsl=between("FLOW_WGSL_BEGIN","FLOW_WGSL_END");
const reflection=between("FLOW_REFLECTION_BEGIN","FLOW_REFLECTION_END");
const kernel=JSON.parse(reflection);
if(kernel.entryPoint!=="copy_f32" || kernel.workgroupSize!==64 ||
   kernel.buffers?.length!==2) {
    throw new Error("unrecognised Flow GPU reflection");
}
const destination=join("site","wasm-crossings","gpu","generated");
mkdirSync(destination,{recursive:true});
writeFileSync(join(destination,"copy_f32.wgsl"),wgsl+"\n");
writeFileSync(join(destination,"copy_f32.json"),
    JSON.stringify(kernel,null,2)+"\n");
console.log("Flow GPU compute graph exported to "+destination);
